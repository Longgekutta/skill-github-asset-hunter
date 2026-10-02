#!/usr/bin/env python3
"""
asset_extractor.py - High-precision GitHub Release Asset Extractor & Direct URL Generator
========================================================================================
Used by skill-github-asset-hunter to parse GitHub Releases, filter ABI architectures,
and extract direct download links with dual-channel acceleration and HTML fallback.

Features:
1. Dual Extraction Engine: Official GitHub API v3 + Resilient HTML Scraper Fallback (bypasses 60 req/hr rate limit)
2. Smart Noise Filtering: Filters out developer debug files (.mapping, .zst, debug-symbols, sha256)
3. Dual-Channel URLs: Provides official GitHub URL and high-speed mirror URL (ghfast.top)
4. Batch & Report Mode: Accepts multiple repos or reads radar report JSON directly (--report radar.json --top 3)
5. Zero-Binary Fallback: Fallback to Tag Source Archives (.zip/.tar.gz) when no release binaries exist
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 skill-github-asset-hunter/2.0.0"
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
    except Exception:
        # Fallback to public web page meta scrape
        try:
            web_url = f"https://github.com/{repo.strip('/')}"
            wreq = urllib.request.Request(web_url, headers=get_headers())
            with urllib.request.urlopen(wreq, timeout=10) as wresp:
                html = wresp.read().decode('utf-8', errors='ignore')
                desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html)
                desc = desc_match.group(1) if desc_match else ""
                return {"stargazers_count": 0, "description": desc}
        except Exception:
            return None

def fetch_latest_release_api(repo: str) -> Optional[Dict[str, Any]]:
    url = f"https://api.github.com/repos/{repo.strip('/')}/releases/latest"
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
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

def fetch_latest_release_html(repo: str) -> Optional[Dict[str, Any]]:
    """
    HTML 静态网页直接嗅探回退引擎：
    当 GitHub API 遭遇 403 Rate Limit (60次/小时) 时，直接通过静态网页解析 /releases/latest，
    确保 100% 连通率与直链直达能力。
    """
    repo_clean = repo.strip('/')
    web_url = f"https://github.com/{repo_clean}/releases/latest"
    req = urllib.request.Request(web_url, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            final_url = resp.geturl()
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Extract tag name from final URL e.g. /releases/tag/v1.10.9
            tag_match = re.search(r'/releases/tag/([^/?#]+)', final_url)
            tag = tag_match.group(1) if tag_match else "latest"
            
            # Find all release download asset links
            # href="/connectbot/connectbot/releases/download/v1.10.9/ConnectBot-v1.10.9-oss.apk"
            pattern = rf'/{repo_clean}/releases/download/[^/]+/([^\s"\'<>]+)'
            matches = list(set(re.findall(pattern, html)))
            
            assets = []
            for aname in matches:
                assets.append({
                    "name": aname,
                    "size": 0,
                    "download_count": 0,
                    "browser_download_url": f"https://github.com/{repo_clean}/releases/download/{tag}/{aname}"
                })
                
            return {
                "tag_name": tag,
                "published_at": "",
                "html_url": final_url,
                "assets": assets,
                "source": "html_scraper_fallback"
            }
    except Exception:
        return None

def categorize_asset(name: str) -> Dict[str, Any]:
    nl = name.lower()
    
    # OS
    os_type = "UNKNOWN"
    if nl.endswith(".apk") or "android" in nl:
        os_type = "Android"
    elif nl.endswith((".dmg", ".pkg")) or "mac" in nl or "darwin" in nl or "osx" in nl:
        os_type = "macOS"
    elif nl.endswith((".exe", ".msi")) or "windows" in nl or re.search(r'(^|[\-_.\b])win(32|64|dows)?([\-_.\b]|$)', nl):
        os_type = "Windows"
    elif nl.endswith((".appimage", ".deb", ".rpm")) or "linux" in nl:
        os_type = "Linux"
    elif nl.endswith((".zip", ".tar.gz", ".7z", ".tgz")):
        if "mac" in nl or "darwin" in nl or "osx" in nl:
            os_type = "macOS"
        elif "linux" in nl:
            os_type = "Linux"
        elif "windows" in nl or re.search(r'(^|[\-_.\b])win(32|64|dows)?([\-_.\b]|$)', nl):
            os_type = "Windows"
        else:
            os_type = "Archive"

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

    # Identify whether it is a primary installer (vs debug metadata)
    is_installer = False
    if nl.endswith((".apk", ".exe", ".msi", ".dmg", ".pkg", ".appimage", ".deb", ".rpm")):
        is_installer = True
    elif nl.endswith((".zip", ".tar.gz")) and not any(k in nl for k in ("symbols", "mapping", "debug", "src", "source")):
        is_installer = True

    is_debug = any(k in nl for k in ("mapping", "symbol", "debug", "hash", "sha256", "sha512", "md5", "sig", ".txt", ".aab"))

    return {
        "os": os_type,
        "arch": arch,
        "is_installer": is_installer,
        "is_debug": is_debug
    }

def extract_direct_assets(repo: str) -> Dict[str, Any]:
    info = fetch_repo_info(repo) or {"stargazers_count": 0, "description": ""}
    
    # 1. Try GitHub API
    rel = fetch_latest_release_api(repo)
    # 2. Fallback to HTML Scraper
    if not rel:
        rel = fetch_latest_release_html(repo)
        
    if not rel:
        # Zero-binary fallback: return source archive directly
        return {
            "repo": repo,
            "stars": info.get("stargazers_count", 0),
            "description": info.get("description", ""),
            "latest_tag": "HEAD",
            "published_at": "",
            "release_page": f"https://github.com/{repo.strip('/')}/releases",
            "source_archive": {
                "zip": f"https://github.com/{repo.strip('/')}/archive/refs/heads/main.zip",
                "tar": f"https://github.com/{repo.strip('/')}/archive/refs/heads/main.tar.gz"
            },
            "assets": [],
            "note": "No formal release binary published; source archives provided."
        }
        
    tag = rel.get("tag_name", "")
    published_at = rel.get("published_at", "")[:10]
    raw_assets = rel.get("assets", [])
    
    installers = []
    other_assets = []
    
    for a in raw_assets:
        aname = a.get("name", "")
        cat = categorize_asset(aname)
        
        # Skip pure debug symbols / sha hashes unless requested
        if aname.endswith((".sha256", ".sha512", ".md5", ".sig")) or cat["is_debug"]:
            continue
            
        dl_url = a.get("browser_download_url", "")
        # Domestic accelerated mirror URL (ghfast.top)
        mirror_url = f"https://ghfast.top/{dl_url}" if dl_url else ""
        
        size_mb = round(a.get("size", 0) / (1024 * 1024), 2)
        
        item = {
            "name": aname,
            "os": cat["os"],
            "arch": cat["arch"],
            "size_mb": size_mb,
            "downloads": a.get("download_count", 0),
            "download_url": dl_url,
            "mirror_url": mirror_url,
            "is_installer": cat["is_installer"]
        }
        
        if cat["is_installer"]:
            installers.append(item)
        else:
            other_assets.append(item)
            
    # Sort installers by downloads descending
    installers.sort(key=lambda x: x["downloads"], reverse=True)
    all_filtered = installers + other_assets
    
    return {
        "repo": repo,
        "stars": info.get("stargazers_count", 0),
        "description": info.get("description", ""),
        "latest_tag": tag,
        "published_at": published_at,
        "release_page": rel.get("html_url", ""),
        "total_installers": len(installers),
        "source_archive": {
            "zip": f"https://github.com/{repo.strip('/')}/archive/refs/tags/{tag}.zip" if tag else "",
            "tar": f"https://github.com/{repo.strip('/')}/archive/refs/tags/{tag}.tar.gz" if tag else ""
        },
        "assets": all_filtered
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python asset_extractor.py <owner/repo> [owner/repo2 ...] [--report radar_out.json] [--top 3]")
        sys.exit(1)
        
    targets = []
    top_n = 3
    
    if "--report" in sys.argv:
        r_idx = sys.argv.index("--report")
        if r_idx + 1 < len(sys.argv):
            r_path = sys.argv[r_idx + 1]
            if os.path.exists(r_path):
                with open(r_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "--top" in sys.argv:
                    t_idx = sys.argv.index("--top")
                    top_n = int(sys.argv[t_idx + 1])
                candidates_list = data.get("reports", [])
                if not candidates_list and "generations" in data:
                    for g in data.get("generations", []):
                        for gem in g.get("top_gems", []):
                            candidates_list.append({"repo_name": gem.get("repo")})
                for r in candidates_list[:top_n]:
                    if r.get("repo_name"):
                        targets.append(r.get("repo_name"))
                    
    for arg in sys.argv[1:]:
        if not arg.startswith("--") and "/" in arg and arg not in targets:
            targets.append(arg)
            
    if not targets:
        print("Error: No target repos specified.")
        sys.exit(1)
        
    results = []
    for t in targets:
        res = extract_direct_assets(t)
        results.append(res)
        
    if len(results) == 1:
        print(json.dumps(results[0], ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"total_processed": len(results), "candidates": results}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
