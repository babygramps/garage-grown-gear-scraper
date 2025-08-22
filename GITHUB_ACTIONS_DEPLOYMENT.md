# 🚀 GitHub Actions Deployment Guide
## Garage Grown Gear Scraper

Your repository already has comprehensive GitHub Actions workflows configured! Here's how to deploy and activate them.

## 📋 **Pre-deployment Checklist**

✅ **Local Setup Complete:**
- [x] Scraper working locally
- [x] Google Sheets integration functional
- [x] Data quality excellent (100/100 score)
- [x] Environment variables configured in `.env`

✅ **Repository Ready:**
- [x] GitHub Actions workflows exist (`.github/workflows/`)
- [x] Requirements.txt present
- [x] Main scraper script functional

## 🔧 **Step 1: Set Up GitHub Repository Secrets**

### **Required Secrets:**

1. **Navigate to your GitHub repository**
   - Go to: `Settings` → `Secrets and variables` → `Actions`

2. **Add Required Secrets:**

   **🔑 GOOGLE_SHEETS_CREDENTIALS**
   - Click "New repository secret"
   - Name: `GOOGLE_SHEETS_CREDENTIALS`
   - Value: Your base64-encoded credentials (from your `.env` file)
   - Copy the value after `GOOGLE_SHEETS_CREDENTIALS=` in your `.env`

   **📊 SPREADSHEET_ID**
   - Click "New repository secret"
   - Name: `SPREADSHEET_ID`
   - Value: `16-MpMdDP4vlErFmsi6lBU2DRaKyBMDRGAuNU-DOsT1o`

### **Optional Secrets:**
   
   **🔔 WEBHOOK_URL** (for notifications)
   - Name: `WEBHOOK_URL`
   - Value: Your Slack/Discord webhook URL (if you want notifications)

## 🔧 **Step 2: Update GitHub Actions Configuration**

Your workflows are already well-configured, but let's verify the environment variable mapping:

### **Update Workflow Environment Variables:**

The workflow needs to map GitHub secrets to environment variables. Let me check if this needs updating:

```yaml
# In .github/workflows/scraper.yml, the environment section should include:
env:
  GOOGLE_SHEETS_CREDENTIALS: ${{ secrets.GOOGLE_SHEETS_CREDENTIALS }}
  SPREADSHEET_ID: ${{ secrets.SPREADSHEET_ID }}
  SHEET_NAME: "Garage Grown Gear"  # Match your .env setting
```

## 🔧 **Step 3: Workflow Configuration Updated**

✅ **I've updated the workflow configuration to properly pass environment variables.**

The workflow now correctly maps:
- `GOOGLE_SHEETS_CREDENTIALS` from GitHub secrets
- `SPREADSHEET_ID` from GitHub secrets  
- `SHEET_NAME` set to "Garage Grown Gear" (matching your `.env`)

## 🚀 **Step 4: Deploy to GitHub**

### **Push Changes to GitHub:**

```powershell
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Configure GitHub Actions for automated scraping with quality monitoring"

# Push to main branch
git push origin main
```

## ✅ **Step 5: Verify Deployment**

### **1. Check GitHub Actions Tab:**
- Go to your repository on GitHub
- Click the "Actions" tab
- You should see the workflow listed: "Garage Grown Gear Scraper"

### **2. Test Manual Run:**
- Click on "Garage Grown Gear Scraper" workflow
- Click "Run workflow" button
- Leave defaults (Debug mode: false, Retry count: 3)
- Click "Run workflow"

### **3. Monitor First Run:**
- Watch the workflow progress in real-time
- Check each step for any errors
- Verify data is saved to your Google Sheet

## 📅 **Automated Schedule**

Your scraper will now run automatically:
- **Every 6 hours**: 00:00, 06:00, 12:00, 18:00 UTC
- **Health checks**: Daily at 9:00 AM UTC
- **Manual triggers**: Available anytime via GitHub Actions

## 🔍 **Monitoring & Debugging**

### **View Workflow Results:**
1. GitHub Actions tab shows all runs
2. Click any run to see detailed logs
3. Download artifacts for debugging
4. Check your Google Sheet for new data

### **Quality Reports:**
- Workflows include comprehensive logging
- Artifacts contain quality reports
- Performance metrics tracked
- Error handling with retry logic

### **Troubleshooting:**
- Check "Actions" tab for failed runs
- Download artifacts for detailed logs
- Use manual trigger with debug mode
- Review Google Sheets permissions

## 🔔 **Optional: Set Up Notifications**

### **Slack/Discord Webhooks:**
1. Add `WEBHOOK_URL` to GitHub secrets
2. Update `.env` with: `ENABLE_NOTIFICATIONS=true`
3. Commit and push changes

### **GitHub Notifications:**
- Watch repository for workflow failures
- Configure email notifications in GitHub settings
- Set up mobile notifications via GitHub app

## 📊 **Expected Results**

After deployment, you'll have:
- ✅ **Automated scraping** every 6 hours
- ✅ **Data quality monitoring** (100/100 score)
- ✅ **Error handling and retries** (3 attempts)
- ✅ **Comprehensive logging** and artifacts
- ✅ **Health monitoring** with daily checks
- ✅ **Manual trigger capability** for testing

## 🎯 **Success Metrics**

Monitor these to ensure successful deployment:
1. **Workflow Success Rate**: Should be >95%
2. **Data Quality Score**: Maintain 90+ score
3. **Products Scraped**: ~9-16 products per run
4. **Google Sheets Data**: New rows every 6 hours
5. **No Failed Runs**: Or quick recovery with retries

## 🚨 **Common Issues & Solutions**

### **Authentication Errors:**
- Verify `GOOGLE_SHEETS_CREDENTIALS` secret is correctly base64 encoded
- Check that Google Sheet is shared with service account email
- Confirm `SPREADSHEET_ID` is exactly 44 characters

### **No Data in Sheet:**
- Check workflow logs in GitHub Actions
- Verify sheet name matches: "Garage Grown Gear"
- Ensure service account has Editor permissions

### **Workflow Failures:**
- Review error logs in Actions tab
- Download artifacts for detailed debugging
- Test manually with debug mode enabled
- Check repository secrets are set correctly

## 🎉 **Deployment Complete!**

Once you push the changes and set up the GitHub secrets, your scraper will be fully automated and running on GitHub Actions with:

- 🕕 **Every 6 hours** automated execution
- 📊 **100% data quality** monitoring
- 🔄 **Automatic retries** on failures
- 📈 **Performance tracking** and reporting
- 🛡️ **Error handling** and recovery
- 📱 **Optional notifications** for important events

Your Garage Grown Gear scraper is now enterprise-ready! 🚀

