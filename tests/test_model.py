"""乘法口诀模型测试。"""

import unittest

from multtable.model import (
    HIDDEN_KINDS,
    MAX_FACTOR,
    MIN_FACTOR,
    BlankProblem,
    MultTableError,
    all_pairs,
    check_answer,
    check_factor,
    chinese_number,
    generate_blanks,
    product,
    rhyme,
)


class ProductAndRhymeTest(unittest.TestCase):
    """逐一验证 1–9 的乘积与口诀。"""


def _make_product_test(a, b):
    def test(self):
        self.assertEqual(product(a, b), a * b)
        self.assertEqual(product(b, a), a * b)
        text = rhyme(a, b)
        self.assertEqual(text, rhyme(b, a))
        self.assertTrue(text.startswith("一二三四五六七八九"[min(a, b) - 1]))
        if a * b < 10:
            self.assertIn("得", text)
        elif a * b == 10:
            self.assertTrue(text.endswith("一十"))
        else:
            self.assertTrue(text.endswith(chinese_number(a * b)))

    test.__doc__ = "%d×%d 的乘积与口诀" % (a, b)
    return test


for _a in range(MIN_FACTOR, MAX_FACTOR + 1):
    for _b in range(MIN_FACTOR, MAX_FACTOR + 1):
        setattr(
            ProductAndRhymeTest,
            "test_%d_%d" % (_a, _b),
            _make_product_test(_a, _b),
        )


class BlankProblemTest(unittest.TestCase):
    """逐一验证三种填空形式的题干与答案。"""


def _make_blank_test(a, b, hidden):
    def test(self):
        item = BlankProblem(a, b, hidden)
        self.assertEqual(item.answer, {"product": a * b, "a": a, "b": b}[hidden])
        self.assertIn("____", item.prompt)
        self.assertEqual(item.card, rhyme(a, b))
        self.assertEqual(item.prompt.count("____"), 1)

    test.__doc__ = "隐藏 %s：%d×%d" % (hidden, a, b)
    return test


_index = 0
for _a in range(MIN_FACTOR, MAX_FACTOR + 1):
    for _b in range(MIN_FACTOR, MAX_FACTOR + 1):
        _hidden = HIDDEN_KINDS[_index % len(HIDDEN_KINDS)]
        setattr(
            BlankProblemTest,
            "test_%d_%d_%s" % (_a, _b, _hidden),
            _make_blank_test(_a, _b, _hidden),
        )
        _index += 1


class FactorCheckTest(unittest.TestCase):
    def test_bounds(self):
        self.assertEqual(check_factor(1), 1)
        self.assertEqual(check_factor(9), 9)

    def test_zero(self):
        with self.assertRaises(MultTableError):
            check_factor(0)

    def test_ten(self):
        with self.assertRaises(MultTableError):
            check_factor(10)

    def test_bool(self):
        with self.assertRaises(MultTableError):
            check_factor(True)

    def test_string(self):
        with self.assertRaises(MultTableError):
            check_factor("3")

    def test_product_bad_second(self):
        with self.assertRaises(MultTableError):
            product(3, 12)


class ChineseNumberTest(unittest.TestCase):
    def test_single_digits(self):
        self.assertEqual([chinese_number(i) for i in range(10)], list("零一二三四五六七八九"))

    def test_ten(self):
        self.assertEqual(chinese_number(10), "十")

    def test_eleven(self):
        self.assertEqual(chinese_number(11), "十一")

    def test_twenty(self):
        self.assertEqual(chinese_number(20), "二十")

    def test_twenty_one(self):
        self.assertEqual(chinese_number(21), "二十一")

    def test_eighty_one(self):
        self.assertEqual(chinese_number(81), "八十一")

    def test_negative(self):
        with self.assertRaises(MultTableError):
            chinese_number(-1)

    def test_too_large(self):
        with self.assertRaises(MultTableError):
            chinese_number(82)

    def test_bool(self):
        with self.assertRaises(MultTableError):
            chinese_number(False)


class GenerateBlanksTest(unittest.TestCase):
    def test_all_pairs(self):
        self.assertEqual(len(all_pairs()), 81)
        self.assertEqual(len(set(all_pairs())), 81)

    def test_default_count(self):
        self.assertEqual(len(generate_blanks(12, seed=1)), 12)

    def test_unique(self):
        items = generate_blanks(20, ["product"], seed=3)
        keys = [(item.a, item.b, item.hidden) for item in items]
        self.assertEqual(len(keys), len(set(keys)))

    def test_kinds_filter(self):
        items = generate_blanks(10, ["a"], seed=4)
        self.assertTrue(all(item.hidden == "a" for item in items))

    def test_all_kinds(self):
        items = generate_blanks(40, HIDDEN_KINDS, seed=5)
        self.assertEqual({item.hidden for item in items}, set(HIDDEN_KINDS))

    def test_seed_reproducible(self):
        first = generate_blanks(8, HIDDEN_KINDS, seed=9)
        second = generate_blanks(8, HIDDEN_KINDS, seed=9)
        self.assertEqual(first, second)

    def test_seed_differs(self):
        first = generate_blanks(8, HIDDEN_KINDS, seed=9)
        second = generate_blanks(8, HIDDEN_KINDS, seed=10)
        self.assertNotEqual(first, second)

    def test_zero_count(self):
        with self.assertRaises(MultTableError):
            generate_blanks(0)

    def test_bool_count(self):
        with self.assertRaises(MultTableError):
            generate_blanks(True)

    def test_too_many(self):
        with self.assertRaises(MultTableError):
            generate_blanks(82, ["product"])

    def test_empty_kinds(self):
        with self.assertRaises(MultTableError):
            generate_blanks(3, [])

    def test_unknown_kind(self):
        with self.assertRaises(MultTableError):
            generate_blanks(3, ["guess"])

    def test_capacity_exact(self):
        self.assertEqual(len(generate_blanks(81, ["product"], seed=2)), 81)

    def test_all_values_in_range(self):
        items = generate_blanks(50, HIDDEN_KINDS, seed=11)
        for item in items:
            self.assertGreaterEqual(item.a, 1)
            self.assertLessEqual(item.a, 9)
            self.assertGreaterEqual(item.b, 1)
            self.assertLessEqual(item.b, 9)


class CheckAnswerTest(unittest.TestCase):
    def test_correct(self):
        self.assertTrue(check_answer(BlankProblem(3, 4, "product"), 12))

    def test_incorrect(self):
        self.assertFalse(check_answer(BlankProblem(3, 4, "product"), 11))

    def test_missing_factor(self):
        self.assertTrue(check_answer(BlankProblem(3, 4, "a"), 3))

    def test_bad_problem(self):
        with self.assertRaises(MultTableError):
            check_answer("3×4", 12)

    def test_bad_answer(self):
        with self.assertRaises(MultTableError):
            check_answer(BlankProblem(3, 4, "product"), "12")

    def test_bool_answer(self):
        with self.assertRaises(MultTableError):
            check_answer(BlankProblem(3, 4, "product"), True)


class BlankProblemValidationTest(unittest.TestCase):
    def test_bad_hidden(self):
        with self.assertRaises(MultTableError):
            BlankProblem(3, 4, "sum")

    def test_bad_factor(self):
        with self.assertRaises(MultTableError):
            BlankProblem(10, 4, "product")

    def test_frozen(self):
        item = BlankProblem(3, 4, "product")
        with self.assertRaises(AttributeError):
            item.a = 5  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
