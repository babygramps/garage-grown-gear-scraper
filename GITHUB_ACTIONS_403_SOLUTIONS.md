# GitHub Actions HTTP 403 Solutions

If you're still getting HTTP 403 errors from GitHub Actions, this document provides comprehensive solutions to bypass IP-based blocking.

## 🔍 Why GitHub Actions Gets Blocked

1. **Known IP Ranges**: GitHub Actions runners use datacenter IPs that websites often blacklist
2. **CI/CD Detection**: Request patterns from automated environments are recognizable
3. **Volume-based Blocking**: Multiple users running similar workflows trigger rate limits
4. **Geographic Restrictions**: Runner locations may be in blocked regions

## 🛠️ Implemented Solutions

### 1. **Enhanced Anti-Detection System** ✅
Our scraper now includes:
- **Request Jitter**: Sophisticated timing variations with fatigue simulation
- **Header Rotation**: Dynamic browser fingerprints across Chrome/Firefox versions
- **Gradual Approach**: Multi-step access (homepage → collections → target)
- **GitHub Actions Detection**: Automatic fallback strategies for CI/CD environments

### 2. **Multiple HTTP Client Rotation** ✅
When standard requests fail, the scraper tries:
- **curl with stealth headers**: System-level HTTP client
- **requests with advanced session management**: Python library with retry logic
- **Playwright browser automation**: Real browser rendering

### 3. **Proxy Support** ✅
The scraper now supports:
- **Free proxy rotation**: Automatically tested working proxies
- **Proxy health checking**: Validates proxies before use
- **Failover logic**: Falls back when proxies fail

## 🚀 Quick Setup

### Option 1: Run Setup Scripts (Automatic)
The GitHub Actions workflow now automatically runs:
```bash
python github_actions_workaround.py  # Configure enhanced settings
python free_proxy_setup.py          # Get working proxies (optional)
```

### Option 2: Manual Configuration
1. **Enable Enhanced Delays**:
   ```json
   {
     "enhanced_delays": true,
     "max_retries": 8,
     "base_delay": 10.0,
     "use_multiple_clients": true
   }
   ```

2. **Add Proxy List** (if available):
   ```
   http://proxy1:port
   http://proxy2:port
   ```

## 🔧 Advanced Solutions

### Solution 1: Use Cloud Function Proxy
Deploy a cloud function that acts as a proxy:

```javascript
// Google Cloud Function / AWS Lambda
exports.proxyRequest = async (req, res) => {
    const fetch = require('node-fetch');
    const response = await fetch(req.body.url, {
        headers: req.body.headers
    });
    res.json({
        status: response.status,
        data: await response.text()
    });
};
```

### Solution 2: Self-Hosted Runner
Use your own runner with a residential IP:
```yaml
runs-on: self-hosted  # Instead of ubuntu-latest
```

### Solution 3: Alternative CI Services
Consider switching to:
- **GitLab CI** (different IP ranges)
- **CircleCI** (different geographic regions)
- **Jenkins** (self-hosted)

## 📊 Configuration Options

### Environment Variables
```bash
# Enable Tor routing (requires setup)
ENABLE_TOR=true

# Use specific proxy
PROXY_URL=http://proxy:port

# Enhanced delays for difficult sites  
ENHANCED_DELAYS=true
MAX_RETRIES=8
BASE_DELAY=10.0
```

### GitHub Secrets (Recommended)
Add these to your repository secrets:
- `PROXY_LIST`: Comma-separated list of proxy URLs
- `CLOUD_FUNCTION_URL`: Your cloud function proxy endpoint
- `VPN_CONFIG`: VPN configuration (if using)

## 🧪 Testing Your Setup

Run locally to test:
```bash
python github_actions_workaround.py  # Check available tools
python free_proxy_setup.py           # Test proxy availability
python main.py --dry-run            # Test scraper without storing data
```

## 🔄 Fallback Strategies

The scraper automatically tries these in order:

1. **Standard Scrapling requests** with enhanced headers
2. **Gradual approach** with longer delays
3. **curl-based requests** with system-level evasion
4. **requests session** with advanced retry logic
5. **Playwright browser** automation
6. **Proxy rotation** (if configured)
7. **Cloud function proxy** (if configured)

## 📈 Success Indicators

Look for these in your GitHub Actions logs:
- ✅ `HTTP 200` responses instead of `HTTP 403`
- ✅ `Enhanced scraper found X products!`
- ✅ `GitHub Actions evasion successful`
- ✅ `Using working proxy: http://...`

## ⚠️ Important Notes

1. **Respect robots.txt**: Always check the website's robots.txt
2. **Rate limiting**: Don't overwhelm the server with requests
3. **Legal compliance**: Ensure scraping complies with terms of service
4. **Proxy reliability**: Free proxies may be unreliable or slow

## 🆘 If Nothing Works

Last resort options:

1. **Contact website owner**: Request API access or clarify scraping policy
2. **Use official APIs**: Check if the website provides official data access
3. **Alternative data sources**: Find other sources for the same information
4. **Schedule differently**: Try different times when detection is less strict

## 📞 Support

If you're still experiencing issues:
1. Check the GitHub Actions logs for specific error messages
2. Test the scraper locally to confirm it works outside GitHub Actions
3. Verify your Google Sheets credentials and permissions
4. Consider the timing - some sites have stricter detection during peak hours

The enhanced anti-detection system should handle most blocking scenarios. If issues persist, the problem may be more sophisticated blocking that requires custom solutions for your specific use case.
