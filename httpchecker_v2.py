import asyncio
import argparse
import sys
import os
from pathlib import Path
import pyfiglet
from domain_checker import DomainChecker
from reporter import Reporter
from db_handler import DatabaseHandler

def print_banner():
    ascii_banner = pyfiglet.figlet_format("HTTP Checker v2.0")
    print(ascii_banner)
    print("https://github.com/VanessaEvo/HTTPChecker")
    print("="*80)
    print()

def validate_domain(domain: str) -> str:
    domain = domain.strip()
    if domain.startswith('http://') or domain.startswith('https://'):
        domain = domain.split('://', 1)[1]
    if '/' in domain:
        domain = domain.split('/')[0]
    return domain

def load_domains(file_path: str) -> list:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            domains = [validate_domain(line) for line in f.read().splitlines() if line.strip()]
            domains = list(set(domains))
            return domains
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Advanced HTTP Status Checker with SSL verification, performance metrics, and detailed reporting.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Check domains from a file and save as text:
    python httpchecker_v2.py -i domains.txt -o results.txt

  Check with JSON output and 20 concurrent requests:
    python httpchecker_v2.py -i domains.txt -o results.json -f json -c 20

  Check a single domain with detailed output:
    python httpchecker_v2.py -d example.com -o result.txt -v

  Generate HTML report with database tracking:
    python httpchecker_v2.py -i domains.txt -o report.html -f html --save-db

  Compare two previous scans:
    python httpchecker_v2.py --compare scan1_id scan2_id

  Show scan history:
    python httpchecker_v2.py --history

For more information, visit: https://github.com/VanessaEvo/HTTPChecker
        """
    )

    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument('-i', '--input', type=str,
                            help='Path to file containing list of domains (one per line)')
    input_group.add_argument('-d', '--domain', type=str,
                            help='Single domain to check')

    parser.add_argument('-o', '--output', type=str,
                       help='Path to save the results')

    parser.add_argument('-f', '--format', type=str, choices=['text', 'json', 'csv', 'html'],
                       default='text', help='Output format (default: text)')

    parser.add_argument('-c', '--concurrent', type=int, default=10,
                       help='Maximum concurrent requests (default: 10)')

    parser.add_argument('-t', '--timeout', type=int, default=10,
                       help='Request timeout in seconds (default: 10)')

    parser.add_argument('-r', '--retries', type=int, default=2,
                       help='Maximum retry attempts (default: 2)')

    parser.add_argument('--user-agent', type=str,
                       help='Custom User-Agent header')

    parser.add_argument('--no-ssl-verify', action='store_true',
                       help='Disable SSL certificate verification')

    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')

    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Suppress progress output')

    parser.add_argument('--save-db', action='store_true',
                       help='Save results to Supabase database for historical tracking')

    parser.add_argument('--scan-name', type=str,
                       help='Custom name for this scan (used with --save-db)')

    parser.add_argument('--history', action='store_true',
                       help='Show previous scan history from database')

    parser.add_argument('--compare', nargs=2, metavar=('SCAN_ID1', 'SCAN_ID2'),
                       help='Compare two previous scans from database')

    parser.add_argument('--show-scan', type=str, metavar='SCAN_ID',
                       help='Show results from a specific scan')

    parser.add_argument('--no-banner', action='store_true',
                       help='Hide the ASCII banner')

    args = parser.parse_args()

    if not args.history and not args.compare and not args.show_scan:
        if not args.input and not args.domain:
            parser.error('Either --input/-i or --domain/-d is required')
        if not args.output and not args.quiet:
            parser.error('--output/-o is required unless using --quiet mode')

    return args

async def main():
    args = parse_arguments()

    if not args.no_banner:
        print_banner()

    db_handler = DatabaseHandler()

    if args.history:
        if not db_handler.is_enabled():
            print("Error: Database is not configured. Cannot show history.")
            sys.exit(1)

        print("Recent Scan History:")
        print("-" * 80)
        history = db_handler.get_scan_history()

        if not history:
            print("No scan history found.")
        else:
            for scan in history:
                print(f"ID: {scan['id']}")
                print(f"Name: {scan['scan_name']}")
                print(f"Date: {scan['created_at']}")
                print(f"Total: {scan['total_domains']} | Success: {scan['successful']} | Failed: {scan['failed']}")
                print("-" * 80)
        return

    if args.compare:
        if not db_handler.is_enabled():
            print("Error: Database is not configured. Cannot compare scans.")
            sys.exit(1)

        scan_id1, scan_id2 = args.compare
        print(f"Comparing scans: {scan_id1} vs {scan_id2}")
        print("-" * 80)

        changes = db_handler.compare_scans(scan_id1, scan_id2)

        if not changes:
            print("Could not compare scans.")
            return

        if changes['status_changes']:
            print(f"\nStatus Changes ({len(changes['status_changes'])}):")
            for change in changes['status_changes']:
                print(f"  {change['domain']}: {change['old_status']} → {change['new_status']}")

        if changes['new_errors']:
            print(f"\nNew Errors ({len(changes['new_errors'])}):")
            for error in changes['new_errors']:
                print(f"  {error['domain']}: {error['error']}")

        if changes['resolved_errors']:
            print(f"\nResolved Errors ({len(changes['resolved_errors'])}):")
            for resolved in changes['resolved_errors']:
                print(f"  {resolved['domain']}: Previously '{resolved['previous_error']}'")

        if changes['performance_changes']:
            print(f"\nSignificant Performance Changes ({len(changes['performance_changes'])}):")
            for perf in changes['performance_changes']:
                diff = perf['difference']
                symbol = '↑' if diff > 0 else '↓'
                print(f"  {perf['domain']}: {perf['old_time']:.0f}ms → {perf['new_time']:.0f}ms ({symbol}{abs(diff):.0f}ms)")

        return

    if args.show_scan:
        if not db_handler.is_enabled():
            print("Error: Database is not configured. Cannot show scan.")
            sys.exit(1)

        results = db_handler.get_scan_results(args.show_scan)
        if not results:
            print(f"No results found for scan ID: {args.show_scan}")
        else:
            print(f"Results for scan {args.show_scan}:")
            print("-" * 80)
            for result in results:
                print(f"Domain: {result['domain']}")
                print(f"Status: {result['status_code']} | Time: {result['response_time_ms']}ms")
                if result['error']:
                    print(f"Error: {result['error']}")
                print("-" * 80)
        return

    if args.domain:
        domains = [validate_domain(args.domain)]
    else:
        print(f"Loading domains from: {args.input}")
        domains = load_domains(args.input)
        print(f"Loaded {len(domains)} unique domains\n")

    print(f"Configuration:")
    print(f"  Concurrent Requests: {args.concurrent}")
    print(f"  Timeout: {args.timeout}s")
    print(f"  Max Retries: {args.retries}")
    print(f"  SSL Verification: {'Disabled' if args.no_ssl_verify else 'Enabled'}")
    print(f"  Output Format: {args.format}")
    if args.save_db:
        print(f"  Database Tracking: Enabled")
    print()

    checker = DomainChecker(
        timeout=args.timeout,
        max_retries=args.retries,
        user_agent=args.user_agent,
        verify_ssl=not args.no_ssl_verify
    )

    print(f"Starting scan of {len(domains)} domains...")
    print("-" * 80)

    results = await checker.check_domains_batch(
        domains,
        max_concurrent=args.concurrent,
        progress_callback=None if args.quiet else Reporter.print_progress
    )

    if not args.quiet:
        print("\n" + "=" * 80)
        print("Scan Complete!")
        print("=" * 80)

    if args.output:
        output_path = args.output
        ext_map = {'json': '.json', 'csv': '.csv', 'html': '.html', 'text': '.txt'}

        if not Path(output_path).suffix:
            output_path += ext_map[args.format]

        print(f"\nGenerating {args.format.upper()} report...")

        if args.format == 'json':
            Reporter.generate_json_report(results, output_path)
        elif args.format == 'csv':
            Reporter.generate_csv_report(results, output_path)
        elif args.format == 'html':
            Reporter.generate_html_report(results, output_path)
        else:
            Reporter.generate_text_report(results, output_path)

        print(f"Results saved to: {output_path}")

    if args.save_db:
        if db_handler.is_enabled():
            print("\nSaving results to database...")
            scan_id = await db_handler.save_scan(results, args.scan_name)
            if scan_id:
                print(f"Saved to database with scan ID: {scan_id}")
                print(f"View later with: python httpchecker_v2.py --show-scan {scan_id}")
        else:
            print("Warning: Database is not configured. Results not saved to database.")

    if args.verbose:
        stats = Reporter._calculate_stats(results)
        print("\n" + "=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)
        print(f"Total Domains: {len(results)}")
        print(f"Success Rate: {stats['success_rate']:.2f}%")
        print(f"Average Response Time: {stats['avg_response_time']:.2f}ms")
        print(f"Fastest Response: {stats['min_response_time']:.2f}ms")
        print(f"Slowest Response: {stats['max_response_time']:.2f}ms")
        print(f"Total Errors: {stats['error_count']}")
        print(f"Total Redirects: {stats['redirect_count']}")
        print(f"HTTPS Success: {stats['https_count']}")
        print(f"HTTP Fallback: {stats['http_count']}")

    print("\nDone!")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
