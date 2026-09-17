# PNG/PDF Code Tools

**简体中文** | [English](README_EN.md)

## 这个项目是怎么来的

> **2026.09，第一次打数模。**最后提交论文时，要求在附录里附上源代码，于是我写了一个简单的脚本，把源代码全部截图成 PNG，再放到论文最后。结果用 Overleaf 编辑 LaTeX 时出现了超时问题，只好换成本地编辑：先把 PNG 拼成 PDF，再把 PDF 接到论文末尾。论文终于导出来了——**38 MB**。
>
> 但是提交要求不能超过 **20 MB**。于是，压缩版工具被紧急催生出来：把代码图改成 JPEG，再拼成 PDF。最终文件降到了 **9 MB 左右**，总算有惊无险地交了上去。`- 3-`
>
> 然后故事迎来了最有喜剧效果的一幕：后来和 Ruby 聊天，她告诉我，其实根本不用截图……把源代码直接复制进 LaTeX，最后正常导出就可以了。`= 0 =`

所以，这个仓库既是一套代码截图与 PDF 工具，也是一份“为了交一次论文，顺手造出一套工具链”的事故记录。

---

## 它能做什么

- 将单个 Python 文件或整个代码目录生成高清代码截图
- 为截图添加语法高亮、行号、文件名和页码
- 将大量 PNG 合并为一份 PDF
- 把图片转换为更小的 JPEG，并生成压缩 PDF
- 同时提供命令行工具和 Tkinter 图形界面

## 目录结构

```text
png-pdf-compress/
├── tools/                 # 可执行脚本与 GUI
├── docs/                  # 详细教程
├── output/                # PNG、JPG 和 PDF 输出
├── requirements.txt       # Python 依赖
└── README.md
```

## 安装依赖

在仓库根目录运行：

```bash
python3 -m pip install -r requirements.txt
```

## 推荐方式：使用 GUI

```bash
python3 tools/screenshot_gui.py
```

GUI 支持：

- 选择单个 Python 文件或整个代码文件夹
- 选择截图输出目录
- 调整每张图片的视觉行数
- 调整图片宽度
- 批量生成代码截图
- 在窗口中预览生成结果
- 一键打开输出目录

## 命令行工具

### 1. 标准代码附录截图

适用于包含 `Q1`、`Q2`、`Q3`、`Q4` 的数模代码目录：

```bash
python3 tools/make_code_appendix.py \
  --code-dir /path/to/code \
  --output-dir output/code_appendix_output
```

### 2. 轻量版截图

轻量版会减少图片尺寸和页数，更适合 Overleaf 或受文件大小限制的提交系统。

```bash
python3 tools/make_code_appendix_light.py \
  --code-dir /path/to/code \
  --output-dir output/code_appendix_output
```

### 3. 合并截图为 PDF

```bash
python3 tools/merge_code_screenshots_to_pdf.py
```

脚本会依次查找：

1. `output/code_appendix_output/code_screenshots`
2. `output/code_screenshots`

生成结果为 `output/code_appendix.pdf`。

### 4. 生成压缩 PDF

```bash
python3 tools/compress_code_appendix.py
```

脚本默认读取 `output/code_appendix_output/code_screenshots`，将中间 JPEG 保存到 `output/code_jpg_ultra`，并生成 `output/code_appendix_ultra.pdf`。

## 现有输出

- `output/code_appendix.pdf`：合并后的代码附录
- `output/code_appendix_output/`：当前生成器输出
- `output/code_screenshots/`：完整 PNG 截图
- `output/code_jpg_compressed/`：压缩 JPEG
- `output/code_jpg_ultra/`：高压缩率 JPEG

## 更多文档

- `docs/README_截图生成.md`
- `docs/README_轻量版.md`
- `docs/README_合并PDF.md`

## 小提示

如果比赛或老师允许，直接使用 LaTeX 的代码环境通常比截图更轻、更清晰，也更方便复制和搜索。但当提交格式明确要求截图、需要保留编辑器风格，或者只想快速制作代码附录时，这套工具依然很好用。

## 依赖与说明

- GUI 使用 Python 自带的 Tkinter
- 截图依赖 Pillow 和 Pygments
- PDF 合并依赖 img2pdf
- `output/` 中保存的是已有成果，安装依赖不会修改它们

---

从 **38 MB** 到 **9 MB**，再到一句“其实不用截图”——至少脚本留下来了。🙂
