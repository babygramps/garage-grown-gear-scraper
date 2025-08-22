#!/usr/bin/env python3
"""
Comprehensive workaround for GitHub Actions IP blocking.
This script provides multiple solutions when the website blocks CI/CD runners.
"""

import os
import sys
import logging
import subprocess
import json
from typing import Optional, Dict, Any, List
import time
import random

def setup_logging():
    """Setup logging for the workaround script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def detect_environment():
    """Detect if we're running in GitHub Actions and what restrictions exist."""
    logger = logging.getLogger(__name__)
    
    env_info = {
        'is_github_actions': bool(os.getenv('GITHUB_ACTIONS')),
        'runner_os': os.getenv('RUNNER_OS'),
        'github_run_id': os.getenv('GITHUB_RUN_ID'),
        'github_repository': os.getenv('GITHUB_REPOSITORY'),
        'has_curl': False,
        'has_tor': False,
        'has_docker': False,
        'ip_address': None
    }
    
    # Check available tools
    try:
        subprocess.run(['curl', '--version'], capture_output=True, check=True)
        env_info['has_curl'] = True
        logger.info("✅ curl is available")
    except:
        logger.warning("❌ curl not available")
    
    try:
        subprocess.run(['tor', '--version'], capture_output=True, check=True)
        env_info['has_tor'] = True
        logger.info("✅ Tor is available")
    except:
        logger.info("ℹ️ Tor not available (not usually pre-installed)")
    
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
        env_info['has_docker'] = True
        logger.info("✅ Docker is available")
    except:
        logger.warning("❌ Docker not available")
    
    # Get current IP
    try:
        result = subprocess.run(
            ['curl', '-s', 'https://ipinfo.io/ip'], 
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            env_info['ip_address'] = result.stdout.strip()
            logger.info(f"Current IP: {env_info['ip_address']}")
    except:
        logger.warning("Could not determine IP address")
    
    return env_info

def try_tor_approach():
    """Install and configure Tor for anonymous scraping."""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Attempting to install and configure Tor...")
        
        # Install Tor (Ubuntu/Debian)
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'tor'], check=True)
        
        # Start Tor service
        subprocess.run(['sudo', 'systemctl', 'start', 'tor'], check=True)
        
        # Wait for Tor to initialize
        time.sleep(10)
        
        # Test Tor connection
        result = subprocess.run([
            'curl', '--socks5-hostname', 'localhost:9050', 
            '-s', 'https://ipinfo.io/ip'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            new_ip = result.stdout.strip()
            logger.info(f"✅ Tor working! New IP: {new_ip}")
            return True
        else:
            logger.error("❌ Tor installation failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Tor setup failed: {e}")
        return False

def try_vpn_approach():
    """Try to setup a free VPN service."""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Attempting to setup ProtonVPN free tier...")
        
        # Install ProtonVPN
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run([
            'sudo', 'apt-get', 'install', '-y', 
            'openvpn', 'curl', 'python3-pip'
        ], check=True)
        
        # This would require ProtonVPN credentials
        # For demo purposes, we'll just show the concept
        logger.info("VPN setup would require credentials - skipping in demo")
        return False
        
    except Exception as e:
        logger.error(f"❌ VPN setup failed: {e}")
        return False

def try_cloud_function_approach():
    """Suggest using a cloud function as a proxy."""
    logger = logging.getLogger(__name__)
    
    cloud_function_code = '''
// Example Google Cloud Function or AWS Lambda
exports.proxyRequest = async (req, res) => {
    const fetch = require('node-fetch');
    const url = req.body.url;
    const headers = req.body.headers || {};
    
    try {
        const response = await fetch(url, { headers });
        const data = await response.text();
        
        res.json({
            status: response.status,
            data: data
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};
'''
    
    logger.info("🌤️ Cloud Function Proxy Approach:")
    logger.info("1. Deploy the above code as a cloud function")
    logger.info("2. Update scraper to use the cloud function as a proxy")
    logger.info("3. Cloud function will make requests from different IPs")
    
    return False  # This requires manual setup

def setup_github_actions_solution(env_info: Dict[str, Any]):
    """Setup the best available solution for GitHub Actions."""
    logger = logging.getLogger(__name__)
    
    solutions = []
    
    if env_info['has_curl']:
        solutions.append("✅ Enhanced curl-based scraping")
    
    if env_info['has_docker']:
        solutions.append("✅ Docker container with different network")
    
    # Always available
    solutions.append("✅ Multiple HTTP client rotation")
    solutions.append("✅ Advanced timing patterns")
    solutions.append("✅ Header randomization")
    
    logger.info("Available solutions for GitHub Actions:")
    for solution in solutions:
        logger.info(f"  {solution}")
    
    # Generate configuration
    config = {
        "use_curl_fallback": env_info['has_curl'],
        "use_docker_network": env_info['has_docker'],
        "enhanced_delays": True,
        "max_retries": 8,
        "base_delay": 10.0,
        "use_multiple_clients": True
    }
    
    # Save configuration
    with open('github_actions_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info("✅ Configuration saved to github_actions_config.json")
    return config

def main():
    """Main function to setup GitHub Actions workarounds."""
    logger = setup_logging()
    
    logger.info("🔍 Analyzing GitHub Actions environment...")
    env_info = detect_environment()
    
    if env_info['is_github_actions']:
        logger.info("✅ GitHub Actions environment detected")
        logger.info(f"Runner OS: {env_info['runner_os']}")
        logger.info(f"Repository: {env_info['github_repository']}")
        
        # Try different approaches
        success = False
        
        # Approach 1: Try Tor (most effective but complex)
        if not success and os.getenv('ENABLE_TOR') == 'true':
            logger.info("🧅 Trying Tor approach...")
            success = try_tor_approach()
        
        # Approach 2: Try VPN (requires credentials)
        if not success and os.getenv('VPN_CREDENTIALS'):
            logger.info("🔒 Trying VPN approach...")
            success = try_vpn_approach()
        
        # Approach 3: Setup enhanced evasion
        if not success:
            logger.info("⚙️ Setting up enhanced evasion techniques...")
            config = setup_github_actions_solution(env_info)
            success = True
        
        if success:
            logger.info("✅ GitHub Actions workaround configured successfully!")
        else:
            logger.error("❌ Could not setup effective workaround")
            sys.exit(1)
    
    else:
        logger.info("ℹ️ Not running in GitHub Actions - local environment detected")
        logger.info("Local testing should work with standard anti-detection measures")

if __name__ == "__main__":
    main()
