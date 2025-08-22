# Documentation Index

Welcome to the Garage Grown Gear scraper documentation! This directory contains comprehensive guides to help you set up, configure, and use the scraper effectively.

## 📚 Documentation Overview

### 🚀 Getting Started
- **[Main README](../README.md)** - Project overview, quick start, and basic usage
- **[Google Sheets Setup](GOOGLE_SHEETS_SETUP.md)** - Step-by-step guide to set up Google Sheets API credentials
- **[Configuration Reference](CONFIGURATION.md)** - Complete reference for all configuration options

### 🔧 Advanced Topics
- **[Change Detection](CHANGE_DETECTION.md)** - How the scraper detects and tracks product changes
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Solutions for common issues and debugging tips
- **[FAQ](FAQ.md)** - Frequently asked questions and answers

### 🧪 Development
- **[Testing Guide](../tests/README.md)** - How to run and write tests
- **[GitHub Workflow Setup](../.github/WORKFLOW_SETUP.md)** - GitHub Actions configuration details

## 🎯 Quick Navigation

### New Users
1. Start with the [Main README](../README.md) for project overview
2. Follow the [Google Sheets Setup](GOOGLE_SHEETS_SETUP.md) guide
3. Run `python setup_config.py` to validate your setup
4. Check the [FAQ](FAQ.md) for common questions

### Troubleshooting
1. Run `python setup_config.py` for automated diagnostics
2. Check the [Troubleshooting Guide](TROUBLESHOOTING.md) for specific issues
3. Review the [FAQ](FAQ.md) for common problems
4. Enable debug logging: `LOG_LEVEL=DEBUG python main.py`

### Configuration
1. Copy `.env.example` to `.env`
2. Review the [Configuration Reference](CONFIGURATION.md) for all options
3. Use `python setup_config.py` to validate settings
4. See [Google Sheets Setup](GOOGLE_SHEETS_SETUP.md) for credentials

### Advanced Usage
1. Read about [Change Detection](CHANGE_DETECTION.md) features
2. Check the [Testing Guide](../tests/README.md) for development
3. Review [GitHub Workflow Setup](../.github/WORKFLOW_SETUP.md) for automation

## 📖 Document Summaries

### [Google Sheets Setup Guide](GOOGLE_SHEETS_SETUP.md)
Complete walkthrough for setting up Google Sheets API access, including:
- Creating a Google Cloud project
- Enabling APIs and creating service accounts
- Downloading and configuring credentials
- Setting up spreadsheets and permissions
- GitHub Actions integration

### [Configuration Reference](CONFIGURATION.md)
Comprehensive reference covering:
- All environment variables and their purposes
- Validation rules and acceptable values
- Configuration examples for different use cases
- Security best practices
- Troubleshooting configuration issues

### [Change Detection Guide](CHANGE_DETECTION.md)
Detailed explanation of the change detection system:
- How new products are identified
- Price change tracking and thresholds
- Stock status monitoring
- Notification system configuration
- Data analysis and reporting

### [Troubleshooting Guide](TROUBLESHOOTING.md)
Systematic approach to diagnosing and fixing issues:
- Common error messages and solutions
- Step-by-step debugging procedures
- Performance optimization tips
- Network and API troubleshooting
- Log analysis and interpretation

### [FAQ](FAQ.md)
Answers to frequently asked questions about:
- Setup and installation
- Usage and features
- Customization options
- Performance and limits
- Legal and ethical considerations

## 🛠️ Tools and Scripts

### Configuration Validation
```bash
python setup_config.py
```
Automated script that checks your entire setup and provides specific guidance for any issues.

### Debug Mode
```bash
LOG_LEVEL=DEBUG python main.py
```
Run the scraper with detailed logging to diagnose issues.

### Test Suite
```bash
python -m pytest
```
Run the comprehensive test suite to verify functionality.

## 🆘 Getting Help

### Self-Service Resources
1. **Search the documentation** - Use Ctrl+F to search within documents
2. **Run diagnostics** - Use `python setup_config.py` for automated checks
3. **Check logs** - Enable debug logging for detailed information
4. **Review examples** - Check the `examples/` directory for usage patterns

### Community Support
1. **GitHub Issues** - Report bugs or request features
2. **GitHub Discussions** - Ask questions and share experiences
3. **Documentation Updates** - Suggest improvements to guides

### Before Asking for Help
- ✅ Run `python setup_config.py`
- ✅ Check the relevant documentation section
- ✅ Search existing GitHub issues
- ✅ Try debug logging: `LOG_LEVEL=DEBUG python main.py`
- ✅ Gather error messages and system information

## 📝 Contributing to Documentation

We welcome improvements to the documentation! To contribute:

1. **Fork the repository**
2. **Edit the relevant markdown files**
3. **Test your changes** (check links, formatting, accuracy)
4. **Submit a pull request** with a clear description

### Documentation Standards
- Use clear, concise language
- Include practical examples
- Provide step-by-step instructions
- Add troubleshooting tips
- Keep information up to date

### File Organization
```
docs/
├── README.md                 # This index file
├── GOOGLE_SHEETS_SETUP.md   # Setup guide
├── CONFIGURATION.md         # Config reference
├── CHANGE_DETECTION.md      # Feature guide
├── TROUBLESHOOTING.md       # Problem solving
└── FAQ.md                   # Common questions
```

## 🔄 Keeping Documentation Updated

The documentation is updated with each release. To stay current:

1. **Watch the repository** for updates
2. **Check release notes** for documentation changes
3. **Review updated guides** when upgrading
4. **Contribute improvements** based on your experience

---

**Need immediate help?** Start with `python setup_config.py` and the [Troubleshooting Guide](TROUBLESHOOTING.md)!