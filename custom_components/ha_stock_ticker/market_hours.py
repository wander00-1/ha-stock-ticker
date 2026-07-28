"""ASX trading-hours logic.

Kept free of Home Assistant imports so it can be unit-tested without a full
HA install.
"""

from __future__ import annotations

from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

ASX_TIMEZONE = ZoneInfo("Australia/Sydney")
ASX_MARKET_OPEN = time(10, 0)
ASX_MARKET_CLOSE = time(16, 0)


def is_asx_market_open(now: datetime | None = None) -> bool:
    """Return whether the ASX is within its Mon-Fri 10:00-16:00 session.

    Doesn't account for public holidays.
    """
    local = (now or datetime.now(timezone.utc)).astimezone(ASX_TIMEZONE)
    if local.weekday() >= 5:
        return False
    return ASX_MARKET_OPEN <= local.time() < ASX_MARKET_CLOSE
