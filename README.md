# SPF Missing Scanner

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A straightforward tool to check if domains have proper email authentication (SPF/DMARC) and to demonstrate why these records matter.

> **Important:** This tool is for authorized security testing, educational research, and auditing your own domains. Do not use it against domains you do not own or have explicit permission to test.

## What This Tool Does

Email spoofing is possible when a domain hasn't set up SPF or DMARC records. This tool:

1. **Scans** domains to check for missing SPF and DMARC DNS records
2. **Reports** which domains are vulnerable to email spoofing
3. **Demonstrates** (optionally) by sending a test email that shows how spoofing works

The goal is to help domain owners understand why they need these security records—by seeing the vulnerability in action.

## How It Works (Simple Explanation)

- **SPF** tells receiving mail servers which IP addresses are allowed to send email for your domain. Without it, anyone can claim to be you.
- **DMARC** tells servers what to do with emails that fail SPF or DKIM checks (quarantine or reject). Without it, forged emails go straight to inboxes.

This tool queries public DNS servers, finds domains without these records, and (if you choose) sends a harmless demonstration email to show the impact.

## Installation

```bash
git clone https://github.com/yourusername/spf-missing-scanner.git
cd spf-missing-scanner
pip install dnspython colorama
