# 贡献指南

## 如何添加新信息源

### 方法 1：使用脚本（推荐）

```bash
python3 scripts/update_source.py add \
  --name "工具名称" \
  --url "https://github.com/..." \
  --tier 2 \
  --category optimization \
  --type open_source_project \
  --description "简要描述" \
  --notes "备注"
```

### 方法 2：直接编辑 JSON

编辑 `data/sources.json`，在 `sources` 数组末尾添加：

```json
{
  "id": "T2-031",
  "tier": 2,
  "name": "工具名称",
  "type": "open_source_project",
  "url": "https://...",
  "category": "optimization",
  "description": "描述",
  "freshness_criteria": { "last_commit_days": 90 },
  "added_at": "2026-07-25",
  "notes": ""
}
```

## Tier 分级标准

| Tier | 含义 | 判定标准 |
|------|------|----------|
| 1 | 必读 | 奠基性论文/首选工具/行业标准 |
| 2 | 强烈推荐 | 深度技术参考/高质量开源项目 |
| 3 | 推荐 | 行业应用/扩展阅读/企业资料 |

## Freshness Criteria 字段说明

| 字段 | 适用类型 | 说明 |
|------|----------|------|
| `last_commit_days` | GitHub 项目 | 最近一次提交应在 N 天内 |
| `releases_per_year` | GitHub 项目 | 每年至少 N 次发布 |
| `report_age_months` | 行业报告/论文 | 报告/论文发布不超过 N 个月 |
| `citation_count` | 学术论文 | 引用数至少 N 次 |
| `update_age_months` | 网站/博客 | 最近更新不超过 N 个月 |

## 提交流程

1. Fork 仓库
2. 创建分支：`git checkout -b add-new-source`
3. 提交更改：`git commit -m "add: 新信息源名称"`
4. 推送分支：`git push origin add-new-source`
5. 创建 Pull Request

## 代码风格

- Python 脚本仅使用标准库，不引入第三方依赖
- JSON 文件使用 2 空格缩进
- Markdown 文件换行长度不超过 120 字符
