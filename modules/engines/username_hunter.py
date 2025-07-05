"""
Username Hunter - Find usernames across various platforms
"""

import asyncio
import aiohttp
import random
from typing import List, Dict, Any
from core.config import Config
from core.logger import get_logger

class UsernameHunter:
    """Hunt for usernames across general platforms"""
    
    def __init__(self):
        self.config = Config()
        self.logger = get_logger()
        self.session = None
        
        # General websites and platforms
        self.general_sites = {
            'pastebin': {
                'url': 'https://pastebin.com/u/{}',
                'check_url': 'https://pastebin.com/u/{}',
                'indicators': ['pastebin', 'Public Pastes', 'Profile'],
                'not_found_indicators': ['Unknown User', 'Not Found']
            },
            'about_me': {
                'url': 'https://about.me/{}',
                'check_url': 'https://about.me/{}',
                'indicators': ['about.me', 'profile'],
                'not_found_indicators': ['Page not found']
            },
            'gravatar': {
                'url': 'https://gravatar.com/{}',
                'check_url': 'https://gravatar.com/{}',
                'indicators': ['Gravatar', 'avatar'],
                'not_found_indicators': ['Page not found']
            },
            'keybase': {
                'url': 'https://keybase.io/{}',
                'check_url': 'https://keybase.io/{}',
                'indicators': ['Keybase', 'proofs', 'keys'],
                'not_found_indicators': ['User not found']
            },
            'hackernews': {
                'url': 'https://news.ycombinator.com/user?id={}',
                'check_url': 'https://news.ycombinator.com/user?id={}',
                'indicators': ['Hacker News', 'karma', 'submissions'],
                'not_found_indicators': ['No such user']
            },
            'product_hunt': {
                'url': 'https://producthunt.com/@{}',
                'check_url': 'https://producthunt.com/@{}',
                'indicators': ['Product Hunt', 'followers', 'following'],
                'not_found_indicators': ['Page not found']
            },
            'angel_list': {
                'url': 'https://angel.co/{}',
                'check_url': 'https://angel.co/{}',
                'indicators': ['AngelList', 'angel.co'],
                'not_found_indicators': ['Page not found']
            },
            'foursquare': {
                'url': 'https://foursquare.com/{}',
                'check_url': 'https://foursquare.com/{}',
                'indicators': ['Foursquare', 'check-ins'],
                'not_found_indicators': ['Page not found']
            },
            'last_fm': {
                'url': 'https://last.fm/user/{}',
                'check_url': 'https://last.fm/user/{}',
                'indicators': ['Last.fm', 'scrobbles', 'artists'],
                'not_found_indicators': ['User not found']
            },
            'mix_cloud': {
                'url': 'https://mixcloud.com/{}',
                'check_url': 'https://mixcloud.com/{}',
                'indicators': ['Mixcloud', 'cloudcasts', 'followers'],
                'not_found_indicators': ['Page not found']
            },
            # Adult platforms (for security research)
            'adultfriendfinder': {
                'url': 'https://adultfriendfinder.com/profile/{}',
                'check_url': 'https://adultfriendfinder.com/profile/{}',
                'indicators': ['AdultFriendFinder', 'profile'],
                'not_found_indicators': ['Profile not found', 'User not found']
            },
            'ashley_madison': {
                'url': 'https://ashleymadison.com/profile/{}',
                'check_url': 'https://ashleymadison.com/profile/{}',
                'indicators': ['Ashley Madison', 'profile'],
                'not_found_indicators': ['Profile not found']
            },
            'seeking': {
                'url': 'https://seeking.com/member/{}',
                'check_url': 'https://seeking.com/member/{}',
                'indicators': ['Seeking', 'profile'],
                'not_found_indicators': ['Profile not found']
            },
            'alt_com': {
                'url': 'https://alt.com/profile/{}',
                'check_url': 'https://alt.com/profile/{}',
                'indicators': ['Alt.com', 'profile'],
                'not_found_indicators': ['Profile not found']
            },
            'swappernet': {
                'url': 'https://swappernet.com/{}',
                'check_url': 'https://swappernet.com/{}',
                'indicators': ['SwapperNet', 'profile'],
                'not_found_indicators': ['Profile not found']
            },
            'faphouse': {
                'url': 'https://faphouse.com/models/{}',
                'check_url': 'https://faphouse.com/models/{}',
                'indicators': ['FapHouse', 'model', 'videos'],
                'not_found_indicators': ['Model not found']
            },
            'manyvids': {
                'url': 'https://manyvids.com/Profile/{}/Store/Videos/',
                'check_url': 'https://manyvids.com/Profile/{}/Store/Videos/',
                'indicators': ['ManyVids', 'profile', 'videos'],
                'not_found_indicators': ['Profile not found']
            },
            'clips4sale': {
                'url': 'https://clips4sale.com/studio/{}',
                'check_url': 'https://clips4sale.com/studio/{}',
                'indicators': ['Clips4Sale', 'studio'],
                'not_found_indicators': ['Studio not found']
            },
            'iwantclips': {
                'url': 'https://iwantclips.com/store/{}',
                'check_url': 'https://iwantclips.com/store/{}',
                'indicators': ['iWantClips', 'store'],
                'not_found_indicators': ['Store not found']
            },
            'justforfans': {
                'url': 'https://justfor.fans/{}',
                'check_url': 'https://justfor.fans/{}',
                'indicators': ['JustForFans', 'profile'],
                'not_found_indicators': ['Profile not found']
            }
        }
        
        # Developer platforms
        self.developer_platforms = {
            'github': {
                'url': 'https://github.com/{}',
                'check_url': 'https://github.com/{}',
                'indicators': ['GitHub', 'repositories', 'followers'],
                'not_found_indicators': ['Not Found']
            },
            'gitlab': {
                'url': 'https://gitlab.com/{}',
                'check_url': 'https://gitlab.com/{}',
                'indicators': ['GitLab', 'projects', 'contributions'],
                'not_found_indicators': ['Page not found']
            },
            'bitbucket': {
                'url': 'https://bitbucket.org/{}',
                'check_url': 'https://bitbucket.org/{}',
                'indicators': ['Bitbucket', 'repositories'],
                'not_found_indicators': ['Page not found']
            },
            'stackoverflow': {
                'url': 'https://stackoverflow.com/users/{}',
                'check_url': 'https://stackoverflow.com/users/{}',
                'indicators': ['Stack Overflow', 'reputation', 'answers'],
                'not_found_indicators': ['User not found']
            },
            'codepen': {
                'url': 'https://codepen.io/{}',
                'check_url': 'https://codepen.io/{}',
                'indicators': ['CodePen', 'pens', 'followers'],
                'not_found_indicators': ['Page not found']
            },
            'replit': {
                'url': 'https://replit.com/@{}',
                'check_url': 'https://replit.com/@{}',
                'indicators': ['Replit', 'repls'],
                'not_found_indicators': ['Page not found']
            },
            'hackerone': {
                'url': 'https://hackerone.com/{}',
                'check_url': 'https://hackerone.com/{}',
                'indicators': ['HackerOne', 'reputation', 'reports'],
                'not_found_indicators': ['Page not found']
            },
            'bugcrowd': {
                'url': 'https://bugcrowd.com/{}',
                'check_url': 'https://bugcrowd.com/{}',
                'indicators': ['Bugcrowd', 'researcher'],
                'not_found_indicators': ['Page not found']
            },
            'kaggle': {
                'url': 'https://kaggle.com/{}',
                'check_url': 'https://kaggle.com/{}',
                'indicators': ['Kaggle', 'competitions', 'datasets'],
                'not_found_indicators': ['Page not found']
            },
            'dockerhub': {
                'url': 'https://hub.docker.com/u/{}',
                'check_url': 'https://hub.docker.com/u/{}',
                'indicators': ['Docker Hub', 'repositories'],
                'not_found_indicators': ['Page not found']
            },
            'npm': {
                'url': 'https://npmjs.com/~{}',
                'check_url': 'https://npmjs.com/~{}',
                'indicators': ['npm', 'packages'],
                'not_found_indicators': ['Page not found']
            },
            'pypi': {
                'url': 'https://pypi.org/user/{}',
                'check_url': 'https://pypi.org/user/{}',
                'indicators': ['PyPI', 'packages'],
                'not_found_indicators': ['Page not found']
            }
        }
        
        # Forums and communities
        self.forums = {
            'reddit': {
                'url': 'https://reddit.com/user/{}',
                'check_url': 'https://reddit.com/user/{}',
                'indicators': ['Reddit', 'karma', 'posts'],
                'not_found_indicators': ['page not found']
            },
            'xda': {
                'url': 'https://forum.xda-developers.com/member.php?username={}',
                'check_url': 'https://forum.xda-developers.com/member.php?username={}',
                'indicators': ['XDA', 'posts', 'thanks'],
                'not_found_indicators': ['User not found']
            },
            'disqus': {
                'url': 'https://disqus.com/by/{}',
                'check_url': 'https://disqus.com/by/{}',
                'indicators': ['Disqus', 'comments'],
                'not_found_indicators': ['Page not found']
            },
            'discourse': {
                'url': 'https://meta.discourse.org/u/{}',
                'check_url': 'https://meta.discourse.org/u/{}',
                'indicators': ['Discourse', 'posts', 'topics'],
                'not_found_indicators': ['Page not found']
            }
        }
        
        # Gaming platforms
        self.gaming_platforms = {
            'steam': {
                'url': 'https://steamcommunity.com/id/{}',
                'check_url': 'https://steamcommunity.com/id/{}',
                'indicators': ['Steam', 'games', 'profile'],
                'not_found_indicators': ['The specified profile could not be found']
            },
            'xbox': {
                'url': 'https://xboxgamertag.com/search/{}',
                'check_url': 'https://xboxgamertag.com/search/{}',
                'indicators': ['Xbox', 'gamertag'],
                'not_found_indicators': ['Gamertag not found']
            },
            'playstation': {
                'url': 'https://psnprofiles.com/{}',
                'check_url': 'https://psnprofiles.com/{}',
                'indicators': ['PSN', 'trophies', 'games'],
                'not_found_indicators': ['User not found']
            },
            'epic': {
                'url': 'https://fortnitetracker.com/profile/all/{}',
                'check_url': 'https://fortnitetracker.com/profile/all/{}',
                'indicators': ['Epic', 'stats'],
                'not_found_indicators': ['Player not found']
            },
            'battlenet': {
                'url': 'https://playoverwatch.com/en-us/career/pc/{}',
                'check_url': 'https://playoverwatch.com/en-us/career/pc/{}',
                'indicators': ['Overwatch', 'career'],
                'not_found_indicators': ['Profile not found']
            },
            'minecraft': {
                'url': 'https://namemc.com/profile/{}',
                'check_url': 'https://namemc.com/profile/{}',
                'indicators': ['Minecraft', 'UUID'],
                'not_found_indicators': ['Profile not found']
            },
            'roblox': {
                'url': 'https://roblox.com/users/profile?username={}',
                'check_url': 'https://roblox.com/users/profile?username={}',
                'indicators': ['Roblox', 'profile'],
                'not_found_indicators': ['User not found']
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
                
                return result
        
        except Exception as e:
            self.logger.error(f"Error checking {username} on {platform}: {str(e)}")
            return {
                'platform': platform,
                'username': username,
                'url': platform_data['url'].format(username),
                'exists': False,
                'error': str(e)
            }
    
    async def hunt_platforms(self, username: str, platforms: Dict) -> List[Dict[str, Any]]:
        """Hunt for username across specified platforms"""
        if not self.session:
            await self.create_session()
        
        try:
            tasks = []
            for platform, platform_data in platforms.items():
                task = self.check_username_on_platform(username, platform, platform_data)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            valid_results = []
            for result in results:
                if isinstance(result, dict) and result.get('exists', False):
                    valid_results.append(result)
            
            return valid_results
        finally:
            # Ensure session is closed
            try:
                await self.close_session()
            except Exception as e:
                self.logger.warning(f"Error closing username hunter session: {str(e)}")
    
    async def hunt_general_sites(self, username: str, include_adult: bool = False) -> List[Dict[str, Any]]:
        """Hunt for username across general websites"""
        self.logger.info(f"Hunting general sites for username: {username}")
        
        # Filter out adult platforms if not requested
        platforms_to_check = {}
        adult_platforms = ['adultfriendfinder', 'ashley_madison', 'seeking', 'alt_com', 
                         'swappernet', 'faphouse', 'manyvids', 'clips4sale', 'iwantclips', 'justforfans']
        
        for platform, platform_data in self.general_sites.items():
            if platform in adult_platforms and not include_adult:
                continue  # Skip adult platforms if not requested
            platforms_to_check[platform] = platform_data
        
        return await self.hunt_platforms(username, platforms_to_check)
    
    async def hunt_developer_platforms(self, username: str) -> List[Dict[str, Any]]:
        """Hunt for username across developer platforms"""
        self.logger.info(f"Hunting developer platforms for username: {username}")
        return await self.hunt_platforms(username, self.developer_platforms)
    
    async def hunt_forums(self, username: str) -> List[Dict[str, Any]]:
        """Hunt for username across forums"""
        self.logger.info(f"Hunting forums for username: {username}")
        return await self.hunt_platforms(username, self.forums)
    
    async def hunt_gaming_platforms(self, username: str) -> List[Dict[str, Any]]:
        """Hunt for username across gaming platforms"""
        self.logger.info(f"Hunting gaming platforms for username: {username}")
        return await self.hunt_platforms(username, self.gaming_platforms)
    
    async def hunt_adult_platforms(self, username: str) -> List[Dict[str, Any]]:
        """Hunt for username across adult platforms only"""
        self.logger.info(f"Hunting adult platforms for username: {username}")
        
        # Only adult platforms from general_sites
        adult_platforms = {
            'adultfriendfinder': self.general_sites['adultfriendfinder'],
            'ashley_madison': self.general_sites['ashley_madison'],
            'seeking': self.general_sites['seeking'],
            'alt_com': self.general_sites['alt_com'],
            'swappernet': self.general_sites['swappernet'],
            'faphouse': self.general_sites['faphouse'],
            'manyvids': self.general_sites['manyvids'],
            'clips4sale': self.general_sites['clips4sale'],
            'iwantclips': self.general_sites['iwantclips'],
            'justforfans': self.general_sites['justforfans']
        }
        
        return await self.hunt_platforms(username, adult_platforms)
    
    async def hunt_all_platforms(self, username: str, include_adult: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Hunt for username across all platforms"""
        self.logger.info(f"Starting comprehensive hunt for username: {username}")
        
        results = {
            'general_sites': await self.hunt_general_sites(username, include_adult),
            'developer_platforms': await self.hunt_developer_platforms(username),
            'forums': await self.hunt_forums(username),
            'gaming_platforms': await self.hunt_gaming_platforms(username)
        }
        
        if include_adult:
            results['adult_platforms'] = await self.hunt_adult_platforms(username)
        
        total_found = sum(len(result_list) for result_list in results.values())
        self.logger.info(f"Total profiles found for {username}: {total_found}")
        
        return results