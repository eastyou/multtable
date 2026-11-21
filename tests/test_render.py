"""乘法口诀渲染测试。"""

import unittest

from multtable.model import BlankProblem, MultTableError, all_pairs, generate_blanks
from multtable.render import render_rhyme_cards, render_table, render_worksheet


class TableRenderTest(unittest.TestCase):
    def test_svg_root(self):
        svg = render_table()
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn('viewBox="0 0 460 460"', svg)

    def test_all_products(self):
        svg = render_table()
        for value in range(1, 10):
            self.assertIn(">%d</text>" % value, svg)

    def test_custom_cell(self):
        svg = render_table(60)
        self.assertIn('viewBox="0 0 600 600"', svg)

    def test_table_title(self):
        self.assertIn("乘法口诀表", render_table())

    def test_cell_too_small(self):
        with self.assertRaises(MultTableError):
            render_table(10)

    def test_cell_too_large(self):
        with self.assertRaises(MultTableError):
            render_table(500)

    def test_cell_bool(self):
        with self.assertRaises(MultTableError):
            render_table(True)

    def test_maximum_invalid(self):
        with self.assertRaises(MultTableError):
            render_table(46, 0)


class WorksheetRenderTest(unittest.TestCase):
    def setUp(self):
        self.problems = generate_blanks(6, seed=7)

    def test_html_skeleton(self):
        page = render_worksheet(self.problems)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertTrue(page.rstrip().endswith("</html>"))

    def test_card_count(self):
        page = render_worksheet(self.problems)
        self.assertEqual(page.count('class="card"'), 6)

    def test_prompts_present(self):
        page = render_worksheet(self.problems)
        for item in self.problems:
            self.assertIn(item.prompt.replace("____", "____"), page)

    def test_answers_hidden_by_default(self):
        page = render_worksheet(self.problems)
        self.assertNotIn("参考答案", page)

    def test_answers_section(self):
        page = render_worksheet(self.problems, answers=True)
        self.assertIn("参考答案", page)
        self.assertEqual(page.count("<tr>"), 7)

    def test_custom_title(self):
        page = render_worksheet(self.problems, title="二班口诀练习")
        self.assertIn("二班口诀练习", page)

    def test_empty(self):
        with self.assertRaises(MultTableError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(MultTableError):
            render_worksheet(["3×4"])

    def test_escape_ampersand(self):
        page = render_worksheet(self.problems, title="A&B")
        self.assertIn("A&amp;B", page)


class RhymeCardsTest(unittest.TestCase):
    def test_cards(self):
        page = render_rhyme_cards(all_pairs()[:9], columns=3)
        self.assertEqual(page.count('class="card"'), 9)
        self.assertIn("repeat(3, 1fr)", page)

    def test_empty(self):
        with self.assertRaises(MultTableError):
            render_rhyme_cards([])

    def test_bad_columns(self):
        with self.assertRaises(MultTableError):
            render_rhyme_cards(all_pairs()[:3], 0)

    def test_single_pair(self):
        page = render_rhyme_cards([(3, 4)])
        self.assertIn("三四十二", page)
        self.assertIn("3 × 4 = 12", page)


if __name__ == "__main__":
    unittest.main()
