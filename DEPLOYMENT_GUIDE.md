# Deployment Guide - Bus Reminder Agent

This guide will help you deploy your bus reminder agent to GitHub Actions so it runs automatically every weekday morning.

## Overview

The agent will:
- Run automatically at **7:50 AM UK time** every weekday (Monday-Friday)
- Check Bus 48 times from your home to Bevendean Primary School
- Create a calendar reminder 12 minutes before the best bus departs
- Upload the calendar file as a downloadable artifact

## Prerequisites

✅ GitHub account (free)  
✅ Google account (free)  
✅ 15 minutes of your time

## Part 1: Google Maps API Setup

### Why do we need this?
Google Maps provides real-time bus arrival predictions, which is more accurate than static timetables.

### Steps:

1. **Create a Google Cloud Project**
   - Go to: https://console.cloud.google.com/
   - Click "Select a project" dropdown → "New Project"
   - Project name: `Bus Reminder Agent`
   - Click "Create" and wait for it to finish

2. **Enable Directions API**
   - Make sure your new project is selected
   - Click "☰" menu → "APIs & Services" → "Library"
   - Search for: `Directions API`
   - Click on it → Click "Enable"
   - Wait for it to enable (takes a few seconds)

3. **Create API Key**
   - Click "☰" menu → "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - A popup will show your API key → **Copy it immediately**
   - Save it somewhere safe (you'll need it in the next part)

4. **Secure Your API Key (Recommended)**
   - Click on your API key name
   - Under "API restrictions":
     - Select "Restrict key"
     - Check only "Directions API"
   - Under "Application restrictions":
     - Select "None" (GitHub Actions needs unrestricted access)
   - Click "Save"

### Cost Check
- **Free tier**: $200 credit per month (~40,000 requests)
- **Your usage**: ~20 requests per month (one per weekday)
- **Your cost**: $0 ✅

## Part 2: GitHub Repository Setup

### 1. Fork the Repository

- Go to the repository on GitHub
- Click the **"Fork"** button (top right corner)
- This creates your own copy where you can store your API key securely

### 2. Add Your API Key as a Secret

**Why secrets?** GitHub Secrets are encrypted and never exposed in logs or code.

Steps:
1. In your forked repository, click **"Settings"** (top menu)
2. In the left sidebar, click **"Secrets and variables"** → **"Actions"**
3. Click the green **"New repository secret"** button
4. Fill in:
   - **Name**: `GOOGLE_MAPS_API_KEY` (must be exactly this)
   - **Secret**: Paste your API key from Part 1
5. Click **"Add secret"**

### 3. Verify the Workflow File

The workflow file `.github/workflows/bus-reminder.yml` should already be configured with:

```yaml
schedule:
  - cron: '50 6 * * 1-5'  # 7:50 AM UK time, Monday-Friday
```

**Time Zone Note:**
- `6:50 UTC` = `7:50 AM BST` (British Summer Time, March-October)
- `6:50 UTC` = `6:50 AM GMT` (Greenwich Mean Time, November-February)

If you want it to run at 7:50 AM year-round, you may need to adjust the cron schedule seasonally.

### 4. Enable GitHub Actions

1. Click the **"Actions"** tab in your repository
2. If you see a message about workflows, click **"I understand my workflows, go ahead and enable them"**
3. You should now see "Bus Reminder Agent" in the left sidebar

## Part 3: Test the Agent

### Manual Test Run

1. Go to **Actions** tab
2. Click **"Bus Reminder Agent"** in the left sidebar
3. Click the **"Run workflow"** dropdown (right side)
4. Click the green **"Run workflow"** button
5. Refresh the page after a few seconds
6. Click on the workflow run that just started

### What to Expect

The workflow will:
1. Set up Python environment (~30 seconds)
2. Install dependencies (~10 seconds)
3. Run the bus reminder script (~5 seconds)
4. Upload the calendar file as an artifact

### Check the Results

1. Click on the workflow run
2. Scroll down to "Artifacts" section
3. Download **"bus-reminder-calendar"**
4. Extract the ZIP file
5. You'll find a `.ics` file inside

### Import to Your iPhone

**Method 1: Email**
1. Email the .ics file to yourself
2. Open the email on your iPhone
3. Tap the .ics file attachment
4. Tap "Add to Calendar"
5. Done! The reminder will appear at the specified time

**Method 2: AirDrop**
1. AirDrop the .ics file to your iPhone
2. Open it
3. Tap "Add to Calendar"

**Method 3: iCloud**
1. Upload the .ics file to iCloud Drive
2. Open it on your iPhone
3. Tap "Add to Calendar"

## Part 4: Automatic Daily Operation

### How It Works

Once deployed:
- **Every weekday at 7:50 AM UK time**, GitHub Actions automatically runs the agent
- The agent checks Bus 48 times
- It creates a calendar reminder
- The calendar file is available in the Actions artifacts

### Receiving Daily Reminders

**Current Setup (Manual):**
- Check GitHub Actions each morning
- Download the artifact
- Import to calendar

**Automated Setup (Optional):**

To receive the calendar file automatically via email, you can add email functionality:

1. **Using Gmail SMTP:**

Add these secrets to your repository:
- `EMAIL_USERNAME`: Your Gmail address
- `EMAIL_PASSWORD`: Gmail app password (not your regular password)
- `EMAIL_TO`: Email address to receive reminders

Then add this step to the workflow:

```yaml
- name: Send email with calendar
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "🚌 Bus 48 Reminder for Today"
    to: ${{ secrets.EMAIL_TO }}
    from: Bus Reminder Agent
    body: "Your bus reminder for today is attached. Open the .ics file on your iPhone to add it to your calendar."
    attachments: '*.ics'
```

2. **Using SendGrid (More Reliable):**

- Sign up for free SendGrid account (100 emails/day free)
- Get an API key
- Add `SENDGRID_API_KEY` secret to GitHub
- Use `sendgrid/sendgrid-action` in the workflow

## Part 5: Customization

### Change Schedule Time

Edit `.github/workflows/bus-reminder.yml`:

```yaml
schedule:
  - cron: '30 6 * * 1-5'  # 7:30 AM UK time
```

Cron format: `minute hour day month day-of-week`
- `30 6 * * 1-5` = 6:30 AM UTC, Monday-Friday
- `0 7 * * 1-5` = 7:00 AM UTC, Monday-Friday

### Change Bus Preferences

Edit the environment variables in the workflow file:

```yaml
env:
  MIN_DEPARTURE_TIME: "08:15"  # Earlier bus
  MAX_ARRIVAL_TIME: "08:50"     # Later arrival
  REMINDER_MINUTES_BEFORE: "15" # More notice
```

### Change Addresses

```yaml
env:
  HOME_ADDRESS: "Your new address, Brighton, UK"
  SCHOOL_ADDRESS: "Different school, Brighton, UK"
```

### Support Different Bus Route

```yaml
env:
  PREFERRED_BUS_ROUTE: "25"  # Different route number
```

## Part 6: Monitoring & Maintenance

### Check If It's Working

1. Go to **Actions** tab
2. Look for green checkmarks ✅ next to recent runs
3. Red X ❌ means something failed - click it to see logs

### Common Issues

**Issue: Workflow doesn't run automatically**
- Solution: GitHub Actions can have 5-10 minute delays
- Check: Settings → Actions → ensure Actions is enabled

**Issue: "No suitable bus found"**
- Solution: Check if Bus 48 actually runs at your preferred times
- Try: Adjust MIN_DEPARTURE_TIME or MAX_ARRIVAL_TIME

**Issue: API errors**
- Solution: Check your API key is correct
- Check: Directions API is enabled in Google Cloud
- Check: You haven't exceeded free tier (very unlikely)

**Issue: Calendar file doesn't import**
- Solution: Make sure you're opening it on your iPhone, not computer
- Try: Email it to yourself instead of AirDrop

### View Logs

1. Click on a workflow run
2. Click "Run bus reminder agent"
3. Expand the steps to see detailed logs
4. Look for:
   - ✅ "Retrieved X route options"
   - 🚌 "Bus 48: Departs XX:XX"
   - 🎯 "Selected bus: Departs at XX:XX"

## Part 7: School Holidays

During school holidays, you'll want to disable the agent:

### Option 1: Disable Workflow
1. Go to **Actions** tab
2. Click "Bus Reminder Agent"
3. Click "..." menu → **"Disable workflow"**
4. Re-enable when school starts again

### Option 2: Pause Temporarily
- Just ignore the notifications during holidays
- The agent will still run but you don't have to use the reminders

### Option 3: Automatic Holiday Detection (Advanced)
- Integrate with UK school holiday calendar API
- Requires modifying the Python script
- See README.md for future enhancements

## Part 8: Backup & Recovery

### Backup Your Configuration

Your entire setup is in your GitHub repository, which is automatically backed up.

To create a local backup:
```bash
git clone https://github.com/YOUR-USERNAME/bus-reminder-agent
```

### Restore If Something Breaks

1. Go to your repository
2. Click on `.github/workflows/bus-reminder.yml`
3. Click "History" to see previous versions
4. Revert to a working version if needed

## Part 9: Cost Monitoring

### Google Maps API

Monitor your usage:
1. Go to Google Cloud Console
2. Click "☰" → "APIs & Services" → "Dashboard"
3. Click "Directions API"
4. View usage graphs

**Alert Setup:**
1. Go to "Billing" → "Budgets & alerts"
2. Create budget: $1
3. Set alert at 50% and 100%
4. You'll be notified if costs occur (they shouldn't!)

### GitHub Actions

Monitor your usage:
1. Go to your repository → "Settings"
2. Click "Billing and plans"
3. View Actions minutes used

**Your usage:** ~5 minutes/month (well within 2,000 free minutes)

## Success Checklist

Before considering deployment complete:

- [ ] Google Maps API key created and working
- [ ] API key added to GitHub Secrets
- [ ] Test workflow run completed successfully
- [ ] Calendar file downloaded and tested
- [ ] Calendar reminder imported to iPhone successfully
- [ ] Notification appeared at correct time
- [ ] Automatic schedule enabled (7:50 AM weekdays)
- [ ] Monitoring set up (optional but recommended)

## Getting Help

If something doesn't work:

1. **Check the workflow logs** - Most issues are visible here
2. **Verify your API key** - Try it in a direct API call
3. **Test locally** - Run the Python script on your computer
4. **Check GitHub Actions status** - Sometimes GitHub has outages

## Next Steps

Once everything is working:

1. **Week 1:** Monitor daily to ensure it's working
2. **Week 2:** Start relying on it for your morning routine
3. **Month 1:** Consider setting up automatic email delivery
4. **Future:** Explore enhancements like SMS notifications or web dashboard

## Congratulations! 🎉

Your bus reminder agent is now deployed and will help you never miss the school bus again!
