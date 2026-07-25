#!/usr/bin/env python3
"""
generate_report.py — 从 freshness_report.json 生成 Markdown 报告
"""

import json
import sys
from datetime import datetime
from pathlib import Path

REPORT_JSON = Path(__file__).resolve().parent.parent / "reports" / "freshness_report.json"
REPORT_MD  = Path(__file__).resolve().parent.parent / "reports" / "freshness_report.md"


def main():
    if not REPORT_JSON.exists():
        print("❌ freshness_report.json 不存在，请先运行 check_freshness.py")
        sys.exit(1)

    with open(REPORT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = [
        "# 物流 AI 信息源新鲜度报告",
        "",
    ]
    gen_time = datetime.fromisoformat(data["generated_at"]).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"> 生成时间: {gen_time}")
    lines.append(f"> 总信息源: {data['total_sources']} | ✅ 可达: {data['reachable']} | ❌ 不可达: {data['unreachable']}")
    lines.append("")

    for tier in [1, 2, 3]:
        tier_results = [r for r in data["results"] if r["tier"] == tier]
        if not tier_results:
            continue
        tier_name = {1: "必读", 2: "强烈推荐", 3: "推荐"}[tier]
        lines.append(f"## Tier {tier} — {tier_name}（{len(tier_results)} 条）")
        lines.append("")
        lines.append("| ID | 名称 | 类型 | 状态 | HTTP | 额外信息 |")
        lines.append("|---|------|------|------|------|----------|")

        for r in tier_results:
            status = "✅" if r.get("reachable") else "❌"
            http   = str(r.get("status_code", "-"))
            extra  = ""
            if "github" in r:
                gh = r["github"]
                stars  = gh.get("stars", "-")
                pushed = gh.get("pushed_at", "")[:10]
                arch   = "📦 已归档" if gh.get("archived") else ""
                extra  = f"⭐ {stars} | 推送: {pushed} {arch}"
            elif "arxiv" in r:
                extra = "论文存在" if r["arxiv"].get("exists") else "⚠️ 论文不存在"
            lines.append(f"| {r['id']} | {r['name'][:30]} | {r['type']} | {status} | {http} | {extra} |")

        lines.append("")

    unreachable = [r for r in data["results"] if not r.get("reachable")]
    if unreachable:
        lines.append("## ❌ 不可达信息源")
        lines.append("")
        for r in unreachable:
            lines.append(f"- **{r['id']} {r['name']}** — {r.get('error', 'Unknown error')}")
            lines.append(f"  - URL: {r['url']}")
        lines.append("")

    lines.append("## 🔄 需要关注更新")
    lines.append("")
    lines.append("以下信息源可达，建议人工检查是否有新版本/新发布：")
    lines.append("")
    for r in data["results"]:
        if r.get("reachable") and r["type"] in ["industry_report", "academic_paper", "enterprise_release"]:
            lines.append(f"- **{r['id']} {r['name']}** — 类型: {r['type']}，建议检查是否有新版发布")
    lines.append("")
    lines.append("---")
    lines.append("*本报告由 `check_freshness.py` + `generate_report.py` 自动生成*")
    lines.append("")

    OUTPUT_FILE = REPORT_MD
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"📄 Markdown 报告已生成: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
