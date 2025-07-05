"""
Breach Checker - Check for email addresses in data breaches
"""

import asyncio
import aiohttp
import hashlib
import random
from typing import List, Dict, Any, Optional
from core.config import Config
from core.logger import get_logger

class BreachChecker:
    """Check for email addresses in known data breaches"""
    
    def __init__(self):
        self.config = Config()
        self.logger = get_logger()
        self.session = None
        
        # Known breach databases that can be checked without API keys
        self.breach_sources = {
            'dehashed': {
                'name': 'DeHashed',
                'url': 'https://www.dehashed.com/search',
                'requires_api': True,
                'description': 'Database of leaked credentials'
            },
            'haveibeenpwned': {
                'name': 'Have I Been Pwned',
                'url': 'https://haveibeenpwned.com/api/v3/breachedaccount',
                'requires_api': False,
                'description': 'Troy Hunt\'s breach database'
            },
            'intelx': {
                'name': 'Intelligence X',
                'url': 'https://intelx.io/search',
                'requires_api': True,
                'description': 'OSINT search engine'
            },
            'breachdirectory': {
                'name': 'Breach Directory',
                'url': 'https://breachdirectory.org/search',
                'requires_api': False,
                'description': 'Free breach lookup service'
            }
        }
        
        # Common breach patterns and indicators
        self.breach_indicators = [
            'breach', 'leaked', 'dump', 'database', 'credentials',
            'password', 'hack', 'compromise', 'exposure'
        ]
    
    async def create_session(self):
        """Create aiohttp session"""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        connector = aiohttp.TCPConnector(
            limit=self.config.max_workers,
            verify_ssl=self.config.get('verify_ssl', True)
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                'User-Agent': random.choice(self.config.user_agents)
            }
        )
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def get_sha1_hash(self, email: str) -> str:
        """Generate SHA1 hash for email"""
        return hashlib.sha1(email.lower().strip().encode()).hexdigest()
    
    async def check_haveibeenpwned(self, email: str) -> Optional[Dict[str, Any]]:
        """Check Have I Been Pwned for breaches"""
        try:
            # Note: HIBP API v3 requires API key for email searches
            # This is a demonstration of how it would work
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            
            headers = {
                'User-Agent': random.choice(self.config.user_agents),
                'hibp-api-key': 'YOUR_API_KEY_HERE'  # Would need real API key
            }
            
            # For demo purposes, we'll check the website directly
            web_url = f"https://haveibeenpwned.com/account/{email}"
            
            async with self.session.get(web_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Look for breach indicators in the response
                    if any(indicator in content.lower() for indicator in ['pwned', 'breach', 'found']):
                        return {
                            'source': 'Have I Been Pwned',
                            'email': email,
                            'found': True,
                            'breaches': [],  # Would extract specific breaches from content
                            'url': web_url,
                            'note': 'Manual verification required - automated checking requires API key'
                        }
                    
        except Exception as e:
            self.logger.error(f"Error checking Have I Been Pwned for {email}: {str(e)}")
        
        return None
    
    async def check_breachdirectory(self, email: str) -> Optional[Dict[str, Any]]:
        """Check Breach Directory for email"""
        try:
            # Breach Directory allows limited free searches
            url = "https://breachdirectory.org/search"
            
            # Note: This would require implementing their search mechanism
            # which may involve CSRF tokens and specific form data
            
            data = {
                'query': email,
                'type': 'email'
            }
            
            headers = {
                'User-Agent': random.choice(self.config.user_agents),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://breachdirectory.org/'
            }
            
            # For demonstration, we'll just return a placeholder
            return {
                'source': 'Breach Directory',
                'email': email,
                'found': False,
                'note': 'Manual check required at https://breachdirectory.org/'
            }
            
        except Exception as e:
            self.logger.error(f"Error checking Breach Directory for {email}: {str(e)}")
        
        return None
    
    async def check_local_breach_files(self, email: str) -> List[Dict[str, Any]]:
        """Check local breach files if available"""
        results = []
        
        try:
            # This would check local breach databases if available
            # Common locations for breach files on security research systems
            potential_paths = [
                '/opt/breaches/',
                '/home/breaches/',
                './breach_data/',
                './data/breaches/'
            ]
            
            # Implementation would involve:
            # 1. Reading breach files (usually large text files)
            # 2. Searching for email addresses
            # 3. Extracting associated data (passwords, other info)
            
            # For security and legal reasons, this is left as a placeholder
            self.logger.info(f"Local breach file checking not implemented for security reasons")
            
        except Exception as e:
            self.logger.error(f"Error checking local breach files for {email}: {str(e)}")
        
        return results
    
    async def check_pastebins(self, email: str) -> List[Dict[str, Any]]:
        """Check various pastebin sites for email appearances"""
        results = []
        
        try:
            # Check common paste sites using Google dorks
            paste_sites = [
                'pastebin.com',
                'paste.org',
                'justpaste.it',
                'hastebin.com',
                'dpaste.org'
            ]
            
            for site in paste_sites:
                # Would implement Google search for site:domain "email"
                # This requires careful implementation to avoid rate limiting
                pass
            
        except Exception as e:
            self.logger.error(f"Error checking pastebins for {email}: {str(e)}")
        
        return results
    
    async def check_social_media_breaches(self, email: str) -> List[Dict[str, Any]]:
        """Check for email in known social media breaches"""
        results = []
        
        # Known major breaches that can be checked
        known_breaches = {
            'linkedin_2012': {
                'name': 'LinkedIn (2012)',
                'description': '6.5M LinkedIn passwords',
                'date': '2012-06-05'
            },
            'adobe_2013': {
                'name': 'Adobe (2013)',
                'description': '153M Adobe accounts',
                'date': '2013-10-03'
            },
            'yahoo_2013': {
                'name': 'Yahoo (2013)',
                'description': '3B Yahoo accounts',
                'date': '2013-08-01'
            },
            'equifax_2017': {
                'name': 'Equifax (2017)',
                'description': '147M Equifax records',
                'date': '2017-07-29'
            },
            'facebook_2019': {
                'name': 'Facebook (2019)',
                'description': '533M Facebook users',
                'date': '2019-04-01'
            }
        }
        
        # Note: Actual checking would require access to breach databases
        # This is for demonstration purposes only
        
        return results
    
    async def generate_breach_report(self, email: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive breach report"""
        
        breach_report = {
            'email': email,
            'total_breaches_found': len(results),
            'breach_sources': [],
            'risk_level': 'Unknown',
            'recommendations': [],
            'last_checked': None
        }
        
        if results:
            breach_report['breach_sources'] = [result['source'] for result in results]
            
            # Determine risk level based on number and severity of breaches
            if len(results) >= 5:
                breach_report['risk_level'] = 'High'
            elif len(results) >= 2:
                breach_report['risk_level'] = 'Medium'
            elif len(results) >= 1:
                breach_report['risk_level'] = 'Low'
            else:
                breach_report['risk_level'] = 'Clean'
            
            # Generate recommendations
            if results:
                breach_report['recommendations'] = [
                    'Change passwords for all accounts associated with this email',
                    'Enable two-factor authentication where possible',
                    'Monitor accounts for suspicious activity',
                    'Consider using a password manager',
                    'Check credit reports for unauthorized accounts'
                ]
        
        return breach_report
    
    async def check_breaches(self, email: str) -> Dict[str, Any]:
        """Check all available breach sources for email"""
        if not self.session:
            await self.create_session()
        
        self.logger.info(f"Checking breaches for email: {email}")
        
        try:
            results = []
            
            # Check various sources
            checks = [
                self.check_haveibeenpwned(email),
                self.check_breachdirectory(email)
            ]
            
            for check in checks:
                try:
                    result = await check
                    if result:
                        results.append(result)
                    
                    # Add delay between checks
                    await asyncio.sleep(self.config.delay_between_requests)
                except Exception as e:
                    self.logger.error(f"Error in breach check: {str(e)}")
            
            # Check local files and pastebins
            local_results = await self.check_local_breach_files(email)
            paste_results = await self.check_pastebins(email)
            social_results = await self.check_social_media_breaches(email)
            
            results.extend(local_results)
            results.extend(paste_results)
            results.extend(social_results)
            
            # Generate comprehensive report
            report = await self.generate_breach_report(email, results)
            
            self.logger.info(f"Breach check complete for {email}: {len(results)} potential breaches found")
            
            return report
        finally:
            # Ensure session is closed
            try:
                await self.close_session()
            except Exception as e:
                self.logger.warning(f"Error closing breach checker session: {str(e)}")
    
    async def bulk_check_breaches(self, emails: List[str]) -> Dict[str, Dict[str, Any]]:
        """Check multiple emails for breaches"""
        results = {}
        
        for email in emails:
            results[email] = await self.check_breaches(email)
            # Add delay between bulk checks
            await asyncio.sleep(self.config.delay_between_requests * 2)
        
        return results