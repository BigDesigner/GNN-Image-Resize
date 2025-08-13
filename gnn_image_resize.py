#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNN Image Resize
- Çoklu dosya ve klasör seçimi
- Yüzdeye göre veya piksele göre yeniden boyutlandırma
- 72–300 DPI aralığında DPI yazma
- JPG/PNG/WebP/TIFF/BMP/GIF (statik) gibi yaygın formatlar (Pillow desteği kapsamında)
- Oran koruma, EXIF koruma (opsiyon), kalite ayarı (JPEG/WebP)
- LANCZOS (önerilen) dahil çeşitli yeniden örnekleme filtreleri
- İlerleme çubuğu, iptal etme
"""

import os
import sys
import threading
from pathlib import Path
from typing import List, Optional, Tuple

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageOps, UnidentifiedImageError, ExifTags

APP_NAME = "GNN Image Resize"
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif"}

# Pillow EXIF tag id -> name haritası (gerekirse)
EXIF_TAGS = {v: k for k, v in ExifTags.TAGS.items()}

def clamp(n, lo, hi):
    return max(lo, min(hi, n))

def resample_from_name(name: str):
    name = name.upper()
    if name == "NEAREST":
        return Image.NEAREST
    if name == "BILINEAR":
        return Image.BILINEAR
    if name == "BICUBIC":
        return Image.BICUBIC
    # Varsayılan en iyi kalite
    return Image.LANCZOS

def guess_output_ext(fmt_choice: str, src_ext: str) -> str:
    if fmt_choice == "Orijinal":
        return src_ext.lower()
    mapping = {
        "JPEG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
        "TIFF": ".tiff",
        "BMP": ".bmp",
        "GIF": ".gif",
    }
    return mapping.get(fmt_choice, src_ext.lower())

def normalize_mode_for_save(img: Image.Image, out_fmt: str) -> Image.Image:
    # JPEG alfayı desteklemez -> beyaz zeminle birleştir
    if out_fmt.upper() in ("JPEG", "JPG"):
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
            return bg
        elif img.mode != "RGB":
            return img.convert("RGB")
    # Diğer formatlarda genelde dönüştürmeye gerek yok
    return img

def safe_open_image(path: Path) -> Optional[Image.Image]:
    try:
        im = Image.open(str(path))
        im.load()
        return im
    except (UnidentifiedImageError, OSError):
        return None

def oriented(im: Image.Image) -> Image.Image:
    # EXIF Orientation'a göre döndür
    try:
        im = ImageOps.exif_transpose(im)
    except Exception:
        pass
    return im

def compute_new_size(
    im: Image.Image,
    mode: str,
    percent: int,
    width_px: int,
    height_px: int,
    keep_aspect: bool
) -> Tuple[int, int]:
    w, h = im.size
    if mode == "percent":
        scale = max(1, percent) / 100.0
        return max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    else:
        # pixel mode
        target_w = width_px if width_px > 0 else w
        target_h = height_px if height_px > 0 else h
        if keep_aspect:
            # Sadece biri verildiyse diğeri orana göre
            if width_px > 0 and height_px <= 0:
                ratio = target_w / w
                target_h = max(1, int(round(h * ratio)))
            elif height_px > 0 and width_px <= 0:
                ratio = target_h / h
                target_w = max(1, int(round(w * ratio)))
            else:
                # İkisi de verilmişse; kısa kenarı baz alarak orana uydurmak:
                # (Kullanıcı hem w hem h girmişse oran koruma açıkken,
                #  orana en yakın değer setlenecek)
                src_ratio = w / h
                tgt_ratio = target_w / target_h
                if tgt_ratio > src_ratio:
                    # genişlik fazla -> yükseklik baz
                    target_w = int(round(target_h * src_ratio))
                else:
                    # yükseklik fazla -> genişlik baz
                    target_h = int(round(target_w / src_ratio))
        return max(1, target_w), max(1, target_h)

def save_image(
    im: Image.Image,
    out_path: Path,
    out_fmt_choice: str,
    dpi: Optional[int],
    keep_exif: bool,
    quality: int
):
    params = {}
    out_fmt = None

    if out_fmt_choice == "Orijinal":
        # Pillow, formatı uzantıdan tahmin ediyor
        out_fmt = None
    else:
        out_fmt = out_fmt_choice

    # DPI
    if dpi:
        dpi_val = (dpi, dpi)
        params["dpi"] = dpi_val

    # JPEG/WebP kalite
    if out_fmt_choice in ("JPEG", "WEBP") or out_path.suffix.lower() in (".jpg", ".jpeg", ".webp"):
        params["quality"] = clamp(quality, 1, 100)
        if out_fmt_choice == "JPEG" or out_path.suffix.lower() in (".jpg", ".jpeg"):
            # Dosya boyutunu makul tutmak için optimize
            params["optimize"] = True
            params["subsampling"] = "keep"  # Pillow>=10 için uygun seçenek

    # EXIF
    if keep_exif:
        try:
            exif_bytes = im.info.get("exif", None)
            if exif_bytes:
                params["exif"] = exif_bytes
        except Exception:
            pass

    im.save(str(out_path), format=out_fmt, **params)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("880x640")
        self.minsize(820, 560)

        self.files: List[Path] = []
        self.stop_flag = False
        self.worker: Optional[threading.Thread] = None

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        # Üst: Dosya seçimleri
        top = ttk.LabelFrame(self, text="Girdi")
        top.pack(fill="x", **pad)

        btn_add_files = ttk.Button(top, text="Dosya Ekle", command=self.add_files)
        btn_add_folder = ttk.Button(top, text="Klasör Ekle", command=self.add_folder)
        btn_clear = ttk.Button(top, text="Listeyi Temizle", command=self.clear_list)

        btn_add_files.grid(row=0, column=0, **pad)
        btn_add_folder.grid(row=0, column=1, **pad)
        btn_clear.grid(row=0, column=2, **pad)

        self.tree = ttk.Treeview(self, columns=("path", "size"), show="headings", height=12)
        self.tree.heading("path", text="Dosya Yolu")
        self.tree.heading("size", text="Boyut (px)")
        self.tree.column("path", width=640, anchor="w")
        self.tree.column("size", width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, **pad)

        # Orta: Ayarlar
        mid = ttk.LabelFrame(self, text="Ayarlar")
        mid.pack(fill="x", **pad)

        # Boyutlandırma modu
        self.mode_var = tk.StringVar(value="percent")
        rb1 = ttk.Radiobutton(mid, text="Yüzde (%)", variable=self.mode_var, value="percent", command=self._toggle_mode)
        rb2 = ttk.Radiobutton(mid, text="Piksel (px)", variable=self.mode_var, value="pixel", command=self._toggle_mode)
        rb1.grid(row=0, column=0, sticky="w", **pad)
        rb2.grid(row=0, column=1, sticky="w", **pad)

        # Yüzde
        ttk.Label(mid, text="Yüzde:").grid(row=1, column=0, sticky="e", **pad)
        self.percent_var = tk.IntVar(value=50)
        self.ent_percent = ttk.Spinbox(mid, from_=1, to=1000, textvariable=self.percent_var, width=6)
        self.ent_percent.grid(row=1, column=1, sticky="w", **pad)

        # Piksel
        ttk.Label(mid, text="Genişlik (px):").grid(row=1, column=2, sticky="e", **pad)
        self.width_var = tk.IntVar(value=1920)
        self.ent_width = ttk.Spinbox(mid, from_=1, to=100000, textvariable=self.width_var, width=8)
        self.ent_width.grid(row=1, column=3, sticky="w", **pad)

        ttk.Label(mid, text="Yükseklik (px):").grid(row=1, column=4, sticky="e", **pad)
        self.height_var = tk.IntVar(value=1080)
        self.ent_height = ttk.Spinbox(mid, from_=1, to=100000, textvariable=self.height_var, width=8)
        self.ent_height.grid(row=1, column=5, sticky="w", **pad)

        self.keep_aspect_var = tk.BooleanVar(value=True)
        chk_aspect = ttk.Checkbutton(mid, text="Oranı Koru", variable=self.keep_aspect_var)
        chk_aspect.grid(row=1, column=6, sticky="w", **pad)

        # DPI
        ttk.Label(mid, text="DPI (72–300):").grid(row=2, column=0, sticky="e", **pad)
        self.dpi_var = tk.IntVar(value=300)
        self.ent_dpi = ttk.Spinbox(mid, from_=72, to=300, textvariable=self.dpi_var, width=6)
        self.ent_dpi.grid(row=2, column=1, sticky="w", **pad)

        # Çıktı formatı
        ttk.Label(mid, text="Çıktı Formatı:").grid(row=2, column=2, sticky="e", **pad)
        self.format_var = tk.StringVar(value="Orijinal")
        fmt_combo = ttk.Combobox(mid, textvariable=self.format_var, state="readonly",
                                 values=["Orijinal", "JPEG", "PNG", "WEBP", "TIFF", "BMP", "GIF"], width=10)
        fmt_combo.grid(row=2, column=3, sticky="w", **pad)

        # Kalite (JPEG/WEBP)
        ttk.Label(mid, text="Kalite (1–100):").grid(row=2, column=4, sticky="e", **pad)
        self.quality_var = tk.IntVar(value=90)
        self.ent_quality = ttk.Spinbox(mid, from_=1, to=100, textvariable=self.quality_var, width=6)
        self.ent_quality.grid(row=2, column=5, sticky="w", **pad)

        # Filtre
        ttk.Label(mid, text="Filtre:").grid(row=2, column=6, sticky="e", **pad)
        self.filter_var = tk.StringVar(value="LANCZOS")
        filter_combo = ttk.Combobox(mid, textvariable=self.filter_var, state="readonly",
                                    values=["LANCZOS", "BICUBIC", "BILINEAR", "NEAREST"], width=10)
        filter_combo.grid(row=2, column=7, sticky="w", **pad)

        # EXIF
        self.keep_exif_var = tk.BooleanVar(value=True)
        chk_exif = ttk.Checkbutton(mid, text="EXIF koru (mümkünse)", variable=self.keep_exif_var)
        chk_exif.grid(row=3, column=0, sticky="w", columnspan=2, **pad)

        # Çıktı Klasörü
        out = ttk.LabelFrame(self, text="Çıktı")
        out.pack(fill="x", **pad)

        ttk.Label(out, text="Çıktı Klasörü:").grid(row=0, column=0, sticky="e", **pad)
        self.out_dir_var = tk.StringVar(value=str(Path.cwd() / "resized"))
        ent_out = ttk.Entry(out, textvariable=self.out_dir_var, width=70)
        ent_out.grid(row=0, column=1, sticky="we", **pad)
        btn_out = ttk.Button(out, text="Seç...", command=self.select_out_dir)
        btn_out.grid(row=0, column=2, **pad)

        out.columnconfigure(1, weight=1)

        # Alt: Başlat / Durdur / Durum
        bottom = ttk.Frame(self)
        bottom.pack(fill="x", **pad)

        self.btn_start = ttk.Button(bottom, text="Başlat", command=self.start)
        self.btn_stop = ttk.Button(bottom, text="Durdur", command=self.stop, state="disabled")
        self.btn_start.pack(side="left", padx=6)
        self.btn_stop.pack(side="left", padx=6)

        self.progress = ttk.Progressbar(bottom, mode="determinate")
        self.progress.pack(fill="x", expand=True, padx=6)

        self.status_var = tk.StringVar(value="Hazır.")
        lbl_status = ttk.Label(bottom, textvariable=self.status_var, anchor="w")
        lbl_status.pack(fill="x", padx=6, pady=4)

        self._toggle_mode()

    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Resim dosyalarını seç",
            filetypes=[("Resimler", "*.jpg;*.jpeg;*.png;*.webp;*.bmp;*.tif;*.tiff;*.gif"),
                       ("Tümü", "*.*")]
        )
        for p in paths:
            self._try_add(Path(p))

    def add_folder(self):
        d = filedialog.askdirectory(title="Klasör seç")
        if not d:
            return
        base = Path(d)
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTS:
                self._try_add(path)

    def _try_add(self, path: Path):
        if path.suffix.lower() not in SUPPORTED_EXTS:
            return
        if path not in self.files:
            self.files.append(path)
            size_txt = self._probe_size(path)
            self.tree.insert("", "end", values=(str(path), size_txt))

    def _probe_size(self, path: Path) -> str:
        im = safe_open_image(path)
        if im is None:
            return "?"
        return f"{im.width}x{im.height}"

    def clear_list(self):
        self.files.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)

    def select_out_dir(self):
        d = filedialog.askdirectory(title="Çıktı klasörü seç")
        if d:
            self.out_dir_var.set(d)

    def _toggle_mode(self):
        mode = self.mode_var.get()
        if mode == "percent":
            self.ent_percent.configure(state="normal")
            self.ent_width.configure(state="disabled")
            self.ent_height.configure(state="disabled")
        else:
            self.ent_percent.configure(state="disabled")
            self.ent_width.configure(state="normal")
            self.ent_height.configure(state="normal")

    def lock_ui(self, locked: bool):
        widgets = [
            self.btn_start, self.btn_stop, self.ent_percent, self.ent_width,
            self.ent_height
        ]
        if locked:
            self.btn_start.configure(state="disabled")
            self.btn_stop.configure(state="normal")
        else:
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")

    def start(self):
        if not self.files:
            messagebox.showwarning(APP_NAME, "Önce resim ekleyin.")
            return
        out_dir = Path(self.out_dir_var.get())
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Çıktı klasörü oluşturulamadı:\n{e}")
            return

        self.stop_flag = False
        self.lock_ui(True)
        self.progress.configure(maximum=len(self.files), value=0)
        self.status_var.set("İşlem başlatıldı...")

        args = dict(
            mode=self.mode_var.get(),
            percent=int(self.percent_var.get()),
            width_px=int(self.width_var.get()),
            height_px=int(self.height_var.get()),
            keep_aspect=bool(self.keep_aspect_var.get()),
            dpi=clamp(int(self.dpi_var.get()), 72, 300),
            fmt=self.format_var.get(),
            keep_exif=bool(self.keep_exif_var.get()),
            quality=int(self.quality_var.get()),
            resample=self.filter_var.get(),
            out_dir=out_dir
        )

        self.worker = threading.Thread(target=self._process_all, kwargs=args, daemon=True)
        self.worker.start()
        self.after(200, self._poll_worker)

    def stop(self):
        self.stop_flag = True
        self.status_var.set("Durduruluyor...")

    def _poll_worker(self):
        if self.worker and self.worker.is_alive():
            self.after(200, self._poll_worker)
        else:
            self.lock_ui(False)
            if not self.stop_flag:
                self.status_var.set("Tamamlandı.")
            else:
                self.status_var.set("Durduruldu.")

    def _process_all(
        self,
        mode: str,
        percent: int,
        width_px: int,
        height_px: int,
        keep_aspect: bool,
        dpi: int,
        fmt: str,
        keep_exif: bool,
        quality: int,
        resample: str,
        out_dir: Path
    ):
        errs = 0
        rsmpl = resample_from_name(resample)
        for idx, path in enumerate(self.files, start=1):
            if self.stop_flag:
                break
            try:
                im = safe_open_image(path)
                if im is None:
                    raise ValueError("Açılamadı veya desteklenmiyor.")

                im = oriented(im)
                new_w, new_h = compute_new_size(
                    im, mode, percent, width_px, height_px, keep_aspect
                )
                if (new_w, new_h) != im.size:
                    im = im.resize((new_w, new_h), rsmpl)

                # Çıktı dosya adı
                out_ext = guess_output_ext(fmt, path.suffix)
                out_name = f"{path.stem}_{new_w}x{new_h}{out_ext}"
                out_path = out_dir / out_name

                im_to_save = normalize_mode_for_save(im, fmt if fmt != "Orijinal" else out_ext.replace(".", ""))

                save_image(
                    im_to_save,
                    out_path,
                    fmt if fmt != "Orijinal" else None,
                    dpi,
                    keep_exif,
                    quality
                )
            except Exception as e:
                errs += 1
                print(f"Hata: {path} -> {e}", file=sys.stderr)
            finally:
                self.progress.step(1)
                self.status_var.set(f"{idx}/{len(self.files)} işlendi. Hata: {errs}")

def main():
    # Pillow + Tk birlikte PyInstaller'da bazen arama problemi yaşar:
    # --hidden-import=PIL._tkinter_finder parametresi tavsiye edilir.
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
