# PNG/PDF Code Tools

## 这个项目是怎么来的 / How This Project Started

> **2026.09，第一次打数模。**最后提交论文时，要求在附录里附上源代码，于是我写了一个简单的脚本，把源代码全部截图成 PNG，再放到论文最后。结果用 Overleaf 编辑 LaTeX 时出现了超时问题，只好换成本地编辑：先把 PNG 拼成 PDF，再把 PDF 接到论文末尾。论文终于导出来了——**38 MB**。
>
> 但是提交要求不能超过 **20 MB**。于是，压缩版工具被紧急催生出来：把代码图改成 JPEG，再拼成 PDF。最终文件降到了 **9 MB 左右**，总算有惊无险地交了上去。`- 3-`
>
> 然后故事迎来了最有喜剧效果的一幕：后来和 Ruby 聊天，她告诉我，其实根本不用截图……把源代码直接复制进 LaTeX，最后正常导出就可以了。`= 0 =`

> **September 2026 — my first mathematical modeling competition.** The final paper needed to include all source code in an appendix, so I wrote a small script that turned the code into PNG screenshots and placed them at the end of the paper. Overleaf then began timing out, so we switched to local LaTeX editing, merged the PNG files into a PDF, and attached it to the paper. The paper finally compiled — at a glorious **38 MB**.
>
> There was only one problem: the submission limit was **20 MB**. That emergency created the compressed edition. We switched the code images to JPEG, merged them into a PDF, and brought the final paper down to about **9 MB**. It was submitted safely, if only just. `- 3-`
>
> Then came the plot twist. Later, while chatting with Ruby, she told me that none of the screenshots were actually necessary: the source code could simply be copied into LaTeX and exported normally. `= 0 =`

所以，这个仓库既是一套代码截图与 PDF 工具，也是一份“为了交一次作业，顺手造出一套工具链”的事故记录。

This repository is both a code-screenshot/PDF toolkit and a record of how one submission problem unexpectedly grew into a small toolchain.

---

## 它能做什么 / What It Does

- 将单个 Python 文件或整个代码目录生成高清代码截图。
- 为截图添加语法高亮、行号、文件名和页码。
- 将大量 PNG 合并为一份 PDF。
- 把图片转换为更小的 JPEG，并生成压缩 PDF。
- 同时提供命令行工具和 Tkinter 图形界面。

- Generate high-resolution screenshots from one Python file or an entire code folder.
- Add syntax highlighting, line numbers, filenames, and page numbers.
- Merge large collections of PNG images into one PDF.
- Convert images to smaller JPEG files and build a compressed PDF.
- Use either the command line or a Tkinter graphical interface.

## 目录结构 / Project Structure

```text
png-pdf-compress/
├── tools/                 # 可执行脚本与 GUI / Scripts and GUI
├── docs/                  # 详细教程 / Detailed guides
├── output/                # PNG、JPG 和 PDF 输出 / Generated files
├── requirements.txt       # Python 依赖 / Dependencies
└── README.md
```

## 安装依赖 / Install Dependencies

在仓库根目录运行以下命令：

Run the following command from the repository root:

```bash
python3 -m pip install -r requirements.txt
```

## 推荐方式：使用 GUI / Recommended: Use the GUI

```bash
python3 tools/screenshot_gui.py
```

GUI 支持以下功能：

The GUI provides:

- 选择单个 Python 文件或整个代码文件夹 / Select one Python file or a complete code folder
- 选择截图输出目录 / Choose the output directory
- 调整每张图片的视觉行数 / Adjust the number of visual lines per image
- 调整图片宽度 / Adjust image width
- 批量生成代码截图 / Generate screenshots in batches
- 在窗口中预览生成结果 / Preview generated images inside the app
- 一键打开输出目录 / Open the output folder with one click

## 命令行工具 / Command-Line Tools

### 1. 标准代码附录截图 / Standard Code Appendix Screenshots

适用于包含 `Q1`、`Q2`、`Q3`、`Q4` 的数模代码目录。

Designed for mathematical-modeling projects containing `Q1`, `Q2`, `Q3`, and `Q4` folders.

```bash
python3 tools/make_code_appendix.py \
  --code-dir /path/to/code \
  --output-dir output/code_appendix_output
```

### 2. 轻量版截图 / Lightweight Screenshots

轻量版会减少图片尺寸和页数，更适合 Overleaf 或受文件大小限制的提交系统。

The lightweight edition reduces image dimensions and page count, making it friendlier to Overleaf and size-limited submission systems.

```bash
python3 tools/make_code_appendix_light.py \
  --code-dir /path/to/code \
  --output-dir output/code_appendix_output
```

### 3. 合并截图为 PDF / Merge Screenshots into a PDF

```bash
python3 tools/merge_code_screenshots_to_pdf.py
```

脚本会依次查找：

The script searches these locations in order:

1. `output/code_appendix_output/code_screenshots`
2. `output/code_screenshots`

生成结果为 `output/code_appendix.pdf`。

The generated file is `output/code_appendix.pdf`.

### 4. 生成压缩 PDF / Build a Compressed PDF

```bash
python3 tools/compress_code_appendix.py
```

脚本默认读取 `output/code_appendix_output/code_screenshots`，将中间 JPEG 保存到 `output/code_jpg_ultra`，并生成 `output/code_appendix_ultra.pdf`。

By default, the script reads `output/code_appendix_output/code_screenshots`, saves intermediate JPEG files in `output/code_jpg_ultra`, and generates `output/code_appendix_ultra.pdf`.

## 现有输出 / Existing Output

- `output/code_appendix.pdf`：合并后的代码附录 / Merged code appendix
- `output/code_appendix_output/`：当前生成器输出 / Current generator output
- `output/code_screenshots/`：完整 PNG 截图 / Full PNG screenshot collection
- `output/code_jpg_compressed/`：压缩 JPEG / Compressed JPEG images
- `output/code_jpg_ultra/`：高压缩率 JPEG / More aggressively compressed JPEG images

## 更多文档 / More Documentation

- `docs/README_截图生成.md`
- `docs/README_轻量版.md`
- `docs/README_合并PDF.md`

## 小提示 / A Small Tip

如果比赛或老师允许，直接使用 LaTeX 的代码环境通常比截图更轻、更清晰，也更方便复制搜索。但当提交格式明确要求截图、需要保留编辑器风格，或者只想快速制作代码附录时，这套工具依然很好用。

If the competition or instructor allows it, a native LaTeX code environment is usually smaller, sharper, searchable, and easier to copy than screenshots. This toolkit is still useful when screenshots are explicitly required, when you want to preserve an editor-like appearance, or when you need to assemble a code appendix quickly.

## 依赖与说明 / Dependencies and Notes

- GUI 使用 Python 自带的 Tkinter。 / The GUI uses Python's built-in Tkinter library.
- 截图依赖 Pillow 和 Pygments。 / Screenshot generation requires Pillow and Pygments.
- PDF 合并依赖 img2pdf。 / PDF merging requires img2pdf.
- `output/` 中保存的是已有成果，安装依赖不会修改它们。 / Existing results in `output/` are not modified when dependencies are installed.

---

从 **38 MB** 到 **9 MB**，再到一句“其实不用截图”——至少脚本留下来了。🙂

From **38 MB** to **9 MB**, and finally to “you never needed screenshots” — at least the tools survived. 🙂
