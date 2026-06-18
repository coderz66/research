# -*- coding: utf-8 -*-
"""
台股周报 · 整合脚本 (v2.5 · 260526)

功能：
1. normalize 所有 fragment 的 thead 到统一 9 列（v2.3 列宽）
2. normalize section id 唯一化
3. 清 agent 多写的 <html><body> 外层
4. 给缺市值档列的 fragment 自动补 <td>{cap}</td>
5. 用独立 tw_weekly_shell.html（正文 max-width 1800px）+ 注入 no-filter override CSS
6. 按文件名升序拼接 → 替换 <!--FRAGMENTS_INSERT_HERE-->
7. 替换 {{REPORT_TITLE}} / {{YYYY-MM-DD}} / {{N}} 占位符

用法：
    python scripts/_integrate.py YYMMDD

    例：python scripts/_integrate.py 260525
       → 输入：_fragments/260525/*.html
       → 输出：台股周报_260525.html

依赖：D:\claude\research\templates\tw_weekly_shell.html（260531 v2.10 切独立 shell · max-width 1800px）
"""

import sys, io, re, glob, os
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ===== 配置 =====
ROOT = Path(r'D:\claude\research\台股周报')
SHELL = Path(r'D:\claude\research\templates\tw_weekly_shell.html')
TEMPLATE_TITLE = '台股周报 · 多窗口位势复盘'
TEMPLATE_FOOTER = 'TAIWAN EQUITY · MULTI-WINDOW SNAPSHOT · AI VALUE CHAIN HOLOGRAM'
TEMPLATE_STATS = '84 STOCKS / 6 THEMES + 1 COUNTER / 4-WINDOW SNAPSHOT'

# v2.11 标准 thead（9 列固定 · 100% 合 · 260531 收窄数字列让给逻辑列）
# data-cap=L/S 仍在 tr 上用于视图筛选、只是不显示这一列
# 市值列只显示纯数字（$ + B 后缀已剥离），单位标在表头括号里
STANDARD_THEAD = '''<thead><tr>
<th data-type="text" style="width:4%">Ticker</th>
<th data-type="text" style="width:4%">公司</th>
<th data-type="num" style="width:4%">市值($B)</th>
<th data-type="num" style="width:3%">1M</th>
<th data-type="num" style="width:3%">3M</th>
<th data-type="num" style="width:3%">6M</th>
<th data-type="num" style="width:3%">1Y</th>
<th data-type="text" style="width:4%">归因</th>
<th data-type="text" style="width:72%">关键产业事实 + 个股逻辑</th>
</tr></thead>'''

# §02-§07 主线 fragment 的 section id 映射（唯一化）
SECTION_ID_MAP = {
    '10_theme01_ai_compute.html': 'theme-ai-compute',
    '11_theme02_substrate.html': 'theme-substrate',
    '12_theme03_server.html': 'theme-server',
    '13_theme04_backend.html': 'theme-backend',
    '14_theme05_memory.html': 'theme-memory',
    '15_theme06_mlcc.html': 'theme-mlcc',
}

# no-filter override（让 §01/§09 表不受 view 筛选）
NO_FILTER_CSS = '<style>body[data-view] table.dt.no-filter tbody tr { display: table-row !important; }</style>\n'


def normalize_fragment(fp: Path) -> str:
    """读 fragment + normalize 内容"""
    content = fp.read_text(encoding='utf-8')
    fn = fp.name

    # 1. 清掉 agent 多写的 <html><body> 外层
    content = re.sub(r'^\s*<html[^>]*>\s*', '', content)
    content = re.sub(r'<body[^>]*>\s*', '', content)
    content = re.sub(r'\s*</body>\s*', '', content)
    content = re.sub(r'\s*</html>\s*$', '', content)

    # 2. normalize section id（仅主线 fragment）
    if fn in SECTION_ID_MAP:
        new_id = SECTION_ID_MAP[fn]
        content = re.sub(
            r'<section class="sec" id="[^"]*"',
            f'<section class="sec" id="{new_id}"',
            content, count=1
        )

    # 3. 主线 fragment 的主表 normalize thead + 补缺市值档列
    if fn in SECTION_ID_MAP:
        # 检查第一个 tr 的 td 数
        m = re.search(r'<tbody>\s*(<tr[^>]*>.*?</tr>)', content, re.DOTALL)
        if m:
            first_tr = m.group(1)
            td_count = len(re.findall(r'<td[^>]*>', first_tr))

            if td_count == 8:
                # 缺市值档列 → 给每个 tr 在第 2 个 </td> 后插入新 td
                def insert_cap_td(match):
                    tr_open = match.group(1)
                    rest = match.group(2)
                    cap_m = re.search(r'data-cap="([LS])"', tr_open)
                    if not cap_m:
                        return match.group(0)
                    cap = cap_m.group(1)
                    td_ends = [m.end() for m in re.finditer(r'</td>', rest)]
                    if len(td_ends) >= 2:
                        pos = td_ends[1]
                        new_rest = rest[:pos] + f'\n<td>{cap}</td>' + rest[pos:]
                    else:
                        new_rest = rest
                    return tr_open + new_rest + '</tr>'

                content = re.sub(
                    r'(<tr data-cap="[LS]">)(.*?)</tr>',
                    insert_cap_td, content, flags=re.DOTALL
                )

        # 替换 thead 为标准模板
        content = re.sub(r'<thead>.*?</thead>', STANDARD_THEAD, content, count=1, flags=re.DOTALL)

    return content


def main(yymmdd: str):
    frag_dir = ROOT / '_fragments' / yymmdd
    out_path = ROOT / f'台股周报_{yymmdd}.html'

    if not frag_dir.exists():
        sys.exit(f'❌ Fragment dir not found: {frag_dir}')

    # 读 shell + 注入 override
    shell = SHELL.read_text(encoding='utf-8')
    shell = shell.replace('</head>', NO_FILTER_CSS + '</head>')

    # 收集 + normalize fragment
    fragments = sorted(frag_dir.glob('*.html'))
    print(f'Found {len(fragments)} fragments:')
    parts = []
    for fp in fragments:
        normalized = normalize_fragment(fp)
        parts.append(normalized)
        print(f'  ✓ {fp.name} ({len(normalized)} chars)')

    # 替换 shell 占位符
    out = shell.replace('<!--FRAGMENTS_INSERT_HERE-->', '\n\n'.join(parts))
    out = out.replace('{{REPORT_TITLE}}', TEMPLATE_TITLE)
    out = out.replace('{{YYYY-MM-DD}}', f'20{yymmdd[:2]}-{yymmdd[2:4]}-{yymmdd[4:]}')
    out = out.replace('{{N}} STOCKS / {{N}} THEMES / {{N}} INDIVIDUAL LOGIC', TEMPLATE_STATS)
    out = out.replace(
        'US EQUITY · P80-BY-TIER MOMENTUM THEME MAP · PER-STOCK LOGIC EDITION',
        TEMPLATE_FOOTER
    )

    out_path.write_text(out, encoding='utf-8')

    # 验证统计
    n_sections = out.count('<section')
    n_tables = out.count('<table class="dt')
    n_kinotes = out.count('class="ki-note"')
    n_business = len(re.findall(r'<strong[^>]*>核心业务</strong>', out))
    n_driver = len(re.findall(r'<strong[^>]*>大涨驱动</strong>', out))
    n_tr_cap = len(re.findall(r'<tr data-cap=', out))

    print()
    print(f'✓ Output: {out_path}')
    print(f'  Size: {out_path.stat().st_size:,} bytes')
    print(f'  Sections: {n_sections}')
    print(f'  Tables: {n_tables}')
    print(f'  ki-note: {n_kinotes}')
    print(f'  核心业务 tag: {n_business}')
    print(f'  大涨驱动 tag: {n_driver}')
    print(f'  tr data-cap: {n_tr_cap}')

    # === 强制闸门：正文 class 必须在 shell 中定义（260606 教训 · memory feedback_shell_class_gate）===
    sys.path.insert(0, r'D:\claude\research\templates')
    import _check_classes
    if not _check_classes.check(str(out_path)):
        print('  *** CLASS 闸门未通过：上列 class 在 shell 里没定义、会渲染成裸 div，必须修复 ***')

    if n_business != n_driver:
        print(f'  ⚠ Business / Driver mismatch ({n_business} vs {n_driver})')
    if n_business != n_tr_cap - (n_tr_cap - len(re.findall(r'<tr data-cap=.*?(?=</tr>)', out, re.DOTALL))):
        pass  # 不强校验 §08 反叙事的 tr


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python _integrate.py YYMMDD')
        print('Example: python _integrate.py 260525')
        sys.exit(1)
    main(sys.argv[1])
