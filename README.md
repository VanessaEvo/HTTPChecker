# HTTP Checker v2.0

An advanced, production-ready HTTP status checker with SSL verification, performance metrics, concurrent processing, and comprehensive reporting capabilities.

![HTTP Checker Banner](https://github.com/VanessaEvo/HTTPChecker/blob/main/script.PNG?raw=true)

## Features

### Core Functionality
- **Concurrent Domain Checking** - Check hundreds of domains simultaneously with configurable concurrency
- **HTTPS/HTTP Fallback** - Automatically tries HTTPS first, falls back to HTTP if needed
- **SSL Certificate Validation** - Verify SSL certificates, check expiration dates, and cipher information
- **Smart Retry Logic** - Exponential backoff for failed requests
- **Comprehensive Error Handling** - Detailed error messages for debugging

### Performance Metrics
- **Response Time Measurement** - Track total response time for each domain
- **DNS Resolution Time** - Measure DNS lookup performance
- **Connection Time** - Track TCP connection establishment time
- **Statistical Analysis** - Average, minimum, and maximum response times

### Security Analysis
- **Security Headers Detection** - Check for HSTS, CSP, X-Frame-Options, and more
- **SSL/TLS Information** - Certificate validity, issuer, cipher suite, and protocol version
- **Redirect Chain Analysis** - Full tracking of redirect history with URLs
- **Server Technology Detection** - Identify server software from headers

### Output Formats
- **Text Report** - Detailed human-readable reports with statistics
- **JSON** - Machine-readable format for integration with other tools
- **CSV** - Excel-compatible format for data analysis
- **HTML** - Interactive web-based reports with filtering and styling

### Database Integration
- **Historical Tracking** - Save scan results to Supabase for long-term storage
- **Scan Comparison** - Compare current and previous scans to detect changes
- **Performance Trends** - Track domain performance over time
- **Status Change Alerts** - Identify when domains go down or recover

### User Experience
- **Real-time Progress Bar** - Visual feedback during scanning
- **Configurable Options** - Extensive CLI arguments for customization
- **Verbose & Quiet Modes** - Control output verbosity
- **Custom User-Agent** - Set custom User-Agent headers
- **Domain Validation** - Automatic cleanup of URLs and duplicate removal

## Installation

1. Clone the repository:
```bash
git clone https://github.com/VanessaEvo/HTTPChecker.git
cd HTTPChecker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Configure Supabase for database features:
   - Create a `.env` file in the project directory
   - Add your Supabase credentials:
   ```
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

## Quick Start

### Basic Usage

Check domains from a file:
```bash
python httpchecker_v2.py -i domains.txt -o results.txt
```

Check a single domain:
```bash
python httpchecker_v2.py -d example.com -o result.txt
```

### Input File Format

Create a text file with one domain per line:
```
example.com
google.com
github.com
stackoverflow.com
```

The checker automatically handles:
- URLs with protocols (strips http:// or https://)
- Trailing slashes and paths
- Duplicate domains
- Empty lines

## Command-Line Arguments

### Input/Output Options

| Argument | Short | Description |
|----------|-------|-------------|
| `--input FILE` | `-i` | Path to file containing domains (one per line) |
| `--domain DOMAIN` | `-d` | Check a single domain |
| `--output FILE` | `-o` | Path to save results |
| `--format FORMAT` | `-f` | Output format: text, json, csv, html (default: text) |

### Performance Options

| Argument | Short | Description |
|----------|-------|-------------|
| `--concurrent N` | `-c` | Maximum concurrent requests (default: 10) |
| `--timeout N` | `-t` | Request timeout in seconds (default: 10) |
| `--retries N` | `-r` | Maximum retry attempts (default: 2) |

### HTTP Options

| Argument | Description |
|----------|-------------|
| `--user-agent STRING` | Custom User-Agent header |
| `--no-ssl-verify` | Disable SSL certificate verification |

### Display Options

| Argument | Short | Description |
|----------|-------|-------------|
| `--verbose` | `-v` | Show detailed statistics after scan |
| `--quiet` | `-q` | Suppress progress output |
| `--no-banner` | | Hide ASCII banner |

### Database Options

| Argument | Description |
|----------|-------------|
| `--save-db` | Save results to Supabase database |
| `--scan-name NAME` | Custom name for this scan |
| `--history` | Show previous scan history |
| `--compare ID1 ID2` | Compare two previous scans |
| `--show-scan ID` | Show results from a specific scan |

## Usage Examples

### Example 1: Basic Text Report
```bash
python httpchecker_v2.py -i domains.txt -o results.txt
```

### Example 2: Fast Scan with High Concurrency
```bash
python httpchecker_v2.py -i domains.txt -o results.json -f json -c 50
```

### Example 3: Detailed HTML Report
```bash
python httpchecker_v2.py -i domains.txt -o report.html -f html -v
```

### Example 4: CSV for Excel Analysis
```bash
python httpchecker_v2.py -i domains.txt -o results.csv -f csv
```

### Example 5: Database Tracking
```bash
python httpchecker_v2.py -i domains.txt -o results.txt --save-db --scan-name "Weekly Check"
```

### Example 6: Check Single Domain with Details
```bash
python httpchecker_v2.py -d example.com -o result.txt -v
```

### Example 7: Custom User-Agent
```bash
python httpchecker_v2.py -i domains.txt -o results.txt --user-agent "MyBot/1.0"
```

### Example 8: Quiet Mode (No Progress Bar)
```bash
python httpchecker_v2.py -i domains.txt -o results.txt -q
```

### Example 9: View Scan History
```bash
python httpchecker_v2.py --history
```

### Example 10: Compare Two Scans
```bash
python httpchecker_v2.py --compare scan_id_1 scan_id_2
```

## Understanding Output

### Text Report Structure
```
==================================================
HTTP CHECKER REPORT
Generated: 2024-01-15 10:30:00
Total Domains Checked: 100
==================================================

SUMMARY STATISTICS
--------------------------------------------------
Success Rate: 95.00%
Average Response Time: 245.32ms
Fastest Response: 89.12ms
Slowest Response: 1234.56ms
Total Errors: 5
Total Redirects: 12
HTTPS Success: 88
HTTP Fallback: 7

==================================================
DETAILED RESULTS
==================================================

Domain: example.com
Status Code: 200
Protocol Used: https
Response Time: 234.56ms
DNS Resolution Time: 12.34ms
Connection Time: 45.67ms
Server: nginx/1.18.0
Final URL: https://www.example.com/
Redirects (1):
  1. [301] https://example.com
SSL Certificate Info:
  Version: TLSv1.3
  Cipher: TLS_AES_256_GCM_SHA384
  Valid Until: Dec 31 23:59:59 2024 GMT
Security Headers:
  Strict-Transport-Security: max-age=31536000
  Content-Security-Policy: default-src 'self'
```

### JSON Format
Perfect for automation and integration:
```json
{
  "metadata": {
    "generated_at": "2024-01-15T10:30:00",
    "total_domains": 100,
    "statistics": {
      "success_rate": 95.0,
      "avg_response_time": 245.32
    }
  },
  "results": [
    {
      "domain": "example.com",
      "status_code": 200,
      "response_time_ms": 234.56,
      "ssl_info": {...}
    }
  ]
}
```

### CSV Format
Open in Excel or Google Sheets:
```csv
domain,status_code,protocol_used,response_time_ms,has_hsts,has_csp
example.com,200,https,234.56,Yes,Yes
```

### HTML Format
Interactive report with:
- Sortable tables
- Filter by success/error/redirect
- Color-coded status indicators
- Mobile-responsive design

## Database Features

### Setting Up Supabase

1. Create a Supabase project at https://supabase.com
2. Run the following SQL to create tables:

```sql
CREATE TABLE scans (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  scan_name TEXT NOT NULL,
  total_domains INTEGER,
  successful INTEGER,
  failed INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE domain_results (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  scan_id UUID REFERENCES scans(id),
  domain TEXT NOT NULL,
  status_code INTEGER,
  response_time_ms NUMERIC,
  protocol_used TEXT,
  server_info TEXT,
  has_ssl BOOLEAN,
  redirect_count INTEGER,
  error TEXT,
  final_url TEXT,
  security_headers JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE domain_results ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public read access" ON scans FOR SELECT TO anon USING (true);
CREATE POLICY "Public insert access" ON scans FOR INSERT TO anon WITH CHECK (true);
CREATE POLICY "Public read access" ON domain_results FOR SELECT TO anon USING (true);
CREATE POLICY "Public insert access" ON domain_results FOR INSERT TO anon WITH CHECK (true);
```

3. Add credentials to `.env` file

### Using Database Features

Track scans over time:
```bash
python httpchecker_v2.py -i domains.txt -o results.txt --save-db --scan-name "Daily Check"
```

View scan history:
```bash
python httpchecker_v2.py --history
```

Compare two scans:
```bash
python httpchecker_v2.py --compare abc-123 def-456
```

View specific scan:
```bash
python httpchecker_v2.py --show-scan abc-123
```

## Performance Tips

### Optimizing Speed
- Increase concurrency for faster scans: `-c 50`
- Reduce timeout for unresponsive domains: `-t 5`
- Lower retry attempts: `-r 1`

### Optimizing Accuracy
- Use default concurrency for stability: `-c 10`
- Increase timeout for slow domains: `-t 20`
- Keep retry attempts: `-r 2` or `-r 3`

### Memory Usage
- Large domain lists (1000+): Use `-c 20` to balance speed and memory
- Very large lists (10000+): Process in batches or use `-c 10`

## Troubleshooting

### SSL Errors
If you encounter SSL verification errors:
```bash
python httpchecker_v2.py -i domains.txt -o results.txt --no-ssl-verify
```

### Timeout Issues
For slow networks:
```bash
python httpchecker_v2.py -i domains.txt -o results.txt -t 30
```

### Rate Limiting
If getting rate-limited:
```bash
python httpchecker_v2.py -i domains.txt -o results.txt -c 5
```

### DNS Issues
Check your network connection and DNS settings. The tool will report DNS resolution failures separately.

## Migration from v1.0

The original `httpchecker.py` is still included for compatibility. To use the new version:

**Old command:**
```bash
python httpchecker.py
# Then enter file paths when prompted
```

**New command:**
```bash
python httpchecker_v2.py -i domains.txt -o results.txt
```

Key improvements in v2.0:
- 10-50x faster with concurrent processing
- More accurate with HTTP fallback
- Detailed SSL and security analysis
- Multiple output formats
- Database integration
- No interactive prompts (fully scriptable)

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## License

See LICENSE file for details.

## Author

VanessaEvo - https://github.com/VanessaEvo

## Changelog

### v2.0 (Current)
- Complete rewrite with async/await
- Added concurrent processing
- Added SSL certificate validation
- Added security headers detection
- Added multiple output formats (JSON, CSV, HTML)
- Added Supabase database integration
- Added comprehensive CLI arguments
- Added performance metrics (DNS time, connection time)
- Added HTTP fallback when HTTPS fails
- Added scan comparison and history
- Added retry logic with exponential backoff
- Added progress bar with real-time stats
- Improved error handling and reporting
- Modular code structure

### v1.0
- Initial release
- Basic HTTP status checking
- Simple text output
- Sequential processing

## Support

For issues, questions, or suggestions, please open an issue on GitHub:
https://github.com/VanessaEvo/HTTPChecker/issues

Cheers!

./EOF
