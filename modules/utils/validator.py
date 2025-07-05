"""
Validator utilities for Gotcha! OSINT tool
"""

import re
from typing import Union, List

class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email address format"""
        if not email or not isinstance(email, str):
            return False
        
        # Basic email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email.strip()) is not None
    
    @staticmethod
    def is_valid_username(username: str) -> bool:
        """Validate username format"""
        if not username or not isinstance(username, str):
            return False
        
        # Basic username validation (alphanumeric, underscores, hyphens)
        username = username.strip()
        if len(username) < 1 or len(username) > 50:
            return False
        
        # Allow alphanumeric characters, underscores, hyphens, and dots
        username_pattern = r'^[a-zA-Z0-9._-]+$'
        return re.match(username_pattern, username) is not None
    
    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """Validate domain name format"""
        if not domain or not isinstance(domain, str):
            return False
        
        # Basic domain regex pattern
        domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return re.match(domain_pattern, domain.strip()) is not None
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """Sanitize user input"""
        if not isinstance(input_str, str):
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';\\]', '', input_str.strip())
        return sanitized
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate file path format"""
        if not file_path or not isinstance(file_path, str):
            return False
        
        # Check for path traversal attempts
        if '..' in file_path or file_path.startswith('/'):
            return False
        
        # Basic file path validation
        return len(file_path) > 0 and len(file_path) < 255
    
    @staticmethod
    def validate_targets_from_file(file_path: str) -> List[str]:
        """Validate and extract targets from file"""
        valid_targets = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Check if it's an email or username
                    if '@' in line:
                        if Validator.is_valid_email(line):
                            valid_targets.append(line)
                    else:
                        if Validator.is_valid_username(line):
                            valid_targets.append(line)
        
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")
        
        return valid_targets
    
    @staticmethod
    def validate_output_format(format_str: str) -> bool:
        """Validate output format"""
        valid_formats = ['json', 'csv', 'txt', 'xml']
        return format_str.lower() in valid_formats
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Check if filename is safe"""
        if not filename or not isinstance(filename, str):
            return False
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        return not any(char in filename for char in dangerous_chars)
    
    @staticmethod
    def normalize_username(username: str) -> str:
        """Normalize username for consistent searching"""
        if not username:
            return ""
        
        # Convert to lowercase and strip whitespace
        normalized = username.lower().strip()
        
        # Remove common prefixes
        prefixes_to_remove = ['@', 'user:', 'username:']
        for prefix in prefixes_to_remove:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
        
        return normalized
    
    @staticmethod
    def normalize_email(email: str) -> str:
        """Normalize email for consistent searching"""
        if not email:
            return ""
        
        # Convert to lowercase and strip whitespace
        normalized = email.lower().strip()
        
        # Remove mailto: prefix if present
        if normalized.startswith('mailto:'):
            normalized = normalized[7:]
        
        return normalized