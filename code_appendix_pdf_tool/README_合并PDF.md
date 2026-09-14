# PNG → 单个代码附录 PDF

你现在有约 186 张 PNG，这是正常的：轻量版主要降低每张图片的尺寸和总体积，并不会必然把页数大幅减少。

现在不要再让主论文逐张加载它们，而是先合成一个 PDF。

## 1. 放置脚本

把：

```text
merge_code_screenshots_to_pdf.py
```

放到你当前的：

```text
代码附录生成器/
```

这一层。

目录类似：

```text
代码附录生成器/
├── merge_code_screenshots_to_pdf.py
├── code/
└── code_appendix_output/
    └── code_screenshots/
        ├── Q1/
        ├── Q2/
        ├── Q3/
        └── Q4/
```

## 2. 安装依赖

终端运行：

```bash
python3 -m pip install img2pdf
```

## 3. 合并

运行：

```bash
python3 merge_code_screenshots_to_pdf.py
```

完成后，同一目录会出现：

```text
code_appendix.pdf
```

## 4. 上传到 LaTeX

把：

```text
code_appendix.pdf
```

上传到 `latex_project/`，与 `main.tex` 同一级。

## 5. main.tex 修改

导言区加入：

```latex
\usepackage{pdfpages}
```

删除或注释：

```latex
\input{code_screenshots/appendix_code}
```

正文最后改成：

```latex
\clearpage
\appendix

\section{源程序}

本文主要源程序列于以下附录，完整程序文件同时提交于支撑材料中。

\includepdf[
  pages=-,
  pagecommand={},
  fitpaper=true
]{code_appendix.pdf}
```

然后 Normal Recompile。
