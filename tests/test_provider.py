"""Provider failures use mocked transport only; no requests leave the tests."""
import hashlib
import io
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch
from trendtrade101.provider import capture


class ProviderTests(unittest.TestCase):
    def test_http_429_reports_original_response_without_parsing_or_retry(self):
        body=b"Edge: Too Many Requests"
        error=urllib.error.HTTPError("https://query1.finance.yahoo.com",429,"Too Many Requests",
                                     {"Server":"envoy"},io.BytesIO(body))
        with tempfile.TemporaryDirectory() as d,patch("trendtrade101.provider.urllib.request.urlopen",side_effect=error) as send,patch("trendtrade101.provider.json.loads") as parse:
            result=capture("NVDA","5m",Path(d)/"capture",query={"range":"60d"})
            self.assertEqual(result["http_status"],429)
            self.assertEqual(result["failure_stage"],"http_response_before_json")
            self.assertEqual(result["server"],"envoy")
            self.assertIsNone(result["retry_after"])
            self.assertEqual(result["response_preview"],body.decode())
            self.assertEqual(result["response_preview_sha256"],hashlib.sha256(body).hexdigest())
            self.assertEqual(result["limiting_layer"],"unknown")
            self.assertEqual(result["retry_policy"],"stop_no_automatic_retry")
            send.assert_called_once();parse.assert_not_called()
            self.assertFalse((Path(d)/"capture").exists())

    def test_connect_denial_is_distinct_from_http_response(self):
        error=urllib.error.URLError("Tunnel connection failed: 403 Forbidden")
        with tempfile.TemporaryDirectory() as d,patch("trendtrade101.provider.urllib.request.urlopen",side_effect=error) as send:
            result=capture("NVDA","5m",Path(d),query={"range":"60d"})
            self.assertEqual(result["failure_stage"],"connection_before_response")
            self.assertNotIn("http_status",result)
            self.assertIn("Tunnel connection failed",result["error"])
            send.assert_called_once()

    def test_retry_after_is_reported_without_scheduling_another_attempt(self):
        error=urllib.error.HTTPError("https://query1.finance.yahoo.com",503,"Unavailable",
                                     {"Retry-After":"120"},io.BytesIO(b"x"*10000))
        with tempfile.TemporaryDirectory() as d,patch("trendtrade101.provider.urllib.request.urlopen",side_effect=error) as send:
            result=capture("NVDA","5m",Path(d),query={"range":"60d"})
            self.assertEqual(result["retry_after"],"120")
            self.assertEqual(result["response_preview_bytes"],4096)
            self.assertLessEqual(len(result["response_preview"]),200)
            send.assert_called_once()
