"""乘法口诀表 SVG 与练习纸渲染。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import (
    MAX_FACTOR,
    MIN_FACTOR,
    BlankProblem,
    MultTableError,
    check_factor,
)


def _fmt(value: float) -> str:
    return ("%.2f" % value).rstrip("0").rstrip(".")


def _check_cell(cell: int) -> int:
    if isinstance(cell, bool) or not isinstance(cell, int):
        raise MultTableError("格子尺寸必须是整数")
    if cell < 28 or cell > 120:
        raise MultTableError("格子尺寸必须在 28–120 之间")
    return cell


def render_table(cell: int = 46, maximum: int = MAX_FACTOR) -> str:
    """绘制完整的乘法表（含表头）。"""
    _check_cell(cell)
    check_factor(maximum, "最大乘数")
    count = maximum + 1
    width = count * cell
    parts: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="乘法口诀表">' % (width, width, width, width),
        "<title>乘法口诀表</title>",
        '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (width, width),
    ]
    for row in range(count):
        for col in range(count):
            x = col * cell
            y = row * cell
            if row == 0 and col == 0:
                label = "×"
                fill = "#ebf4ff"
                color = "#2b6cb0"
            elif row == 0:
                label = str(col)
                fill = "#ebf4ff"
                color = "#2b6cb0"
            elif col == 0:
                label = str(row)
                fill = "#ebf4ff"
                color = "#2b6cb0"
            else:
                label = str(row * col)
                fill = "#ffffff" if row % 2 else "#f7fafc"
                color = "#1f2933"
            parts.append(
                '<rect x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="#cbd2d9" '
                'stroke-width="0.8"/>' % (_fmt(x), _fmt(y), _fmt(cell), _fmt(cell), fill)
            )
            parts.append(
                '<text x="%s" y="%s" font-size="%s" text-anchor="middle" fill="%s" '
                'font-family="Helvetica, Arial, sans-serif">%s</text>'
                % (
                    _fmt(x + cell / 2.0),
                    _fmt(y + cell * 0.68),
                    _fmt(cell * 0.38),
                    color,
                    html.escape(label),
                )
            )
    parts.append("</svg>")
    return "\n".join(parts)


_CSS = """
@page { size: A4; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
       color: #1f2933; background: #fff; }
.sheet { padding: 4mm; }
h1 { margin: 0 0 2mm; font-size: 22px; text-align: center; letter-spacing: 2px; }
.meta { margin: 0 0 5mm; text-align: center; color: #616e7c; font-size: 12px; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.card { border: 1px solid #cbd2d9; border-radius: 3mm; padding: 4mm; page-break-inside: avoid; }
.prompt { font-size: 20px; letter-spacing: 1px; margin: 0 0 3mm; }
.cue { font-size: 12px; color: #9aa5b1; margin: 0; }
.answers { page-break-before: always; margin-top: 6mm; }
.answers h2 { font-size: 18px; border-left: 4px solid #2b6cb0; padding-left: 3mm; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border: 1px solid #cbd2d9; padding: 2mm 3mm; text-align: left; }
th { background: #f5f7fa; }
@media print { .sheet { padding: 0; } }
""".strip()


def render_worksheet(
    problems: Sequence[BlankProblem],
    title: str = "乘法口诀练习",
    answers: bool = False,
) -> str:
    """生成可打印的口诀填空练习纸。"""
    items = list(problems)
    if not items:
        raise MultTableError("至少需要一道题")
    for item in items:
        if not isinstance(item, BlankProblem):
            raise MultTableError("题目必须是 BlankProblem")

    cards = []
    for index, item in enumerate(items, 1):
        cards.append(
            '<div class="card"><p class="prompt">%d. %s</p>'
            '<p class="cue">口诀：%s</p></div>'
            % (index, html.escape(item.prompt), html.escape(item.card))
        )

    sections = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % html.escape(title),
        "<style>%s</style></head><body>" % _CSS,
        '<main class="sheet">',
        "<h1>%s</h1>" % html.escape(title),
        '<p class="meta">姓名：__________　班级：__________　日期：__________</p>',
        '<section class="cards">',
        "\n".join(cards),
        "</section>",
    ]

    if answers:
        rows = []
        for index, item in enumerate(items, 1):
            rows.append(
                "<tr><td>%d</td><td>%s</td><td>%d</td><td>%s</td></tr>"
                % (index, html.escape(item.prompt), item.answer, html.escape(item.card))
            )
        sections.append(
            '<section class="answers"><h2>参考答案</h2>'
            "<table><thead><tr><th>题号</th><th>题目</th><th>答案</th><th>口诀</th></tr></thead>"
            "<tbody>%s</tbody></table></section>" % "\n".join(rows)
        )

    sections.append("</main></body></html>")
    return "\n".join(sections)


def render_rhyme_cards(pairs: Sequence[tuple], columns: int = 3) -> str:
    """把若干乘数对渲染成口诀卡片页。"""
    items = list(pairs)
    if not items:
        raise MultTableError("至少需要一条口诀")
    if isinstance(columns, bool) or not isinstance(columns, int) or columns < 1:
        raise MultTableError("列数必须是正整数")
    from .model import rhyme

    cells = []
    for a, b in items:
        cells.append(
            '<div class="card"><p class="prompt">%s</p><p class="cue">%d × %d = %d</p></div>'
            % (html.escape(rhyme(a, b)), a, b, a * b)
        )
    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="zh-CN"><head><meta charset="utf-8">',
            "<title>口诀卡片</title>",
            "<style>%s</style></head><body>" % _CSS.replace(
                "grid-template-columns: 1fr 1fr", "grid-template-columns: repeat(%d, 1fr)" % columns
            ),
            '<main class="sheet"><h1>乘法口诀卡片</h1><section class="cards">',
            "\n".join(cells),
            "</section></main></body></html>",
        ]
    )
