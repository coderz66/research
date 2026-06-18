# 日韩周报工作流（v2.2 · 260526 市值排序修复）

> 韩股 + 日股合并周度复盘，单一 HTML 按主题混编。
> 与美股周报独立、与 A 股映射独立、与 A 股周报独立。

---

## 触发方式

用户说：
- "日韩周报"
- "韩股周报" / "日股周报"
- "韩日周报"
- "KR JP weekly"

→ 进入 `D:\claude\research\templates\jp_kr_weekly_prompt.md` SOP（v2）。

---

## 数据流（v2 · 用户提供 xlsx + 后处理脚本层）

```
用户提供 xlsx/csv（Wind 导出）
       ↓
[Phase 0] 读 xlsx → _phase0_data_summary.md
       ↓
[Phase 0] 主题分类 → _phase0_themes_YYMMDD.md（含跨市场映射框架）
       ↓
[Phase 0] AskUserQuestion 确认 + WebSearch 财报日期 → _phase0_facts_YYMMDD.md
       ↓
[Phase A] 11 Opus agent fan-out（10 主线 + masthead）
       ↓
[Phase A.5] 后处理批量脚本（USD 换算 / 数字列权威覆盖 / 核心业务+大涨驱动注入）
       ↓
[Phase B] 3 Opus agent · §01 Exec Summary（必）+ §12 + §13（可选）
       ↓
[Phase C] 整合 → 日韩周报_YYMMDD.html
       ↓
[Phase D] git push + index.html 卡片
```

**v2 不接 DB pipeline**（不跑 `weekly_query.py`、不挂三道门）—— 用户 xlsx 直接读 + Python 后处理脚本权威化字段。

---

## 目录结构

```
D:\claude\research\日韩周报\
├── README.md                       ← 本文件
├── _fragments\
│   └── YYMMDD\                     ← 每期一个子目录
│       ├── 00_masthead.html
│       ├── 09_exec_summary.html
│       ├── 10..19_theme*.html      ← 10 主线
│       ├── 89_cross_signals.html   ← v2 可选
│       └── 90_final_read.html      ← v2 可选
├── _phase0_data_summary.md         ← 每期 xlsx 摘要
├── _phase0_themes_YYMMDD.md        ← 每期主线分配 + 跨市场映射
├── _phase0_facts_YYMMDD.md         ← 每期 fact base（财报日期等）
├── _phase01_summary_data.md        ← §01 Exec Summary 数据预算（行业热度+极值池）
├── _inject_returns.py              ← Phase A.5 后处理（数字列）
├── _inject_usd_mcap.py             ← Phase A.5 后处理（USD 换算）
├── _inject_business.py             ← Phase A.5 后处理（核心业务一句话）
├── _inject_drivers.py              ← Phase A.5 后处理（大涨驱动一句话）
└── 日韩周报_YYMMDD.html             ← 最终产物
```

---

## v2.1 表格结构（固化 · 不再变）

**9 列固定宽**：

```
Ticker 6% / 公司 4% / 市值 4% / 1M 4% / 3M 4% / 6M 4% / 1Y 4% / 归因 4% / 个股逻辑 66%
```

- 不显示国别列（`data-country="kr/jp"` 写在 `<tr>` 属性上做视图过滤）
- **市值独立成列**（v2.1）· USD 换算 · 不写本币、不写交易所
- 数字列固定 4 列 1M/3M/6M/1Y（**不要硬凑 1W**——KR/JP Wind xlsx 通常没有）

---

## v2 td 6-block 结构（固化 · 不再变）

每只标的的「个股逻辑」单元格按此顺序：

| Block | 长度 | 内容 |
|---|---|---|
| 1. **核心业务** | 20-40 字 | 国别+主业+行业地位+关键客户/份额 |
| 2. **大涨驱动** | 25-55 字 | 公司名+1Y涨幅+具体业务+客户/订单/产品+数字证据 |
| 3. **近期走势** | 80-150 字 | 1M-3M 关键拐点 + catalyst |
| 4. **财报/经营** | 60-120 字 | 最近季度+next 季度共识 + 业务占比 |
| 5. **产业链/客户** | 60-120 字 | 上下游 ticker 网络 KR↔JP↔US |
| 6. **ki-note** | 100-180 字 | thesis 阶段定位+alpha 类型+催化时点 |

**用户阅读路径**：核心业务 + 大涨驱动 30 秒抓核心 alpha；想深入读 3-6 详细。

---

## v2.2 市值列排序机制（关键陷阱）

市值列显示 `$1.25T` / `$231B` / `$3.6B` **T/B 单位混用** · 字符串排序会错排（字典序 `1.01T` < `3.6B`）。

**正确做法**：
```html
<th data-type="num" style="width:4%">市值</th>
<td class="num" data-sort-value="1248.2">$1.25T</td>
<td class="num" data-sort-value="3.62">$3.6B</td>
```

shell sort JS（v2.2）优先读 `data-sort-value`、fallback `parseFloat(textContent)`。**单位换算到 $B**：T×1000 / M÷1000 / B 不变。

此机制是**通用 pattern**（所有 HTML 报告表格的"显示值 ≠ 排序值"列均可复用）—— 详见 memory `feedback_html_table_sort_value`。

---

## v2 USD 换算口径

**汇率**（2026-05 近期、新一期检查）：
- USD/KRW = **1370**
- USD/JPY = **155**

**Wind `总市值1` 列单位 = 亿 of local currency**（不是万元）

**换算公式**：
```python
usd_b = mcap_local_亿 * 1e8 / FX / 1e9
```

**显示格式**：
- ≥ $1T → `$X.XT`
- $100-999B → `$XXXB`
- $10-99B → `$XXB`
- $1-9.9B → `$X.XB`

---

## 章节结构（13 段）

| § | 文件名 | 内容 | 模型 | v2 状态 |
|---|---|---|---|---|
| §00 | `00_masthead.html` | masthead + view-tabs（全部/韩股/日股） | Opus | ✅ |
| §01 | `09_exec_summary.html` | 两国大盘 + 行业热度透视 + 5 核心信号 + 主线优先级 | Opus | ✅ |
| §02-§11 | `10..19_theme*.html` | 10 条主线（KR/JP 混编、8 列 6-block） | Opus × 10 | ✅ |
| §12 | `89_cross_signals.html` | KR↔JP 跨市场映射 | Opus | 🟡 可选 |
| §13 | `90_final_read.html` | 综合判断 + 下周观察 | Opus | 🟡 可选 |

> 🔴 **§01 核心信号丰富度（260615 固化）**：5 个核心信号 note-block **每个 ≥280–400 字、五维讲透**——① 逻辑链条（Bull/Bear 阶段 + 本周是轮动/获利了结/拐点）② 产业链最新变化（订单/价格/库存/capex 四维带数字）③ 相关公司最新变化（点名 3-5 家 + 本周涨跌幅 hl 高亮）④ 财报重点（有则写 YoY/QoQ 具体数字、无则不硬写）⑤ 反叙事/分界（只用产业信号、禁价格信号）。所有数字必须正文 theme sections 可溯源、不脑补、不引入快照日后新闻。完整规范见 `templates\jp_kr_weekly_prompt.md` 的〈核心信号丰富度规范〉。单薄的「一句 What + 一句 Why」是 FAIL。

---

## v2 模型规则（[[feedback_agent_model_default]] v4）

| 任务性质 | 模型 |
|---|---|
| **内容撰写**（10 主线 / §01-§13 / 核心业务 / 大涨驱动）| **Opus 4.7** |
| **结构性改造**（整合 / 后处理 / 列宽 / 整理）| **Sonnet** |

---

## v2 与美股周报核心差异

| 维度 | 美股周报 | 日韩周报 v2 |
|---|---|---|
| Beta 基准 | 25 ETF β strip | ❌ 无 → §01 两国大盘+行业热度 |
| 市值分档 | mcap_tier 5 档 | ❌ 无 → 视图 3 档 all/kr/jp |
| 数据 pipeline | DB + 三道门 | xlsx 直接读 + 后处理脚本 |
| 表格列 | 7 列 | 8 列（无国别可见列） |
| td 结构 | 4-block | **6-block**（多核心业务+大涨驱动） |
| 市值显示 | `$XB · L` | `$X.XT/$XXXB/$X.XB` 无交易所标签 |
| 跨市场 | A 股映射段 | KR↔JP 双边映射段（v2 可选） |
| 归因 tag | 9 个 | 11 个（加 t-fx + t-policy） |

---

## 时间预算

中位 **100-150 min**。

| Phase | 耗时 |
|---|---|
| Phase 0 | 15-30 min |
| Phase A | 45-60 min |
| Phase A.5（后处理）| 10-15 min |
| Phase B | 15-25 min |
| Phase C/D | 15-20 min |

---

## v2 待完善（v3 候选）

- [ ] §12 跨市场映射 + §13 Final Read 标准模板固化
- [ ] Phase A agent prompt 直接产出完整 6-block（跳过 Phase A.5 inject_business/inject_drivers）
- [ ] 数据 pipeline 化（KRX / JPX / TickFlow KR-JP）
- [ ] index.html 独立 `data-category="kr-jp"` 颜色

---

## v2 已知踩坑（已固化进 prompt）

1. **Wind xlsx 列名陷阱**：`所属Wind行业名称(2024)` + `.1` + `.2` 实际是 L3+L1+L2 三级、不是 L1+L2+L3
2. **Wind 市值单位**：`总市值1` 列在 KR/JP 池中是 **亿 of local currency**（不是万元）
3. **1W 列陷阱**：KR/JP Wind xlsx 通常无 1W、不要硬凑（v1 13_theme04 agent 误写 1W/1M/3M）
4. **标的遗漏**：Phase 0.2 强制校验 N_assigned == N_pool（v1 漏 6526.T + 034220.KS）
5. **ticker 凭记忆**：日韩 ticker 变化频繁（新 IPO / 改名 / 退市），必须 WebSearch 验证

---

*创建：2026-05-25 v1 · 更新：2026-05-26 v2 实证后固化*
