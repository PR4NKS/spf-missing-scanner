# SPF/DMARC Security Scanner & Email Authentication Auditor

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Security Research](https://img.shields.io/badge/purpose-security%20research-red.svg)]()

## 📋 Overview

**SPF/DMARC Security Scanner** is an educational security research tool designed to help domain owners, security professionals, and system administrators audit email authentication configurations across their infrastructure.

The tool identifies missing or misconfigured **SPF (Sender Policy Framework)** and **DMARC (Domain-based Message Authentication, Reporting & Conformance)** records—two critical DNS-based email security standards that prevent domain spoofing, phishing attacks, and email fraud.

> **⚠️ Legal Notice:** This tool is intended for **authorized security testing and educational purposes only**. Always obtain written permission before scanning domains you do not own. Unauthorized scanning may violate computer fraud and abuse laws in your jurisdiction.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Bulk Domain Scanning** | Scan single domains, batched lists, or large-scale inventories for SPF/DMARC presence |
| 📊 **Vulnerability Scoring** | Automated risk assessment (0-10 scale) based on missing or weak records |
| 📧 **Educational SMTP Simulation** | Demonstrates real-world email spoofing risks when protections are absent |
| 📄 **Comprehensive Reporting** | Export findings as formatted text reports with actionable recommendations |
| ⚡ **Concurrent Processing** | Multi-threaded DNS queries for high-performance enumeration |
| 🎨 **Color-Coded Output** | Enhanced terminal visualization for rapid threat assessment |
| 🔐 **DKIM Detection** | Optional DomainKeys Identified Mail (DKIM) selector enumeration |
| 📈 **Trend Analysis** | Track configuration changes over time with historical scanning |

---

## 🧠 Why SPF and DMARC Matter

### SPF (Sender Policy Framework)

SPF authenticates email senders by publishing authorized IP addresses and mail servers in DNS TXT records. Receiving servers validate that incoming mail originates from approved sources.

**Example SPF Record:**
```dns
v=spf1 ip4:192.0.2.0/24 include:_spf.google.com -all
```

**Without SPF:**
- ❌ Attackers can forge emails appearing to come from your domain
- ❌ No mechanism to verify sender authenticity
- ❌ Increased phishing and brand impersonation risk

### DMARC (Domain-based Message Authentication, Reporting & Conformance)

DMARC builds on SPF and DKIM by specifying how receiving servers should handle authentication failures and where to send forensic reports.

**Example DMARC Record:**
```dns
v=DMARC1; p=reject; pct=100; rua=mailto:dmarc@example.com; ruf=mailto:forensics@example.com; fo=1
```

**Without DMARC:**
- ❌ Zero visibility into unauthorized email activity
- ❌ No enforcement policy for failed authentication
- ❌ Missing actionable abuse reports
- ❌ Compliance gaps for regulated industries

---

## 📦 Installation

### Prerequisites

- **Python:** 3.8 or higher
- **pip:** Python package manager
- **Operating System:** Linux, macOS, Windows (WSL recommended)

### Method 1: Quick Install

```bash
# Clone the repository
git clone https://github.com/PR4NKS/spf-dmarc-scanner.git
cd spf-dmarc-scanner

# Install dependencies
pip install -r requirements.txt

# Verify installation
python scanner.py --help
```

### Method 2: Virtual Environment (Recommended)

```bash
# Create isolated environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Method 3: Manual Dependency Installation

```bash
pip install dnspython==2.4.2 colorama==0.4.6
```

### Verify Installation

```bash
python scanner.py --version
python scanner.py --help
```

---

## 🚀 Usage Guide

### Basic Scanning

**Scan a single domain:**
```bash
python scanner.py --domain example.com
```

**Scan multiple domains from command line:**
```bash
python scanner.py --bulk example.com test.org mydomain.net security.io
```

**Scan domains from a file:**
```bash
python scanner.py --list domains.txt
```

### Advanced Operations

**Enable educational SMTP simulation (demonstrates spoofing vulnerability):**
```bash
python scanner.py --domain vulnerable-domain.com --simulate
```

**Generate detailed report with timestamp:**
```bash
python scanner.py --list domains.txt --output "report_$(date +%Y%m%d).txt"
```

**High-speed scanning with increased threads:**
```bash
python scanner.py --list large_domains.txt --threads 50
```

**Verbose debugging output:**
```bash
python scanner.py --domain example.com --verbose
```

**JSON output for automation/parsing:**
```bash
python scanner.py --domain example.com --format json > results.json
```

### Example Output
<img width="633" height="332" alt="image" src="https://github.com/user-attachments/assets/fbe75f17-27e1-4309-8197-5558d747c39f" />


---

## 📁 Input File Format

Create a text file (`domains.txt`) with one domain per line:

```text
# Corporate Domains - Production
example.com
mail.example.com
subdomain.example.com

# Partner Domains - Review Quarterly
partner-company.net
vendor-portal.io

# Legacy Domains - Decommission Q3
old-brand.org
deprecated.example.net
```

**Supported formats:**
- Plain domain names: `example.com`
- Subdomains: `mail.example.com`
- Comment lines: `# This is ignored`
- Blank lines: Automatically skipped

---

## 🔧 Command Line Reference

### Core Arguments

| Argument | Short | Type | Description |
|----------|-------|------|-------------|
| `--domain` | `-d` | `string` | Single domain to scan |
| `--list` | `-l` | `file` | Path to file containing domains (one per line) |
| `--bulk` | `-b` | `string[]` | Space-separated list of domains |

### Configuration Options

| Argument | Short | Type | Default | Description |
|----------|-------|------|---------|-------------|
| `--threads` | `-t` | `int` | `10` | Number of concurrent DNS query threads |
| `--timeout` | | `int` | `5` | DNS query timeout in seconds |
| `--retries` | | `int` | `3` | Number of retry attempts for failed queries |
| `--nameserver` | `-ns` | `string` | System | Custom DNS server (e.g., `8.8.8.8`) |

### Output Options

| Argument | Short | Type | Description |
|----------|-------|------|-------------|
| `--output` | `-o` | `file` | Save results to specified file |
| `--format` | `-f` | `text|json|csv` | Output format (default: `text`) |
| `--verbose` | `-v` | `flag` | Enable detailed logging |
| `--quiet` | `-q` | `flag` | Suppress non-critical output |
| `--no-color` | | `flag` | Disable colored terminal output |

### Security Testing

| Argument | Short | Type | Description |
|----------|-------|------|-------------|
| `--simulate` | `-s` | `flag` | Run educational SMTP simulation (shows spoofing risk) |
| `--check-dkim` | | `flag` | Attempt common DKIM selector enumeration |
| `--mx-test` | | `flag` | Test MX server connectivity and TLS support |

### Utility Commands

| Argument | Short | Description |
|----------|-------|-------------|
| `--version` | | Display scanner version and exit |
| `--help` | `-h` | Show comprehensive help message |
| `--examples` | | Display usage examples |

---

## 📊 Understanding Results

### Vulnerability Scoring System (0-10)

| Score Range | Risk Level | Interpretation | Action Required |
|-------------|-----------|----------------|-----------------|
| **0-2** | ✅ Secure | Both SPF and DMARC properly configured with strict policies | Maintain monitoring, review quarterly |
| **3-5** | ⚠️ Moderate | One record missing or weak policy (e.g., `p=none`) | Implement missing record within 30 days |
| **6-8** | 🔶 High | Missing SPF or overly permissive configuration | Create/fix records within 7 days |
| **9-10** | 🔴 Critical | No SPF and no DMARC, or `+all` SPF policy | **Urgent: Fix immediately** |

### Record Status Indicators

| Status | Icon | Meaning | Explanation |
|--------|------|---------|-------------|
| **VALID** | ✅ | Properly configured | Record found and passes basic validation |
| **INVALID** | ❌ | Missing or malformed | No record found or syntax errors detected |
| **WARNING** | ⚠️ | Weak configuration | Record exists but policy is too permissive |
| **PARTIAL** | 🔶 | Incomplete setup | One mechanism present, other missing |
| **ERROR** | ⛔ | Query failed | DNS timeout, NXDOMAIN, or network issue |

### SPF Policy Qualifiers

| Qualifier | Meaning | Security Impact | Recommendation |
|-----------|---------|-----------------|----------------|
| `+all` | Pass all (allow any server) | 🔴 **Critical vulnerability** | Never use—defeats SPF purpose |
| `~all` | Soft fail (likely unauthorized) | ⚠️ Low protection | Use `-all` for better security |
| `-all` | Hard fail (reject unauthorized) | ✅ Strongest protection | **Recommended for production** |
| `?all` | Neutral (no policy) | 🔶 No protection | Use `-all` instead |

### DMARC Policy Levels

| Policy | Tag | Meaning | Use Case |
|--------|-----|---------|----------|
| `p=none` | Monitoring | No enforcement, reports only | Initial deployment, testing phase |
| `p=quarantine` | Suspicious | Send failures to spam folder | Gradual rollout, low-risk domains |
| `p=reject` | Block | Reject all authentication failures | **Production standard for security** |

---

## 🛡️ Security Best Practices

### Recommended Configuration

**Minimum Secure SPF Record:**
```dns
v=spf1 mx include:_spf.google.com -all
```

**Production-Grade DMARC Record:**
```dns
v=DMARC1; p=reject; pct=100; rua=mailto:dmarc-reports@example.com; ruf=mailto:dmarc-forensics@example.com; fo=1; adkim=s; aspf=s
```

### Deployment Checklist

- [ ] **Week 1-2:** Deploy SPF with `-all`, DMARC with `p=none`
- [ ] **Week 3-4:** Monitor DMARC reports, identify legitimate senders
- [ ] **Week 5-6:** Update SPF to include all authorized senders
- [ ] **Week 7-8:** Escalate DMARC to `p=quarantine`, `pct=10`
- [ ] **Week 9-12:** Gradually increase `pct` to `100`
- [ ] **Month 4+:** Escalate to `p=reject` for full enforcement

### Common Pitfalls to Avoid

❌ **Don't:** Use `+all` or `?all` in SPF records  
✅ **Do:** Always end SPF with `-all` or `~all`

❌ **Don't:** Set DMARC `p=reject` without monitoring first  
✅ **Do:** Start with `p=none`, analyze reports, then escalate

❌ **Don't:** Exceed 10 DNS lookups in SPF (breaks validation)  
✅ **Do:** Flatten includes or use SPF macros for complex setups

❌ **Don't:** Forget subdomain DMARC policies  
✅ **Do:** Set `sp=reject` for subdomain protection

---

## 📈 Sample Workflows

### Workflow 1: Initial Domain Audit

```bash
# Scan all company domains
python scanner.py --list company_domains.txt --output initial_audit.txt --verbose

# Review critical vulnerabilities
grep "CRITICAL" initial_audit.txt

# Generate executive summary
python scanner.py --list company_domains.txt --format json | jq '.summary'
```

### Workflow 2: Continuous Monitoring

```bash
#!/bin/bash
# Monthly cron job: 0 0 1 * * /path/to/monthly_scan.sh

TIMESTAMP=$(date +%Y%m%d)
python scanner.py --list /etc/scanner/domains.txt \
  --output "/var/log/scanner/report_${TIMESTAMP}.txt" \
  --format json > "/var/log/scanner/report_${TIMESTAMP}.json"

# Alert on new vulnerabilities
python scanner.py --compare "/var/log/scanner/report_$(date -d '1 month ago' +%Y%m%d).json" \
  "/var/log/scanner/report_${TIMESTAMP}.json" --alert-slack
```

### Workflow 3: Pre-Deployment Validation

```bash
# Before launching new domain
NEW_DOMAIN="newproject.example.com"

python scanner.py --domain $NEW_DOMAIN --verbose
python scanner.py --domain $NEW_DOMAIN --check-dkim --mx-test

# Must score 0-2 before going live
```

---

## 🐛 Troubleshooting

### Common Issues

**Problem:** `ModuleNotFoundError: No module named 'dns'`  
**Solution:** Install dnspython: `pip install dnspython`

**Problem:** `[ERROR] DNS timeout for example.com`  
**Solution:** Increase timeout: `--timeout 10` or specify DNS server: `--nameserver 8.8.8.8`

**Problem:** `PermissionError` when saving output  
**Solution:** Check file permissions or use absolute path: `--output /tmp/report.txt`

**Problem:** No color output on Windows  
**Solution:** Install colorama: `pip install colorama` or use `--no-color`

**Problem:** Rate limiting from DNS servers  
**Solution:** Reduce threads: `--threads 5` or add delays between queries

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/PR4NKS/spf-dmarc-scanner.git
cd spf-dmarc-scanner

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Check code quality
flake8 scanner.py
black scanner.py --check
```

---

## ⚖️ Legal Disclaimer

This tool is provided for **educational and authorized security testing purposes only**.

- ✅ **Authorized Use:** Testing your own domains, client domains with written permission, security research with proper authorization
- ❌ **Prohibited Use:** Scanning third-party domains without consent, malicious reconnaissance, harassment

**By using this software, you agree to:**
1. Obtain written authorization before scanning domains you do not own
2. Comply with applicable laws (CFAA, GDPR, local regulations)
3. Use findings responsibly and ethically
4. Not use this tool for illegal activities

The authors assume no liability for misuse or damages caused by this software.

---

## 🙏 Acknowledgments

- **DNSPython** - Robust DNS toolkit for Python
- **Colorama** - Cross-platform colored terminal output
- **IETF RFC 7208** - SPF specification
- **IETF RFC 7489** - DMARC specification
- The security research community

---

## 📞 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/PR4NKS/spf-dmarc-scanner/issues)
- **Discussions:** [GitHub Discussions](https://github.com/PR4NKS/spf-dmarc-scanner/discussions)
- **Email:** security@example.com
- **Twitter:** [@PR4NKS](https://twitter.com/PR4NKS)

---

## 🗺️ Roadmap

- [ ] **v2.2:** BIMI (Brand Indicators for Message Identification) support
- [ ] **v2.3:** TLS-RPT (SMTP TLS Reporting) analysis
- [ ] **v2.4:** MTA-STS (SMTP MTA Strict Transport Security) validation
- [ ] **v2.5:** Web dashboard for historical trend analysis
- [ ] **v3.0:** API endpoint for CI/CD integration
- [ ] **v3.1:** Slack/Discord/Teams webhook notifications
- [ ] **v3.2:** Machine learning for anomaly detection

---

<div align="center">

**Made with ☕ by security researchers, for security researchers**

⭐ Star this repo if you find it useful! ⭐

[Report Bug](https://github.com/PR4NKS/spf-dmarc-scanner/issues) · [Request Feature](https://github.com/PR4NKS/spf-dmarc-scanner/issues) · [Documentation](https://docs.example.com)

</div>
