"""Unit tests for market_hours.py.

Loaded by file path rather than as part of the ha_stock_ticker package, so
importing this test doesn't trigger custom_components/ha_stock_ticker/
__init__.py (which pulls in homeassistant.* and isn't installed here).
"""

import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

MODULE_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "ha_stock_ticker" / "market_hours.py"
_spec = importlib.util.spec_from_file_location("market_hours", MODULE_PATH)
market_hours = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(market_hours)

SYDNEY = ZoneInfo("Australia/Sydney")


def sydney(year, month, day, hour, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=SYDNEY)


class TestIsAsxMarketOpen(unittest.TestCase):
    # 2026-07-29 is a Wednesday; 2026-07-31 a Friday; 2026-08-01/02 a weekend.

    def test_open_during_session(self):
        self.assertTrue(market_hours.is_asx_market_open(sydney(2026, 7, 29, 11, 30)))

    def test_closed_before_open(self):
        self.assertFalse(market_hours.is_asx_market_open(sydney(2026, 7, 29, 9, 59)))

    def test_open_at_exact_open_boundary(self):
        self.assertTrue(market_hours.is_asx_market_open(sydney(2026, 7, 29, 10, 0)))

    def test_closed_at_exact_close_boundary(self):
        # Close is exclusive — 16:00 itself counts as closed.
        self.assertFalse(market_hours.is_asx_market_open(sydney(2026, 7, 29, 16, 0)))

    def test_open_just_before_close(self):
        self.assertTrue(market_hours.is_asx_market_open(sydney(2026, 7, 29, 15, 59)))

    def test_closed_after_close(self):
        self.assertFalse(market_hours.is_asx_market_open(sydney(2026, 7, 29, 16, 1)))

    def test_closed_on_saturday(self):
        self.assertFalse(market_hours.is_asx_market_open(sydney(2026, 8, 1, 11, 0)))

    def test_closed_on_sunday(self):
        self.assertFalse(market_hours.is_asx_market_open(sydney(2026, 8, 2, 11, 0)))

    def test_open_on_friday(self):
        self.assertTrue(market_hours.is_asx_market_open(sydney(2026, 7, 31, 11, 0)))

    def test_converts_non_sydney_timezone_before_checking(self):
        # 01:30 UTC == 11:30 AEST (UTC+10) on the same Wednesday.
        utc_time = datetime(2026, 7, 29, 1, 30, tzinfo=timezone.utc)
        self.assertTrue(market_hours.is_asx_market_open(utc_time))

    def test_defaults_to_current_time_when_now_is_omitted(self):
        result = market_hours.is_asx_market_open()
        self.assertIsInstance(result, bool)


class TestShouldPoll(unittest.TestCase):
    def test_always_fetches_when_no_data_yet(self):
        # Even if the market happens to be closed on the very first cycle.
        self.assertTrue(market_hours.should_poll(market_open=False, was_open_last_check=False, has_data=False))

    def test_fetches_while_market_is_open(self):
        self.assertTrue(market_hours.should_poll(market_open=True, was_open_last_check=True, has_data=True))

    def test_fetches_once_more_on_the_open_to_closed_transition(self):
        # This is the fix for the "last updated" timestamp freezing well
        # before the actual close instead of reflecting it.
        self.assertTrue(market_hours.should_poll(market_open=False, was_open_last_check=True, has_data=True))

    def test_skips_once_the_transition_fetch_has_happened(self):
        self.assertFalse(market_hours.should_poll(market_open=False, was_open_last_check=False, has_data=True))


if __name__ == "__main__":
    unittest.main()
