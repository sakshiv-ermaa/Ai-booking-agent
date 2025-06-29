# backend/calendar_service.py
from datetime import datetime, timedelta
import os
from fastapi import HTTPException
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pytz

# Configuration
TIMEZONE = pytz.timezone("Asia/Kolkata")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CREDS_PATH", "credentials.json")
CALENDAR_ID = "da4bbeac9b6f10db027aed50b445f6c0772b50ce191bfa35ff550b7ecdc9b53b@group.calendar.google.com"

# Initialize service
try:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    service = build("calendar", "v3", credentials=creds)
except Exception as e:
    print(f"⚠️ Calendar service initialization failed: {e}")
    service = None

def is_slot_available(dt: datetime) -> bool:
    if not service:
        raise HTTPException(status_code=503, detail="Calendar service unavailable")

    try:
        start = dt.astimezone(TIMEZONE).isoformat()
        end = (dt + timedelta(minutes=30)).astimezone(TIMEZONE).isoformat()

        events = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        return not events.get("items")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar error: {str(e)}")

def book_event(dt: datetime) -> str:
    """Book an event and return a confirmation message with calendar link"""
    if not service:
        raise HTTPException(status_code=503, detail="Calendar service unavailable")

    try:
        event = {
            "summary": "Scheduled Appointment",
            "start": {"dateTime": dt.astimezone(TIMEZONE).isoformat(), "timeZone": str(TIMEZONE)},
            "end": {
                "dateTime": (dt + timedelta(minutes=30)).astimezone(TIMEZONE).isoformat(),
                "timeZone": str(TIMEZONE)
            },
        }

        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        event_link = created_event.get("htmlLink", "")

        return (
            f"✅ Booked for {dt.strftime('%A, %b %d at %I:%M %p')}\n"
            f"🔗 [View in Calendar]({event_link})"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")


def suggest_next_available(dt: datetime) -> datetime:
    dt += timedelta(minutes=30)  # Move forward

    # Keep moving forward until it's a weekday and available
    while is_weekend(dt.date()) or not is_slot_available(dt):
        dt += timedelta(minutes=30)

    return dt


# Updated utils.py for better parsing
import dateparser
from datetime import datetime
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

def extract_datetime_parts(text: str) -> dict:
    settings = {
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.now(),
        'RETURN_AS_TIMEZONE_AWARE': True,
        'PREFER_DAY_OF_MONTH': 'first'
    }

    try:
        parsed = dateparser.parse(text, settings=settings)
        result = {"date": None, "time": None}

        if parsed:
            if parsed.date() >= datetime.now().date():
                result["date"] = parsed.date()
                result["time"] = parsed.time()
                logger.info(f"Parsed '{text}' as {result}")
            else:
                logger.warning(f"Past date detected in '{text}'")

        return result
    except Exception as e:
        logger.error(f"Date parsing failed for '{text}': {e}")
        return {"date": None, "time": None}

def extract_multiple_datetimes(text: str) -> List[Tuple[datetime, str]]:
    # Extract multiple potential date/times
    results = []
    settings = {
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.now(),
        'RETURN_AS_TIMEZONE_AWARE': True,
    }
    try:
        matches = dateparser.search.search_dates(text, settings=settings)
        if matches:
            for phrase, dt in matches:
                if dt.date() >= datetime.now().date():
                    results.append((dt, phrase))
    except Exception as e:
        logger.warning(f"Multi-date parse error: {e}")
    return results

def is_weekend(date_obj) -> bool:
    return date_obj.weekday() >= 5

def format_nice(dt: datetime) -> str:
    return dt.strftime("%A, %b %d at %I:%M %p")

