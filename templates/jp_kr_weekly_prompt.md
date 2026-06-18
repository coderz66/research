# 日韩周报 · Standard Prompt (**v2.2 · 260526 市值排序修复**)

> Workflow: `D:\claude\research\日韩周报\` · 周度触发 · 总耗时 ~90-135 min
> 配套 shell: `D:\claude\research\templates\jp_kr_weekly_shell.html`
> 数据输入：**用户提供 xlsx / csv**（不接 DB pipeline、不跑 weekly_query.py）
> v1→v2 关键变化见文末「v2 改造日志」

---

## ⚠️ 写报告前必读

### 必读 memory（按权重排序）
1. [[project_jp_kr_weekly]] — 工作流主索引
2. [[feedback_agent_model_default]] — v4：内容撰写 Opus / 结构性改造 Sonnet
3. [[feedback_no_trader_actions_in_report]] — 禁出场信号 / 仓位管理 / 减仓加仓措辞
4. [[feedback_weekly_fragment_format_consistency]] — 美股周报 11 条铁律可借鉴
5. [[project_us_weekly]] — 美股周报作业流程（架构参考、不照搬细节）

### 与美股周报的核心差异（不要照搬）

| 维度 | 美股周报 | 日韩周报 v2 |
|---|---|---|
| **Beta 基准** | 25 ETF β strip | ❌ 无 ETF 基准 → §01 改"两国大盘 + 行业热度透视" |
| **数据 pipeline** | weekly_query.py 三道门 | ✅ 用户 xlsx 直接读 |
| **市值分档** | 5 档 mcap_tier (L1-L5) → 4 档视图 | ❌ 不分 mcap_tier → 视图 3 档：全部/韩股/日股 |
| **视图过滤实现** | `data-cap` on `<tr>` | ✅ `data-country="kr/jp"` on `<tr>`（**不显示国别列**、纯属性过滤）|
| **表格列数** | 7 列含归因 | ✅ **9 列**：Ticker / 公司 / 市值 / 1M / 3M / 6M / 1Y / 归因 / 个股逻辑 |
| **td 结构** | 4-block（边际/财报/产业链/ki-note）| ✅ **6-block**：核心业务 / 大涨驱动 / 近期走势 / 财报经营 / 产业链客户 / ki-note |
| **市值显示** | `$XB · L`（公司列小字）| ✅ **市值独立成列**（v2.1）· USD 换算（USD/KRW=1370 · USD/JPY=155）· 删交易所后缀 |
| **跨市场映射** | §13 A 股映射指引 | ✅ §12 独立段：KR↔JP 上下游联动（HBM/MLCC/EV 电池/汽车） |
| **归因 tag** | 9 个 | ✅ 11 个（加 `t-fx` 汇率 + `t-policy` BOJ/BOK） |
| **Phase E review** | 询问后触发深化 ≥$30B | ❌ 不做 |

---

## Agent 模型选择规则

按 [[feedback_agent_model_default]] v4 二档：

| 任务性质 | 模型 | 例子 |
|---|---|---|
| **内容撰写** | **Opus 4.7** | 10 主线 fragment / §01 Exec Summary / §12 Cross Signals / §13 Final Read / masthead / 核心业务一句话 / 大涨驱动一句话 |
| **结构性改造** | **Sonnet** | 整合 fragment / 列宽调整 / 删 trader actions / 修 typo / 批量 USD 换算脚本 |

⚠ 不要全部用 Opus —— 机械任务触发 socket error；不要全部用 Sonnet —— 写产业研究深度差距明显。

---

## 章节顺序（整合后固定）

```
00_masthead.html         ← <header> masthead + view-tabs (all/kr/jp)
09_exec_summary.html     ← §01 Executive Summary（两国大盘+行业热度+核心信号+主线优先级）
10_theme01_*.html        ← §02 主线 1
11_theme02_*.html        ← §03 主线 2
...
19_theme10_*.html        ← §11 主线 10
89_cross_signals.html    ← §12 跨市场映射信号（KR↔JP 上下游联动）·（v1 还没固化、v2 中可选）
90_final_read.html       ← §13 综合判断 + 下周观察 ·（v1 还没固化、v2 中可选）
```

按文件名升序拼接 = 正确顺序。

---

## Phase 0 · 设计 + 用户确认（15-30 min）

### Phase 0.1 · 接收用户数据（≤5 min）

用户提供 xlsx（典型 Wind 导出），列结构通常为：
- `证券代码` (ticker — KR `XXXXXX.KS/.KQ` / JP `XXXX.T`)
- `证券简称` (company name)
- `所属Wind行业名称(2024)` × 3 列（L3 / L1 / L2，注意顺序）
- `总市值1` (单位 **亿 of local currency**，Wind 标准)
- `年成交额` / `近一年` / `近六月` / `近三月` / `近一月`

⚠ Wind xlsx **常见噪声**：
- 末尾"数据来源：Wind"footer 行（过滤掉）
- NaN ticker（过滤掉）
- 多列同名 `所属Wind行业名称(2024)` `.1` `.2` 实际是 L3 / L1 / L2 三级、不是 L1 / L2 / L3

读完后主 Claude 出 `_phase0_data_summary.md`：行数 / KR-JP 比例 / 行业分布 / 涨跌分布。

### Phase 0.2 · 主题分类提案 + Phase 0 facts 文件（10-15 min）

按 sector / industry / 涨跌方向聚出 **10 条主线**（或按数据 8-12 条）。

输出 `_phase0_themes_YYMMDD.md` 包含：
1. 全局市场环境（口径 / 主叙事 / 反叙事观察点 / KR-JP 池子画像）
2. **跨市场映射框架**（HBM 链 / BOM 链 / 电力链 / 核电链 / 机器人链 · agent 在 ki-note 中调用）
3. 每条主线：thesis + 标的清单 + 完整 1M/3M/6M/1Y 表格 + 国别分布

### Phase 0.3 · 一次性 AskUserQuestion 确认（5-10 min）

```python
AskUserQuestion(
  question="日韩周报 YYMMDD 本期结构确认 · 一次性勾选所有需要的变更",
  questions=[
    {"header": "主线数量", "options": ["10 主线（标准）", "8 主线", "12 主线", "其他"]},
    {"header": "区间列",   "options": ["1M / 3M / 6M / 1Y（标准 4 列）", "其他"]},
    {"header": "数据缺口", "options": ["数据齐全", "需补 X", "由我 WebSearch 补"]},
  ]
)
```

⚠ **xlsx 列不一定全含 1W**——日韩 Wind 池常见只有 1M/3M/6M/1Y，**不要硬凑 1W 列**（v1 教训：13_theme04 agent 误写 1W/1M/3M 列、与其余 fragment 不一致）。

### Phase 0.4 · WebSearch fact-check（10-15 min）⚠ 强制

主 Claude 先 WebSearch：
1. 涉及所有 ticker 的财报日期（已报 + 即将报）
2. **KR 财报季**：Q1 4 月底-5 月初；Q2 7 月底-8 月初；Q3 10 月底；Q4 1-2 月
3. **JP 财报季**：3 月期末 4 月底-5 月初出全年；半年报 10 月底-11 月；季度 7 月底 + 1 月底
4. **下周 binary event**：BOJ / BOK 政策决议 / 半导体合约价 / 政策 / KOSDAQ 政策基金

输出 `_phase0_facts_YYMMDD.md` 作为 Phase A 各 agent prompt 的 fact base。

---

## Phase A · Fan-out 内容撰写（45-60 min · 11 Opus agent 并行）

### Phase A 流程
- 创建 fragment 目录：`D:\claude\research\日韩周报\_fragments\YYMMDD\`
- 一次性 spawn 11 个 Opus 4.7 agent（10 主线 + masthead）
- 每个 agent 独立 fragment 文件

### Phase A · 每个主线 agent prompt 必传项

```markdown
## 必读
1. **本期数据**：`D:\claude\research\日韩周报\_phase0_themes_YYMMDD.md` § T{NN}
2. **fact base**：`D:\claude\research\日韩周报\_phase0_facts_YYMMDD.md`
3. **标准结构**：`D:\claude\research\templates\jp_kr_weekly_prompt.md` § §C-PRIME

## 硬约束（12 条铁律 · 不可违反）
1. 边界：只输出 `<section class="sec" id="theme-NN">...</section>`
2. 章节头三件套：sec-num / sec-title (含 <em>) / sec-sub ≤30字 thesis
3. Bull/Bear/Mixed Logic note 仅 2 段（行业阶段定位 + catalyst window）—— 禁出场信号 / 仓位管理
4. 4 段 kicker 精确名：「本周关键变化」「财报季分析」「时间催化」「订单与产业链」
5. **每个 theme 只用 1 张 9 列主表**（禁按国别/方向/市值拆多表）
6. **9 列宽固定（v2.3）**：Ticker 6% / 公司 4% / 市值 4% / 1M 3% / 3M 3% / 6M 3% / 1Y 3% / 归因 4% / 个股逻辑 70%（v2.3：涨跌幅列 4→3% 收窄、空间给逻辑列 66→70%）；**涨跌幅数字不写 %**（纯整数 + 正负号，如 +59 / -4，节省列宽 + 视觉统一）
7. **data-country="kr" 或 "jp"** 写在 `<tr>` 属性上（视图过滤靠它、不显示国别列）
8. 数字整数百分比、`<span class="hl">` 高亮、`<em>` amber 斜体
9. **td 6-block 必备结构**（见下方模板）
10. Bull/Bear cards 并列、各 5 条
11. **市值独立列**：USD 市值（如 `$1.25T` / `$231B` / `$3.6B`）作为独立 `<td class="num">` 列 · **不写本币、不写交易所** · 公司列只显示公司名（不带 br + span 小字）
12. WebSearch 验证至少 4-7 项关键产业事实
```

### §C-PRIME 主线 fragment 9 步标准结构

```html
<section class="sec" id="theme-NN">
  <!-- 1. 章节头三件套 -->
  <div class="sec-num">§NN</div>
  <h2 class="sec-title">主线名 · <em>关键词</em></h2>
  <div class="sec-sub">≤30字 thesis</div>

  <!-- 2. Bull/Bear/Mixed Logic note · 2 段 -->
  <div class="note-block">
    <span class="kicker">Bull Logic · ...</span>
    <p><strong>1. 行业阶段定位</strong>：thesis lifecycle 位置 + 产业基础四维度数字</p>
    <p><strong>2. 关键 catalyst window</strong>：未来 2-4 周 binary event 时间线</p>
  </div>

  <!-- 3-6. 4 段标准 kicker -->
  <p><span class="kicker">本周关键变化</span>·...</p>
  <p><span class="kicker">财报季分析</span>·...</p>
  <p><span class="kicker">时间催化</span>·...</p>
  <p><span class="kicker">订单与产业链</span>·...</p>

  <!-- 7. 主表 1 张 9 列（v2.1 · 市值独立列） -->
  <table class="dt">
    <thead><tr>
      <th data-type="text" style="width:6%">Ticker</th>
      <th data-type="text" style="width:4%">公司</th>
      <th data-type="text" style="width:4%">市值</th>
      <th data-type="num" style="width:3%">1M</th>
      <th data-type="num" style="width:3%">3M</th>
      <th data-type="num" style="width:3%">6M</th>
      <th data-type="num" style="width:3%">1Y</th>
      <th data-type="text" style="width:4%">归因</th>
      <th data-type="text" style="width:70%">关键产业事实 + 个股逻辑</th>
    </tr></thead>
    <tbody>
      <!-- 按 1Y 降序排 · ⚠ 涨跌幅数字不写 %（纯整数 + 正负号，节省列宽） -->
      <tr data-country="kr">
        <td class="tk">000660.KS</td>
        <td class="name">SK海力士</td>
        <td class="num">$1.01T</td>
        <td class="num pos">+59</td>
        <td class="num pos">+105</td>
        <td class="num pos">+273</td>
        <td class="num pos">+874</td>
        <td><span class="tag t-er">财报</span><span class="tag t-map-d">直接</span></td>
        <td>
          <strong>核心业务</strong>：[20-40 字 · 国别+主业+行业地位+关键客户/份额]<br>
          <strong>大涨驱动</strong>：[25-55 字 · 公司名+1Y涨幅+具体业务+客户/订单/产品+数字证据]<br>
          <strong>近期走势</strong>：[80-150 字 · 1M-3M 关键拐点 + catalyst]<br>
          <strong>财报/经营</strong>：[60-120 字 · 最近季度+next 季度共识 + HBM 占收入比]<br>
          <strong>产业链/客户</strong>：[60-120 字 · 上下游 ticker 网络 KR↔JP↔US]
          <span class="ki-note">[100-180 字 · thesis 阶段定位+alpha 类型+催化时点（禁 Beta 校准 / 禁仓位语言）]</span>
        </td>
      </tr>
    </tbody>
  </table>

  <!-- 8. Bull/Bear cards · 并列 5 条 -->
  <div class="cards">
    <div class="card bull">
      <div class="card-title">Bull 在买什么</div>
      <div class="card-body"><ol><li>...</li> × 5 </ol></div>
    </div>
    <div class="card bear">
      <div class="card-title">Bear 在担心什么</div>
      <div class="card-body"><ol><li>...</li> × 5 </ol></div>
    </div>
  </div>

  <!-- 9. （可选）至多 1 个收尾 note：KR vs JP 弹性比较 / 反叙事 callout -->
  <div class="note-block">
    <span class="kicker">KR vs JP 弹性比较 · ...</span>
    <p>...</p>
  </div>
</section>
```

### **6-block td 关键说明**（v2 新增 · 用户必读两连击）

| Block | 长度 | 内容 |
|---|---|---|
| **核心业务** | 20-40 字 | 国别+主业+行业地位+关键客户/份额 · **纯业务、不写涨幅** |
| **大涨驱动** | 25-55 字 | 公司名+1Y涨幅+具体业务+客户/订单/产品+数字证据 · 一句话讲清"为啥涨成这样" |
| **近期走势** | 80-150 字 | 1M-3M 关键拐点 + catalyst |
| **财报/经营** | 60-120 字 | 最近季度 + next 季度共识 + 业务占比 |
| **产业链/客户** | 60-120 字 | 上下游 ticker 网络 KR↔JP↔US |
| **ki-note** | 100-180 字 | thesis 阶段定位+alpha 类型+催化时点 |

**用户使用路径**：核心业务（公司做啥）→ 大涨驱动（为啥涨）→ 30 秒抓核心 alpha；要深就读 4-block 详细。

### 市值列（USD）规则 · v2.1 独立成列 · **v2.2 加 data-sort-value 修复排序**

⚠ **关键陷阱**：市值列显示 `$1.25T` / `$231B` / `$3.6B` 混用 T/B 单位 · 若列头按字符串排序会把 `$1.01T` 排到 `$3.6B` 之后（字典序 `1` < `3`）—— **必须用 data-sort-value 通用机制**：

```html
<th data-type="num" style="width:4%">市值</th>
...
<td class="num" data-sort-value="1248.2">$1.25T</td>     <!-- 三星 -->
<td class="num" data-sort-value="230.69">$231B</td>      <!-- KIOXIA -->
<td class="num" data-sort-value="3.62">$3.6B</td>        <!-- POWERX -->
```

shell sort JS 已升级（v2.2）：`type === "num"` 时**优先读 `aCell.dataset.sortValue`**、fallback `parseFloat(textContent)`。详见 [[feedback_html_table_sort_value]]。

**单位换算**（写 data-sort-value 时统一到 $B）：
- $X.XT → multiply by 1000 (e.g., `$1.25T` → `1250`)
- $XXXB / $X.XB → 直接用 B 数值
- $XXXM → divide by 1000 (e.g., `$850M` → `0.85`)

**汇率口径**（2026-05 近期合理水平、新一期需检查）：
- USD/KRW = **1370**
- USD/JPY = **155**

**Wind 市值数据单位**：`总市值1` 列在 Wind KR/JP 池中是 **亿 of local currency**（不是万元、不是 base currency）。

**换算公式**：
```python
usd_b = mcap_local_亿 * 1e8 / FX / 1e9   # FX = 1370 KR / 155 JP
```

**显示格式分档**：
- ≥ $1T → `$X.XT`（如 `$1.25T`）
- $100-999B → `$XXXB`（如 `$231B`）
- $10-99B → `$XXB`（如 `$34B`）
- $1-9.9B → `$X.XB`（如 `$3.6B`）
- < $1B → `$XXXM`（罕见）

**禁止内容**：
- ❌ 本币（`₩X.X万亿` / `¥X.X万亿`）
- ❌ 交易所后缀（` · TSE Prime` / ` · KOSPI` / ` · KOSDAQ` / ` · KRX`）
- ✅ 只显示 USD（如 `$1.25T`）

### 归因 tag 清单（11 个）

| Tag | 含义 |
|---|---|
| `t-er` / `t-er-miss` | 财报 beat / miss |
| `t-cat` | 催化（产品/合同/订单/M&A） |
| `t-map-d` / `t-map-i` / `t-map-s` | 直接/间接/情绪映射 |
| `t-guide-cut` | 指引下修 |
| `t-rot` | 板块轮动 |
| `t-fx` | **汇率联动**（KRW/JPY 波动）· 日韩独有 |
| `t-policy` | **BOK/BOJ 政策**（韩国 Value-Up / 日本 GX 等）· 日韩独有 |
| `t-none` | 无 |

每标的挂 1-3 个 tag。

### Phase A · masthead agent

masthead agent（Opus）输出：
- Eyebrow（`KOREA & JAPAN MOMENTUM · YYYY / MM / DD · ISSUE #N`）
- Title（两行 Cormorant + `<em>` amber 高亮关键词）
- Description（200-280 字、强调 momentum snapshot 非 weekly 事件型）
- Pills × 6-10
- `<nav class="view-tabs">` · 3 档全部/韩股/日股 · 显示池子规模数字

---

## Phase A.5 · 后处理批量脚本（10-15 min · 主 Claude 直接做）

**v2 教训**：agent 写 fragment 时，市值小字 / 1M/3M/6M/1Y 数字 / 核心业务 / 大涨驱动 等会有偏差。整合前用 Python BeautifulSoup 批量重写权威字段。

### 后处理脚本清单

| 脚本 | 作用 | 输入 |
|---|---|---|
| `_inject_returns.py`（标准化数字列）| 从 phase 0 facts 重写 1M/3M/6M/1Y 4 列数据 | xlsx 数据 |
| `_inject_usd_mcap.py`（USD 换算）| 把本币小字替换为 USD + 删交易所后缀 | xlsx 数据 + FX |
| `_inject_business.py`（核心业务一句话）| 在每个 td 顶部注入「核心业务」 | agent JSON 输出 |
| `_inject_drivers.py`（大涨驱动一句话）| 在「核心业务」后注入「大涨驱动」 | agent JSON 输出 |

**实际工作流**：
1. 11 agent 写完主线 fragment（含表格 + 6-block td）
2. 跑 `_inject_returns.py` —— 用 xlsx 数据强制覆盖所有数字列（防 agent 写错列名）
3. 跑 `_inject_usd_mcap.py` —— 本币 → USD + 删交易所后缀
4. （若 agent 没写 核心业务 / 大涨驱动）spawn 10 agent 写 JSON、跑 `_inject_business.py` + `_inject_drivers.py`
5. 整合脚本拼合 fragments

⚠ **更优实践（v2 起）**：在 Phase A agent prompt 里直接要求写完整 6-block td、跳过 _inject_business / _inject_drivers。仅保留 `_inject_returns.py` + `_inject_usd_mcap.py` 作为权威数据强制层。

---

## Phase B · §01 + §12 + §13（15-25 min · 3 Opus agent 并行 · 依赖 Phase A · 可选）

⚠ Phase B 必须等 Phase A 完成后再启动。

### §01 Exec Summary（必做）

| Block | 内容 |
|---|---|
| Block 1 · 两国大盘 strip | KOSPI / KOSDAQ / TOPIX / N225 · 1W / 1M / 1Y 三视角 |
| Block 2 · 行业热度透视 | 16 个 Wind L2 行业 8×2 grid · 按 6M 降序 · 反叙事行业（如软件服务 1Y 负）双 class 高亮 |
| Block 3 · §1 take-away | 250-350 字连贯叙事 · 回答 3 问（池子画像 / 决定性产业变化 / 反叙事监控）|
| Block 4 · §2 核心信号 | 5 个 note-block · **每个 ≥280–400 字、五维讲透**（见下方〈核心信号丰富度规范〉）|
| Block 5 · §3 主线优先级 | 10 主线 9 列表 · 按本期 momentum 强度排序 |

#### 核心信号丰富度规范（🔴 260615 固化 · 下次必遵守，不可退回单薄版）

每个核心信号 `note-block` **不少于 280–400 字（中文）**，可拆 2–3 个 `<p>`，必须把以下五维讲透——单薄的「一句 What + 一句 Why」是 FAIL：

1. **逻辑链条**：本周这条主线为什么走出这个走势——明确 Bull/Bear 阶段定位 + 本周性质（资金轮动 / 获利了结 / 真拐点，三选一并说清）。开头 1–2 句点出。
2. **产业链最新变化**：用 **订单 / 价格 / 库存 / capex 四维度** 的具体信号支撑——合约价涨幅、交期、份额、产能利用率/稼动率、缺口年份、月营收创高等，**带数字**。
3. **相关上市公司最新变化**：点名 **3–5 家代表公司** + 各自最新经营动态 + 本周涨跌幅（关键数字用 `<span class="hl">…</span>` 高亮）。
4. **财报重点**：若正文有财报，**必须明确写出营收 / 营利 / 净利 / 指引的 YoY 或 QoQ 具体数字并重点讲**；正文无财报数字的公司不硬写财报。
5. **反叙事 / 分界**：结尾给一句**可观察的产业信号分界**（「轮动升级为拐点的分界 = …」），**只用产业信号、禁价格信号**（Bull Logic 下出场只能用产业拐点）。

硬约束：① **所有数字必须能在正文 theme sections 找到出处**——不脑补、不编造新财报/订单/涨跌幅；② 不引入数据快照日之后的新闻（保持周快照一致）；③ 保持 `note-block` + `kicker` + `<p>` HTML 结构，`<strong>` 强调、`<em>` 标分界条件。

### §12 Cross-market Signals（可选 · 复杂的可放 v2.x）

KR↔JP 上下游联动表：HBM 链 / BOM 链 / 电力链 / 核电链 / 机器人链。

### §13 Final Read（可选）

250-350 字市场结构 take-away + 下周 catalyst 时间线表 + A 股映射指引 + 监控信号。

---

## Phase C · Integrate + Push（10-15 min · 主 Claude 直接做）

> ⚠ **整合后强制闸门（260606 教训 · 不可跳过）**：写出最终 HTML 后必跑 class 存在性检查
> `python D:\claude\research\templates\_check_classes.py 日韩周报\日韩周报_YYMMDD.html`
> ——报告正文用到的每个 class 必须在复用的 shell（含注入 override）里真实定义，否则渲染成裸 div。
> 此 shell **没有** `.gate` / `.no-filter`，用到时整合脚本必须注入 override（`.note-block.gate` 渐变 +
> `body[data-view] table.dt.no-filter tbody tr{display:table-row!important}`，否则 §01 表在 kr/jp 视图被隐藏）。
> 验证截图要覆盖 masthead / heat-strip / 主表 / cards / note-block / exec / final 每一种区块，不能只截开头。
> 详见 memory [[feedback_shell_class_gate]]。`_build.py` / `_integrate.py` 已自动调用此闸门。


```python
# 整合脚本核心
shell = Path("templates/jp_kr_weekly_shell.html").read_text(encoding="utf-8")
fragments = sorted(Path("_fragments/YYMMDD/").glob("*.html"))
body = "\n\n".join(f.read_text(encoding="utf-8") for f in fragments)
out = shell.replace("<!--FRAGMENTS_INSERT_HERE-->", body)
out = out.replace("{{YYYY-MM-DD}}", "YYYY-MM-DD")
out = out.replace("{{REPORT_TITLE}}", "日韩周报")
out = re.sub(r"\{\{N\}\} STOCKS", f"{n_total} STOCKS", out)
out = re.sub(r"\{\{N\}\} THEMES", f"{n_themes} THEMES", out)
out = re.sub(r"\{\{N\}\} KR", f"{n_kr} KR", out)
out = re.sub(r"\{\{N\}\} JP", f"{n_jp} JP", out)
Path("日韩周报_YYMMDD.html").write_text(out, encoding="utf-8")
```

git push:
```bash
cd /d/claude/research
git add "日韩周报/日韩周报_YYMMDD.html"
git commit -m "..."
git push origin main
```

---

## Phase D · index.html 卡片 + 发布（5 min）

1. 编辑 `D:\claude\research\index.html`：新增 `<a class="report-card" data-category="a-share">` 卡片到 report-grid 顶部（日韩沿用 a-share 红色类；台股用 us-equity 紫色类）
   - ⚠ **`.card-desc` 只写核心一句话**（≤35 字、点出本期主旨即可，不堆数字/标的清单）——260606 用户固化要求
2. 更新 sidebar `<div class="sb-recent-item">` 置顶本周
3. `total-count` +1
4. `git add index.html && git commit && git push`

GitHub Pages 1-2 min 同步：https://coderz66.github.io/research/日韩周报/日韩周报_YYMMDD.html

---

## 时间预算

| Phase | 任务 | 耗时 |
|---|---|---|
| Phase 0 | 接数据 + 主题分类 + AskUserQuestion + WebSearch | 15-30 min |
| Phase A | 11 Opus agent 并行（10 主线 + masthead） | 45-60 min |
| Phase A.5 | 后处理批量脚本（USD/数字列） | 10-15 min |
| Phase B | §01 + §12 + §13（可选 3 agent） | 15-25 min |
| Phase C | integrate + push | 10-15 min |
| Phase D | index 卡片 + 发布 | 5 min |
| **Total** | | **~100-150 min** |

---

## 主线 fragment 写作禁忌

❌ **绝对禁止**：
- "出场信号 / 仓位管理 / 减仓 X / 加仓 X / 建议持有 N 个月 / 注意控制仓位" trader 操作语言
- "注意风险 / 投资有风险 / 仅供参考 / 短期波动 / 可能回调" 风险套话
- "technical rebound / resistance break / oversold / 涨多了 / 技术破位" 价格信号
- 按国别 / 方向 / 市值拆多表（必须单表 + data-country）
- 小数百分比（"+5.67%"），必须整数（"+6%"）
- **本币市值**（`₩X.X万亿` / `¥X.X万亿`）或**交易所标签**（`TSE Prime` / `KOSPI`）—— 都换 USD
- 用美股周报"Beta 校准 / P80 by tier"概念（日韩没接 DB / 没 ETF 基准）
- **凭训练数据写 KR/JP ticker**（必须 WebSearch 验证、上市状态变化频繁）
- 1W 列（KR/JP Wind xlsx 通常无 1W、不要硬凑）

✅ **必做**：
- 整数百分比 + 符号
- 关键数字 `<span class="hl">` 高亮
- 关键词 `<em>...</em>` amber 斜体
- ticker 格式统一：KR `XXXXXX.KS / XXXXXX.KQ` · JP `XXXX.T`
- **6-block td 结构齐全**（核心业务 / 大涨驱动 / 近期走势 / 财报经营 / 产业链客户 / ki-note）
- KR ↔ JP 跨市场映射主动提示
- 妖股标 `t-map-s`，不用估值否定
- 公司列小字：**USD 市值唯一**（如 `$1.01T`）

---

## v2.2 改造日志（260526 · 当日修订）

- 市值列原 data-type="text"、点列头排序走字典序（`$1.01T` < `$3.6B` 错排）
- 修复：每行加 `data-sort-value` 属性存底层 $B 数值（如 三星 `$1.25T` → `data-sort-value="1248.2"`）
- 列头 data-type text → num
- shell 全局 sort JS 升级：优先读 dataset.sortValue、fallback parseFloat(textContent)
- **首次点击方向（v2.2 同期加）**：num 列默认 desc（top movers / top mcap 优先）、text 列默认 asc
- **通用机制**：所有 `display ≠ sort 值`的列都可复用此模式（详见 [[feedback_html_table_sort_value]]）

## v2.1 改造日志（260526）

- 市值小字（原在公司列 `<br>` 后 `<span>` 内）→ **独立成列**
- 公司列宽 8% → 4%（缩半）
- 新增市值列 4%
- 表格从 8 列 → 9 列
- 公司列只保留公司名（无 br / span）

## v2 改造日志（260525 实证后固化）

### 从 v1 到 v2 的关键变更

1. **td 4-block → 6-block**：新增「核心业务」「大涨驱动」两条用户必读一句话，作为快速 scan 入口
2. **表格 9 列 → 8 列**：删除国别列、`data-country` 改写为 `<tr>` 属性、视图过滤功能不变
3. **市值小字本币 → USD**：USD/KRW=1370 · USD/JPY=155、显示格式 $X.XT / $XXXB / $X.XB
4. **删交易所后缀**：不写 TSE Prime / KOSPI / KOSDAQ / KRX
5. **列宽固化**：Ticker 6% / 公司 8% / 1M 4% / 3M 4% / 6M 4% / 1Y 4% / 归因 4% / 个股逻辑 66%
6. **Phase A.5 新增**：批量后处理脚本层（_inject_returns + _inject_usd_mcap 强制覆盖权威字段）
7. **xlsx 列识别**：注意 Wind `所属Wind行业名称(2024)`+`.1`+`.2` 实际是 L3+L1+L2 三级、不是 L1+L2+L3
8. **Phase A agent prompt 字符要求**：核心业务 20-40 字 / 大涨驱动 25-55 字 / 4-block 各 60-180 字 / ki-note 100-180 字

### 260525 实证踩坑（已固化）

- 13_theme04_power_grid agent 误写「1W/1M/3M」列、与其它 fragment 不一致 → v2 强制 4 列 1M/3M/6M/1Y
- 三星 mcap 解读错单位（Wind `总市值1` 是 亿 不是 万元）→ v2 明确单位
- 6526.T 索喜科技 + 034220.KS 乐金显示 主线分配遗漏 → v2 强制 Phase 0.2 校验 N_assigned == N_pool
- agent 凭记忆写日韩 ticker 容易过时（KR 6 位 vs 4 位、JP 4 位、新 IPO） → v2 强制 WebSearch 验证

### 待完善（v3 候选）

- §12 Cross-market Signals 标准模板（v2 还没固化）
- §13 Final Read 标准模板（v2 还没固化）
- 直接让 agent 在 Phase A 一次写完 6-block td（跳过 Phase A.5 inject 步骤）
- 数据 pipeline 化（不再走 xlsx、接 KRX/JPX API 或 TickFlow KR/JP）

---

## 触发关键词

用户说以下任一关键词 → 默认进入本周报工作流：
- "日韩周报"、"韩股周报"、"日股周报"、"韩日周报"、"KR JP weekly"

⚠ 不明确时（如"看下日韩这周"）→ 主 Claude 自己判断 + 直接执行，不询问。

---

*最后更新：2026-05-26 · v2 基于 日韩周报_260525.html 实证固化*
