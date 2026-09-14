#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
把 code_appendix_output/code_screenshots/Q1~Q4 中的 PNG
按 Q1 -> Q2 -> Q3 -> Q4、文件名顺序，直接合并成一个多页 PDF。

优点：
- 不再让 LaTeX 逐张解码 100+ PNG
- img2pdf 直接把图片封装进 PDF，速度快、内存占用低
"""

from pathlib import Path
import re
import sys

try:
    import img2pdf
except ImportError:
    print("缺少依赖，请先运行：")
    print("python3 -m pip install img2pdf")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent

# 自动寻找截图目录
candidates = [
    ROOT / "code_appendix_output" / "code_screenshots",
    ROOT / "code_screenshots",
]

SCREENSHOT_DIR = next((p for p in candidates if p.exists()), None)

if SCREENSHOT_DIR is None:
    print("❌ 没找到 code_screenshots 文件夹。")
    print("请把本脚本放到“代码附录生成器”目录里再运行。")
    sys.exit(1)

OUT_PDF = ROOT / "code_appendix.pdf"


def natural_key(path: Path):
    # 自然排序，确保 _002 在 _010 前面
    return [
        int(x) if x.isdigit() else x.lower()
        for x in re.split(r"(\d+)", path.name)
    ]


images = []

for q in ["Q1", "Q2", "Q3", "Q4"]:
    folder = SCREENSHOT_DIR / q
    if not folder.exists():
        print(f"⚠️ 未找到 {folder}")
        continue

    q_images = sorted(folder.glob("*.png"), key=natural_key)
    print(f"{q}: {len(q_images)} 张")
    images.extend(q_images)

if not images:
    print("❌ 没找到任何 PNG。")
    sys.exit(1)

print(f"\n共找到 {len(images)} 张图片")
print("正在合并 PDF……")

with open(OUT_PDF, "wb") as f:
    f.write(
        img2pdf.convert(
            [str(p) for p in images]
        )
    )

size_mb = OUT_PDF.stat().st_size / 1024 / 1024

print("\n✅ 完成！")
print(f"输出文件：{OUT_PDF}")
print(f"PDF 页数：{len(images)}")
print(f"PDF 大小：{size_mb:.1f} MB")
print("\n下一步：")
print("1. 把 code_appendix.pdf 上传到 LaTeX 工程，与 main.tex 同级")
print("2. main.tex 导言区加：\\usepackage{pdfpages}")
print("3. 删除/注释：\\input{code_screenshots/appendix_code}")
print("4. 改为：")
print(r"\includepdf[pages=-,pagecommand={},fitpaper=true]{code_appendix.pdf}")
