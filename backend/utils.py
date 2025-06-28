from typing import List, Tuple
import dateparser
import dateparser.search
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def extract_multiple_datetimes(text: str) -> List[Tuple[datetime, str]]:
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
    return date_obj.weekday() >= 5  # 5=Saturday, 6=Sunday

def format_nice(dt: datetime) -> str:
    return dt.strftime("%A, %b %d at %I:%M %p")
def get_next_weekday(start_date: datetime.date) -> datetime:
    """Get the next weekday (Mon–Fri) from a given date."""
    next_day = start_date + timedelta(days=1)
    while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        next_day += timedelta(days=1)
    return datetime.combine(next_day, datetime.min.time())
