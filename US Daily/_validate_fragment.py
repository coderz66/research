"""
_validate_fragment.py — Daily theme fragment 格式校验（v5 格式固化 · 第二道防线）

用法：
    python _validate_fragment.py _fragments/260522/30_ai_storage_dc.html
    python _validate_fragment.py _fragments/260522/  # 扫整个目录

输出：违规清单 + exit code（0 = 全通过、非 0 = 有违规）

校验规则（与 template_美股日报.html 顶部 SOP 同步）：
  1. 不能有 <style> 或 <script> 标签
  2. theme 表格固定 6 列：Ticker | 名称 | L | 日涨跌幅 | 归因 | 关键信息点
  3. 所有 class 必须在白名单（不接受 ticker-cell / cap-badge / driver-tag 等自创类）
  4. 归因 tag class 限定 9 种（t-er / t-er-miss / t-guide-cut / t-cat / t-map-d/i/s / t-none / t-rot / t-macro / t-geo）
  5. L tier 用 tag.l1-l4
  6. 数字精度 1 位小数（+X.X% / -X.X%）
"""
import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ===== 白名单 =====
ALLOWED_CLASSES = {
    # 顶层布局
    'sec', 'sec-num', 'sec-title', 'sec-sub', 'sub-h', 'kicker',
    'masthead', 'h-eyebrow', 'h-title', 'h-desc', 'h-pills', 'pill',
    'grid', 'grid-3', 'grid-4', 'grid-5', 'cell', 'lbl', 'val', 'note',
    'beta-strip', 'beta-grid', 'beta-item', 'bn', 'bv', 'bd', 'footer',
    'cards', 'card', 'card-title', 'card-meta', 'card-body',
    'note-block', 'geo',
    # 表格
    'dt', 'tk', 'name', 'num', 'pos', 'neg', 'mono', 'asc', 'desc',
    # 标签
    'tag', 't-er', 't-er-miss', 't-guide-cut', 't-cat',
    't-map-d', 't-map-i', 't-map-s', 't-none', 't-rot',
    't-macro', 't-geo',
    'l1', 'l2', 'l3', 'l4', 'l5',  # tier
    # ki-note
    'ki-note',
    # 其它
    'hl', 'bull', 'bear', 'flat', 'up', 'dn',
    'theme-strength', 'theme-bar',
    'signal-up', 'signal-down', 'signal-flat',
    'serif',
}

ATTRIBUTION_TAGS = {
    't-er', 't-er-miss', 't-guide-cut', 't-cat',
    't-map-d', 't-map-i', 't-map-s', 't-none', 't-rot',
    't-macro', 't-geo'
}

TIER_TAGS = {'l1', 'l2', 'l3', 'l4', 'l5'}

THEME_THEAD_EXPECTED = ['Ticker', '名称', 'L', '日涨跌幅', '归因', '关键信息点']


def validate(fp: Path) -> list[str]:
    """返回违规消息列表（空 = 全通过）"""
    src = fp.read_text(encoding='utf-8')
    issues = []
    name = fp.name

    # === 规则 1：禁 <style> / <script> ===
    if re.search(r'<style\b', src):
        issues.append(f'[{name}] 含 <style> 标签——fragment 不允许自带 CSS（全局 CSS 在 shell 中）')
    if re.search(r'<script\b', src):
        issues.append(f'[{name}] 含 <script> 标签——fragment 不允许自带 JS')

    # === 规则 2：class 白名单 ===
    all_classes = set()
    for m in re.finditer(r'class="([^"]+)"', src):
        for c in m.group(1).split():
            all_classes.add(c)
    invalid = all_classes - ALLOWED_CLASSES
    # 过滤一些 inline style hack 不算违规
    invalid = {c for c in invalid if not c.startswith('ANCHOR-')}
    if invalid:
        issues.append(f'[{name}] 自创 class（不在白名单）: {sorted(invalid)}')

    # === 规则 3：theme 节表格 6 列 ===
    # 仅校验 theme 节（不是 macro / earnings / forward / exec_summary / theme_map / masthead）
    is_theme = bool(re.search(r'id="theme\d+-tbl"', src))
    if is_theme:
        thead_m = re.search(r'<thead>(.*?)</thead>', src, re.S)
        if thead_m:
            cols = re.findall(r'<th[^>]*>([^<]*)</th>', thead_m.group(1))
            cols = [c.strip() for c in cols]
            if cols != THEME_THEAD_EXPECTED:
                issues.append(f'[{name}] theme 表头不对 · 实际 {cols} · 期望 {THEME_THEAD_EXPECTED}')
        # 检查 tbody 每行 td 数
        tbody_m = re.search(r'<tbody>(.*?)</tbody>', src, re.S)
        if tbody_m:
            for i, tr_m in enumerate(re.finditer(r'<tr[^>]*>(.*?)</tr>', tbody_m.group(1), re.S)):
                td_count = len(re.findall(r'<td\b', tr_m.group(1)))
                if td_count != 6:
                    # 抽 ticker
                    tk = re.search(r'<td class="tk">([^<]+)</td>', tr_m.group(1))
                    tk = tk.group(1) if tk else f'row#{i}'
                    issues.append(f'[{name}] theme 表 {tk} 行 td 数 = {td_count} (期望 6)')

    # === 规则 4：归因 tag 在白名单 ===
    for m in re.finditer(r'<span class="tag\s+([\w-]+)"', src):
        cls = m.group(1)
        if cls not in ATTRIBUTION_TAGS and cls not in TIER_TAGS:
            issues.append(f'[{name}] 未知归因/tier tag class: tag.{cls}')

    # === 规则 5：数字精度 1 位小数 ===
    # 检查 num pos / num neg 内的数字
    for m in re.finditer(r'<td class="num (?:pos|neg)"[^>]*>([+\-−][\d.]+%)</td>', src):
        val = m.group(1)
        # 提取数字部分（去掉 + / - / − / %）
        digits = re.sub(r'[+\-−%]', '', val)
        if '.' not in digits:
            issues.append(f'[{name}] 数字精度不是 1 位小数: {val}（应为整数 + ".X%"）')
        elif len(digits.split('.')[1]) != 1:
            issues.append(f'[{name}] 数字精度不是 1 位小数: {val}')

    return issues


def main():
    if len(sys.argv) < 2:
        print('用法: python _validate_fragment.py <fragment.html | _fragments/YYMMDD/>')
        sys.exit(2)

    target = Path(sys.argv[1])
    if target.is_dir():
        files = sorted(target.glob('*.html'))
    else:
        files = [target]

    total_issues = 0
    for fp in files:
        if not fp.exists():
            print(f'⚠ {fp} 不存在')
            continue
        issues = validate(fp)
        if issues:
            print(f'❌ {fp.name}: {len(issues)} 个违规')
            for i in issues:
                print(f'   {i}')
            total_issues += len(issues)
        else:
            print(f'✓ {fp.name}: 通过')

    print()
    if total_issues == 0:
        print(f'=== 全部通过 ({len(files)} 个文件) ===')
        sys.exit(0)
    else:
        print(f'=== 共 {total_issues} 个违规、{len(files)} 个文件 ===')
        sys.exit(1)


if __name__ == '__main__':
    main()
