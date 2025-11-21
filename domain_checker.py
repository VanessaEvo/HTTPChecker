import asyncio
import aiohttp
import ssl
import socket
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import certifi

class DomainResult:
    def __init__(self, domain: str):
        self.domain = domain
        self.status_code = None
        self.headers = {}
        self.redirect_history = []
        self.response_time = None
        self.dns_time = None
        self.connection_time = None
        self.ssl_info = {}
        self.error = None
        self.protocol_used = None
        self.server_info = None
        self.security_headers = {}
        self.timestamp = datetime.now()
        self.final_url = None

    def to_dict(self) -> Dict:
        return {
            'domain': self.domain,
            'status_code': self.status_code,
            'headers': dict(self.headers) if self.headers else {},
            'redirect_history': self.redirect_history,
            'response_time_ms': round(self.response_time * 1000, 2) if self.response_time else None,
            'dns_time_ms': round(self.dns_time * 1000, 2) if self.dns_time else None,
            'connection_time_ms': round(self.connection_time * 1000, 2) if self.connection_time else None,
            'ssl_info': self.ssl_info,
            'error': self.error,
            'protocol_used': self.protocol_used,
            'server_info': self.server_info,
            'security_headers': self.security_headers,
            'timestamp': self.timestamp.isoformat(),
            'final_url': self.final_url
        }

class DomainChecker:
    def __init__(self, timeout: int = 10, max_retries: int = 2,
                 user_agent: str = None, verify_ssl: bool = True):
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent or 'HTTPChecker/2.0 (https://github.com/VanessaEvo/HTTPChecker)'
        self.verify_ssl = verify_ssl

    async def check_domain(self, domain: str, semaphore: asyncio.Semaphore) -> DomainResult:
        async with semaphore:
            result = DomainResult(domain)

            for attempt in range(self.max_retries + 1):
                try:
                    result = await self._check_with_protocol(domain, 'https', result)
                    if result.error and 'SSL' not in result.error:
                        result = await self._check_with_protocol(domain, 'http', result)
                    break
                except Exception as e:
                    if attempt == self.max_retries:
                        result.error = f"Max retries exceeded: {str(e)}"
                    else:
                        await asyncio.sleep(2 ** attempt)

            return result

    async def _check_with_protocol(self, domain: str, protocol: str, result: DomainResult) -> DomainResult:
        url = f"{protocol}://{domain}"
        start_time = asyncio.get_event_loop().time()

        dns_start = asyncio.get_event_loop().time()
        try:
            socket.gethostbyname(domain)
            result.dns_time = asyncio.get_event_loop().time() - dns_start
        except socket.gaierror:
            result.error = "DNS resolution failed"
            return result

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        if not self.verify_ssl:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        headers = {'User-Agent': self.user_agent}

        try:
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                conn_start = asyncio.get_event_loop().time()
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    result.connection_time = asyncio.get_event_loop().time() - conn_start
                    result.response_time = asyncio.get_event_loop().time() - start_time
                    result.status_code = response.status
                    result.headers = dict(response.headers)
                    result.protocol_used = protocol
                    result.final_url = str(response.url)

                    result.redirect_history = []
                    for redirect in response.history:
                        result.redirect_history.append({
                            'status': redirect.status,
                            'url': str(redirect.url)
                        })

                    result.server_info = response.headers.get('Server', 'Unknown')

                    result.security_headers = self._extract_security_headers(response.headers)

                    if protocol == 'https':
                        result.ssl_info = await self._get_ssl_info(domain)

                    result.error = None

        except aiohttp.ClientSSLError as e:
            result.error = f"SSL error: {str(e)}"
        except aiohttp.ClientConnectorError as e:
            result.error = f"Connection error: {str(e)}"
        except asyncio.TimeoutError:
            result.error = "Request timed out"
        except Exception as e:
            result.error = f"Request exception: {str(e)}"

        return result

    def _extract_security_headers(self, headers: Dict) -> Dict:
        security_headers = {}
        important_headers = [
            'Strict-Transport-Security',
            'Content-Security-Policy',
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Referrer-Policy',
            'Permissions-Policy'
        ]

        for header in important_headers:
            if header in headers:
                security_headers[header] = headers[header]

        return security_headers

    async def _get_ssl_info(self, domain: str) -> Dict:
        ssl_info = {}
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    ssl_info['version'] = ssock.version()
                    ssl_info['cipher'] = ssock.cipher()[0] if ssock.cipher() else 'Unknown'

                    if cert:
                        ssl_info['subject'] = dict(x[0] for x in cert.get('subject', []))
                        ssl_info['issuer'] = dict(x[0] for x in cert.get('issuer', []))
                        ssl_info['valid_from'] = cert.get('notBefore', 'Unknown')
                        ssl_info['valid_until'] = cert.get('notAfter', 'Unknown')
                        ssl_info['serial_number'] = cert.get('serialNumber', 'Unknown')
        except Exception as e:
            ssl_info['error'] = str(e)

        return ssl_info

    async def check_domains_batch(self, domains: List[str],
                                  max_concurrent: int = 10,
                                  progress_callback=None) -> List[DomainResult]:
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = []

        for domain in domains:
            task = self.check_domain(domain, semaphore)
            tasks.append(task)

        results = []
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            results.append(result)
            if progress_callback:
                progress_callback(i + 1, len(domains), result)

        return results
