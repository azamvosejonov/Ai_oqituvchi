import asyncio
from datetime import datetime
import pytz

async def get_location_from_ip(ip: str) -> dict:
    """
    Placeholder function to simulate fetching location data from an IP address.
    In a real application, this would call an external geolocation API.
    """
    # Simulate network delay
    await asyncio.sleep(0.1)

    # Return mock data that matches the LocationInfo schema
    now = datetime.now(pytz.utc)
    return {
        "ip": ip,
        "country": "Mock Country",
        "region": "Mock Region",
        "city": "Mock City",
        "timezone": "UTC",
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "utc_offset": "+00:00",
        "display_time": now.strftime("%I:%M:%S %p"),
        "login_time": now.isoformat(),
    }

def format_user_time_display(location_data: dict) -> str:
    """
    Formats a display string for the user's local time and timezone.
    """
    if not location_data:
        return "Unknown location and time"
    
    city = location_data.get("city", "Unknown City")
    display_time = location_data.get("display_time", "Unknown Time")
    timezone = location_data.get("timezone", "Unknown Timezone")
    
    return f"Your current time in {city} is {display_time} ({timezone})"
