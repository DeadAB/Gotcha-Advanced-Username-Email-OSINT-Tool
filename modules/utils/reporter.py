"""
Reporter module for generating and saving reports
"""

import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.logger import get_logger
from core.banner import print_section_header, print_success, print_info, print_warning

class Reporter:
    """Generate and save reports in various formats"""
    
    def __init__(self):
        self.logger = get_logger()
        
    def print_report(self, results: List[Dict[str, Any]], quiet: bool = False):
        """Print results to console"""
        if not results:
            print_warning("No results found")
            return
        
        for result in results:
            if 'username' in result:
                self._print_username_report(result, quiet)
            elif 'email' in result:
                self._print_email_report(result, quiet)
    
    def _print_username_report(self, result: Dict[str, Any], quiet: bool = False):
        """Print username scan results"""
        username = result.get('username', 'Unknown')
        
        if not quiet:
            print_section_header(f"Username: {username}")
        
        # Count total profiles found
        total_found = 0
        for category in ['social_media', 'general_sites', 'developer_platforms', 'forums', 'gaming']:
            profiles = result.get(category, [])
            total_found += len(profiles)
        
        print_success(f"Total profiles found: {total_found}")
        
        # Print by category
        categories = {
            'social_media': 'Social Media Platforms',
            'general_sites': 'General Websites',
            'developer_platforms': 'Developer Platforms',
            'forums': 'Forums & Communities',
            'gaming': 'Gaming Platforms'
        }
        
        for category, title in categories.items():
            profiles = result.get(category, [])
            if profiles:
                print(f"\n{title} ({len(profiles)} found):")
                for profile in profiles:
                    platform = profile.get('platform', 'Unknown')
                    url = profile.get('url', 'No URL')
                    status = "✓" if profile.get('exists', False) else "✗"
                    print(f"  {status} {platform}: {url}")
                    
                    # Print additional info if available
                    additional_info = profile.get('additional_info', {})
                    if additional_info:
                        for key, value in additional_info.items():
                            print(f"    └─ {key}: {value}")
    
    def _print_email_report(self, result: Dict[str, Any], quiet: bool = False):
        """Print email scan results"""
        email = result.get('email', 'Unknown')
        
        if not quiet:
            print_section_header(f"Email: {email}")
        
        # Social accounts
        social_accounts = result.get('social_accounts', [])
        if social_accounts:
            print(f"\nSocial Accounts ({len(social_accounts)} found):")
            for account in social_accounts:
                platform = account.get('platform', 'Unknown')
                exists = "✓" if account.get('exists', False) else "✗"
                print(f"  {exists} {platform}")
                
                if account.get('profile_url'):
                    print(f"    └─ Profile: {account['profile_url']}")
                if account.get('avatar_url'):
                    print(f"    └─ Avatar: {account['avatar_url']}")
        
        # Professional accounts
        professional_accounts = result.get('professional_accounts', [])
        if professional_accounts:
            print(f"\nProfessional Accounts ({len(professional_accounts)} found):")
            for account in professional_accounts:
                platform = account.get('platform', 'Unknown')
                username = account.get('username', 'Unknown')
                exists = "✓" if account.get('exists', False) else "✗"
                print(f"  {exists} {platform}: {username}")
                
                if account.get('profile_url'):
                    print(f"    └─ Profile: {account['profile_url']}")
        
        # Breach information
        breaches = result.get('breaches', {})
        if breaches:
            risk_level = breaches.get('risk_level', 'Unknown')
            total_breaches = breaches.get('total_breaches_found', 0)
            
            print(f"\nBreach Information:")
            print(f"  Risk Level: {risk_level}")
            print(f"  Total Breaches: {total_breaches}")
            
            if breaches.get('breach_sources'):
                print(f"  Sources: {', '.join(breaches['breach_sources'])}")
            
            if breaches.get('recommendations'):
                print(f"  Recommendations:")
                for rec in breaches['recommendations']:
                    print(f"    • {rec}")
        
        # Domain analysis
        domain_info = result.get('domain_info', {})
        if domain_info and domain_info.get('domain'):
            print(f"\nDomain Analysis:")
            print(f"  Domain: {domain_info['domain']}")
            print(f"  Corporate: {'Yes' if domain_info.get('is_corporate') else 'No'}")
            print(f"  Disposable: {'Yes' if domain_info.get('is_disposable') else 'No'}")
            
            if domain_info.get('mx_records'):
                print(f"  MX Records: {len(domain_info['mx_records'])}")
    
    def save_report(self, results: List[Dict[str, Any]], output_file: str, format_type: str = 'json'):
        """Save results to file"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type.lower() == 'json':
                self._save_json_report(results, output_path)
            elif format_type.lower() == 'csv':
                self._save_csv_report(results, output_path)
            elif format_type.lower() == 'txt':
                self._save_txt_report(results, output_path)
            elif format_type.lower() == 'xml':
                self._save_xml_report(results, output_path)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            print_success(f"Report saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving report: {str(e)}")
            raise
    
    def _save_json_report(self, results: List[Dict[str, Any]], output_path: Path):
        """Save results as JSON"""
        report_data = {
            'scan_timestamp': datetime.now().isoformat(),
            'total_targets': len(results),
            'results': results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    def _save_csv_report(self, results: List[Dict[str, Any]], output_path: Path):
        """Save results as CSV"""
        if not results:
            return
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write headers
            if 'username' in results[0]:
                writer.writerow(['Username', 'Platform', 'URL', 'Exists', 'Category'])
                
                # Write username data
                for result in results:
                    username = result.get('username', '')
                    for category in ['social_media', 'general_sites', 'developer_platforms', 'forums', 'gaming']:
                        profiles = result.get(category, [])
                        for profile in profiles:
                            writer.writerow([
                                username,
                                profile.get('platform', ''),
                                profile.get('url', ''),
                                profile.get('exists', False),
                                category
                            ])
            
            elif 'email' in results[0]:
                writer.writerow(['Email', 'Platform', 'Account_Type', 'Exists', 'Profile_URL'])
                
                # Write email data
                for result in results:
                    email = result.get('email', '')
                    
                    # Social accounts
                    for account in result.get('social_accounts', []):
                        writer.writerow([
                            email,
                            account.get('platform', ''),
                            'Social',
                            account.get('exists', False),
                            account.get('profile_url', '')
                        ])
                    
                    # Professional accounts
                    for account in result.get('professional_accounts', []):
                        writer.writerow([
                            email,
                            account.get('platform', ''),
                            'Professional',
                            account.get('exists', False),
                            account.get('profile_url', '')
                        ])
    
    def _save_txt_report(self, results: List[Dict[str, Any]], output_path: Path):
        """Save results as plain text"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("GOTCHA! OSINT TOOL REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total targets scanned: {len(results)}\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"TARGET {i}\n")
                f.write("-" * 20 + "\n")
                
                if 'username' in result:
                    f.write(f"Username: {result.get('username', 'Unknown')}\n\n")
                    
                    for category in ['social_media', 'general_sites', 'developer_platforms', 'forums', 'gaming']:
                        profiles = result.get(category, [])
                        if profiles:
                            f.write(f"{category.replace('_', ' ').title()} ({len(profiles)} found):\n")
                            for profile in profiles:
                                status = "FOUND" if profile.get('exists', False) else "NOT FOUND"
                                f.write(f"  [{status}] {profile.get('platform', 'Unknown')}: {profile.get('url', 'No URL')}\n")
                            f.write("\n")
                
                elif 'email' in result:
                    f.write(f"Email: {result.get('email', 'Unknown')}\n\n")
                    
                    social_accounts = result.get('social_accounts', [])
                    if social_accounts:
                        f.write(f"Social Accounts ({len(social_accounts)} found):\n")
                        for account in social_accounts:
                            status = "FOUND" if account.get('exists', False) else "NOT FOUND"
                            f.write(f"  [{status}] {account.get('platform', 'Unknown')}\n")
                        f.write("\n")
                    
                    professional_accounts = result.get('professional_accounts', [])
                    if professional_accounts:
                        f.write(f"Professional Accounts ({len(professional_accounts)} found):\n")
                        for account in professional_accounts:
                            status = "FOUND" if account.get('exists', False) else "NOT FOUND"
                            f.write(f"  [{status}] {account.get('platform', 'Unknown')}\n")
                        f.write("\n")
                
                f.write("\n" + "=" * 50 + "\n\n")
    
    def _save_xml_report(self, results: List[Dict[str, Any]], output_path: Path):
        """Save results as XML"""
        root = ET.Element("gotcha_report")
        root.set("timestamp", datetime.now().isoformat())
        root.set("total_targets", str(len(results)))
        
        for result in results:
            if 'username' in result:
                target_elem = ET.SubElement(root, "username_target")
                target_elem.set("username", result.get('username', ''))
                
                for category in ['social_media', 'general_sites', 'developer_platforms', 'forums', 'gaming']:
                    profiles = result.get(category, [])
                    if profiles:
                        category_elem = ET.SubElement(target_elem, category)
                        for profile in profiles:
                            profile_elem = ET.SubElement(category_elem, "profile")
                            profile_elem.set("platform", profile.get('platform', ''))
                            profile_elem.set("exists", str(profile.get('exists', False)))
                            profile_elem.set("url", profile.get('url', ''))
            
            elif 'email' in result:
                target_elem = ET.SubElement(root, "email_target")
                target_elem.set("email", result.get('email', ''))
                
                # Add social accounts
                social_accounts = result.get('social_accounts', [])
                if social_accounts:
                    social_elem = ET.SubElement(target_elem, "social_accounts")
                    for account in social_accounts:
                        account_elem = ET.SubElement(social_elem, "account")
                        account_elem.set("platform", account.get('platform', ''))
                        account_elem.set("exists", str(account.get('exists', False)))
                
                # Add professional accounts
                professional_accounts = result.get('professional_accounts', [])
                if professional_accounts:
                    prof_elem = ET.SubElement(target_elem, "professional_accounts")
                    for account in professional_accounts:
                        account_elem = ET.SubElement(prof_elem, "account")
                        account_elem.set("platform", account.get('platform', ''))
                        account_elem.set("exists", str(account.get('exists', False)))
        
        # Write XML to file
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
    
    def generate_summary_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from results"""
        stats = {
            'total_targets': len(results),
            'username_targets': 0,
            'email_targets': 0,
            'total_profiles_found': 0,
            'platforms_with_hits': set(),
            'most_common_platforms': {},
            'scan_timestamp': datetime.now().isoformat()
        }
        
        platform_counts = {}
        
        for result in results:
            if 'username' in result:
                stats['username_targets'] += 1
                
                for category in ['social_media', 'general_sites', 'developer_platforms', 'forums', 'gaming']:
                    profiles = result.get(category, [])
                    stats['total_profiles_found'] += len(profiles)
                    
                    for profile in profiles:
                        platform = profile.get('platform', 'Unknown')
                        stats['platforms_with_hits'].add(platform)
                        platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            elif 'email' in result:
                stats['email_targets'] += 1
                
                social_accounts = result.get('social_accounts', [])
                professional_accounts = result.get('professional_accounts', [])
                
                stats['total_profiles_found'] += len(social_accounts) + len(professional_accounts)
                
                for account in social_accounts + professional_accounts:
                    platform = account.get('platform', 'Unknown')
                    stats['platforms_with_hits'].add(platform)
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Convert set to list for JSON serialization
        stats['platforms_with_hits'] = list(stats['platforms_with_hits'])
        
        # Get top 10 most common platforms
        sorted_platforms = sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
        stats['most_common_platforms'] = dict(sorted_platforms[:10])
        
        return stats