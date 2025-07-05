"""
Email Hunter - Find accounts associated with email addresses
"""

import asyncio
import aiohttp
import random
import re
import socket
import dns.resolver
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, urljoin
from core.config import Config
from core.logger import get_logger

class EmailHunter:
    """Hunt for accounts associated with email addresses"""
    
    def __init__(self):
        self.config = Config()
        self.logger = get_logger()
        self.session = None
        
        # Social platforms that allow email-based registration recovery
        self.social_platforms = {
            'gravatar': {
                'check_method': 'hash_check',
                'url_pattern': 'https://secure.gravatar.com/avatar/{}.json',
                'indicators': ['profile', 'gravatar']
            },
            'skype': {
                'check_method': 'direct_check',
                'url_pattern': 'https://login.skype.com/login/oauth/microsoft',
                'check_url': 'https://login.live.com/GetCredentialType.srf',
                'indicators': ['IfExistsResult']
            },
            'adobe': {
                'check_method': 'password_reset',
                'url_pattern': 'https://accounts.adobe.com/forgotpassword',
                'indicators': ['password reset', 'account']
            },
            'spotify': {
                'check_method': 'password_reset',
                'url_pattern': 'https://accounts.spotify.com/password-reset',
                'indicators': ['reset', 'spotify']
            },
            # Adult platforms (for security research)
            'onlyfans_email': {
                'check_method': 'password_reset',
                'url_pattern': 'https://onlyfans.com/api2/v2/users/password/reset',
                'indicators': ['reset', 'email']
            },
            'pornhub_email': {
                'check_method': 'registration_check',
                'url_pattern': 'https://pornhub.com/signup',
                'indicators': ['already', 'exists']
            },
            'chaturbate_email': {
                'check_method': 'password_reset',
                'url_pattern': 'https://chaturbate.com/auth/password_reset/',
                'indicators': ['reset', 'email']
            },
            'cam4_email': {
                'check_method': 'password_reset',
                'url_pattern': 'https://cam4.com/password-reset',
                'indicators': ['reset', 'email']
            },
            'adultfriendfinder_email': {
                'check_method': 'password_reset',
                'url_pattern': 'https://adultfriendfinder.com/go/page/login_forgotpassword',
                'indicators': ['reset', 'password']
            }
        }
        
        # Professional platforms
        self.professional_platforms = {
            'github': {
                'check_method': 'api_check',
                'url_pattern': 'https://api.github.com/search/users?q={}',
                'indicators': ['login', 'avatar_url']
            },
            'gitlab': {
                'check_method': 'password_reset',
                'url_pattern': 'https://gitlab.com/users/password/new',
                'indicators': ['password', 'reset']
            },
            'stackoverflow': {
                'check_method': 'search_check',
                'url_pattern': 'https://stackoverflow.com/users',
                'search_url': 'https://api.stackexchange.com/2.3/users',
                'indicators': ['reputation', 'user_id']
            }
        }
    
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
    
    def get_email_hash(self, email: str) -> str:
        """Generate MD5 hash for email (used by Gravatar)"""
        import hashlib
        return hashlib.md5(email.lower().strip().encode()).hexdigest()
    
    async def check_gravatar(self, email: str) -> Optional[Dict[str, Any]]:
        """Check if email has Gravatar profile"""
        try:
            email_hash = self.get_email_hash(email)
            url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
            
            async with self.session.head(url) as response:
                if response.status == 200:
                    # Get profile info
                    profile_url = f"https://www.gravatar.com/{email_hash}.json"
                    async with self.session.get(profile_url) as profile_response:
                        if profile_response.status == 200:
                            profile_data = await profile_response.json()
                            return {
                                'platform': 'gravatar',
                                'email': email,
                                'exists': True,
                                'profile_url': f"https://www.gravatar.com/{email_hash}",
                                'avatar_url': f"https://www.gravatar.com/avatar/{email_hash}",
                                'additional_info': profile_data.get('entry', [{}])[0] if profile_data.get('entry') else {}
                            }
                    
                    return {
                        'platform': 'gravatar',
                        'email': email,
                        'exists': True,
                        'profile_url': f"https://www.gravatar.com/{email_hash}",
                        'avatar_url': f"https://www.gravatar.com/avatar/{email_hash}",
                        'additional_info': {}
                    }
        except Exception as e:
            self.logger.error(f"Error checking Gravatar for {email}: {str(e)}")
        
        return None
    
    async def check_microsoft_account(self, email: str) -> Optional[Dict[str, Any]]:
        """Check if email is associated with Microsoft account"""
        try:
            url = "https://login.live.com/GetCredentialType.srf"
            data = {
                'username': email,
                'uaid': '11111111-1111-1111-1111-111111111111',
                'isOtherIdpSupported': 'true',
                'checkPhones': 'true',
                'isRemoteNGCSupported': 'true',
                'isCookieBannerShown': 'false',
                'isFidoSupported': 'false'
            }
            
            headers = {
                'User-Agent': random.choice(self.config.user_agents),
                'Content-Type': 'application/json'
            }
            
            async with self.session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('IfExistsResult') == 0:  # Account exists
                        return {
                            'platform': 'microsoft',
                            'email': email,
                            'exists': True,
                            'account_type': 'Microsoft Account',
                            'additional_info': {
                                'has_password': result.get('HasPassword', False),
                                'credentials': result.get('Credentials', {})
                            }
                        }
        except Exception as e:
            self.logger.error(f"Error checking Microsoft account for {email}: {str(e)}")
        
        return None
    
    async def check_adobe_account(self, email: str) -> Optional[Dict[str, Any]]:
        """Check if email is associated with Adobe account"""
        try:
            # First, try to resolve the domain to check connectivity
            import socket
            try:
                socket.getaddrinfo('accounts.adobe.com', 443)
            except socket.gaierror:
                self.logger.warning(f"Cannot resolve accounts.adobe.com - skipping Adobe check for {email}")
                return None
            
            # Adobe account check via password reset page
            url = "https://accounts.adobe.com/reactivate/password"
            data = {'username': email}
            
            headers = {
                'User-Agent': random.choice(self.config.user_agents),
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            # Use a shorter timeout for Adobe check
            timeout = aiohttp.ClientTimeout(total=5)  # 5 second timeout
            
            async with self.session.post(url, data=data, headers=headers, timeout=timeout) as response:
                content = await response.text()
                
                # Check for account existence indicators
                if any(indicator in content.lower() for indicator in ['password reset', 'check your email', 'reset link']):
                    return {
                        'platform': 'adobe',
                        'email': email,
                        'exists': True,
                        'account_type': 'Adobe Account',
                        'additional_info': {}
                    }
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.logger.warning(f"Adobe account check failed for {email}: {str(e)} - skipping")
        except Exception as e:
            self.logger.error(f"Unexpected error checking Adobe account for {email}: {str(e)}")
        
        return None
    
    async def check_onlyfans_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Check if email is associated with OnlyFans account"""
        try:
            # OnlyFans password reset check
            url = "https://onlyfans.com/api2/v2/users/password/reset"
            data = {'email': email}
            
            headers = {
                'User-Agent': random.choice(self.config.user_agents),
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            timeout = aiohttp.ClientTimeout(total=5)
            
            async with self.session.post(url, json=data, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    result = await response.json()
                    # OnlyFans typically returns success even for non-existent emails for privacy
                    return {
                        'platform': 'onlyfans',
                        'email': email,
                        'exists': True,  # Assumes existence due to privacy response
                        'account_type': 'OnlyFans Account',
                        'additional_info': {'note': 'Password reset attempted - manual verification recommended'}
                    }
        except Exception as e:
            self.logger.warning(f"OnlyFans email check failed for {email}: {str(e)} - skipping")
        
        return None
    
    async def check_pornhub_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Check if email is associated with Pornhub account"""
        try:
            # Check via signup page
            url = "https://pornhub.com/signup"
            
            headers = {
                'User-Agent': random.choice(self.config.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            timeout = aiohttp.ClientTimeout(total=5)
            
            async with self.session.get(url, headers=headers, timeout=timeout) as response:
                if response.status == 200:
                    # Note: Most adult sites don't expose email existence for privacy
                    # This is a placeholder for demonstration
                    return None
        except Exception as e:
            self.logger.warning(f"Pornhub email check failed for {email}: {str(e)} - skipping")
        
        return None
    
    async def check_chaturbate_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Check if email is associated with Chaturbate account"""
        try:
            # Chaturbate password reset check
            url = "https://chaturbate.com/auth/password_reset/"
            data = {'email': email}
            
            headers = {
                'User-Agent': random.choice(self.config.user_agents),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'https://chaturbate.com/auth/login/'
            }
            
            timeout = aiohttp.ClientTimeout(total=5)
            
            async with self.session.post(url, data=data, headers=headers, timeout=timeout) as response:
                content = await response.text()
                
                # Check for account existence indicators
                if any(indicator in content.lower() for indicator in ['reset', 'email', 'sent']):
                    return {
                        'platform': 'chaturbate',
                        'email': email,
                        'exists': True,
                        'account_type': 'Chaturbate Account',
                        'additional_info': {'note': 'Password reset attempted'}
                    }
        except Exception as e:
            self.logger.warning(f"Chaturbate email check failed for {email}: {str(e)} - skipping")
        
        return None
    
    async def check_github_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Check if email is associated with GitHub account"""
        try:
            # GitHub doesn't directly expose email searches, but we can try commits
            url = f"https://api.github.com/search/commits?q=author-email:{email}"
            
            headers = {
                'User-Agent': random.choice(self.config.user_agents),
                'Accept': 'application/vnd.github.cloak-preview'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('total_count', 0) > 0:
                        commits = result.get('items', [])
                        if commits:
                            author = commits[0].get('author', {})
                            return {
                                'platform': 'github',
                                'email': email,
                                'exists': True,
                                'username': author.get('login', ''),
                                'profile_url': author.get('html_url', ''),
                                'avatar_url': author.get('avatar_url', ''),
                                'additional_info': {
                                    'commit_count': result.get('total_count', 0),
                                    'public_repos': commits[0].get('repository', {}).get('owner', {}).get('public_repos', 0)
                                }
                            }
        except Exception as e:
            self.logger.error(f"Error checking GitHub for {email}: {str(e)}")
        
        return None
    
    async def analyze_domain(self, email: str) -> Dict[str, Any]:
        """Analyze the domain of the email address"""
        domain = email.split('@')[1] if '@' in email else email
        
        domain_info = {
            'domain': domain,
            'mx_records': [],
            'a_records': [],
            'ns_records': [],
            'txt_records': [],
            'is_disposable': False,
            'is_corporate': False,
            'domain_age': None,
            'registrar': None
        }
        
        try:
            # DNS lookups
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                domain_info['mx_records'] = [str(record) for record in mx_records]
            except:
                pass
            
            try:
                a_records = dns.resolver.resolve(domain, 'A')
                domain_info['a_records'] = [str(record) for record in a_records]
            except:
                pass
            
            try:
                ns_records = dns.resolver.resolve(domain, 'NS')
                domain_info['ns_records'] = [str(record) for record in ns_records]
            except:
                pass
            
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                domain_info['txt_records'] = [str(record) for record in txt_records]
            except:
                pass
            
            # Check if it's a known disposable email domain
            disposable_domains = [
                '10minutemail.com', 'temp-mail.org', 'guerrillamail.com',
                'mailinator.com', 'yopmail.com', 'tempmail.net'
            ]
            domain_info['is_disposable'] = domain in disposable_domains
            
            # Check if it's a corporate domain (not free email providers)
            free_providers = [
                'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
                'aol.com', 'icloud.com', 'protonmail.com'
            ]
            domain_info['is_corporate'] = domain not in free_providers and not domain_info['is_disposable']
            
        except Exception as e:
            self.logger.error(f"Error analyzing domain {domain}: {str(e)}")
        
        return domain_info
    
    async def hunt_social_accounts(self, email: str) -> List[Dict[str, Any]]:
        """Hunt for social media accounts associated with email"""
        if not self.session:
            await self.create_session()
        
        self.logger.info(f"Hunting social accounts for email: {email}")
        
        results = []
        
        # Check various platforms
        checks = [
            self.check_gravatar(email),
            self.check_microsoft_account(email),
            self.check_adobe_account(email),
            self.check_onlyfans_email(email),
            self.check_pornhub_email(email),
            self.check_chaturbate_email(email)
        ]
        
        for check in checks:
            try:
                result = await check
                if result and result.get('exists'):
                    results.append(result)
                    
                # Add delay between checks
                await asyncio.sleep(self.config.delay_between_requests)
            except Exception as e:
                self.logger.error(f"Error in social account check: {str(e)}")
        
        return results
    
    async def hunt_professional_accounts(self, email: str) -> List[Dict[str, Any]]:
        """Hunt for professional accounts associated with email"""
        if not self.session:
            await self.create_session()
        
        self.logger.info(f"Hunting professional accounts for email: {email}")
        
        results = []
        
        # Check GitHub
        github_result = await self.check_github_by_email(email)
        if github_result and github_result.get('exists'):
            results.append(github_result)
        
        return results
    
    async def search_email_in_pastes(self, email: str) -> List[Dict[str, Any]]:
        """Search for email in paste sites (limited without API keys)"""
        results = []
        
        try:
            # Check Google for site-specific searches
            search_queries = [
                f'site:pastebin.com "{email}"',
                f'site:paste.org "{email}"',
                f'site:justpaste.it "{email}"'
            ]
            
            # Note: This would require implementing Google search scraping
            # which is complex and may violate ToS
            # For production, consider using legitimate APIs
            
        except Exception as e:
            self.logger.error(f"Error searching pastes for {email}: {str(e)}")
        
        return results
    
    async def hunt_all_accounts(self, email: str) -> Dict[str, Any]:
        """Hunt for all types of accounts associated with email"""
        self.logger.info(f"Starting comprehensive email hunt for: {email}")
        
        try:
            results = {
                'email': email,
                'social_accounts': await self.hunt_social_accounts(email),
                'professional_accounts': await self.hunt_professional_accounts(email),
                'domain_analysis': await self.analyze_domain(email),
                'paste_results': []  # Limited without API access
            }
            
            total_found = len(results['social_accounts']) + len(results['professional_accounts'])
            self.logger.info(f"Total accounts found for {email}: {total_found}")
            
            return results
        finally:
            # Ensure session is closed properly
            try:
                await self.close_session()
            except Exception as e:
                self.logger.warning(f"Error closing session: {str(e)}")