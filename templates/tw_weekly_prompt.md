# 台股周报 · Standard Prompt (v2.5 · 260526 首版)

> Workflow: `D:\claude\research\台股周报\` · 周度/月度触发 · 总耗时 35-55 min
> 配套 shell: `D:\claude\research\templates\tw_weekly_shell.html`（**独立台股 shell · 不复用美股 us_weekly_shell，避免互相误改** · 已含 max-width:1800px / beta-* / gate / data-cap 视图 · 260606 用户固化）
> 数据输入：**用户提供 xlsx**（Wind/iFind 导出 · 不接 DB pipeline）

---

## ⚠ 写报告前必读

### 必读 memory（按权重排序）
1. [[project_tw_weekly]] — 项目级 SOP + v1→v2.5 迭代经验
2. [[feedback_agent_model_default]] — v4 内容撰写 Opus / 结构性改造 Sonnet
3. [[feedback_no_trader_actions_in_report]] — 禁出场信号 / 仓位管理 / 减仓加仓措辞
4. [[feedback_weekly_fragment_format_consistency]] — 11 条铁律（部分适用）
5. [[project_jp_kr_weekly]] — 信息密度 paradigm 参考（不要从美股拿）
6. CLAUDE.md §4 Trader Framework + §6 周报方法论

### 与其他周报的关键差异

| 维度 | 美股 | 日韩 | **台股** |
|---|---|---|---|
| Beta 基准 | 25 ETF β strip | 两国大盘 | **❌ 无**（xlsx 无 1W）|
| 市值分档 | 5 档 mcap_tier → 4 档视图 | data-country | **3 档：L≥$30B / S<$30B / all**（`data-cap="L"/"S"`）|
| 时间窗口 | 1W + DB | 1W + xlsx | **1M / 3M / 6M / 1Y 四窗口**（无 1W）|
| 主表列数 | 8 列 | 8 列（加国别）| **9 列**（v2.7 · 加独立市值($B) 列 · 删市值档列）|
| td 结构 | 一句话业务定位 | 4-block | **6-block**（加核心业务 + 大涨驱动）|
| 跨市场映射 | §13 A 股映射 | §12 KR↔JP | §09 末尾 A 股映射指引 |

---

## Agent 模型选择规则

按 [[feedback_agent_model_default]] v4：

| 任务性质 | 模型 | 例子 |
|---|---|---|
| **内容撰写** | **Opus 4.7** | 7 agent fan-out（6 主线 + 反叙事）·  §00/§01/§09 |
| **结构性改造** | **Sonnet** | 整合 fragment / normalize / 删 trader actions |

---

## 章节顺序

```
00_masthead.html        ← §00 masthead + view-tabs（all/large/small）
09_exec_summary.html    ← §01 Executive Summary（6 主线表 + 5 核心信号）
10_theme01_*.html       ← §02 主线 1 AI 算力中枢（TSMC+ASIC+封测）
11_theme02_*.html       ← §03 主线 2 AI 板材链（ABF+PCB+CCL）
12_theme03_*.html       ← §04 主线 3 AI 服务器（ODM+网通+电源）
13_theme04_*.html       ← §05 主线 4 AI 后段（封测+测试+散热+厂房）
14_theme05_*.html       ← §06 主线 5 存储循环（DRAM/NAND/IC 设计）
15_theme06_*.html       ← §07 主线 6 MLCC + 被动元件
16_theme07_*.html       ← §08 反叙事观察（高位回调+AI 链外溢+防守）
90_final_read.html      ← §09 综合判断 + 跨主线联动 + 30-60 天 catalyst
```

**按文件名升序拼接 = 正确顺序。**

---

## Phase 0 · 主线分配 + 用户确认（10-15 min）

### Phase 0.1 · 读 xlsx（≤5 min）

xlsx 预期列结构（Wind/iFind）：
- 证券代码（4 位 + .TW 后缀）
- 证券简称
- 所属 Wind 行业名称（2024）× 3 级
- 总市值（亿台币）
- 年成交额（亿台币）
- **近一年 / 近六月 / 近三月 / 近一月**（百分比）

⚠ Wind xlsx 列序是 1Y/6M/3M/1M、不是按时间正序——读取后用 `df.columns = ['ticker','name','wind_l3','wind_l2','wind_l1','mcap_TWD_yi','vol_yr_TWD_yi','ret_1Y','ret_6M','ret_3M','ret_1M']` 显式命名。

台币换 USD 用 **0.033** 比率。

### Phase 0.2 · 主线分配（5-8 min）

按 AI 产业链而非市值切，6 主线 + §08 反叙事覆盖全部 84 标的：

| § | 主线 | 典型标的 | 标的数 |
|---|---|---|---|
| §02 | AI 算力中枢（TSMC + ASIC + 封测）| 2330/2454/3711/2303/3443/3661 | 6-9 |
| §03 | AI 板材链（ABF + 高速 PCB + CCL）| 2383/3037/8046/3189/2368/4958 | 8-12 |
| §04 | AI 服务器（ODM + 网通 + 电源 + 线束）| 2308/2317/2382/6669/2345/3231 | 15-20 |
| §05 | AI 后段（封测 + 测试 + 散热 + 厂房）| 7769/2360/3017/3653/6515/2449/6239 | 12-16 |
| §06 | 存储循环（DRAM/NAND/NOR/MCU + IC 设计）| 2408/2344/2337/4919/3034/2379 | 10-14 |
| §07 | MLCC + 被动元件 | 2327/2492/3026 | 3-5 |
| §08 | 反叙事观察（高位回调 + AI 链外溢 + 防守）| 1M < 0 + 面板 + 化工 + 电信 | 20-30 |

输出 `D:\claude\research\台股周报\_phase0_taiwan_YYMMDD.md` 含每只股归类。

### Phase 0.3 · 一次性 AskUserQuestion 确认

```python
AskUserQuestion(
  question="台股周报 YYMMDD 本期结构确认",
  questions=[
    {"header": "主线粒度", "options": ["6 主线 + 反叙事观察 (Recommended)", "4 主线粗粒度", "8 主线细粒度"]},
    {"header": "时间窗口", "options": ["1M+3M+6M+1Y 四列 (Recommended)", "1M+1Y 双列", "全部四列"]},
    {"header": "视图档", "options": ["3 档：全部/大盘≥$30B/中小盘 (Recommended)", "单视图", "按行业切"]},
  ]
)
```

---

## Phase A · 7 Opus agent fan-out（10-15 min）

### 创建 fragment 目录
`D:\claude\research\台股周报\_fragments\YYMMDD\`

### 每个 agent 收到的标准 prompt 必传

```markdown
你是台股周报 fan-out 的 Opus agent，负责写 §0X 主线 N · [主线名] fragment。

## 标的清单（含 cap / 1M/3M/6M/1Y）
[从 Phase 0 分配的表格中拷贝该主线的标的]

## 必跑 WebSearch（每只股至少 1 次拉具体财报/订单/产能/客户数字）
[列出该主线的 N 个 search query]

## 输出位置
`D:\claude\research\台股周报\_fragments\YYMMDD\1X_themeNN_*.html`

## 硬约束（10 条铁律）

1. **边界**：只输出 `<section class="sec" id="theme-XXX">...</section>`，**禁 `<html><body>` 外层**
2. **章节头三件套**：sec-num / sec-title（含 `<em>`）/ sec-sub ≤30 字 thesis
3. **Bull/Bear note-block 2 段**：① 行业阶段定位 ② 关键 catalyst window
   - **禁出场信号 / 仓位管理**（研究报告 ≠ trader 操作）
4. **4 段标准 kicker**（在 note-block 后表之前）名字严格不变：
   - 本周关键变化 / 财报季分析 / 时间催化 / 订单与产业链
5. **主表 9 列固定**（v2.9 列宽：Ticker 6% / 公司 4% / 市值($B) 5% / 1M 3% / 3M 3% / 6M 3% / 1Y 3% / 归因 4% / 逻辑 69%；v2.9 涨跌幅列 4→3% 收窄、空间给逻辑列 65→69%）；**涨跌幅数字不写 %**（纯整数 + 正负号，如 +6 / -3，节省列宽 + 视觉统一）
6. **每只股 td 4-block**（主 Claude 后处理还会注入核心业务 + 大涨驱动两段、agent 不写）：
   - `<strong>近期走势 / 本周边际变化</strong>` 80-150 字
   - `<strong>财报</strong>` 60-120 字
   - `<strong>产业链</strong>` 60-120 字
   - `<span class="ki-note">归因 + alpha 类型 + thesis 阶段 + catalyst</span>` 100-180 字
7. **Bull/Bear cards 表后并列 · 各 5 条**
8. **归因 tag 仅用 6 个**：t-er / t-cat / t-map-d / t-map-i / t-map-s / t-rot
9. **数字格式**：整数 + `+/-`、无小数、涨用 `class="num pos"`、跌用 `class="num neg"`
10. **禁忌**：
    - 禁套话：注意风险 / 建议关注 / 短期波动 / 控制仓位 / 突破阻力 / 技术面
    - 禁自创 class（严格用 shell 标准 class）
    - 禁拆多张表（一主线一张 9 列表）
```

### §C-PRIME 主线 fragment 标准结构

```html
<section class="sec" id="theme-XXX">
  <!-- 1. 章节头三件套 -->
  <div class="sec-num">§0X · 主线 N</div>
  <h2 class="sec-title">主线名 · <em>关键词</em></h2>
  <p class="sec-sub"><em>≤30 字 thesis</em></p>

  <!-- 2. Bull/Bear note-block 2 段 -->
  <div class="note-block">
    <span class="kicker">Bull Logic · 行业阶段定位</span>
    <p><strong>1. 行业阶段定位</strong>：thesis lifecycle 位置 + 产业基础四维度数字（订单/价格/产能/客户）</p>
    <p><strong>2. 关键 catalyst window</strong>：未来 4-8 周 binary event 时间线</p>
  </div>

  <!-- 3-6. 4 段标准 kicker -->
  <p><span class="kicker">本周关键变化</span>·...</p>
  <p><span class="kicker">财报季分析</span>·...</p>
  <p><span class="kicker">时间催化</span>·...</p>
  <p><span class="kicker">订单与产业链</span>·...</p>

  <!-- 7. 主表 9 列固定（v2.7 · 删市值档列让给逻辑列） -->
  <table class="dt">
    <thead><tr>
      <th data-type="text" style="width:6%">Ticker</th>
      <th data-type="text" style="width:4%">公司</th>
      <th data-type="num" style="width:5%">市值($B)</th>
      <th data-type="num" style="width:3%">1M</th>
      <th data-type="num" style="width:3%">3M</th>
      <th data-type="num" style="width:3%">6M</th>
      <th data-type="num" style="width:3%">1Y</th>
      <th data-type="text" style="width:4%">归因</th>
      <th data-type="text" style="width:69%">关键产业事实 + 个股逻辑</th>
    </tr></thead>
    <tbody>
      <!-- 排序：先 cap=L 后 cap=S、组内按 1Y 降序 -->
      <!-- agent 写时 td.name 只写公司名（中英），不加市值小字 - 主 Claude 后处理用 scripts/_inject_mcap_column.py 注入独立市值列 -->
      <!-- data-cap="L"/"S" 仍在 tr 上用于 view 筛选、不在表格里显示市值档列 -->
      <tr data-cap="L">
        <td class="tk">2330.TW</td>
        <td class="name">台积电 TSMC</td>
        <td class="num">$2195B</td>
        <td class="num pos">+6</td>
        <td class="num pos">+18</td>
        <td class="num pos">+69</td>
        <td class="num pos">+138</td>
        <td><span class="tag t-er">财报</span><span class="tag t-cat">capex</span></td>
        <td>
          <strong>近期走势</strong>：[80-150 字 · 本期 1M 涨跌核心驱动、与同业对比]<br/>
          <strong>财报</strong>：[60-120 字 · 已报最近季报数字 + 即将报 + 共识]<br/>
          <strong>产业链</strong>：[60-120 字 · 上下游 TW↔US↔CN 网络 + 客户结构]
          <span class="ki-note">[100-180 字 · 归因 + alpha 类型(个股 alpha / 产业 beta / 复合) + thesis 阶段 + 关键 catalyst 时间点]</span>
        </td>
      </tr>
      <!-- ... -->
    </tbody>
  </table>

  <!-- 8. Bull/Bear cards 并列各 5 条 -->
  <div class="cards">
    <div class="card bull">
      <div class="card-title">Bull · <em>正在 price in 什么</em></div>
      <div class="card-meta">行业阶段 · 中段/加速段</div>
      <div class="card-body"><ol>
        <li><strong>催化 1</strong>：[具体数字]</li>
        ... × 5
      </ol></div>
    </div>
    <div class="card bear">
      <div class="card-title">Bear · <em>需要警惕什么</em></div>
      <div class="card-meta">反向信号窗口</div>
      <div class="card-body"><ol>
        <li><strong>风险 1</strong>：[可观察信号]</li>
        ... × 5
      </ol></div>
    </div>
  </div>
</section>
```

### 归因 tag 清单（仅 6 个 · 不要自创）

| Tag | 含义 | 颜色 |
|---|---|---|
| `t-er` | 财报驱动（vs estimate + 指引修正）| 绿底 |
| `t-cat` | 催化（订单/产品/政策/价格）| 黄底 |
| `t-map-d` | 直接产业链映射 | 深棕 |
| `t-map-i` | 间接产业链映射 | 浅棕 |
| `t-map-s` | 情绪/概念映射（妖股）| 灰底 |
| `t-rot` | 板块轮动 | 灰底 |

每只股挂 **1-3 个 tag**。

### §08 反叙事观察特殊结构

§08 与 §02-§07 主线表结构不同：
- 不需要 4 段 kicker
- 不需要 Bull/Bear cards
- 2 张简表（A 组：AI 链 1M 回调 / B 组：AI 链外溢 + 防守）
- 每表 8 列：Ticker / 公司 / 类别 / 1M / 3M / 6M / 1Y / 信号
- 每表前 1 段 narrative + 每表后 1 个 ki-note

---

## Phase B · 主 Claude 写 §00 / §01 / §09（8-12 min）

### §00 masthead
- navy/amber 风格、watermark "TAIWAN AI"
- 7 个主线 pills + 数量标记
- 3 档视图 tab：全部 / 大盘 ≥ $30B / 中小盘 < $30B

### §01 Exec Summary
- 6 主线一句话表（含 1M 中位 / 1Y 中位 / 阶段 / 核心 thesis）
- 5 核心信号 note-block — **每个 ≥280–400 字、五维讲透**（见下方〈核心信号丰富度规范〉），末尾保留「A 股对应」句
- 主线优先级 note-block（按 catalyst window 排序）

#### 核心信号丰富度规范（🔴 260615 固化 · 下次必遵守，不可退回单薄版）

每个核心信号 `note-block` **不少于 280–400 字（中文）**，可拆 2–3 个 `<p>`，必须把以下五维讲透——单薄的「一句 What + 一句 Why」是 FAIL：

1. **逻辑链条**：本周这条主线为什么走出这个走势——明确 Bull/Bear 阶段定位 + 本周性质（资金轮动 / 获利了结 / 真拐点，三选一并说清；如 GB200→GB300 平台转换、板块轮动）。开头 1–2 句点出。
2. **产业链最新变化**：用 **订单 / 价格 / 库存 / capex 四维度** 的具体信号支撑——合约价涨幅、交期、份额、产能利用率/稼动率、缺口年份、月营收创高等，**带数字**。
3. **相关上市公司最新变化**：点名 **3–5 家代表公司** + 各自最新经营动态 + 本周涨跌幅（关键数字用 `<span class="hl">…</span>` 高亮）。
4. **财报重点**：若正文有财报，**必须明确写出月营收 / 营利 / 净利 / 指引的 YoY 或 QoQ 具体数字并重点讲**；正文无财报数字的公司不硬写财报。
5. **反叙事 / 分界**：结尾给一句**可观察的产业信号分界**，**只用产业信号、禁价格信号**（Bull Logic 下出场只能用产业拐点）；并**保留每条末尾原有的「A 股对应」句**。

硬约束：① **所有数字必须能在正文 theme sections 找到出处**——不脑补、不编造新财报/订单/涨跌幅；② 不引入数据快照日之后的新闻（保持周快照一致）；③ 台股**红涨绿跌**，措辞注意方向；④ 保持 `note-block` + `kicker` + `<p>` HTML 结构，`<strong>` 强调、`<em>` 标分界条件。

### §09 Final Read
- 综合判断 cards（Bull 整体定位 + Bear 三个反向信号窗口）
- 跨主线联动表（3 个产业链锚点）
- 未来 30-60 天 catalyst 表（5 个可观察变量）
- 数据口径诚实说明 note-block
- A 股映射指引 note-block

---

## Phase C · 后处理（5-10 min）

### Step 1: 注入"核心业务 + 大涨驱动"
主 Claude 跑 `scripts/_inject_business_driver.py`：
- 准备 STOCKS dict 含 66 只股的（business, driver）tuple
- 业务 20-40 字（公司做什么 + 产品矩阵 + 市场地位 + 品牌名）
- 驱动 25-55 字（alpha 催化、含具体数字 / 客户 / 订单 / 价格）
- 用 regex 找到每只股 tr 内的 `<strong>近期走势</strong>` 锚点
- 在锚点前插入 2 个 strong block（核心业务 + 大涨驱动）

### Step 2: 整合到 shell
主 Claude 跑 `scripts/_integrate.py`：
- 读 `templates/tw_weekly_shell.html`（独立台股 shell）
- 注入 no-filter override CSS（让 §01/§09 表不受 view 筛选）
- normalize 所有 fragment 的 thead 到统一 9 列（v2.3 列宽）
- normalize section id 唯一化
- 清掉 agent 多写的 `<html><body>` 外层
- 按文件名升序拼接 fragment → 替换 `<!--FRAGMENTS_INSERT_HERE-->`
- 替换 {{REPORT_TITLE}} / {{YYYY-MM-DD}} / {{N}} 占位符
- 写出 `台股周报_YYMMDD.html`

### Step 3: 验证
- **强制 class 闸门（260606 教训 · 不可跳过）**：写出 HTML 后必跑
  `python D:\claude\research\templates\_check_classes.py 台股周报\台股周报_YYMMDD.html`
  ——正文每个 class 必须在复用 shell（含注入 override）里真实定义，否则裸 div。
  台股 tw_weekly_shell **没有**日韩独有的 `.heat-strip/.heat-grid/.heat-item`——热度条要用 shell 内置的
  `.beta-strip/.beta-grid/.beta-item`（`.bn/.bv/.bd`）。`_integrate.py` 已自动调用此闸门。详见 [[feedback_shell_class_gate]]。
- 浏览器打开 + cross-check：
  - 所有主表都是 9 列（本期若含 1W 则 10 列）
  - 所有 ticker 的 td 都含 "核心业务" + "大涨驱动" 两 strong block
  - 视图切换正常（all/large/small）
  - 数字格式整数无小数
  - **截图覆盖每种区块类型**（masthead / beta-strip / 主表 / cards / note-block / exec / final），不能只截开头

---

## Phase D · index.html 卡片 + git push（2-3 min）

1. 编辑 `D:\claude\research\index.html`：report-grid 顶部新增 `<a class="report-card" data-category="us-equity">` 卡片（台股=us-equity 紫色类）
   - ⚠ **`.card-desc` 只写核心一句话**（≤35 字、点本期主旨，不堆数字/标的清单）——260606 用户固化要求
   - sidebar 置顶本期 + `total-count` +1
2. push：
```bash
cd D:/claude/research
git add "台股周报/台股周报_YYMMDD.html" index.html
git commit -m "台股周报 YYMMDD · [本期主旨]"
git push
```

⚠ **正文宽度**：台股独立 `tw_weekly_shell.html` 已内置 `max-width:1800px`（对齐日韩），无需 override。**绝不复用 us_weekly_shell**（改美股 shell 会误伤美股周报、反之亦然）。

公网：https://coderz66.github.io/research/台股周报/台股周报_YYMMDD.html

---

## 整合 cross-check 必做项

1. **逐主线点名核对 ticker 数**：v1 漏 3653 健策（最大单股异动）的教训
2. **section id 唯一化**：v1 多个 fragment 共用 theme-05
3. **清 `<html><body>` 外层**：agent 多写时用 re.sub 兜底
4. **thead 强制 normalize**：agent prompt 给的列宽示例不是强约束、Python 整段替换更稳
5. **核心业务 + 大涨驱动注入数 = 66**：tag 数对齐 tr 数

---

## 字数预算（v2.5 实证）

| Fragment | 字节 | ki-note | 备注 |
|---|---|---|---|
| §00 masthead | ~1.5 KB | 0 | |
| §01 exec | ~6 KB | 0 | 7 行表 + 5 核心信号 |
| §02 中枢 | ~30 KB | 8 | 8 只股 |
| §03 板材 | ~33 KB | 10 | 10 只股 |
| §04 服务器 | ~50 KB | 19 | 19 只股 · 最长 |
| §05 后段 | ~37 KB | 14 | 14 只股 |
| §06 存储 | ~37 KB | 12 | 12 只股 |
| §07 MLCC | ~21 KB | 3 | 3 只股 · 最深 |
| §08 反叙事 | ~11 KB | 2 | 24 只股 简表 |
| §09 final | ~8 KB | 0 | |
| **合并** | **~245 KB** | **68** | |

vs 日韩周报 291 KB / 100 ki-note 接近水平。

---

*最后更新：2026-05-26 · v2.5*
