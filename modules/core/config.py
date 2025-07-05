"""
Configuration module for Gotcha! OSINT tool
"""

import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration manager for Gotcha!"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
            ],
            "timeout": 10,
            "max_workers": 50,
            "delay_between_requests": 0.1,
            "max_retries": 3,
            "verify_ssl": True,
            "proxy": {
                "enabled": False,
                "http": None,
                "https": None
            },
            "output": {
                "default_format": "json",
                "save_screenshots": False,
                "include_metadata": True
            },
            "social_media": {
                "enabled": True,
                "platforms": [
                    "twitter", "instagram", "facebook", "linkedin", "github",
                    "youtube", "tiktok", "snapchat", "pinterest", "reddit",
                    "discord", "telegram", "whatsapp", "spotify", "twitch"
                ]
            },
            "developer_platforms": {
                "enabled": True,
                "platforms": [
                    "github", "gitlab", "bitbucket", "stackoverflow", "hackerone",
                    "bugcrowd", "codepen", "replit", "devto", "hackernoon",
                    "medium", "kaggle", "dockerhub", "npm", "pypi"
                ]
            },
            "gaming_platforms": {
                "enabled": True,
                "platforms": [
                    "steam", "xbox", "playstation", "nintendo", "epic",
                    "twitch", "discord", "battlenet", "origin", "uplay"
                ]
            },
            "breach_check": {
                "enabled": True,
                "sources": [
                    "haveibeenpwned", "dehashed", "intelx", "breachdirectory"
                ]
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with default config
                    return {**default_config, **loaded_config}
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Save default config if file doesn't exist
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key: str, default: Any = None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    @property
    def user_agents(self):
        """Get list of user agents"""
        return self.get('user_agents', [])
    
    @property
    def timeout(self):
        """Get request timeout"""
        return self.get('timeout', 10)
    
    @property
    def max_workers(self):
        """Get maximum number of workers"""
        return self.get('max_workers', 50)
    
    @property
    def delay_between_requests(self):
        """Get delay between requests"""
        return self.get('delay_between_requests', 0.1)
    
    @property
    def max_retries(self):
        """Get maximum number of retries"""
        return self.get('max_retries', 3)