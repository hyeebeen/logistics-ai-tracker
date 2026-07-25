#!/usr/bin/env python3
"""
check_freshness.py — 物流 AI 信息源新鲜度检测

检测内容：
  1. HTTP 可达性（HEAD 请求，405 时回退 GET）
  2. GitHub 仓库星标数和最近提交时间（通过公开 API）
  3. arXiv 论文是否存在
  4. 最终修改时间（Last-Modified 头）

无需第三方依赖，仅使用 Python 标准库。
"""

import json
import urllib.request
import urllib.error
import socket
import ssl
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────
SOURCES_FILE = Path(__file__).resolve().parent.parent / "data" / "sources.json"
OUTPUT_FILE   = Path(__file__).resolve().parent.parent / "reports" / "freshness_report.json"
TIMEOUT       = 15
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def head_url(url: str) -> dict:
    """发送 HEAD 请求，返回状态信息。405 时回退 GET。"""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "logistics-ai-tracker/1.0"})
        resp = urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX)
        return {
            "reachable": True,
            "status_code": resp.status,
            "last_modified": resp.headers.get("Last-Modified", ""),
            "content_type": resp.headers.get("Content-Type", ""),
        }
    except urllib.error.HTTPError as e:
        if e.code == 405:
            return get_url(url)
        return {"reachable": False, "status_code": e.code, "error": str(e)}
    except Exception as e:
        return {"reachable": False, "status_code": 0, "error": str(e)}


def get_url(url: str) -> dict:
    """GET 回退（仅取 headers）。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "logistics-ai-tracker/1.0", "Range": "bytes=0-0"})
        resp = urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX)
        return {
            "reachable": True,
            "status_code": resp.status,
            "last_modified": resp.headers.get("Last-Modified", ""),
            "content_type": resp.headers.get("Content-Type", ""),
        }
    except Exception as e:
        return {"reachable": False, "status_code": 0, "error": str(e)}


def check_github_repo(url: str) -> dict:
    """通过 GitHub 公开 API 检查仓库活跃度。"""
    parts = url.rstrip("/").split("/")
    if "github.com" not in parts or len(parts) < 5:
        return {}
    owner_repo = f"{parts[-2]}/{parts[-1]}"
    api_url = f"https://api.github.com/repos/{owner_repo}"
    try:
        req = urllib.request.Request(api_url, headers={
            "User-Agent": "logistics-ai-tracker/1.0",
            "Accept": "application/vnd.github+json",
        })
        resp = urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX)
        data = json.loads(resp.read())
        return {
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "pushed_at": data.get("pushed_at", ""),
            "updated_at": data.get("updated_at", ""),
            "archived": data.get("archived", False),
        }
    except Exception:
        return {}


def check_arxiv(url: str) -> dict:
    """检查 arXiv 论文是否存在。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "logistics-ai-tracker/1.0"})
        resp = urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX)
        return {"exists": resp.status == 200, "status_code": resp.status}
    except Exception as e:
        return {"exists": False, "error": str(e)}


def check_source(source: dict) -> dict:
    """检测单个信息源。"""
    url = source["url"]
    result = {
        "id": source["id"],
        "name": source["name"],
        "tier": source["tier"],
        "url": url,
        "type": source["type"],
        "category": source["category"],
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

    http_result = head_url(url)
    result.update(http_result)

    if "github.com" in url:
        gh = check_github_repo(url)
        if gh:
            result["github"] = gh

    if "arxiv.org" in url:
        ax = check_arxiv(url)
        if ax:
            result["arxiv"] = ax

    return result


def main():
    if not SOURCES_FILE.exists():
        print(f"❌ sources.json 不存在: {SOURCES_FILE}")
        sys.exit(1)

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    sources = data.get("sources", [])
    print(f"🔍 开始检测 {len(sources)} 个信息源...\n")

    results = []
    for i, src in enumerate(sources, 1):
        print(f"  [{i}/{len(sources)}] {src['id']} {src['name'][:40]:40s}", end=" ", flush=True)
        result = check_source(src)
        results.append(result)

        icon = "✅" if result.get("reachable") else "❌"
        code  = result.get("status_code", 0)
        print(f"{icon} ({code})")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_sources": len(results),
        "reachable": sum(1 for r in results if r.get("reachable")),
        "unreachable": sum(1 for r in results if not r.get("reachable")),
        "results": results,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n📊 检测完成: {report['reachable']}/{report['total_sources']} 可达")
    print(f"📄 报告已保存: {OUTPUT_FILE}")
    return report


if __name__ == "__main__":
    main()
