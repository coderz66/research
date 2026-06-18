# 台股周报工作流（v2.5 · 260526 修订）

> 84 标的 multi-window 位势复盘 · 6 主线 + 反叙事观察 · 9 段结构
> 与日韩周报 / 美股周报 / A 股周报 / A 股映射全部独立

---

## 触发方式

用户说：
- "台股周报" / "台股周度" / "台股复盘"
- "TW weekly"
- 同目录提供 xlsx 文件（Wind/iFind 导出）

→ 进入本工作流 `D:\claude\research\台股周报\` + 加载 `templates/tw_weekly_prompt.md`。

---

## 数据流（v1 · 用户提供 xlsx · 无 pipeline）

```
用户提供 xlsx（Wind 84 标的 + 4 窗口）
       ↓
Phase 0 主 Claude 读 xlsx → _phase0_taiwan_YYMMDD.md（主线分配 + ticker 清单）
       ↓
Phase 0 AskUserQuestion 确认（主线粒度 / 窗口列数 / 视图档）
       ↓
Phase 1 6 Opus agent fan-out（§02-§07 主线 fragment）+ 1 Opus agent（§08 反叙事）
       ↓
Phase 2 主 Claude 写 §00 masthead / §01 exec summary / §09 final read
       ↓
Phase 3 主 Claude 后处理：
         · scripts/_inject_business_driver.py 给 66 只股加 "核心业务" + "大涨驱动" 两段
         · scripts/_integrate.py normalize thead + section id + 清 html/body + 拼接 shell
       ↓
Phase 4 git add / commit / push → coderz66/research → GitHub Pages
```

---

## 章节结构（9 段 · 顺序固定）

| § | 文件 | 写作者 | 内容 |
|---|---|---|---|
| §00 | `00_masthead.html` | 主 Claude | navy/amber masthead + 7 个主线 pills + 3 档视图 tab |
| §01 | `09_exec_summary.html` | 主 Claude | 6 主线一句话表 + 5 核心信号 + 主线优先级 |
| §02 | `10_theme01_ai_compute.html` | Opus agent #1 | AI 算力中枢（TSMC + ASIC + 封测）|
| §03 | `11_theme02_substrate.html` | Opus agent #2 | AI 板材链（ABF + 高速 PCB + CCL）|
| §04 | `12_theme03_server.html` | Opus agent #3 | AI 服务器（ODM + 网通 + 电源 + 线束）|
| §05 | `13_theme04_backend.html` | Opus agent #4 | AI 后段（封测 + 测试 + 探针 + 散热 + 厂房）|
| §06 | `14_theme05_memory.html` | Opus agent #5 | 存储循环（DRAM/NAND/NOR/MCU + IC 设计）|
| §07 | `15_theme06_mlcc.html` | Opus agent #6 | MLCC + 被动元件 |
| §08 | `16_theme07_counter.html` | Opus agent #7 | 反叙事观察（高位回调 + AI 链外溢 + 防守）|
| §09 | `90_final_read.html` | 主 Claude | 综合判断 + 跨主线联动 + 未来 30-60 天 catalyst |

> 🔴 **§01 核心信号丰富度（260615 固化）**：5 个核心信号 note-block **每个 ≥280–400 字、五维讲透**——① 逻辑链条（Bull/Bear 阶段 + 本周是轮动/获利了结/拐点，如 GB200→GB300 转换）② 产业链最新变化（订单/价格/库存/capex 四维带数字）③ 相关公司最新变化（点名 3-5 家 + 本周涨跌幅 hl 高亮）④ 财报重点（有则写月营收/营利/净利 YoY/QoQ 具体数字、无则不硬写）⑤ 反叙事/分界（只用产业信号、禁价格信号），**并保留每条末尾的「A 股对应」句**。所有数字必须正文 theme sections 可溯源、不脑补、不引入快照日后新闻；台股红涨绿跌。完整规范见 `templates\tw_weekly_prompt.md` 的〈核心信号丰富度规范〉。单薄的「一句 What + 一句 Why」是 FAIL。

**按文件名升序拼接 = 正确顺序。**

---

## 与其他周报的核心差异

| 维度 | 美股 | 日韩 | **台股** |
|---|---|---|---|
| Beta 基准 | 25 ETF β strip | 无（两国大盘） | **无**（xlsx 无 1W） |
| 市值分档 | 5 档 mcap_tier | data-country=kr/jp | **3 档：L≥$30B / S<$30B / all** |
| 时间窗口 | 1W + DB | 1W + xlsx | **1M/3M/6M/1Y 四窗口、无 1W** |
| 数据 pipeline | DB + 三道门 | xlsx | xlsx |
| 主表列数 | 8 列 | 8 列 | **9 列**（v2.7 · 加独立市值($B) 列 · 删市值档列、data-cap 仍在 tr 上）|
| td 内结构 | 一句话业务定位 | 4-block | **6-block**（v2.5 加核心业务 + 大涨驱动）|
| 跨市场映射 | A 股映射 | KR↔JP | A 股映射指引（§09 末尾）|
| Shell | 独立 | 独立 | **复用 us_weekly_shell.html** + override |

---

## 标准 td 结构（v2.5 · 6-block · 在 65% 宽的逻辑列内）

每只股的最后一列（"关键产业事实+个股逻辑" · 65% 宽 v2.7）：

```html
<strong style="color:var(--accent)">核心业务</strong>：[公司做什么 · 20-40 字]<br/>
<strong style="color:var(--accent)">大涨驱动</strong>：[为啥涨 · 25-55 字]<br/>
<strong>近期走势 / 本周边际变化</strong>：[80-150 字 · 本期叙事 + 具体数字]<br/>
<strong>财报</strong>：[60-120 字 · 已报数字 + 即将报 + 共识]<br/>
<strong>产业链</strong>：[60-120 字 · 上下游 ticker 网络 + 客户结构]
<span class="ki-note">[100-180 字 · 归因 + alpha 类型 + thesis 阶段 + catalyst]</span>
```

**核心业务 / 大涨驱动** 由主 Claude 后处理统一注入（`scripts/_inject_business_driver.py`），agent 只写后 4 段。

---

## 主表 9 列标准（v2.7 · 固定列宽合 100%）

| 列 | 宽 | data-type |
|---|---|---|
| Ticker | 6% | text |
| 公司 | 4% | text |
| 市值($B) | 5% | num |
| 1M | 4% | num |
| 3M | 4% | num |
| 6M | 4% | num |
| 1Y | 4% | num |
| 归因 | 4% | text |
| 关键产业事实 + 个股逻辑 | **65%** | text |

**v2.6 → v2.7**：删"市值档"列（4%），让给逻辑列（61→65%）。`data-cap="L"/"S"` 仍在 `<tr>` 属性上用于 view 筛选——只是不在表格里显示这一列。逻辑列拿到最大空间。

详见 `templates/tw_weekly_prompt.md` §C-PRIME 标准结构。

---

## 目录结构

```
D:\claude\research\台股周报\
├── README.md                          ← 本文件
├── 台股YYMMDD.xlsx                    ← 用户提供输入
├── 台股周报_YYMMDD.html                ← 最终产物
├── _phase0_taiwan_YYMMDD.md            ← 每期 Phase 0 数据 + 主线分配
├── _phase0_taiwan_data.csv             ← 每期 CSV
├── _fragments/
│   └── YYMMDD/                         ← 每期一个子目录
│       ├── 00_masthead.html
│       ├── 09_exec_summary.html
│       ├── 10_theme01_*.html ~ 15_theme06_*.html
│       ├── 16_theme07_counter.html
│       └── 90_final_read.html
└── scripts/
    ├── _integrate.py                   ← 整合脚本（normalize + 拼接 shell）
    └── _inject_business_driver.py      ← 后处理：注入 66 只股核心业务 + 大涨驱动
```

---

## 时间预算

| Phase | 内容 | 耗时 |
|---|---|---|
| Phase 0 | 读 xlsx + 主线分配 + Phase 0 doc | 10-15 min |
| Phase 1 | 7 Opus agent fan-out（6 主线 + 反叙事）| 10-15 min |
| Phase 2 | 主 Claude 写 §00/§01/§09 | 8-12 min |
| Phase 3 | 注入 + 整合 + 验证 | 5-10 min |
| Phase 4 | git push | 1-2 min |
| **总计** | | **35-55 min**（v2.5 优化后） |

---

## 关键经验沉淀（v1→v2.6 迭代）

| 版本 | 修订 | 核心教训 |
|---|---|---|
| **v1** | 复用美股 shell + 自写省略 prompt | 信息密度太低、ki-note 23 个、用户反馈"3 倍差距" |
| **v2** | 参照日韩 §C-PRIME 9 步 + 强约束 prompt | ki-note 68、字节 245K · 0 自创 class · §05 漏 3653 健策 |
| **v2.1** | normalize thead 统一 9 列 | 6 agent 3/6 缺市值档列 + 列宽 7 种组合 |
| **v2.2** | 加"大涨驱动"一句话 | 用户必读、最快抓核心 alpha |
| **v2.3** | 归因列 8→4%、逻辑列 59→63% | 归因 tag 只占 1-3 个空间够用 |
| **v2.4** | 大涨驱动加业务前缀（单 strong）| 让陌生 ticker 也能秒懂主线归属 |
| **v2.5** | 拆为核心业务 + 大涨驱动两 strong | 视觉更清晰、扫读更快、字数加长 |
| **v2.6** | 市值($B)独立成列、公司列 7→4% | agent 写法不一致（"$XXX B"/"NT$X 万亿"），独立列统一从 CSV 拿 USD 数字 |
| **v2.7** | 删市值档列、逻辑列 61→65% | 市值数字独立列+视图 tab 已足够，市值档列冗余；逻辑列拿到最大空间 |
| **v2.8** | shell 数字列首次点击默认 desc | 市值/涨跌幅扫读 99% 场景是看 top winners/losers · num=desc / text=asc · 美股周报同步受益 |

**关键规则**：
1. **Shell 复用没问题，但 td 内信息密度 paradigm 从日韩拿，不要从美股拿**
2. **fan-out 后必须 cross-check ticker 数**——v1 漏 3653 健策最大单股异动
3. **thead 必须强制 normalize**——agent 不会严格遵守列宽 prompt，Python 整段替换更稳
4. **核心业务 + 大涨驱动由主 Claude 注入**——不交给 agent 写，统一字数 + 风格

---

## 触发新一期的最小指令

> "用 D:\claude\research\台股周报\台股YYMMDD.xlsx 跑台股周报"

主 Claude 自动：
1. 读 xlsx → Phase 0 → AskUserQuestion 确认（生成 `_phase0_taiwan_YYMMDD.md` + `_phase0_taiwan_data.csv`）
2. fan-out 7 agent（agent 写 td.name 只写公司名、不写市值小字）
3. 写 §00/§01/§09
4. 跑 scripts 注入 + 整合：
   ```
   cp scripts/stocks_data_260525.py scripts/stocks_data_YYMMDD.py  # 改本期内容
   bash 内 inline EOF heredoc 跑 _inject_business_driver.py（注入核心业务+大涨驱动）
   bash 内 inline EOF heredoc 跑 _inject_mcap_column.py（注入独立市值列）
   bash 内 inline EOF heredoc 跑整合逻辑（normalize thead+清外层+拼接 shell）
   ```
5. push GitHub

### ⚠ Windows cmd 跑脚本编码限制

中文路径 `台股周报\` 下直接 `python scripts/xxx.py` 会因 cmd GBK 编码触发
`SyntaxError: 'unicodeescape' codec can't decode bytes`。

解决方案（按优先级）：
1. **推荐**：主 Claude 用 bash inline `python << EOF...EOF` heredoc 跑（编码无忧）
2. 若必须文件式调用，从 ASCII cwd（如 `D:/claude/`）用绝对路径 + `python -X utf8 ...`
3. 或临时把脚本 cp 到 ASCII 路径（如 `D:/tmp/`）跑完删

---

*创建：2026-05-26 · v2.5 首版固化*
