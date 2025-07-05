"""
Social Media Hunter - Find usernames across social platforms
"""

import asyncio
import aiohttp
import random
from typing import List, Dict, Any
from urllib.parse import urljoin
from core.config import Config
from core.logger import get_logger

class SocialMediaHunter:
    """Hunt for usernames across social media platforms"""
    
    def __init__(self):
        self.config = Config()
        self.logger = get_logger()
        self.session = None
        
        # Social media platforms with their URL patterns
        self.platforms = {
            'twitter': {
                'url': 'https://twitter.com/{}',
                'check_url': 'https://twitter.com/{}',
                'indicators': ['Profile', 'Joined', 'Following', 'Followers'],
                'not_found_indicators': ['This account doesn\'t exist', 'Account suspended']
            },
            'instagram': {
                'url': 'https://instagram.com/{}',
                'check_url': 'https://instagram.com/{}',
                'indicators': ['followers', 'following', 'posts'],
                'not_found_indicators': ['Sorry, this page isn\'t available']
            },
            'facebook': {
                'url': 'https://facebook.com/{}',
                'check_url': 'https://facebook.com/{}',
                'indicators': ['Facebook'],
                'not_found_indicators': ['This content isn\'t available']
            },
            'linkedin': {
                'url': 'https://linkedin.com/in/{}',
                'check_url': 'https://linkedin.com/in/{}',
                'indicators': ['LinkedIn', 'connections', 'Experience'],
                'not_found_indicators': ['This profile doesn\'t exist']
            },
            'github': {
                'url': 'https://github.com/{}',
                'check_url': 'https://github.com/{}',
                'indicators': ['repositories', 'followers', 'following'],
                'not_found_indicators': ['Not Found']
            },
            'youtube': {
                'url': 'https://youtube.com/@{}',
                'check_url': 'https://youtube.com/@{}',
                'indicators': ['subscribers', 'videos', 'YouTube'],
                'not_found_indicators': ['This channel doesn\'t exist']
            },
            'tiktok': {
                'url': 'https://tiktok.com/@{}',
                'check_url': 'https://tiktok.com/@{}',
                'indicators': ['Following', 'Followers', 'Likes'],
                'not_found_indicators': ['Couldn\'t find this account']
            },
            'reddit': {
                'url': 'https://reddit.com/user/{}',
                'check_url': 'https://reddit.com/user/{}',
                'indicators': ['Post Karma', 'Comment Karma'],
                'not_found_indicators': ['page not found']
            },
            'pinterest': {
                'url': 'https://pinterest.com/{}',
                'check_url': 'https://pinterest.com/{}',
                'indicators': ['Pinterest', 'pins', 'boards'],
                'not_found_indicators': ['Sorry, we couldn\'t find that page']
            },
            'snapchat': {
                'url': 'https://snapchat.com/add/{}',
                'check_url': 'https://snapchat.com/add/{}',
                'indicators': ['Snapchat'],
                'not_found_indicators': ['Oh snap! Something went wrong']
            },
            'discord': {
                'url': 'https://discord.com/users/{}',
                'check_url': 'https://discord.com/users/{}',
                'indicators': ['Discord'],
                'not_found_indicators': ['User not found']
            },
            'twitch': {
                'url': 'https://twitch.tv/{}',
                'check_url': 'https://twitch.tv/{}',
                'indicators': ['Twitch', 'followers', 'following'],
                'not_found_indicators': ['Sorry. Unless you\'ve got a time machine']
            },
            'spotify': {
                'url': 'https://open.spotify.com/user/{}',
                'check_url': 'https://open.spotify.com/user/{}',
                'indicators': ['Spotify', 'playlists'],
                'not_found_indicators': ['Page not found']
            },
            'medium': {
                'url': 'https://medium.com/@{}',
                'check_url': 'https://medium.com/@{}',
                'indicators': ['Medium', 'followers', 'following'],
                'not_found_indicators': ['Page not found']
            },
            'devto': {
                'url': 'https://dev.to/{}',
                'check_url': 'https://dev.to/{}',
                'indicators': ['DEV Community', 'posts', 'followers'],
                'not_found_indicators': ['404']
            },
            'behance': {
                'url': 'https://behance.net/{}',
                'check_url': 'https://behance.net/{}',
                'indicators': ['Behance', 'projects', 'followers'],
                'not_found_indicators': ['Page Not Found']
            },
            'dribbble': {
                'url': 'https://dribbble.com/{}',
                'check_url': 'https://dribbble.com/{}',
                'indicators': ['Dribbble', 'shots', 'followers'],
                'not_found_indicators': ['Page not found']
            },
            'vimeo': {
                'url': 'https://vimeo.com/{}',
                'check_url': 'https://vimeo.com/{}',
                'indicators': ['Vimeo', 'videos', 'followers'],
                'not_found_indicators': ['Page not found']
            },
            'soundcloud': {
                'url': 'https://soundcloud.com/{}',
                'check_url': 'https://soundcloud.com/{}',
                'indicators': ['SoundCloud', 'followers', 'following'],
                'not_found_indicators': ['We can\'t find that user']
            },
            'tumblr': {
                'url': 'https://{}.tumblr.com',
                'check_url': 'https://{}.tumblr.com',
                'indicators': ['Tumblr'],
                'not_found_indicators': ['There\'s nothing here']
            },
            'flickr': {
                'url': 'https://flickr.com/people/{}',
                'check_url': 'https://flickr.com/people/{}',
                'indicators': ['Flickr', 'photos'],
                'not_found_indicators': ['Page not found']
            },
            # Adult platforms (for security research)
            'pornhub': {
                'url': 'https://pornhub.com/users/{}',
                'check_url': 'https://pornhub.com/users/{}',
                'indicators': ['profile', 'videos', 'subscribers'],
                'not_found_indicators': ['User not found', 'Page not found']
            },
            'xvideos': {
                'url': 'https://xvideos.com/profiles/{}',
                'check_url': 'https://xvideos.com/profiles/{}',
                'indicators': ['profile', 'videos'],
                'not_found_indicators': ['User not found', 'Profile not found']
            },
            'redtube': {
                'url': 'https://redtube.com/users/{}',
                'check_url': 'https://redtube.com/users/{}',
                'indicators': ['profile', 'videos'],
                'not_found_indicators': ['User not found']
            },
            'onlyfans': {
                'url': 'https://onlyfans.com/{}',
                'check_url': 'https://onlyfans.com/{}',
                'indicators': ['OnlyFans', 'profile'],
                'not_found_indicators': ['User not found', 'Page not found']
            },
            'chaturbate': {
                'url': 'https://chaturbate.com/{}',
                'check_url': 'https://chaturbate.com/{}',
                'indicators': ['chaturbate', 'profile'],
                'not_found_indicators': ['User not found']
            },
            'cam4': {
                'url': 'https://cam4.com/{}',
                'check_url': 'https://cam4.com/{}',
                'indicators': ['cam4', 'profile'],
                'not_found_indicators': ['User not found']
            },
            'myfreecams': {
                'url': 'https://profiles.myfreecams.com/{}',
                'check_url': 'https://profiles.myfreecams.com/{}',
                'indicators': ['MyFreeCams', 'profile'],
                'not_found_indicators': ['Profile not found']
            },
            'stripchat': {
                'url': 'https://stripchat.com/{}',
                'check_url': 'https://stripchat.com/{}',
                'indicators': ['stripchat', 'profile'],
                'not_found_indicators': ['User not found']
            },
            'livejasmin': {
                'url': 'https://livejasmin.com/en/girl/{}',
                'check_url': 'https://livejasmin.com/en/girl/{}',
                'indicators': ['LiveJasmin', 'profile'],
                'not_found_indicators': ['Profile not found']
            },
            'bongacams': {
                'url': 'https://bongacams.com/{}',
                'check_url': 'https://bongacams.com/{}',
                'indicators': ['BongaCams', 'profile'],
                'not_found_indicators': ['User not found']
            },
            'camsoda': {
                'url': 'https://camsoda.com/{}',
                'check_url': 'https://camsoda.com/{}',
                'indicators': ['CamSoda', 'profile'],
                'not_found_indicators': ['User not found']
            },
            'fetlife': {
                'url': 'https://fetlife.com/users/{}',
                'check_url': 'https://fetlife.com/users/{}',
                'indicators': ['FetLife', 'profile', 'kinks'],
                'not_found_indicators': ['User not found']
            }
        }
    
    async def create_session(self):
        """Create aiohttp session with proper configuration"""
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
    
    async def check_username_on_platform(self, username: str, platform: str, platform_data: Dict) -> Dict[str, Any]:
        """Check if username exists on a specific platform"""
        try:
            url = platform_data['check_url'].format(username)
            
            headers = {
                'User-Agent': random.choice(self.config.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            async with self.session.get(url, headers=headers) as response:
                content = await response.text()
                
                result = {
                    'platform': platform,
                    'username': username,
                    'url': platform_data['url'].format(username),
                    'exists': False,
                    'status_code': response.status,
                    'response_time': 0,
                    'additional_info': {}
                }
                
                # Check if profile exists
                if response.status == 200:
                    # Check for positive indicators
                    positive_indicators = any(indicator.lower() in content.lower() 
                                           for indicator in platform_data['indicators'])
                    
                    # Check for negative indicators
                    negative_indicators = any(indicator.lower() in content.lower() 
                                           for indicator in platform_data['not_found_indicators'])
                    
                    if positive_indicators and not negative_indicators:
                        result['exists'] = True
                        result['additional_info'] = await self.extract_additional_info(content, platform)
                
                elif response.status == 404:
                    result['exists'] = False
                
                return result
        
        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout checking {username} on {platform}")
            return {
                'platform': platform,
                'username': username,
                'url': platform_data['url'].format(username),
                'exists': False,
                'status_code': 0,
                'error': 'Timeout'
            }
        except Exception as e:
            self.logger.error(f"Error checking {username} on {platform}: {str(e)}")
            return {
                'platform': platform,
                'username': username,
                'url': platform_data['url'].format(username),
                'exists': False,
                'status_code': 0,
                'error': str(e)
            }
    
    async def extract_additional_info(self, content: str, platform: str) -> Dict[str, Any]:
        """Extract additional information from profile pages"""
        info = {}
        
        try:
            if platform == 'twitter':
                # Extract follower count, following count, etc.
                pass
            elif platform == 'github':
                # Extract repository count, contribution info, etc.
                pass
            elif platform == 'linkedin':
                # Extract professional information
                pass
            # Add more platform-specific extraction logic here
        except Exception as e:
            self.logger.debug(f"Error extracting info from {platform}: {str(e)}")
        
        return info
    
    async def hunt_username(self, username: str, include_adult: bool = False) -> List[Dict[str, Any]]:
        """Hunt for a username across social media platforms"""
        self.logger.info(f"Starting social media hunt for username: {username}")
        
        if not self.session:
            await self.create_session()
        
        try:
            # Filter platforms based on adult content preference
            platforms_to_check = {}
            adult_platforms = ['pornhub', 'xvideos', 'redtube', 'onlyfans', 'chaturbate', 
                             'cam4', 'myfreecams', 'stripchat', 'livejasmin', 'bongacams', 
                             'camsoda', 'fetlife']
            
            for platform, platform_data in self.platforms.items():
                if platform in adult_platforms and not include_adult:
                    continue  # Skip adult platforms if not requested
                platforms_to_check[platform] = platform_data
            
            # Create tasks for selected platforms
            tasks = []
            for platform, platform_data in platforms_to_check.items():
                task = self.check_username_on_platform(username, platform, platform_data)
                tasks.append(task)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return only valid results
            valid_results = []
            for result in results:
                if isinstance(result, dict) and result.get('exists', False):
                    valid_results.append(result)
            
            self.logger.info(f"Found {len(valid_results)} profiles for {username}")
            return valid_results
        finally:
            # Ensure session is closed
            try:
                await self.close_session()
            except Exception as e:
                self.logger.warning(f"Error closing social media hunter session: {str(e)}")
    
    async def hunt_multiple_usernames(self, usernames: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Hunt for multiple usernames"""
        results = {}
        
        for username in usernames:
            results[username] = await self.hunt_username(username)
            # Add delay between username checks
            await asyncio.sleep(self.config.delay_between_requests)
        
        return results
    
    def get_platform_list(self) -> List[str]:
        """Get list of supported platforms"""
        return list(self.platforms.keys())
    
    def add_custom_platform(self, name: str, url_pattern: str, indicators: List[str], not_found_indicators: List[str]):
        """Add a custom platform to check"""
        self.platforms[name] = {
            'url': url_pattern,
            'check_url': url_pattern,
            'indicators': indicators,
            'not_found_indicators': not_found_indicators
        }