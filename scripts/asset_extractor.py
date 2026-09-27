#!/usr/bin/env python3
"""
asset_extractor.py - High-precision GitHub Release Asset Extractor & Direct URL Generator
Used by skill-github-asset-hunter to parse GitHub Releases, filter ABI architectures, and extract direct download links.
"""
import sys
import os
import json
import re
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional

TOKEN = os.environ.get("GITHUB_TOKEN", "")

def get_headers():
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "skill-github-asset-hunter/1.0.0"
    }
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    return headers

def fetch_repo_info(repo: str) -> Optional[Dict[str, Any]]:
    url = f"https://api.github.com/repos/{repo.strip('/')}"
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return None

def fetch_latest_release(repo: str) -> Optional[Dict[str, Any]]:
    url = f"https://api.github.com/repos/{repo.strip('/')}/releases/latest"
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        # Fallback to list
        try:
            list_url = f"https://api.github.com/repos/{repo.strip('/')}/releases?per_page=1"
            list_req = urllib.request.Request(list_url, headers=get_headers())
            with urllib.request.urlopen(list_req, timeout=10) as lresp:
                data = json.loads(lresp.read().decode('utf-8'))
                if data and isinstance(data, list):
                    return data[0]
        except Exception:
            pass
    return None

def categorize_asset(name: str) -> Dict[str, str]:
    nl = name.lower()
    
    # OS
    os_type = "UNKNOWN"
    if nl.endswith(".apk") or "android" in nl:
        os_type = "Android"
    elif nl.endswith((".exe", ".msi")) or "win" in nl or "windows" in nl:
        os_type = "Windows"
    elif nl.endswith((".dmg", ".pkg")) or "mac" in nl or "darwin" in nl or "osx" in nl:
        os_type = "macOS"
    elif nl.endswith((".appimage", ".deb", ".rpm")) or "linux" in nl:
        os_type = "Linux"
    elif nl.endswith((".zip", ".tar.gz", ".7z", ".tgz")):
        if "win" in nl: os_type = "Windows"
        elif "mac" in nl or "darwin" in nl: os_type = "macOS"
        elif "linux" in nl: os_type = "Linux"
        else: os_type = "Archive"

    # Architecture
    arch = "Universal / Any"
    if "arm64" in nl or "aarch64" in nl or "v8a" in nl:
        arch = "ARM64"
    elif "v7a" in nl or "armeabi" in nl:
        arch = "ARMv7"
    elif "x86_64" in nl or "amd64" in nl or "x64" in nl:
        arch = "x86_64"
    elif "x86" in nl or "i386" in nl or "i686" in nl:
        arch = "x86 (32-bit)"

    return {"os": os_type, "arch": arch}

def extract_direct_assets(repo: str) -> Dict[str, Any]:
    info = fetch_repo_info(repo)
    rel = fetch_latest_release(repo)
    
    if not info or not rel:
        return {"error": f"Failed to retrieve release data for {repo}"}
        
    tag = rel.get("tag_name", "")
    published_at = rel.get("published_at", "")[:10]
    raw_assets = rel.get("assets", [])
    
    categorized = []
    for a in raw_assets:
        aname = a.get("name", "")
        cat = categorize_asset(aname)
        
        # Skip pure debug symbols / sha hashes unless requested
        if aname.endswith((".sha256", ".sha512", ".md5", ".sig")):
            continue
            
        categorized.append({
            "name": aname,
            "os": cat["os"],
            "arch": cat["arch"],
            "size_mb": round(a.get("size", 0) / (1024 * 1024), 2),
            "downloads": a.get("download_count", 0),
            "download_url": a.get("browser_download_url")
        })
        
    return {
        "repo": repo,
        "stars": info.get("stargazers_count", 0),
        "description": info.get("description", ""),
        "latest_tag": tag,
        "published_at": published_at,
        "release_page": rel.get("html_url", ""),
        "assets": categorized
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python asset_extractor.py <owner/repo>")
        sys.exit(1)
        
    target_repo = sys.argv[1]
    res = extract_direct_assets(target_repo)
    print(json.dumps(res, ensure_ascii=False, indent=2))
