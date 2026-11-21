"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    MAX_FACTOR,
    HIDDEN_KINDS,
    MultTableError,
    check_answer,
    generate_blanks,
    product,
    rhyme,
)
from .render import render_rhyme_cards, render_table, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="multtable",
        description="乘法口诀表：可打印口诀表、填空练习纸与口诀查询",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    table = subparsers.add_parser("table", help="输出乘法表 SVG")
    table.add_argument("--cell", type=int, default=46, help="格子边长，默认 46")
    table.add_argument("--max", dest="maximum", type=int, default=MAX_FACTOR, help="最大乘数，默认 9")
    table.add_argument("-o", "--output", default=None, help="输出文件")

    sheet = subparsers.add_parser("sheet", help="生成 A4 填空练习纸")
    sheet.add_argument("--count", type=int, default=10, help="题目数量，默认 10")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument(
        "--hidden",
        default=",".join(HIDDEN_KINDS),
        help="隐藏项，用逗号分隔：product、a、b",
    )
    sheet.add_argument("--title", default="乘法口诀练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")

    cards = subparsers.add_parser("cards", help="输出口诀卡片 HTML")
    cards.add_argument("--columns", type=int, default=3, help="卡片列数，默认 3")
    cards.add_argument("-o", "--output", default=None, help="输出文件")

    show = subparsers.add_parser("rhyme", help="查询一条口诀")
    show.add_argument("a", type=int, help="第一个乘数")
    show.add_argument("b", type=int, help="第二个乘数")
    show.add_argument("--answer", type=int, default=None, help="校验答案")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _parse_hidden(text: str) -> List[str]:
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise MultTableError("至少需要一种隐藏项")
    return parts


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "table":
            _write_output(render_table(args.cell, args.maximum), args.output)
            return 0
        if args.command == "cards":
            pairs = [(a, b) for a in range(1, 10) for b in range(a, 10)]
            _write_output(render_rhyme_cards(pairs, args.columns), args.output)
            return 0
        if args.command == "rhyme":
            value = product(args.a, args.b)
            print(rhyme(args.a, args.b))
            print("%d × %d = %d" % (args.a, args.b, value))
            if args.answer is not None:
                from .model import BlankProblem

                correct = check_answer(BlankProblem(args.a, args.b, "product"), args.answer)
                print("作答：%s" % ("正确" if correct else "错误"))
                return 0 if correct else 1
            return 0
        problems = generate_blanks(
            args.count, _parse_hidden(args.hidden), args.seed
        )
        _write_output(render_worksheet(problems, args.title, args.answers), args.output)
        return 0
    except MultTableError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
