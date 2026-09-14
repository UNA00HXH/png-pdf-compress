# Overleaf 轻量版代码附录生成器

这是针对“Draft 能过、Normal 编译超时”调整的版本。

主要变化：
- 图片宽度：1600 → 1200 px
- 每张视觉行：48 → 60
- 代码字号按比例降低
- 因此 PNG 数量和总体积都会明显下降
- 文件标题使用 `\detokenize{...}`，避免下划线触发 `Missing $ inserted`

## 使用

把 `make_code_appendix_light.py` 放在 `code/` 文件夹旁边：

```text
项目/
├── make_code_appendix_light.py
└── code/
    ├── Q1/
    ├── Q2/
    ├── Q3/
    └── Q4/
```

终端：

```bash
python3 -m pip install pillow pygments
python3 make_code_appendix_light.py
```

生成后，把新的 `code_screenshots/` 整个替换 LaTeX 工程里的旧 `code_screenshots/`。

主文件保持：

```latex
\usepackage{graphicx}

...

\clearpage
\appendix
\input{code_screenshots/appendix_code}
```

建议先 Draft 编译确认 Errors=0，再切 Normal。
