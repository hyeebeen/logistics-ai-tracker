# logistics-ai-tracker

> 物流 AI 信息源持续追踪仓库。基于 19 轮深度挖掘（270+ 维度，250+ 次 Web 搜索，1990 行发现）整理，用于定期检测信息源时效性并生成追踪报告。

## 仓库结构

```
.
├── data
│   └── sources.json            # 信息源结构化数据（30 条，3 级分层）
├── reports
│   └── freshness_report.md     # 最近一次新鲜度检测报告
├── scripts
│   ├── check_freshness.py      # HTTP HEAD 新鲜度检测脚本
│   ├── generate_report.py      # Markdown 报告生成
│   └── update_source.py        # 新增/更新信息源工具
├── .github
│   └── workflows
│       └── freshness-check.yml # 每周一 09:00 UTC 自动检测
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

## 快速开始

```bash
# 1. 仅使用 Python 标准库，无需安装第三方包
python3 --version  # 要求 >= 3.9

# 2. 手动运行新鲜度检测（检测全部 30 个信息源的 HTTP 可达性）
python3 scripts/check_freshness.py

# 3. 生成 Markdown 报告
python3 scripts/generate_report.py > reports/freshness_report.md

# 4. 添加新信息源
python3 scripts/update_source.py --add --name "新工具" --url "https://..." --tier 2 --category optimization
```

## 信息源覆盖

| 类别 | 数量 | 说明 |
|------|------|------|
| 开源项目 | 15 | OR-Tools、PyVRP、LangGraph、Milvus、PaddleOCR 等 |
| 学术论文 | 9 | SupChain-Bench、SC-TGN、Chronos/TimesFM、Pointer Networks 等 |
| 行业报告/企业资料 | 7 | Gartner MQ、CFLP、Flexport/Project44 等 |
| 政策法规 | 2 | EU AI Act、MIT CTL |
| 生态平台 | 4 | Awesome-Chinese-LLM、JioNLP、HuggingFace 等 |

## 信息源分级

| Tier | 含义 | 数量 |
|------|------|------|
| 1 | 必读（奠基性/首选工具） | 10 |
| 2 | 强烈推荐（深度技术参考） | 15 |
| 3 | 推荐（行业应用/扩展阅读） | 25 |

## 自动化

GitHub Actions 每周一 09:00 UTC 自动运行 `check_freshness.py`，结果提交到 `reports/freshness_report.md`，并创建 Issue 提醒需要关注的信息源。

## 贡献

参见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

## 许可证

MIT License — 见 [LICENSE](./LICENSE)。
