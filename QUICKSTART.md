# Quick Start Guide - Bus Reminder Agent

Get your bus reminder agent running in 10 minutes!

## Prerequisites

- A GitHub account (free)
- A Google account (free)

## Step-by-Step Setup

### 1. Get Google Maps API Key (5 minutes)

1. Visit: https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name it "Bus Reminder" → Click "Create"
4. Wait for project creation, then select it
5. Click "Enable APIs and Services"
6. Search for "Directions API" → Click it → Click "Enable"
7. Go to "Credentials" (left sidebar)
8. Click "Create Credentials" → "API Key"
9. **Copy your API key** (you'll need this!)
10. (Optional) Click "Restrict Key" → Select "Directions API" → Save

### 2. Set Up GitHub Repository (3 minutes)

1. Go to this repository on GitHub
2. Click the **"Fork"** button (top right)
3. In your forked repository, click **"Settings"**
4. Go to **"Secrets and variables"** → **"Actions"**
5. Click **"New repository secret"**
6. Name: `GOOGLE_MAPS_API_KEY`
7. Value: Paste your API key from step 1
8. Click **"Add secret"**

### 3. Enable and Test (2 minutes)

1. Go to the **"Actions"** tab
2. Click "I understand my workflows, go ahead and enable them"
3. Click "Bus Reminder Agent" (left sidebar)
4. Click **"Run workflow"** → **"Run workflow"** (green button)
5. Wait 30 seconds, then refresh the page
6. Click on the workflow run to see the results
7. Download the **"bus-reminder-calendar"** artifact
8. Extract the .ics file and open it on your iPhone

### 4. Set Up Daily Delivery (Optional)

The agent now runs automatically every weekday at 7:50 AM UK time!

To receive the calendar file automatically:

**Option A: Check GitHub Actions daily**
- Go to Actions tab each morning
- Download the artifact
- Import to your calendar

**Option B: Set up email notifications**
- Follow the advanced setup in README.md
- Requires email service configuration

## What Happens Next?

- **Every weekday at 7:50 AM**, the agent checks Bus 48 times
- It creates a calendar reminder for the best bus (after 8:20 AM, arrives by 8:45 AM)
- You'll get a notification **12 minutes before** the bus departs
- If no suitable bus is found, you'll get an alert

## Testing Right Now

Want to see it work immediately?

```bash
# On your computer (requires Python 3)
git clone https://github.com/YOUR-USERNAME/bus-reminder-agent
cd bus-reminder-agent
pip install -r requirements.txt
export GOOGLE_MAPS_API_KEY="your_key_here"
python bus_reminder.py
```

You'll see output like:

```
🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌
BUS REMINDER AGENT
Running at: 2025-10-05 07:50:00 BST
🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌🚌

🔍 Checking bus times from Google Maps API...
✅ Retrieved 3 route options

📋 Found 2 Bus 48 option(s):
  🚌 Bus 48: Departs 08:25 → Arrives 08:42
     ✅ Suitable (after 08:20, arrives by 08:45)
  🚌 Bus 48: Departs 08:40 → Arrives 08:57
     ❌ Not suitable: arrives too late (after 08:45)

🎯 Selected bus: Departs at 08:25

============================================================
📅 CALENDAR REMINDER TO CREATE
============================================================
Title: 🚌 Bus 48 to School
Start Time: 2025-10-05 08:25 BST
Reminder: 2025-10-05 08:13 BST
Description:
Bus 48 to Bevendean
From: Mithras House
Departure: 08:25
Expected arrival: 08:42
Journey time: 17 minutes

⏰ Leave now to catch the bus!
============================================================

✅ Calendar file created: bus_reminder_20251005_0825.ics
📧 You can email this file to yourself or import it directly to your calendar

✅ Bus reminder agent completed successfully!
```

## Troubleshooting

**"No API key available"**
→ Make sure you added the API key to GitHub Secrets correctly

**"No suitable Bus 48 found"**
→ Check if Bus 48 actually runs at your preferred times
→ Try adjusting MIN_DEPARTURE_TIME or MAX_ARRIVAL_TIME in the workflow file

**Workflow doesn't run automatically**
→ GitHub Actions may have a 5-10 minute delay
→ Check that Actions is enabled in your repository settings

## Need Help?

1. Check the full README.md for detailed documentation
2. Look at the workflow logs in GitHub Actions
3. Test locally using the command above

## Customization

Edit `.github/workflows/bus-reminder.yml` to change:
- Schedule time (cron expression)
- Home/school addresses
- Bus route number
- Time preferences
- Reminder timing

That's it! You're all set up! 🎉
