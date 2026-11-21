# multtable

[![CI](https://github.com/eastyou/multtable/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/multtable/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

把 1–9 的乘法口诀做成可打印的表格、卡片和填空练习纸，题目自动去重，答案单独成页。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 生成完整 9×9 乘法表 SVG
multtable table -o table.svg

# 生成 12 道口诀填空，附答案
multtable sheet --count 12 --seed 1 --answers -o sheet.html

# 只练“求乘数”的题型
multtable sheet --count 8 --hidden a,b -o factor.html

# 打印口诀卡片
multtable cards --columns 3 -o cards.html

# 查询一条口诀，可顺便校验答案
multtable rhyme 3 4
# 三四十二
# 3 × 4 = 12
multtable rhyme 3 4 --answer 12
# 作答：正确
```

## 功能

- 9×9 乘法表 SVG，格子尺寸可调
- 口诀自动生成：三四十二、二五一十、二三得六
- 三种填空：求积、求第一个乘数、求第二个乘数
- 题目去重，随机种子可复现
- A4 打印样式，答案单独一页
- 口诀卡片按列排版，适合裁剪背诵

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou
