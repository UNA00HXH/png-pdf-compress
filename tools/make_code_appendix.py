#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
一键把 Q1~Q4 Python 源代码批量生成“论文附录截图”，并自动生成 appendix_code.tex。

适配当前目录结构：
code/
├── Q1/q1/*.py
├── Q2/q2/*.py
├── Q3/q3/*.py
└── Q4/q4/*.py

默认行为：
- 只截真正的算法源码目录 q1/q2/q3/q4
- 忽略 __pycache__、tests、reviews、plot_*.py、__init__.py 等
- 每张约 48 个“视觉行”
- 自动处理超长代码行
- 自动加文件名、原始行号、页码
- 自动生成 LaTeX 文件 appendix_code.tex
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    from pygments import lex
    from pygments.lexers import PythonLexer
    from pygments.token import Token
except ImportError:
    print("\n缺少依赖，请先运行：")
    print("python3 -m pip install pillow pygments")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ============================================================
# 你通常只需要改这里
# ============================================================

VISUAL_LINES_PER_IMAGE = 48

# 输出图片尺寸。1600px 宽适合放进论文 PDF，清晰度较高。
IMAGE_WIDTH = 1600

# 代码字号（像素）
CODE_FONT_SIZE = 27
TITLE_FONT_SIZE = 30
SMALL_FONT_SIZE = 22

# 是否把 Q4/q4/v2 也纳入。当前项目中它属于 Q4 源程序的一部分。
INCLUDE_Q4_V2 = True

# 默认不放入附录的文件名 / 前缀
IGNORE_FILE_NAMES = {
    "__init__.py",
}
IGNORE_PREFIXES = (
    "plot_",
    "test_",
)

# 目录层面忽略
IGNORE_DIR_NAMES = {
    "__pycache__",
    "tests",
    "reviews",
    ".git",
    ".venv",
    "venv",
    "env",
    "__MACOSX",
}


# ============================================================
# 字体
# ============================================================

def first_existing(paths):
    for p in paths:
        if Path(p).exists():
            return str(p)
    return None


def get_fonts():
    # macOS 优先
    mono = first_existing([
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ])

    # 中文回退
    cjk = first_existing([
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ])

    if not mono:
        raise RuntimeError("找不到等宽字体。")
    if not cjk:
        cjk = mono

    return {
        "code": ImageFont.truetype(mono, CODE_FONT_SIZE),
        "line": ImageFont.truetype(mono, SMALL_FONT_SIZE),
        "title": ImageFont.truetype(cjk, TITLE_FONT_SIZE),
        "cjk": ImageFont.truetype(cjk, CODE_FONT_SIZE),
        "small_cjk": ImageFont.truetype(cjk, SMALL_FONT_SIZE),
    }


# ============================================================
# 代码筛选
# ============================================================

def find_code_root(script_dir: Path, explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"找不到代码目录：{p}")
        return p

    candidates = [
        PROJECT_ROOT / "code",
        PROJECT_ROOT,
        script_dir / "code",
        script_dir,
    ]
    for p in candidates:
        if all((p / f"Q{i}").exists() for i in range(1, 5)):
            return p.resolve()

    raise FileNotFoundError(
        "没有自动找到 code/Q1~Q4。\n"
        "请把本脚本放在 code 文件夹旁边，或运行：\n"
        "python3 make_code_appendix.py --code-dir /你的/code/路径"
    )


def should_ignore(path: Path) -> bool:
    if any(part in IGNORE_DIR_NAMES for part in path.parts):
        return True
    if path.name in IGNORE_FILE_NAMES:
        return True
    if any(path.name.startswith(x) for x in IGNORE_PREFIXES):
        return True
    return False


def collect_files(code_root: Path):
    groups = {}
    for qi in range(1, 5):
        qname = f"Q{qi}"
        package = code_root / qname / f"q{qi}"
        files = []

        if package.exists():
            for p in sorted(package.rglob("*.py")):
                if should_ignore(p):
                    continue
                if qi == 4 and "v2" in p.parts and not INCLUDE_Q4_V2:
                    continue
                files.append(p)

        # 如果实际源码没有放在 qN/ 里，再兜底找 QN 根目录下的 main/run 文件
        for candidate_name in (f"q{qi}_main.py", "run_all.py"):
            p = code_root / qname / candidate_name
            if p.exists() and p not in files and not should_ignore(p):
                files.append(p)

        groups[qname] = files

    return groups


# ============================================================
# 代码渲染
# ============================================================

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")

def is_cjk_char(ch):
    return bool(CJK_RE.match(ch))


def split_font_runs(text: str):
    if not text:
        return []
    runs = []
    cur = text[0]
    cur_cjk = is_cjk_char(text[0])
    for ch in text[1:]:
        flag = is_cjk_char(ch)
        if flag == cur_cjk:
            cur += ch
        else:
            runs.append((cur, cur_cjk))
            cur = ch
            cur_cjk = flag
    runs.append((cur, cur_cjk))
    return runs


TOKEN_COLORS = {
    Token.Keyword: "#7C3AED",
    Token.Keyword.Constant: "#7C3AED",
    Token.Keyword.Namespace: "#7C3AED",
    Token.Keyword.Type: "#7C3AED",
    Token.Name.Builtin: "#2563EB",
    Token.Name.Builtin.Pseudo: "#2563EB",
    Token.Name.Function: "#0F766E",
    Token.Name.Class: "#0F766E",
    Token.Name.Decorator: "#B45309",
    Token.Literal.String: "#B45309",
    Token.Literal.Number: "#C2410C",
    Token.Operator: "#334155",
    Token.Punctuation: "#475569",
    Token.Comment: "#64748B",
    Token.Comment.Single: "#64748B",
    Token.Comment.Multiline: "#64748B",
}

def token_color(ttype):
    cur = ttype
    while cur != Token:
        if cur in TOKEN_COLORS:
            return TOKEN_COLORS[cur]
        cur = cur.parent
    return "#111827"


def text_width(draw, text, font):
    if not text:
        return 0
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def smart_visual_wrap(line: str, draw, fonts, max_width: int):
    """
    只负责决定“视觉换行”的字符串分块；不修改源代码。
    后续第一页显示真实行号，续行显示 ↳。
    """
    if line == "":
        return [""]

    # tab 展开，避免宽度不可预测
    line = line.replace("\t", "    ")

    chunks = []
    current = ""
    current_w = 0

    for ch in line:
        font = fonts["cjk"] if is_cjk_char(ch) else fonts["code"]
        cw = text_width(draw, ch, font)
        if current and current_w + cw > max_width:
            chunks.append(current)
            # 续行增加少量视觉缩进
            current = "    " + ch
            current_w = text_width(draw, "    ", fonts["code"]) + cw
        else:
            current += ch
            current_w += cw

    chunks.append(current)
    return chunks


def pygments_segments(line: str):
    # pygments 对单行进行高亮；保留末尾但去掉 lexer 额外产生的换行
    out = []
    for ttype, value in lex(line, PythonLexer()):
        value = value.rstrip("\n")
        if value:
            out.append((value, token_color(ttype)))
    return out


def draw_colored_line(draw, x, y, text, fonts):
    """
    对一行重新 token 化并绘制。中文字符自动切到中文字体。
    """
    cursor = x
    for seg, color in pygments_segments(text):
        for run, is_cjk in split_font_runs(seg):
            font = fonts["cjk"] if is_cjk else fonts["code"]
            draw.text((cursor, y), run, font=font, fill=color)
            cursor += text_width(draw, run, font)


def build_visual_lines(source_lines, draw, fonts, code_area_width):
    visual = []
    for line_no, raw in enumerate(source_lines, start=1):
        raw = raw.rstrip("\n\r")
        wrapped = smart_visual_wrap(raw, draw, fonts, code_area_width)
        for idx, piece in enumerate(wrapped):
            visual.append({
                "source_line": line_no,
                "continuation": idx > 0,
                "text": piece,
            })
    return visual


def safe_name(path: Path):
    s = str(path).replace("\\", "__").replace("/", "__")
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", s)
    return s


def render_file(path: Path, code_root: Path, out_dir: Path, fonts):
    source = path.read_text(encoding="utf-8", errors="replace")
    source_lines = source.splitlines()
    if not source_lines:
        source_lines = [""]

    margin_x = 58
    title_h = 90
    footer_h = 54
    line_h = int(CODE_FONT_SIZE * 1.55)
    line_number_w = 100
    divider_gap = 24
    code_x = margin_x + line_number_w + divider_gap
    code_area_width = IMAGE_WIDTH - code_x - margin_x

    dummy = Image.new("RGB", (IMAGE_WIDTH, 300), "white")
    dummy_draw = ImageDraw.Draw(dummy)

    visual = build_visual_lines(source_lines, dummy_draw, fonts, code_area_width)
    pages = [
        visual[i:i + VISUAL_LINES_PER_IMAGE]
        for i in range(0, len(visual), VISUAL_LINES_PER_IMAGE)
    ]

    rel = path.relative_to(code_root)
    group = rel.parts[0] if rel.parts else "code"
    group_dir = out_dir / group
    group_dir.mkdir(parents=True, exist_ok=True)

    generated = []

    for page_idx, page in enumerate(pages, start=1):
        image_h = title_h + len(page) * line_h + footer_h + 30
        img = Image.new("RGB", (IMAGE_WIDTH, image_h), "#FFFFFF")
        draw = ImageDraw.Draw(img)

        # 顶部
        draw.rectangle((0, 0, IMAGE_WIDTH, title_h), fill="#F8FAFC")
        title = str(rel)
        draw.text((margin_x, 23), title, font=fonts["title"], fill="#0F172A")

        page_text = f"{page_idx} / {len(pages)}"
        page_w = text_width(draw, page_text, fonts["line"])
        draw.text(
            (IMAGE_WIDTH - margin_x - page_w, 31),
            page_text,
            font=fonts["line"],
            fill="#64748B",
        )

        # 分隔线
        draw.line(
            (margin_x + line_number_w, title_h + 14,
             margin_x + line_number_w, image_h - footer_h - 8),
            fill="#E2E8F0",
            width=2,
        )

        y = title_h + 22
        for item in page:
            if item["continuation"]:
                no_text = "↳"
            else:
                no_text = str(item["source_line"])

            no_w = text_width(draw, no_text, fonts["line"])
            draw.text(
                (margin_x + line_number_w - no_w - 18, y + 3),
                no_text,
                font=fonts["line"],
                fill="#94A3B8",
            )
            draw_colored_line(draw, code_x, y, item["text"], fonts)
            y += line_h

        # 页脚
        footer_y = image_h - footer_h
        draw.line((margin_x, footer_y, IMAGE_WIDTH - margin_x, footer_y),
                  fill="#E2E8F0", width=1)

        line_start = page[0]["source_line"]
        line_end = page[-1]["source_line"]
        footer = f"Source lines {line_start}–{line_end}"
        draw.text((margin_x, footer_y + 15), footer,
                  font=fonts["line"], fill="#94A3B8")

        filename = f"{safe_name(rel.with_suffix(''))}_{page_idx:03d}.png"
        out_path = group_dir / filename
        img.save(out_path, "PNG", optimize=True)
        generated.append(out_path)

    return generated


# ============================================================
# LaTeX 生成
# ============================================================

def latex_escape(s: str) -> str:
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(c, c) for c in s)


def make_latex(groups, rendered_map, out_dir: Path, code_root: Path):
    tex = []
    tex.append(r"% Auto-generated by make_code_appendix.py")
    tex.append(r"% 主文件导言区请确保包含：\usepackage{graphicx}")
    tex.append("")
    tex.append(r"\section{源程序}")
    tex.append(
        "本文主要源程序按问题编号列于下文。"
        "完整程序文件同时提交于支撑材料中。"
    )
    tex.append("")

    chinese = {
        "Q1": "问题一源程序",
        "Q2": "问题二源程序",
        "Q3": "问题三源程序",
        "Q4": "问题四源程序",
    }

    for group, files in groups.items():
        if not files:
            continue
        tex.append(rf"\subsection{{{chinese.get(group, group)}}}")
        tex.append("")

        for p in files:
            rel = p.relative_to(code_root)
            tex.append(rf"\subsubsection*{{\texttt{{{latex_escape(str(rel))}}}}}")
            tex.append("")

            for img in rendered_map[p]:
                # appendix_code.tex 与 code_screenshots 位于同一 output 目录
                rel_img = img.relative_to(out_dir).as_posix()
                tex.extend([
                    r"\begin{center}",
                    rf"\includegraphics[width=\textwidth]{{{rel_img}}}",
                    r"\end{center}",
                    r"\vspace{0.4em}",
                    "",
                ])

    tex_path = out_dir / "appendix_code.tex"
    tex_path.write_text("\n".join(tex), encoding="utf-8")
    return tex_path


# ============================================================
# main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="批量生成数模论文附录代码截图"
    )
    parser.add_argument(
        "--code-dir",
        default=None,
        help="code 文件夹路径；默认自动寻找",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="输出目录；默认是仓库 output/code_appendix_output",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    code_root = find_code_root(script_dir, args.code_dir)

    if args.output_dir:
        out_dir = Path(args.output_dir).expanduser().resolve()
    else:
        out_dir = PROJECT_ROOT / "output" / "code_appendix_output"

    screenshots_dir = out_dir / "code_screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 64)
    print("代码附录截图生成器")
    print("=" * 64)
    print(f"代码目录：{code_root}")
    print(f"输出目录：{out_dir}")
    print()

    groups = collect_files(code_root)

    print("将处理以下源码：")
    total_files = 0
    for group, files in groups.items():
        print(f"\n[{group}]")
        if not files:
            print("  （未找到）")
        for p in files:
            print(f"  - {p.relative_to(code_root)}")
            total_files += 1

    if total_files == 0:
        print("\n没有找到可处理的 .py 文件。")
        sys.exit(1)

    print(f"\n共 {total_files} 个 Python 文件。")
    print("开始生成图片……\n")

    fonts = get_fonts()
    rendered_map = {}
    total_images = 0

    for group, files in groups.items():
        for idx, p in enumerate(files, start=1):
            imgs = render_file(p, code_root, screenshots_dir, fonts)
            rendered_map[p] = imgs
            total_images += len(imgs)
            print(
                f"✅ {p.relative_to(code_root)} "
                f"→ {len(imgs)} 张"
            )

    tex_path = make_latex(
        groups,
        rendered_map,
        screenshots_dir,
        code_root,
    )

    print("\n" + "=" * 64)
    print("完成！")
    print(f"源程序文件数：{total_files}")
    print(f"代码截图总数：{total_images}")
    print(f"截图目录：{screenshots_dir}")
    print(f"LaTeX 文件：{tex_path}")
    print("=" * 64)
    print("\n把整个 code_screenshots 文件夹复制到你的 LaTeX 工程里，")
    print("再把 appendix_code.tex 复制到同一个 code_screenshots 文件夹中。")
    print("主文件最后写：")
    print(r"    \clearpage")
    print(r"    \appendix")
    print(r"    \input{code_screenshots/appendix_code}")
    print("\n导言区确保有：")
    print(r"    \usepackage{graphicx}")


if __name__ == "__main__":
    main()
