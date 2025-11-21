import os
from typing import List, Optional
from datetime import datetime
from domain_checker import DomainResult

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

class DatabaseHandler:
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.enabled = False

        if SUPABASE_AVAILABLE:
            url = os.getenv('VITE_SUPABASE_URL')
            key = os.getenv('VITE_SUPABASE_ANON_KEY')

            if url and key:
                try:
                    self.supabase = create_client(url, key)
                    self.enabled = True
                except Exception as e:
                    print(f"Warning: Could not connect to Supabase: {e}")

    def is_enabled(self) -> bool:
        return self.enabled

    async def save_scan(self, results: List[DomainResult], scan_name: str = None) -> Optional[str]:
        if not self.enabled:
            return None

        try:
            scan_data = {
                'scan_name': scan_name or f"Scan {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                'total_domains': len(results),
                'successful': len([r for r in results if r.status_code and not r.error]),
                'failed': len([r for r in results if r.error]),
                'created_at': datetime.now().isoformat()
            }

            scan_response = self.supabase.table('scans').insert(scan_data).execute()

            if scan_response.data:
                scan_id = scan_response.data[0]['id']

                domain_results = []
                for result in results:
                    domain_results.append({
                        'scan_id': scan_id,
                        'domain': result.domain,
                        'status_code': result.status_code,
                        'response_time_ms': round(result.response_time * 1000, 2) if result.response_time else None,
                        'protocol_used': result.protocol_used,
                        'server_info': result.server_info,
                        'has_ssl': bool(result.ssl_info and not result.ssl_info.get('error')),
                        'redirect_count': len(result.redirect_history),
                        'error': result.error,
                        'final_url': result.final_url,
                        'security_headers': result.security_headers,
                        'created_at': result.timestamp.isoformat()
                    })

                self.supabase.table('domain_results').insert(domain_results).execute()

                return scan_id

        except Exception as e:
            print(f"Warning: Could not save to database: {e}")
            return None

    def get_scan_history(self, limit: int = 10):
        if not self.enabled:
            return []

        try:
            response = self.supabase.table('scans').select('*').order('created_at', desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Warning: Could not fetch scan history: {e}")
            return []

    def get_scan_results(self, scan_id: str):
        if not self.enabled:
            return []

        try:
            response = self.supabase.table('domain_results').select('*').eq('scan_id', scan_id).execute()
            return response.data
        except Exception as e:
            print(f"Warning: Could not fetch scan results: {e}")
            return []

    def compare_scans(self, scan_id1: str, scan_id2: str):
        if not self.enabled:
            return None

        try:
            results1 = self.get_scan_results(scan_id1)
            results2 = self.get_scan_results(scan_id2)

            domains1 = {r['domain']: r for r in results1}
            domains2 = {r['domain']: r for r in results2}

            changes = {
                'status_changes': [],
                'new_errors': [],
                'resolved_errors': [],
                'performance_changes': []
            }

            for domain in set(domains1.keys()) | set(domains2.keys()):
                r1 = domains1.get(domain)
                r2 = domains2.get(domain)

                if r1 and r2:
                    if r1['status_code'] != r2['status_code']:
                        changes['status_changes'].append({
                            'domain': domain,
                            'old_status': r1['status_code'],
                            'new_status': r2['status_code']
                        })

                    if not r1['error'] and r2['error']:
                        changes['new_errors'].append({
                            'domain': domain,
                            'error': r2['error']
                        })

                    if r1['error'] and not r2['error']:
                        changes['resolved_errors'].append({
                            'domain': domain,
                            'previous_error': r1['error']
                        })

                    if r1['response_time_ms'] and r2['response_time_ms']:
                        time_diff = r2['response_time_ms'] - r1['response_time_ms']
                        if abs(time_diff) > 100:
                            changes['performance_changes'].append({
                                'domain': domain,
                                'old_time': r1['response_time_ms'],
                                'new_time': r2['response_time_ms'],
                                'difference': time_diff
                            })

            return changes

        except Exception as e:
            print(f"Warning: Could not compare scans: {e}")
            return None
