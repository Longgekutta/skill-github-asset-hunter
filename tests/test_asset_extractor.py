#!/usr/bin/env python3
"""
Unit tests for skill-github-asset-hunter scripts/asset_extractor.py
"""
import unittest
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

from asset_extractor import categorize_asset, extract_direct_assets

class TestAssetExtractor(unittest.TestCase):

    def test_categorize_apk(self):
        res1 = categorize_asset("ConnectBot-v1.10.9-oss-arm64-v8a.apk")
        self.assertEqual(res1["os"], "Android")
        self.assertEqual(res1["arch"], "ARM64")
        self.assertTrue(res1["is_installer"])
        self.assertFalse(res1["is_debug"])

        res2 = categorize_asset("app-armeabi-v7a-release.apk")
        self.assertEqual(res2["os"], "Android")
        self.assertEqual(res2["arch"], "ARMv7")
        self.assertTrue(res2["is_installer"])

    def test_categorize_windows(self):
        res1 = categorize_asset("ToolSetup-x64.exe")
        self.assertEqual(res1["os"], "Windows")
        self.assertEqual(res1["arch"], "x86_64")
        self.assertTrue(res1["is_installer"])

        res2 = categorize_asset("installer-win-x86.msi")
        self.assertEqual(res2["os"], "Windows")
        self.assertEqual(res2["arch"], "x86 (32-bit)")
        self.assertTrue(res2["is_installer"])

    def test_categorize_macos(self):
        res1 = categorize_asset("Client-arm64.dmg")
        self.assertEqual(res1["os"], "macOS")
        self.assertEqual(res1["arch"], "ARM64")
        self.assertTrue(res1["is_installer"])

        res2 = categorize_asset("Client-darwin-universal.pkg")
        self.assertEqual(res2["os"], "macOS")
        self.assertEqual(res2["arch"], "Universal / Any")
        self.assertTrue(res2["is_installer"])

    def test_categorize_linux(self):
        res1 = categorize_asset("App-x86_64.AppImage")
        self.assertEqual(res1["os"], "Linux")
        self.assertEqual(res1["arch"], "x86_64")
        self.assertTrue(res1["is_installer"])

        res2 = categorize_asset("package_amd64.deb")
        self.assertEqual(res2["os"], "Linux")
        self.assertEqual(res2["arch"], "x86_64")
        self.assertTrue(res2["is_installer"])

    def test_filter_debug_symbols(self):
        res1 = categorize_asset("mapping.txt")
        self.assertTrue(res1["is_debug"])

        res2 = categorize_asset("symbols.zip")
        self.assertTrue(res2["is_debug"])

        res3 = categorize_asset("app-release.apk.sha256")
        self.assertTrue(res3["is_debug"])

    def test_radar_report_parsing_both_formats(self):
        with tempfile.TemporaryDirectory() as tmp:
            # 1. 传统 reports 格式
            p1 = os.path.join(tmp, "r1.json")
            with open(p1, "w", encoding="utf-8") as f:
                json.dump({"reports": [{"repo_name": "org/repo1"}, {"repo_name": "org/repo2"}]}, f)

            with open(p1, "r", encoding="utf-8") as f:
                d1 = json.load(f)
            t1 = [r.get("repo_name") for r in d1.get("reports", [])[:2]]
            self.assertEqual(t1, ["org/repo1", "org/repo2"])

            # 2. 多代饱和 generations 格式
            p2 = os.path.join(tmp, "r2.json")
            with open(p2, "w", encoding="utf-8") as f:
                json.dump({
                    "generations": [
                        {"generation": 1, "top_gems": [{"repo": "org/gem1"}, {"repo": "org/gem2"}]}
                    ]
                }, f)

            with open(p2, "r", encoding="utf-8") as f:
                d2 = json.load(f)
            candidates = []
            if not d2.get("reports") and "generations" in d2:
                for g in d2.get("generations", []):
                    for gem in g.get("top_gems", []):
                        candidates.append({"repo_name": gem.get("repo")})
            t2 = [r.get("repo_name") for r in candidates[:2]]
            self.assertEqual(t2, ["org/gem1", "org/gem2"])

if __name__ == "__main__":
    unittest.main()
