"""Offline provider and rendering QA. No HeyGen credits or external calls."""
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import importlib.util

MODULE=Path(__file__).resolve().parents[1]/"production.py"
spec=importlib.util.spec_from_file_location("mathmagic_production",MODULE)
production=importlib.util.module_from_spec(spec)
spec.loader.exec_module(production)


class FakeResponse:
    def __init__(self, content):
        self.content=io.BytesIO(content)
    def read(self,n=-1):
        return self.content.read(n)
    def __enter__(self):
        return self
    def __exit__(self,*args):
        pass


class ProductionTests(unittest.TestCase):
    def test_paid_generation_requires_both_flags(self):
        with patch.dict(os.environ,{"HEYGEN_API_KEY":"mock"}):
            with self.assertRaises(PermissionError):
                production.submit_transparent_video("Hello","pose","voice",approved=False,allow_paid=True)
            with self.assertRaises(PermissionError):
                production.submit_transparent_video("Hello","pose","voice",approved=True,allow_paid=False)

    def test_paid_generation_requires_secret(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(PermissionError):
                production.submit_transparent_video("Hello","pose","voice",approved=True,allow_paid=True)

    def test_status_request_mock(self):
        def opener(req,timeout=30):
            self.assertEqual(req.full_url,"https://api.heygen.com/v1/video_status.get?video_id=abc123")
            return FakeResponse(b'{"data":{"status":"completed","video_url":"https://resource2.heygen.ai/a.webm"}}')
        self.assertEqual(production.get_video_status("abc123",opener=opener)["status"],"completed")

    def test_submit_payload_mock_no_real_api(self):
        def opener(req,timeout=30):
            self.assertEqual(req.full_url,"https://api.heygen.com/v1/video.webm")
            payload=json.loads(req.data)
            self.assertEqual(payload["avatar_pose_id"],"pose")
            self.assertEqual(payload["voice_id"],"voice")
            return FakeResponse(b'{"data":{"video_id":"mock123"}}')
        with patch.dict(os.environ,{"HEYGEN_API_KEY":"mock"}):
            self.assertEqual(production.submit_transparent_video("Hi","pose","voice",
                approved=True,allow_paid=True,opener=opener),"mock123")

    def test_reject_untrusted_downloads(self):
        with tempfile.TemporaryDirectory() as folder:
            for url in ("http://resource2.heygen.ai/a.webm","https://127.0.0.1/a.webm",
                        "https://evil.example.org/a.webm"):
                with self.assertRaises(ValueError):
                    production.download_video(url,Path(folder)/"bad.webm")

    def test_mock_download(self):
        with tempfile.TemporaryDirectory() as folder:
            path=production.download_video("https://resource2.heygen.ai/a.webm",
                Path(folder)/"test.webm",opener=lambda url,timeout=120:FakeResponse(b"x"*2048))
            self.assertEqual(path.stat().st_size,2048)

    def test_invalid_status_id(self):
        with self.assertRaises(ValueError):
            production.get_video_status("../../etc/passwd")


if __name__=="__main__":
    unittest.main()
