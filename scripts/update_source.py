#!/usr/bin/env python3
"""
update_source.py — 新增/更新信息源工具

用法:
  python3 update_source.py add --name "新工具" --url "https://..." --tier 2 --category optimization
  python3 update_source.py list
  python3 update_source.py update T1-001 --notes "更新备注"
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCES_FILE = Path(__file__).resolve().parent.parent / "data" / "sources.json"


def load_data():
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(SOURCES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存到 {SOURCES_FILE}")


def gen_id(data, tier):
    tier_sources = [s for s in data["sources"] if s["tier"] == tier]
    return f"T{tier}-{len(tier_sources) + 1:03d}"


def add_source(args):
    data = load_data()
    new_id = gen_id(data, args.tier)
    new_source = {
        "id": new_id,
        "tier": args.tier,
        "name": args.name,
        "type": args.type or "open_source_project",
        "url": args.url,
        "category": args.category or "general",
        "description": args.description or "",
        "freshness_criteria": {},
        "added_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "notes": args.notes or "",
    }
    data["sources"].append(new_source)
    data["metadata"]["total_sources"] = len(data["sources"])
    save_data(data)
    print(f"  新增: {new_id} {args.name}")


def list_sources(args):
    data = load_data()
    for tier in [1, 2, 3]:
        tier_sources = [s for s in data["sources"] if s["tier"] == tier]
        tier_name = {1: "必读", 2: "强烈推荐", 3: "推荐"}[tier]
        print(f"\n=== Tier {tier} — {tier_name}（{len(tier_sources)} 条）===")
        for s in tier_sources:
            print(f"  {s['id']}  {s['name'][:40]:40s}  {s['url'][:60]}")


def update_source(args):
    data = load_data()
    found = False
    for s in data["sources"]:
        if s["id"] == args.source_id:
            found = True
            if args.name:
                s["name"] = args.name
            if args.url:
                s["url"] = args.url
            if args.description:
                s["description"] = args.description
            if args.notes:
                s["notes"] = args.notes
            print(f"  更新: {s['id']} {s['name']}")
            break
    if not found:
        print(f"❌ 未找到 ID: {args.source_id}")
        sys.exit(1)
    save_data(data)


def main():
    parser = argparse.ArgumentParser(description="物流 AI 信息源管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    add_parser = subparsers.add_parser("add", help="新增信息源")
    add_parser.add_argument("--name", required=True, help="信息源名称")
    add_parser.add_argument("--url", required=True, help="URL")
    add_parser.add_argument("--tier", type=int, required=True, choices=[1, 2, 3], help="层级 1/2/3")
    add_parser.add_argument("--category", help="类别")
    add_parser.add_argument("--type", help="类型")
    add_parser.add_argument("--description", help="描述")
    add_parser.add_argument("--notes", help="备注")

    subparsers.add_parser("list", help="列出所有信息源")

    update_parser = subparsers.add_parser("update", help="更新信息源")
    update_parser.add_argument("source_id", help="信息源 ID，如 T1-001")
    update_parser.add_argument("--name", help="新名称")
    update_parser.add_argument("--url", help="新 URL")
    update_parser.add_argument("--description", help="新描述")
    update_parser.add_argument("--notes", help="新备注")

    args = parser.parse_args()
    if args.command == "add":
        add_source(args)
    elif args.command == "list":
        list_sources(args)
    elif args.command == "update":
        update_source(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
