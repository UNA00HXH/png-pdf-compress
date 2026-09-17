# 代码附录截图生成器｜Mac 保姆级使用说明

> 当前仓库已经整理。请在仓库根目录运行：
>
> ```bash
> python3 tools/make_code_appendix.py --code-dir /你的/code/路径
> ```
>
> 如果希望使用界面，请运行 `python3 tools/screenshot_gui.py`。

这个脚本已经按你上传的 `code.zip` 目录结构做了适配。

## 0. 最终你会得到什么

运行一次：

```bash
python3 make_code_appendix.py
```

自动得到：

```text
code_appendix_output/
└── code_screenshots/
    ├── Q1/
    │   ├── Q1__q1__geometry_001.png
    │   └── ...
    ├── Q2/
    ├── Q3/
    ├── Q4/
    └── appendix_code.tex
```

脚本会自动：
- 找 Q1～Q4 的真正源码；
- 忽略 tests、reviews、`__pycache__`；
- 忽略 `plot_*.py` 和 `__init__.py`；
- 自动分页；
- 加源文件路径、行号和页码；
- 自动处理长代码行；
- 自动生成 LaTeX 附录。

---

# 1. 解压你的 code.zip

例如放在桌面：

```text
桌面/
└── 数模代码附录/
    ├── code/
    │   ├── Q1/
    │   ├── Q2/
    │   ├── Q3/
    │   └── Q4/
    └── make_code_appendix.py
```

**重点：**
`make_code_appendix.py` 和 `code` 文件夹处于同一级。

---

# 2. VS Code 打开这个文件夹

VS Code：

**File → Open Folder**

选择：

```text
数模代码附录
```

---

# 3. 打开终端

VS Code 顶部：

**Terminal → New Terminal**

你应该看到类似：

```text
Una@MacBook-Pro 数模代码附录 %
```

---

# 4. 检查 Python

复制：

```bash
python3 --version
```

如果看到：

```text
Python 3.x.x
```

就可以。

---

# 5. 安装依赖

复制这一句：

```bash
python3 -m pip install pillow pygments
```

如果出现 `Successfully installed ...` 就完成。

如果显示已经安装，也是正常的。

---

# 6. 运行

确保终端现在就在：

```text
数模代码附录
```

运行：

```bash
python3 make_code_appendix.py
```

然后等它自己跑。

最后应该看到：

```text
完成！
源程序文件数：...
代码截图总数：...
截图目录：.../code_appendix_output/code_screenshots
LaTeX 文件：.../appendix_code.tex
```

---

# 7. 找到生成结果

VS Code 左边刷新一下，或者 Finder 打开：

```text
code_appendix_output/
```

里面就是全部代码截图。

---

# 8. 放进 LaTeX

最简单的方法：

把生成的：

```text
code_screenshots/
```

整个复制进你的 LaTeX 项目。

你的项目例如：

```text
paper/
├── main.tex
├── abstract.tex
├── q1.tex
├── q2.tex
├── q3.tex
├── q4.tex
└── code_screenshots/
    ├── Q1/
    ├── Q2/
    ├── Q3/
    ├── Q4/
    └── appendix_code.tex
```

## 导言区

检查 `main.tex` 前面是否有：

```latex
\usepackage{graphicx}
```

如果没有就加。

## 正文最后

在参考文献之后、`\end{document}` 之前写：

```latex
\clearpage
\appendix
\input{code_screenshots/appendix_code}
```

然后重新编译。

---

# 9. 如果图片太多怎么办

脚本默认截“真正的算法源码”，不是把 ZIP 里所有 Python 都塞进去。

目前默认：

### 保留

```text
Q1/q1/*.py
Q2/q2/*.py
Q3/q3/*.py
Q4/q4/*.py
```

包括 Q4 的：

```text
Q4/q4/v2/*.py
```

以及必要的 `qN_main.py` / `run_all.py`。

### 自动忽略

```text
__pycache__/
tests/
reviews/
.venv/
plot_*.py
test_*.py
__init__.py
```

因此不会把绘图脚本、缓存和测试代码疯狂塞进论文。

---

# 10. 想每张代码更少/更多

打开：

```text
make_code_appendix.py
```

找到：

```python
VISUAL_LINES_PER_IMAGE = 48
```

例如改为：

```python
VISUAL_LINES_PER_IMAGE = 42
```

图片字会更疏。

改为：

```python
VISUAL_LINES_PER_IMAGE = 55
```

一张图容纳更多代码。

**论文中建议 45～50 左右，不要为了少几页把字压得特别小。**

---

# 11. 如果脚本没找到 code 文件夹

直接指定路径，例如：

```bash
python3 make_code_appendix.py --code-dir "/Users/你的用户名/Desktop/code"
```

路径有空格时一定保留双引号。

---

# 12. 重新生成

你修改源码后直接再次运行：

```bash
python3 make_code_appendix.py
```

它会覆盖同名截图，因此不用重新手工截图。
