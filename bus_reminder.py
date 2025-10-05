#!/usr/bin/env python3
"""
Bus Reminder Agent with Google Calendar Integration
Checks Bus 48 times and creates Google Calendar reminders directly
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuration from environment variables
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
GOOGLE_CALENDAR_CREDENTIALS = os.getenv('GOOGLE_CALENDAR_CREDENTIALS', '')
GOOGLE_CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
HOME_ADDRESS = os.getenv('HOME_ADDRESS', '110 Saunders Park View, Brighton BN2 4NY, UK')
SCHOOL_ADDRESS = os.getenv('SCHOOL_ADDRESS', 'Bevendean Primary School, Brighton, UK')
PREFERRED_BUS_ROUTE = os.getenv('PREFERRED_BUS_ROUTE', '48')
MIN_DEPARTURE_TIME = os.getenv('MIN_DEPARTURE_TIME', '08:20')
MAX_ARRIVAL_TIME = os.getenv('MAX_ARRIVAL_TIME', '08:45')
REMINDER_MINUTES_BEFORE = int(os.getenv('REMINDER_MINUTES_BEFORE', '12'))

# Timezone
UK_TZ = pytz.timezone('Europe/London')


class BusReminderAgent:
    """Agent to check bus times and create calendar reminders"""
    
    def __init__(self):
        self.api_key = GOOGLE_MAPS_API_KEY
        self.calendar_service = None
        self.calendar_id = GOOGLE_CALENDAR_ID
        
        if not self.api_key:
            print("⚠️  WARNING: GOOGLE_MAPS_API_KEY not set.")
        
        # Initialize Google Calendar API
        if GOOGLE_CALENDAR_CREDENTIALS:
            try:
                credentials_dict = json.loads(GOOGLE_CALENDAR_CREDENTIALS)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=['https://www.googleapis.com/auth/calendar']
                 )
                self.calendar_service = build('calendar', 'v3', credentials=credentials)
                print("✅ Google Calendar API initialized")
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize Google Calendar API: {e}")
        
    def get_transit_directions(self) -> Optional[Dict]:
        """
        Get transit directions from home to school using Google Maps API
        """
        if not self.api_key:
            print("❌ No API key available")
            return None
            
        url = "https://maps.googleapis.com/maps/api/directions/json"
        
        # Get current time in UK timezone
        now = datetime.now(UK_TZ )
        
        params = {
            'origin': HOME_ADDRESS,
            'destination': SCHOOL_ADDRESS,
            'mode': 'transit',
            'transit_mode': 'bus',
            'departure_time': int(now.timestamp()),
            'alternatives': 'true',
            'key': self.api_key
        }
        
        try:
            print(f"🔍 Checking bus times from Google Maps API...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'OK':
                print(f"❌ API Error: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                return None
                
            print(f"✅ Retrieved {len(data.get('routes', []))} route options")
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None
    
    def parse_bus_routes(self, directions_data: Dict) -> List[Dict]:
        """
        Parse directions data and extract bus route information
        """
        bus_options = []
        
        if not directions_data or 'routes' not in directions_data:
            return bus_options
        
        for route in directions_data['routes']:
            for leg in route['legs']:
                for step in leg['steps']:
                    if step.get('travel_mode') == 'TRANSIT':
                        transit_details = step.get('transit_details', {})
                        line = transit_details.get('line', {})
                        
                        # Check if this is our bus route
                        if line.get('short_name') == PREFERRED_BUS_ROUTE:
                            departure = transit_details.get('departure_time', {})
                            arrival = transit_details.get('arrival_time', {})
                            
                            bus_info = {
                                'route': line.get('short_name'),
                                'route_name': line.get('name'),
                                'departure_stop': transit_details.get('departure_stop', {}).get('name'),
                                'arrival_stop': transit_details.get('arrival_stop', {}).get('name'),
                                'departure_time': datetime.fromtimestamp(departure.get('value'), UK_TZ),
                                'arrival_time': datetime.fromtimestamp(arrival.get('value'), UK_TZ),
                                'duration_minutes': step.get('duration', {}).get('value', 0) // 60
                            }
                            
                            bus_options.append(bus_info)
        
        return bus_options
    
    def select_best_bus(self, bus_options: List[Dict]) -> Optional[Dict]:
        """
        Select the best bus based on user preferences
        """
        if not bus_options:
            print("❌ No Bus 48 options found")
            return None
        
        print(f"\n📋 Found {len(bus_options)} Bus 48 option(s):")
        
        # Parse time constraints
        min_hour, min_minute = map(int, MIN_DEPARTURE_TIME.split(':'))
        max_hour, max_minute = map(int, MAX_ARRIVAL_TIME.split(':'))
        
        now = datetime.now(UK_TZ)
        min_departure = now.replace(hour=min_hour, minute=min_minute, second=0, microsecond=0)
        max_arrival = now.replace(hour=max_hour, minute=max_minute, second=0, microsecond=0)
        
        suitable_buses = []
        
        for bus in bus_options:
            dep_time = bus['departure_time']
            arr_time = bus['arrival_time']
            
            print(f"  🚌 Bus {bus['route']}: Departs {dep_time.strftime('%H:%M')} → Arrives {arr_time.strftime('%H:%M')}")
            
            # Check if bus meets criteria
            if dep_time >= min_departure and arr_time <= max_arrival:
                suitable_buses.append(bus)
                print(f"     ✅ Suitable (after {MIN_DEPARTURE_TIME}, arrives by {MAX_ARRIVAL_TIME})")
            else:
                reasons = []
                if dep_time < min_departure:
                    reasons.append(f"too early (before {MIN_DEPARTURE_TIME})")
                if arr_time > max_arrival:
                    reasons.append(f"arrives too late (after {MAX_ARRIVAL_TIME})")
                print(f"     ❌ Not suitable: {', '.join(reasons)}")
        
        if not suitable_buses:
            print("\n⚠️  No suitable buses found matching criteria")
            return None
        
        # Select the earliest suitable bus
        best_bus = min(suitable_buses, key=lambda x: x['departure_time'])
        print(f"\n🎯 Selected bus: Departs at {best_bus['departure_time'].strftime('%H:%M')}")
        
        return best_bus
    
    def calculate_reminder_time(self, bus_departure: datetime) -> Optional[datetime]:
        """
        Calculate when to send the reminder
        """
        reminder_time = bus_departure - timedelta(minutes=REMINDER_MINUTES_BEFORE)
        now = datetime.now(UK_TZ)
        
        if reminder_time < now:
            print(f"⚠️  Reminder time ({reminder_time.strftime('%H:%M')}) is in the past!")
            return now  # Send immediately
        
        return reminder_time
    
    def create_google_calendar_event(self, bus_info: Dict, reminder_time: datetime) -> bool:
        """
        Create a Google Calendar event with reminder
        """
        if not self.calendar_service:
            print("❌ Google Calendar API not initialized")
            return False
        
        print("\n" + "="*60)
        print("📅 CREATING GOOGLE CALENDAR EVENT")
        print("="*60)
        
        event_title = f"🚌 Bus {bus_info['route']} to School"
        event_description = (
            f"Bus {bus_info['route']} to {bus_info.get('route_name', 'Bevendean')}\n"
            f"From: {bus_info['departure_stop']}\n"
            f"Departure: {bus_info['departure_time'].strftime('%H:%M')}\n"
            f"Expected arrival: {bus_info['arrival_time'].strftime('%H:%M')}\n"
            f"Journey time: {bus_info['duration_minutes']} minutes\n\n"
            f"⏰ Leave now to catch the bus!"
        )
        
        # Calculate minutes before for the reminder
        minutes_before = int((bus_info['departure_time'] - reminder_time).total_seconds() / 60)
        
        # Create event
        event = {
            'summary': event_title,
            'description': event_description,
            'start': {
                'dateTime': bus_info['departure_time'].isoformat(),
                'timeZone': 'Europe/London',
            },
            'end': {
                'dateTime': (bus_info['departure_time'] + timedelta(minutes=5)).isoformat(),
                'timeZone': 'Europe/London',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': minutes_before},
                ],
            },
        }
        
        try:
            created_event = self.calendar_service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            print(f"✅ Calendar event created successfully!")
            print(f"Title: {event_title}")
            print(f"Start Time: {bus_info['departure_time'].strftime('%Y-%m-%d %H:%M %Z')}")
            print(f"Reminder: {minutes_before} minutes before ({reminder_time.strftime('%H:%M')})")
            print(f"Event Link: {created_event.get('htmlLink', 'N/A')}")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating calendar event: {e}")
            return False
    
    def send_alert(self, message: str):
        """
        Send an alert notification (for errors or no bus found)
        """
        print("\n" + "="*60)
        print("⚠️  ALERT NOTIFICATION")
        print("="*60)
        print(message)
        print("="*60)
        
        if not self.calendar_service:
            return
        
        # Create an immediate calendar alert
        now = datetime.now(UK_TZ)
        alert_title = "⚠️ Bus Alert"
        
        event = {
            'summary': alert_title,
            'description': message,
            'start': {
                'dateTime': (now + timedelta(minutes=1)).isoformat(),
                'timeZone': 'Europe/London',
            },
            'end': {
                'dateTime': (now + timedelta(minutes=2)).isoformat(),
                'timeZone': 'Europe/London',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 0},
                ],
            },
        }
        
        try:
            self.calendar_service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            print("✅ Alert added to Google Calendar")
        except Exception as e:
            print(f"⚠️  Could not add alert to calendar: {e}")
    
    def run(self):
        """
        Main execution flow
        """
        print("\n" + "🚌"*20)
        print("BUS REMINDER AGENT")
        print(f"Running at: {datetime.now(UK_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print("🚌"*20 + "\n")
        
        # Step 1: Get transit directions
        directions = self.get_transit_directions()
        
        if not directions:
            self.send_alert(
                "❌ Unable to check bus times from Google Maps.\n"
                "Please check the bus schedule manually at:\n"
                "https://www.buses.co.uk/stops/149000007061"
             )
            return False
        
        # Step 2: Parse bus routes
        bus_options = self.parse_bus_routes(directions)
        
        # Step 3: Select best bus
        best_bus = self.select_best_bus(bus_options)
        
        if not best_bus:
            self.send_alert(
                f"⚠️ No suitable Bus {PREFERRED_BUS_ROUTE} found.\n"
                f"Criteria: Departs after {MIN_DEPARTURE_TIME}, arrives by {MAX_ARRIVAL_TIME}\n\n"
                "Please check alternative transport options or an earlier bus."
            )
            return False
        
        # Step 4: Calculate reminder time
        reminder_time = self.calculate_reminder_time(best_bus['departure_time'])
        
        # Step 5: Create Google Calendar event
        success = self.create_google_calendar_event(best_bus, reminder_time)
        
        if success:
            print("\n✅ Bus reminder agent completed successfully!")
            return True
        else:
            print("\n❌ Failed to create calendar reminder")
            return False


def main():
    """Main entry point"""
    agent = BusReminderAgent()
    success = agent.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
