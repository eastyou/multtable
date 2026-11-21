"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from multtable.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_table_stdout(self):
        code, out, _ = run(["table"])
        self.assertEqual(code, 0)
        self.assertIn("<svg", out)

    def test_table_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "table.svg"
            code, out, _ = run(["table", "--cell", "50", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())
            self.assertIn("已写入", out)

    def test_table_bad_cell(self):
        code, _, err = run(["table", "--cell", "5"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_table_bad_max(self):
        code, _, err = run(["table", "--max", "12"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="card"'), 3)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "2", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "4", "--seed", "5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8").count('class="card"'), 4)

    def test_sheet_hidden_product(self):
        code, out, _ = run(["sheet", "--count", "4", "--hidden", "product", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count("= ____"), 4)

    def test_sheet_bad_hidden(self):
        code, _, err = run(["sheet", "--hidden", "guess"])
        self.assertEqual(code, 2)
        self.assertIn("填空类型", err)

    def test_sheet_empty_hidden(self):
        code, _, err = run(["sheet", "--hidden", " , "])
        self.assertEqual(code, 2)
        self.assertIn("隐藏项", err)

    def test_sheet_too_many(self):
        code, _, err = run(["sheet", "--count", "999"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_rhyme(self):
        code, out, _ = run(["rhyme", "3", "4"])
        self.assertEqual(code, 0)
        self.assertIn("三四十二", out)
        self.assertIn("3 × 4 = 12", out)

    def test_rhyme_answer_correct(self):
        code, out, _ = run(["rhyme", "3", "4", "--answer", "12"])
        self.assertEqual(code, 0)
        self.assertIn("正确", out)

    def test_rhyme_answer_wrong(self):
        code, out, _ = run(["rhyme", "3", "4", "--answer", "11"])
        self.assertEqual(code, 1)
        self.assertIn("错误", out)

    def test_rhyme_bad_factor(self):
        code, _, err = run(["rhyme", "0", "4"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "a" / "sheet.html"
            code, _, _ = run(["sheet", "--count", "1", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())

    def test_cards_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "cards.html"
            code, _, _ = run(["cards", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())
            self.assertIn("乘法口诀卡片", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
