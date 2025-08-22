#!/usr/bin/env python3
"""
Setup script to configure free proxy services for GitHub Actions.
This helps bypass IP-based blocking in CI/CD environments.
"""

import requests
import logging
from typing import List, Optional
import json
import random

class FreeProxyManager:
    """Manages free proxy services for anti-detection."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_free_proxies(self) -> List[str]:
        """Get a list of free working proxies."""
        proxies = []
        
        # Try multiple free proxy sources
        sources = [
            self._get_proxies_from_proxylist,
            self._get_proxies_from_freeproxy,
            self._get_proxies_manual_list
        ]
        
        for source in sources:
            try:
                source_proxies = source()
                if source_proxies:
                    proxies.extend(source_proxies)
                    self.logger.info(f"Retrieved {len(source_proxies)} proxies from {source.__name__}")
            except Exception as e:
                self.logger.warning(f"Failed to get proxies from {source.__name__}: {e}")
        
        # Remove duplicates
        proxies = list(set(proxies))
        
        # Test and filter working proxies
        working_proxies = self._test_proxies(proxies[:20])  # Test max 20 to save time
        
        self.logger.info(f"Found {len(working_proxies)} working proxies out of {len(proxies)} total")
        return working_proxies
    
    def _get_proxies_from_proxylist(self) -> List[str]:
        """Get proxies from proxy-list.download API."""
        try:
            # Free proxy list API
            url = "https://www.proxy-list.download/api/v1/get?type=http&anon=elite&format=plain"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                proxies = []
                for line in response.text.strip().split('\n'):
                    if ':' in line:
                        ip, port = line.strip().split(':')
                        proxies.append(f"http://{ip}:{port}")
                return proxies[:10]  # Limit to 10 proxies
        except Exception as e:
            self.logger.warning(f"Failed to get proxies from proxy-list.download: {e}")
        
        return []
    
    def _get_proxies_from_freeproxy(self) -> List[str]:
        """Get proxies from another free source."""
        try:
            # Another free proxy source
            url = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                proxies = []
                for line in response.text.strip().split('\n')[:10]:  # Limit to 10
                    if ':' in line and '.' in line:
                        proxy = f"http://{line.strip()}"
                        proxies.append(proxy)
                return proxies
        except Exception as e:
            self.logger.warning(f"Failed to get proxies from GitHub source: {e}")
        
        return []
    
    def _get_proxies_manual_list(self) -> List[str]:
        """Fallback manual list of known free proxies."""
        # These are example proxies - in practice you'd maintain an updated list
        manual_proxies = [
            "http://51.158.68.133:8811",
            "http://51.158.108.135:8811", 
            "http://164.92.111.134:8080",
            "http://185.162.231.167:80",
            "http://20.111.54.16:8123"
        ]
        return manual_proxies
    
    def _test_proxies(self, proxies: List[str]) -> List[str]:
        """Test which proxies are actually working."""
        working_proxies = []
        
        for proxy in proxies[:10]:  # Test max 10 to save time
            try:
                # Test with a simple HTTP request
                response = requests.get(
                    "http://httpbin.org/ip",
                    proxies={"http": proxy, "https": proxy},
                    timeout=10
                )
                
                if response.status_code == 200:
                    working_proxies.append(proxy)
                    self.logger.info(f"Proxy working: {proxy}")
                else:
                    self.logger.debug(f"Proxy failed: {proxy}")
                    
            except Exception as e:
                self.logger.debug(f"Proxy test failed for {proxy}: {e}")
        
        return working_proxies
    
    def save_proxies_to_env(self, proxies: List[str]) -> None:
        """Save working proxies to environment variable format."""
        if proxies:
            proxy_string = ",".join(proxies)
            print(f"PROXY_LIST={proxy_string}")
            
            # Also save to a file for GitHub Actions
            with open("proxy_list.txt", "w") as f:
                for proxy in proxies:
                    f.write(f"{proxy}\n")
            
            print(f"Saved {len(proxies)} working proxies to proxy_list.txt")
        else:
            print("No working proxies found")

def main():
    """Main function to setup free proxies."""
    logging.basicConfig(level=logging.INFO)
    
    manager = FreeProxyManager()
    print("Searching for free working proxies...")
    
    proxies = manager.get_free_proxies()
    manager.save_proxies_to_env(proxies)
    
    if proxies:
        print(f"SUCCESS: Found {len(proxies)} working proxies")
        print("You can now use these in your scraper:")
        for i, proxy in enumerate(proxies[:3], 1):
            print(f"  {i}. {proxy}")
    else:
        print("WARNING: No working proxies found")
        print("The scraper will run without proxies (may be blocked)")

if __name__ == "__main__":
    main()
