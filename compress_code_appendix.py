from pathlib import Path
from PIL import Image
import img2pdf

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "code_appendix_output" / "code_screenshots"
TMP = ROOT / "code_jpg_ultra"
OUT = ROOT / "code_appendix_ultra.pdf"

TMP.mkdir(exist_ok=True)

jpg_files = []

for q in ["Q1", "Q2", "Q3", "Q4"]:
    src_dir = SRC / q
    out_dir = TMP / q
    out_dir.mkdir(parents=True, exist_ok=True)

    for png in sorted(src_dir.glob("*.png")):
        jpg = out_dir / f"{png.stem}.jpg"

        with Image.open(png) as im:
            # 转灰度，代码附录不需要彩色
            im = im.convert("L")

            # 最大宽度压到 900 px
            if im.width > 900:
                new_h = round(im.height * 900 / im.width)
                im = im.resize(
                    (900, new_h),
                    Image.Resampling.LANCZOS
                )

            im.save(
                jpg,
                "JPEG",
                quality=45,
                optimize=True,
                progressive=True
            )

        jpg_files.append(jpg)

print(f"共 {len(jpg_files)} 张，开始合并……")

with open(OUT, "wb") as f:
    f.write(img2pdf.convert([str(p) for p in jpg_files]))

size = OUT.stat().st_size / 1024 / 1024
print(f"完成：{OUT}")
print(f"大小：{size:.2f} MB")