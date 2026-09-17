#!/usr/bin/env python3
"""Tkinter GUI for the code screenshot renderer."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from PIL import Image, ImageTk
    import make_code_appendix as renderer
except ImportError as exc:
    raise SystemExit(
        "Missing dependencies. Run: python3 -m pip install pillow pygments"
    ) from exc


class ScreenshotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Code Screenshot Generator")
        self.geometry("1060x720")
        self.minsize(900, 620)

        self.source = tk.StringVar()
        self.output = tk.StringVar()
        self.lines_per_image = tk.IntVar(value=48)
        self.image_width = tk.IntVar(value=1600)
        self.status = tk.StringVar(value="请选择 Python 文件或代码文件夹。")
        self.generated: list[Path] = []
        self.preview_photo = None

        self._build_interface()

    def _build_interface(self):
        outer = ttk.Frame(self, padding=16)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=2)
        outer.columnconfigure(1, weight=3)
        outer.rowconfigure(1, weight=1)

        ttk.Label(
            outer,
            text="Code Screenshot Generator",
            font=("TkDefaultFont", 20, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        settings = ttk.LabelFrame(outer, text="截图设置", padding=14)
        settings.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        settings.columnconfigure(1, weight=1)
        settings.rowconfigure(8, weight=1)

        ttk.Label(settings, text="源文件或文件夹").grid(
            row=0, column=0, sticky="w", pady=5
        )
        ttk.Entry(settings, textvariable=self.source).grid(
            row=0, column=1, columnspan=2, sticky="ew", pady=5
        )
        ttk.Button(settings, text="选择文件…", command=self.choose_file).grid(
            row=1, column=1, sticky="ew", padx=(0, 4), pady=(0, 8)
        )
        ttk.Button(settings, text="选择文件夹…", command=self.choose_folder).grid(
            row=1, column=2, sticky="ew", padx=(4, 0), pady=(0, 8)
        )

        ttk.Label(settings, text="输出目录").grid(
            row=2, column=0, sticky="w", pady=5
        )
        ttk.Entry(settings, textvariable=self.output).grid(
            row=2, column=1, sticky="ew", pady=5
        )
        ttk.Button(settings, text="选择…", command=self.choose_output).grid(
            row=2, column=2, padx=(8, 0), pady=5
        )

        ttk.Label(settings, text="每张视觉行数").grid(
            row=3, column=0, sticky="w", pady=5
        )
        ttk.Spinbox(
            settings,
            from_=20,
            to=100,
            textvariable=self.lines_per_image,
            width=10,
        ).grid(row=3, column=1, sticky="w", pady=5)

        ttk.Label(settings, text="图片宽度（px）").grid(
            row=4, column=0, sticky="w", pady=5
        )
        ttk.Spinbox(
            settings,
            from_=800,
            to=3000,
            increment=100,
            textvariable=self.image_width,
            width=10,
        ).grid(row=4, column=1, sticky="w", pady=5)

        controls = ttk.Frame(settings)
        controls.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(14, 8))
        controls.columnconfigure(0, weight=1)
        self.generate_button = ttk.Button(
            controls,
            text="生成截图",
            command=self.start_generation,
        )
        self.generate_button.grid(row=0, column=1, padx=4)
        ttk.Button(
            controls,
            text="打开输出目录",
            command=self.open_output,
        ).grid(row=0, column=2, padx=4)

        ttk.Label(settings, text="生成结果").grid(
            row=6, column=0, columnspan=3, sticky="w", pady=(10, 4)
        )
        list_frame = ttk.Frame(settings)
        list_frame.grid(row=8, column=0, columnspan=3, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.result_list = tk.Listbox(list_frame, exportselection=False)
        self.result_list.grid(row=0, column=0, sticky="nsew")
        self.result_list.bind("<<ListboxSelect>>", self.show_selected_preview)
        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.result_list.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.result_list.configure(yscrollcommand=scrollbar.set)

        preview = ttk.LabelFrame(outer, text="预览", padding=10)
        preview.grid(row=1, column=1, sticky="nsew")
        preview.columnconfigure(0, weight=1)
        preview.rowconfigure(0, weight=1)
        self.preview_label = ttk.Label(
            preview,
            text="生成截图后，在左侧列表中选择图片进行预览。",
            anchor="center",
            justify="center",
        )
        self.preview_label.grid(row=0, column=0, sticky="nsew")

        ttk.Label(outer, textvariable=self.status, wraplength=1000).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(12, 0)
        )

    def choose_file(self):
        selected = filedialog.askopenfilename(
            title="选择 Python 文件",
            filetypes=[("Python", "*.py"), ("All files", "*.*")],
        )
        if selected:
            self.set_source(Path(selected))

    def choose_folder(self):
        selected = filedialog.askdirectory(title="选择代码文件夹")
        if selected:
            self.set_source(Path(selected))

    def set_source(self, source: Path):
        self.source.set(str(source))
        if not self.output.get().strip():
            base = source.parent if source.is_file() else source
            self.output.set(str(base / "code_screenshots"))

    def choose_output(self):
        selected = filedialog.askdirectory(title="选择截图输出目录")
        if selected:
            self.output.set(selected)

    def validate_settings(self):
        source = Path(self.source.get().strip()).expanduser().resolve()
        output_text = self.output.get().strip()
        if not source.exists():
            raise ValueError("请选择存在的 Python 文件或代码文件夹。")
        if source.is_file() and source.suffix.lower() != ".py":
            raise ValueError("单文件模式仅支持 .py 文件。")
        if not output_text:
            raise ValueError("请选择输出目录。")

        output = Path(output_text).expanduser().resolve()
        lines = self.lines_per_image.get()
        width = self.image_width.get()
        if not 20 <= lines <= 100:
            raise ValueError("每张视觉行数必须在 20 到 100 之间。")
        if not 800 <= width <= 3000:
            raise ValueError("图片宽度必须在 800 到 3000 像素之间。")
        return source, output, lines, width

    def start_generation(self):
        try:
            settings = self.validate_settings()
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("无法生成", str(exc))
            return

        self.generate_button.configure(state="disabled")
        self.status.set("正在生成截图，请稍候…")
        threading.Thread(
            target=self.generate,
            args=settings,
            daemon=True,
        ).start()

    def collect_files(self, source: Path):
        if source.is_file():
            return source.parent, [source]
        files = [
            path
            for path in sorted(source.rglob("*.py"))
            if not renderer.should_ignore(path.relative_to(source))
        ]
        return source, files

    def generate(self, source: Path, output: Path, lines: int, width: int):
        try:
            renderer.VISUAL_LINES_PER_IMAGE = lines
            renderer.IMAGE_WIDTH = width
            output.mkdir(parents=True, exist_ok=True)
            code_root, files = self.collect_files(source)
            if not files:
                raise ValueError("所选位置没有找到可处理的 Python 文件。")

            fonts = renderer.get_fonts()
            generated = []
            for path in files:
                generated.extend(
                    renderer.render_file(path, code_root, output, fonts)
                )
            self.after(0, self.finish_generation, generated, None)
        except Exception as exc:
            self.after(0, self.finish_generation, [], exc)

    def finish_generation(self, generated, error):
        self.generate_button.configure(state="normal")
        if error is not None:
            self.status.set("截图生成失败。")
            messagebox.showerror("生成失败", str(error))
            return

        self.generated = generated
        self.result_list.delete(0, tk.END)
        for path in generated:
            self.result_list.insert(tk.END, path.name)
        self.status.set(f"生成完成：共 {len(generated)} 张，保存在 {self.output.get()}")
        if generated:
            self.result_list.selection_set(0)
            self.result_list.event_generate("<<ListboxSelect>>")

    def show_selected_preview(self, _event=None):
        selection = self.result_list.curselection()
        if not selection or not self.generated:
            return
        path = self.generated[selection[0]]
        image = Image.open(path)
        image.thumbnail((600, 590), Image.Resampling.LANCZOS)
        self.preview_photo = ImageTk.PhotoImage(image)
        self.preview_label.configure(image=self.preview_photo, text="")
        self.status.set(f"正在预览：{path}")

    def open_output(self):
        output_text = self.output.get().strip()
        if not output_text:
            messagebox.showwarning("没有输出目录", "请先选择输出目录。")
            return
        output = Path(output_text).expanduser()
        if not output.is_dir():
            messagebox.showwarning("目录不存在", "请先生成截图。")
            return
        if sys.platform == "darwin":
            subprocess.Popen(["open", str(output)])
        elif os.name == "nt":
            os.startfile(output)
        else:
            subprocess.Popen(["xdg-open", str(output)])


def main():
    app = ScreenshotApp()
    app.mainloop()


if __name__ == "__main__":
    main()
