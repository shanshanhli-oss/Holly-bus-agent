# 🚌 Bus Reminder Agent

An intelligent agent that automatically checks Bus 48 times in Brighton and sends calendar reminders to your iPhone 10-15 minutes before the bus arrives.

## Features

- ✅ Checks real-time Bus 48 departure times using Google Maps API
- ✅ Filters buses based on your preferences (departs after 8:20 AM, arrives by 8:45 AM)
- ✅ Creates calendar reminders (.ics files) compatible with iPhone Calendar
- ✅ Runs automatically every weekday morning at 7:50 AM
- ✅ Sends alerts if no suitable bus is found or if the system is down
- ✅ Completely free to run (uses free tiers of Google Maps and GitHub Actions)

## How It Works

1. **Every weekday at 7:50 AM**, GitHub Actions triggers the agent
2. The agent queries **Google Maps Directions API** for transit routes from your home to Bevendean Primary School
3. It filters for **Bus 48** routes that:
   - Depart after 8:20 AM
   - Arrive at school by 8:45 AM
4. Selects the best bus and calculates reminder time (12 minutes before departure)
5. Creates a **calendar event file (.ics)** with a reminder notification
6. You can download and import this file to your iPhone calendar, or set up automatic email delivery

## Setup Instructions

### Step 1: Get a Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **Directions API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Directions API"
   - Click "Enable"
4. Create an API key:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key
5. (Optional) Restrict the API key:
   - Click on your API key
   - Under "API restrictions", select "Restrict key"
   - Choose "Directions API"
   - Save

**Cost:** Google provides $200 free credit per month, which is approximately 40,000 Directions API requests. This agent will use about 20 requests per month, so it's completely free.

### Step 2: Fork This Repository

1. Click the "Fork" button at the top right of this GitHub repository
2. This creates your own copy of the repository

### Step 3: Add Your API Key to GitHub Secrets

1. In your forked repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `GOOGLE_MAPS_API_KEY`
4. Value: Paste your Google Maps API key
5. Click **Add secret**

### Step 4: Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. Click "I understand my workflows, go ahead and enable them"
3. The workflow will now run automatically every weekday at 7:50 AM UK time

### Step 5: Test the Agent

1. Go to **Actions** tab
2. Select "Bus Reminder Agent" workflow
3. Click "Run workflow" → "Run workflow" (manual trigger)
4. Wait for the workflow to complete
5. Download the calendar file from the workflow artifacts
6. Import it to your iPhone calendar to test

## Getting Calendar Reminders on Your iPhone

### Option A: Manual Download (Simple)

1. After each workflow run, go to **Actions** → Select the latest run
2. Download the **bus-reminder-calendar** artifact
3. Extract the .ics file
4. Email it to yourself or use AirDrop to send it to your iPhone
5. Open the file on your iPhone → It will automatically add to Calendar with the reminder

### Option B: Automatic Email Delivery (Advanced)

To automatically receive the calendar file via email, you'll need to add email functionality to the workflow. Here's how:

1. Set up a free email service like SendGrid or use Gmail SMTP
2. Add email credentials to GitHub Secrets
3. Modify the workflow to send the .ics file as an email attachment

**Example using Gmail SMTP** (add to workflow):

```yaml
- name: Send email with calendar
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "🚌 Bus 48 Reminder"
    to: your-email@example.com
    from: Bus Reminder Agent
    attachments: '*.ics'
```

### Option C: Direct Google Calendar Integration (Most Advanced)

For direct integration with Google Calendar API:

1. Enable Google Calendar API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Modify the Python script to use Google Calendar API instead of .ics files
4. This requires additional setup but provides seamless integration

## Configuration

You can customize the agent by editing the environment variables in `.github/workflows/bus-reminder.yml`:

```yaml
env:
  HOME_ADDRESS: "110 Saunders Park View, Brighton BN2 4NY, UK"
  SCHOOL_ADDRESS: "Bevendean Primary School, Brighton, UK"
  PREFERRED_BUS_ROUTE: "48"
  MIN_DEPARTURE_TIME: "08:20"  # Only consider buses after this time
  MAX_ARRIVAL_TIME: "08:45"     # Must arrive by this time
  REMINDER_MINUTES_BEFORE: "12" # Send reminder this many minutes before
```

## Troubleshooting

### The workflow doesn't run automatically

- Check that GitHub Actions is enabled in your repository settings
- Verify the cron schedule is correct (6:50 UTC = 7:50 BST)
- Note: GitHub Actions may have a delay of 5-10 minutes

### No bus found

- The agent will send an alert if no Bus 48 meets your criteria
- Check if your time constraints are too strict
- Verify that Bus 48 actually runs at that time on weekdays

### API errors

- Verify your Google Maps API key is correct
- Check that Directions API is enabled
- Ensure you haven't exceeded the free tier limits

### Calendar file doesn't import

- Make sure the .ics file is not corrupted
- Try opening it in a text editor to verify the format
- Some email clients may block .ics attachments - try a different method

## Manual Testing

You can test the agent locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export GOOGLE_MAPS_API_KEY="your_key_here"

# Run the agent
python bus_reminder.py
```

## File Structure

```
bus-reminder-agent/
├── bus_reminder.py           # Main Python script
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment variables
├── .github/
│   └── workflows/
│       └── bus-reminder.yml # GitHub Actions workflow
└── README.md                # This file
```

## How to Stop the Agent

If you need to temporarily disable the agent (e.g., during school holidays):

1. Go to your repository → **Actions**
2. Select "Bus Reminder Agent" workflow
3. Click the "..." menu → **Disable workflow**

To re-enable, click "Enable workflow"

## Privacy & Security

- Your API key is stored securely in GitHub Secrets (encrypted)
- The agent only accesses public transit data
- No personal data is logged or stored
- All code is open source and can be audited

## Cost Breakdown

| Service | Free Tier | Usage | Monthly Cost |
|---------|-----------|-------|--------------|
| Google Maps Directions API | $200 credit (~40,000 requests) | ~20 requests | **$0** |
| GitHub Actions | 2,000 minutes | ~5 minutes | **$0** |
| **Total** | | | **$0/month** |

## Future Enhancements

Potential improvements you could add:

- [ ] Direct Google Calendar API integration
- [ ] SMS notifications as backup
- [ ] Automatic detection of UK school holidays
- [ ] Support for multiple bus routes
- [ ] Weather-based adjustments
- [ ] Historical data tracking and analytics
- [ ] Web dashboard for configuration

## Support

If you encounter issues:

1. Check the workflow logs in GitHub Actions
2. Verify your API key and configuration
3. Test manually using the instructions above
4. Check that Bus 48 is running at your specified times

## License

MIT License - Feel free to modify and use as needed.

## Credits

Built with ❤️ for getting kids to school on time!
