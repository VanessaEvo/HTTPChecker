import json
import csv
from typing import List
from datetime import datetime
from domain_checker import DomainResult

class Reporter:
    @staticmethod
    def generate_text_report(results: List[DomainResult], file_path: str):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("HTTP CHECKER REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Domains Checked: {len(results)}\n")
            f.write("="*80 + "\n\n")

            stats = Reporter._calculate_stats(results)
            f.write("SUMMARY STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Success Rate: {stats['success_rate']:.2f}%\n")
            f.write(f"Average Response Time: {stats['avg_response_time']:.2f}ms\n")
            f.write(f"Fastest Response: {stats['min_response_time']:.2f}ms\n")
            f.write(f"Slowest Response: {stats['max_response_time']:.2f}ms\n")
            f.write(f"Total Errors: {stats['error_count']}\n")
            f.write(f"Total Redirects: {stats['redirect_count']}\n")
            f.write(f"HTTPS Success: {stats['https_count']}\n")
            f.write(f"HTTP Fallback: {stats['http_count']}\n\n")

            f.write("="*80 + "\n")
            f.write("DETAILED RESULTS\n")
            f.write("="*80 + "\n\n")

            for result in results:
                f.write(f"Domain: {result.domain}\n")
                f.write(f"Status Code: {result.status_code or 'N/A'}\n")
                f.write(f"Protocol Used: {result.protocol_used or 'N/A'}\n")

                if result.error:
                    f.write(f"Error: {result.error}\n")
                else:
                    f.write(f"Response Time: {result.response_time*1000:.2f}ms\n")
                    f.write(f"DNS Resolution Time: {result.dns_time*1000:.2f}ms\n" if result.dns_time else "")
                    f.write(f"Connection Time: {result.connection_time*1000:.2f}ms\n" if result.connection_time else "")
                    f.write(f"Server: {result.server_info}\n")
                    f.write(f"Final URL: {result.final_url}\n")

                    if result.redirect_history:
                        f.write(f"Redirects ({len(result.redirect_history)}):\n")
                        for i, redirect in enumerate(result.redirect_history, 1):
                            f.write(f"  {i}. [{redirect['status']}] {redirect['url']}\n")

                    if result.ssl_info and not result.ssl_info.get('error'):
                        f.write("SSL Certificate Info:\n")
                        f.write(f"  Version: {result.ssl_info.get('version', 'N/A')}\n")
                        f.write(f"  Cipher: {result.ssl_info.get('cipher', 'N/A')}\n")
                        f.write(f"  Valid Until: {result.ssl_info.get('valid_until', 'N/A')}\n")

                    if result.security_headers:
                        f.write("Security Headers:\n")
                        for header, value in result.security_headers.items():
                            f.write(f"  {header}: {value}\n")

                    if result.headers:
                        f.write("Response Headers:\n")
                        for key, value in list(result.headers.items())[:10]:
                            f.write(f"  {key}: {value}\n")

                f.write("-"*80 + "\n\n")

    @staticmethod
    def generate_json_report(results: List[DomainResult], file_path: str):
        data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_domains': len(results),
                'statistics': Reporter._calculate_stats(results)
            },
            'results': [result.to_dict() for result in results]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def generate_csv_report(results: List[DomainResult], file_path: str):
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'domain', 'status_code', 'protocol_used', 'response_time_ms',
                'dns_time_ms', 'connection_time_ms', 'server_info', 'final_url',
                'redirect_count', 'ssl_valid_until', 'has_hsts', 'has_csp',
                'error', 'timestamp'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                writer.writerow({
                    'domain': result.domain,
                    'status_code': result.status_code or 'N/A',
                    'protocol_used': result.protocol_used or 'N/A',
                    'response_time_ms': round(result.response_time * 1000, 2) if result.response_time else 'N/A',
                    'dns_time_ms': round(result.dns_time * 1000, 2) if result.dns_time else 'N/A',
                    'connection_time_ms': round(result.connection_time * 1000, 2) if result.connection_time else 'N/A',
                    'server_info': result.server_info or 'N/A',
                    'final_url': result.final_url or 'N/A',
                    'redirect_count': len(result.redirect_history),
                    'ssl_valid_until': result.ssl_info.get('valid_until', 'N/A') if result.ssl_info else 'N/A',
                    'has_hsts': 'Yes' if 'Strict-Transport-Security' in result.security_headers else 'No',
                    'has_csp': 'Yes' if 'Content-Security-Policy' in result.security_headers else 'No',
                    'error': result.error or 'None',
                    'timestamp': result.timestamp.isoformat()
                })

    @staticmethod
    def generate_html_report(results: List[DomainResult], file_path: str):
        stats = Reporter._calculate_stats(results)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTTP Checker Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
               background: #f5f7fa; color: #2c3e50; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
                  padding: 40px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                  gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 25px; border-radius: 8px;
                     box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-card h3 {{ color: #667eea; font-size: 0.9em; margin-bottom: 10px; text-transform: uppercase; }}
        .stat-card .value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        table {{ width: 100%; background: white; border-collapse: collapse; border-radius: 8px;
                 overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: #667eea; color: white; padding: 15px; text-align: left; font-weight: 600; }}
        td {{ padding: 12px 15px; border-bottom: 1px solid #ecf0f1; }}
        tr:hover {{ background: #f8f9fa; }}
        .status-success {{ color: #27ae60; font-weight: bold; }}
        .status-error {{ color: #e74c3c; font-weight: bold; }}
        .status-redirect {{ color: #f39c12; font-weight: bold; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 600; }}
        .badge-https {{ background: #d4edda; color: #155724; }}
        .badge-http {{ background: #fff3cd; color: #856404; }}
        .filter-buttons {{ margin-bottom: 20px; }}
        .filter-btn {{ padding: 10px 20px; margin-right: 10px; background: white; border: 2px solid #667eea;
                      color: #667eea; border-radius: 5px; cursor: pointer; font-weight: 600; }}
        .filter-btn.active {{ background: #667eea; color: white; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>HTTP Checker Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Total Domains: {len(results)}</p>
        </header>

        <div class="stats">
            <div class="stat-card">
                <h3>Success Rate</h3>
                <div class="value">{stats['success_rate']:.1f}%</div>
            </div>
            <div class="stat-card">
                <h3>Avg Response Time</h3>
                <div class="value">{stats['avg_response_time']:.0f}ms</div>
            </div>
            <div class="stat-card">
                <h3>Total Errors</h3>
                <div class="value">{stats['error_count']}</div>
            </div>
            <div class="stat-card">
                <h3>HTTPS Success</h3>
                <div class="value">{stats['https_count']}</div>
            </div>
            <div class="stat-card">
                <h3>Total Redirects</h3>
                <div class="value">{stats['redirect_count']}</div>
            </div>
            <div class="stat-card">
                <h3>Fastest Response</h3>
                <div class="value">{stats['min_response_time']:.0f}ms</div>
            </div>
        </div>

        <div class="filter-buttons">
            <button class="filter-btn active" onclick="filterTable('all')">All</button>
            <button class="filter-btn" onclick="filterTable('success')">Success</button>
            <button class="filter-btn" onclick="filterTable('error')">Errors</button>
            <button class="filter-btn" onclick="filterTable('redirect')">Redirects</button>
        </div>

        <table id="resultsTable">
            <thead>
                <tr>
                    <th>Domain</th>
                    <th>Status</th>
                    <th>Protocol</th>
                    <th>Response Time</th>
                    <th>Server</th>
                    <th>Redirects</th>
                    <th>Security</th>
                </tr>
            </thead>
            <tbody>
"""

        for result in results:
            status_class = 'status-success' if result.status_code and 200 <= result.status_code < 300 else 'status-error'
            if result.redirect_history:
                status_class = 'status-redirect'

            row_class = 'error' if result.error else ('redirect' if result.redirect_history else 'success')

            html += f"""
                <tr class="row-{row_class}">
                    <td><strong>{result.domain}</strong></td>
                    <td class="{status_class}">{result.status_code or 'Error'}</td>
                    <td>"""

            if result.protocol_used:
                badge_class = 'badge-https' if result.protocol_used == 'https' else 'badge-http'
                html += f'<span class="badge {badge_class}">{result.protocol_used.upper()}</span>'
            else:
                html += 'N/A'

            html += f"""</td>
                    <td>{round(result.response_time * 1000, 2) if result.response_time else 'N/A'}ms</td>
                    <td>{result.server_info or 'N/A'}</td>
                    <td>{len(result.redirect_history) if result.redirect_history else '0'}</td>
                    <td>"""

            security_badges = []
            if result.security_headers.get('Strict-Transport-Security'):
                security_badges.append('HSTS')
            if result.security_headers.get('Content-Security-Policy'):
                security_badges.append('CSP')

            html += ', '.join(security_badges) if security_badges else 'None'

            html += "</td></tr>"

        html += """
            </tbody>
        </table>
    </div>

    <script>
        function filterTable(filter) {
            const rows = document.querySelectorAll('#resultsTable tbody tr');
            const buttons = document.querySelectorAll('.filter-btn');

            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');

            rows.forEach(row => {
                if (filter === 'all') {
                    row.style.display = '';
                } else if (row.classList.contains('row-' + filter)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)

    @staticmethod
    def _calculate_stats(results: List[DomainResult]) -> dict:
        successful_results = [r for r in results if r.status_code and not r.error]
        response_times = [r.response_time * 1000 for r in successful_results if r.response_time]

        stats = {
            'success_rate': (len(successful_results) / len(results) * 100) if results else 0,
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'error_count': len([r for r in results if r.error]),
            'redirect_count': sum(len(r.redirect_history) for r in results),
            'https_count': len([r for r in results if r.protocol_used == 'https']),
            'http_count': len([r for r in results if r.protocol_used == 'http'])
        }

        return stats

    @staticmethod
    def print_progress(current: int, total: int, result: DomainResult):
        percentage = (current / total) * 100
        status = f"[{result.status_code}]" if result.status_code else "[ERROR]"
        time_str = f"{result.response_time*1000:.0f}ms" if result.response_time else "N/A"

        bar_length = 40
        filled = int(bar_length * current / total)
        bar = '█' * filled + '░' * (bar_length - filled)

        print(f'\r[{bar}] {percentage:.1f}% | {status} {result.domain} - {time_str}', end='', flush=True)

        if current == total:
            print()
