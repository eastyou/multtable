"""乘法口诀表的数据模型。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

MIN_FACTOR = 1
MAX_FACTOR = 9
DIGITS = "零一二三四五六七八九"
HIDDEN_KINDS = ("product", "a", "b")


class MultTableError(ValueError):
    """乘法口诀相关的输入错误。"""


def check_factor(value: int, name: str = "乘数") -> int:
    """校验乘数必须为 1–9 的整数。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise MultTableError("%s必须是整数" % name)
    if value < MIN_FACTOR or value > MAX_FACTOR:
        raise MultTableError("%s必须在 %d–%d 之间" % (name, MIN_FACTOR, MAX_FACTOR))
    return value


def product(a: int, b: int) -> int:
    """返回两个乘数的积。"""
    check_factor(a, "第一个乘数")
    check_factor(b, "第二个乘数")
    return a * b


def chinese_number(value: int) -> str:
    """把 0–81 的整数写成中文读法。"""
    if isinstance(value, bool) or not isinstance(value, int):
        raise MultTableError("数字必须是整数")
    if value < 0 or value > 81:
        raise MultTableError("数字必须在 0–81 之间")
    if value < 10:
        return DIGITS[value]
    tens, ones = divmod(value, 10)
    head = "十" if tens == 1 else DIGITS[tens] + "十"
    return head if ones == 0 else head + DIGITS[ones]


def rhyme(a: int, b: int) -> str:
    """返回乘法口诀，如 3×4 → 三四十二。"""
    check_factor(a, "第一个乘数")
    check_factor(b, "第二个乘数")
    small, large = (a, b) if a <= b else (b, a)
    value = small * large
    if value < 10:
        return "%s%s得%s" % (DIGITS[small], DIGITS[large], DIGITS[value])
    if value == 10:
        return "%s%s一十" % (DIGITS[small], DIGITS[large])
    return "%s%s%s" % (DIGITS[small], DIGITS[large], chinese_number(value))


@dataclass(frozen=True)
class BlankProblem:
    """一道口诀填空题。"""

    a: int
    b: int
    hidden: str

    def __post_init__(self) -> None:
        check_factor(self.a, "第一个乘数")
        check_factor(self.b, "第二个乘数")
        if self.hidden not in HIDDEN_KINDS:
            raise MultTableError("隐藏项只能是 product、a 或 b")

    @property
    def answer(self) -> int:
        """题目要求的答案。"""
        if self.hidden == "a":
            return self.a
        if self.hidden == "b":
            return self.b
        return self.a * self.b

    @property
    def prompt(self) -> str:
        """题干文本，未知项用下划线表示。"""
        left = "____" if self.hidden == "a" else str(self.a)
        right = "____" if self.hidden == "b" else str(self.b)
        result = "____" if self.hidden == "product" else str(self.a * self.b)
        return "%s × %s = %s" % (left, right, result)

    @property
    def card(self) -> str:
        """口诀写法，例如 三四十二。"""
        return rhyme(self.a, self.b)


def all_pairs() -> List[Tuple[int, int]]:
    """返回 1–9 的全部 81 个有序乘数组合。"""
    return [(a, b) for a in range(MIN_FACTOR, MAX_FACTOR + 1) for b in range(MIN_FACTOR, MAX_FACTOR + 1)]


def generate_blanks(
    count: int = 10,
    hidden: Sequence[str] = HIDDEN_KINDS,
    seed: Optional[int] = None,
) -> List[BlankProblem]:
    """随机生成不重复的口诀填空题。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise MultTableError("题目数量必须是整数")
    if count < 1:
        raise MultTableError("题目数量至少为 1")
    kinds = list(hidden)
    if not kinds:
        raise MultTableError("至少需要一种填空类型")
    for kind in kinds:
        if kind not in HIDDEN_KINDS:
            raise MultTableError("未知填空类型：%s" % kind)
    pairs = all_pairs()
    capacity = len(pairs) * len(kinds)
    if count > capacity:
        raise MultTableError("题目数量不能超过 %d" % capacity)

    rng = random.Random(seed)
    rng.shuffle(pairs)
    problems: List[BlankProblem] = []
    for pair in pairs:
        for kind in kinds:
            if len(problems) >= count:
                return problems
            problems.append(BlankProblem(pair[0], pair[1], kind))
    rng.shuffle(problems)
    return problems[:count]


def check_answer(problem: BlankProblem, answer: int) -> bool:
    """判断作答是否正确。"""
    if not isinstance(problem, BlankProblem):
        raise MultTableError("题目必须是 BlankProblem")
    if isinstance(answer, bool) or not isinstance(answer, int):
        raise MultTableError("答案必须是整数")
    return problem.answer == answer
