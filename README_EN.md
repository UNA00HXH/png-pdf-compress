# PNG/PDF Code Tools

[简体中文](README.md) | **English**

## How This Project Started

> **September 2026 — my first mathematical modeling competition.** The final paper needed to include all source code in an appendix, so I wrote a small script that turned the code into PNG screenshots and placed them at the end of the paper. Overleaf then began timing out, so we switched to local LaTeX editing, merged the PNG files into a PDF, and attached it to the paper. The paper finally compiled — at a glorious **38 MB**.
>
> There was only one problem: the submission limit was **20 MB**. That emergency created the compressed edition. We switched the code images to JPEG, merged them into a PDF, and brought the final paper down to about **9 MB**. It was submitted safely, if only just. `- 3-`
>
> Then came the plot twist. Later, while chatting with Ruby, she told me that none of the screenshots were actually necessary: the source code could simply be copied into LaTeX and exported normally. `= 0 =`

This repository is both a code-screenshot/PDF toolkit and a record of how one paper-submission problem unexpectedly grew into a small toolchain.

---

## What It Does

- Generate high-resolution screenshots from one Python file or an entire code folder
- Add syntax highlighting, line numbers, filenames, and page numbers
- Merge large collections of PNG images into one PDF
- Convert images to smaller JPEG files and build a compressed PDF
- Use either command-line tools or a Tkinter graphical interface

## Project Structure

```text
png-pdf-compress/
├── tools/                 # Executable scripts and GUI
├── docs/                  # Detailed guides
├── output/                # Generated PNG, JPG, and PDF files
├── requirements.txt       # Python dependencies
└── README.md
```

## Install Dependencies

Run the following command from the repository root:

```bash
python3 -m pip install -r requirements.txt
```

## Recommended: Use the GUI

```bash
python3 tools/screenshot_gui.py
```

The GUI lets you:

- Select one Python file or an entire code folder
- Choose the screenshot output directory
- Adjust the number of visual lines per image
- Adjust image width
- Generate screenshots in batches
- Preview generated images inside the window
- Open the output folder with one click

## Command-Line Tools

### 1. Standard Code Appendix Screenshots

Designed for mathematical-modeling projects containing `Q1`, `Q2`, `Q3`, and `Q4` folders:

```bash
python3 tools/make_code_appendix.py \
  --code-dir /path/to/code \
  --output-dir output/code_appendix_output
```

### 2. Lightweight Screenshots

The lightweight edition reduces image dimensions and page count, making it friendlier to Overleaf and size-limited submission systems.

```bash
python3 tools/make_code_appendix_light.py \
  --code-dir /path/to/code \
  --output-dir output/code_appendix_output
```

### 3. Merge Screenshots into a PDF

```bash
python3 tools/merge_code_screenshots_to_pdf.py
```

The script searches these locations in order:

1. `output/code_appendix_output/code_screenshots`
2. `output/code_screenshots`

The generated file is `output/code_appendix.pdf`.

### 4. Build a Compressed PDF

```bash
python3 tools/compress_code_appendix.py
```

By default, the script reads `output/code_appendix_output/code_screenshots`, saves intermediate JPEG files in `output/code_jpg_ultra`, and generates `output/code_appendix_ultra.pdf`.

## Existing Output

- `output/code_appendix.pdf`: merged code appendix
- `output/code_appendix_output/`: current generator output
- `output/code_screenshots/`: complete PNG screenshot collection
- `output/code_jpg_compressed/`: compressed JPEG images
- `output/code_jpg_ultra/`: more aggressively compressed JPEG images

## More Documentation

- `docs/README_截图生成.md`
- `docs/README_轻量版.md`
- `docs/README_合并PDF.md`

## A Small Tip

If the competition or instructor allows it, a native LaTeX code environment is usually smaller, sharper, searchable, and easier to copy than screenshots. This toolkit is still useful when screenshots are explicitly required, when you want to preserve an editor-like appearance, or when you need to assemble a code appendix quickly.

## Dependencies and Notes

- The GUI uses Python's built-in Tkinter library
- Screenshot generation requires Pillow and Pygments
- PDF merging requires img2pdf
- Existing results in `output/` are not modified when dependencies are installed

---

From **38 MB** to **9 MB**, and finally to “you never needed screenshots” — at least the tools survived. 🙂
