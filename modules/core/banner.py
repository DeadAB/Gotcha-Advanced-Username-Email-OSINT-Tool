"""
Banner module for Gotcha! OSINT tool
"""

import random
from colorama import Fore, Style, init

# Initialize colorama
init()

def print_banner():
    """Print the Gotcha! banner"""
    
    banners = [
        f"""
{Fore.RED}
 ██████╗  ██████╗ ████████╗ ██████╗██╗  ██╗ █████╗ ██╗
██╔════╝ ██╔═══██╗╚══██╔══╝██╔════╝██║  ██║██╔══██╗██║
██║  ███╗██║   ██║   ██║   ██║     ███████║███████║██║
██║   ██║██║   ██║   ██║   ██║     ██╔══██║██╔══██║╚═╝
╚██████╔╝╚██████╔╝   ██║   ╚██████╗██║  ██║██║  ██║██╗
 ╚═════╝  ╚═════╝    ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝
{Style.RESET_ALL}""",
        
        f"""
{Fore.CYAN}
  ____       _       _           _ 
 / ___| ___ | |_ ___| |__   __ _| |
| |  _ / _ \| __/ __| '_ \ / _` | |
| |_| | (_) | || (__| | | | (_| |_|
 \____|\___/ \__\___|_| |_|\__,_(_)
{Style.RESET_ALL}""",
        
        f"""
{Fore.YELLOW}
   ___      _       _           _ 
  / __|___ | |_ ___| |_  __ _  | |
 | (_ / _ \|  _/ __| ' \/ _` | |_|
  \___\___/ \__\___|_||_\__,_| (_)
{Style.RESET_ALL}"""
    ]
    
    print(random.choice(banners))
    print(f"{Fore.GREEN}[+] Advanced Username & Email OSINT Tool{Style.RESET_ALL}")
    print(f"{Fore.BLUE}[+] Version: 1.0.0{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}[+] Author: Security Research Team{Style.RESET_ALL}")
    print(f"{Fore.WHITE}[+] Find online profiles without API keys{Style.RESET_ALL}")
    print("="*60)
    print()

def print_section_header(title):
    """Print a section header"""
    print(f"\n{Fore.CYAN}{'='*20} {title} {'='*20}{Style.RESET_ALL}")

def print_success(message):
    """Print success message"""
    print(f"{Fore.GREEN}[+] {message}{Style.RESET_ALL}")

def print_warning(message):
    """Print warning message"""
    print(f"{Fore.YELLOW}[!] {message}{Style.RESET_ALL}")

def print_error(message):
    """Print error message"""
    print(f"{Fore.RED}[-] {message}{Style.RESET_ALL}")

def print_info(message):
    """Print info message"""
    print(f"{Fore.BLUE}[*] {message}{Style.RESET_ALL}")