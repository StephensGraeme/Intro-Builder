#!/usr/bin/env python3
"""
Intro Builder  v1.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, font as tkfont
import subprocess
import threading
import os
import sys
import re
import shutil
import json
import base64
import queue
from pathlib import Path

# ──────────────────────────────────────────────
# Dark theme
# ──────────────────────────────────────────────
BG       = "#0e0e12"
SURFACE  = "#18181f"
CARD     = "#22222d"
BORDER   = "#2e2e3a"
ACCENT   = "#e05a2b"
ACCENT2  = "#f08040"
TEXT     = "#e8e8f0"
SUBTEXT  = "#8888aa"
SUCCESS  = "#3ecf74"
WARNING  = "#f0b040"
DANGER   = "#e05050"
ENTRY_BG = "#1a1a24"

FONT_UI      = ("Courier New", 10)
FONT_LABEL   = ("Courier New", 9)
FONT_TITLE   = ("Courier New", 17, "bold")
FONT_SECTION = ("Courier New", 10, "bold")
FONT_MONO    = ("Courier New", 9)

# ──────────────────────────────────────────────
# Helper widgets
# ──────────────────────────────────────────────
def styled_frame(parent, **kw):
    kw.setdefault("bg", CARD)
    kw.setdefault("relief", "flat")
    return tk.Frame(parent, **kw)

def styled_label(parent, text, size=9, bold=False, color=TEXT, **kw):
    weight = "bold" if bold else "normal"
    kw.setdefault("bg", parent.cget("bg"))
    return tk.Label(parent, text=text,
                    font=("Courier New", size, weight),
                    fg=color, **kw)

def styled_entry(parent, textvariable=None, width=30, **kw):
    return tk.Entry(parent, textvariable=textvariable, width=width,
                    bg=ENTRY_BG, fg=TEXT, insertbackground=ACCENT,
                    relief="flat", font=FONT_UI,
                    highlightbackground=BORDER, highlightcolor=ACCENT,
                    highlightthickness=1, **kw)

def styled_button(parent, text, command, accent=False, danger=False,
                  small=False, **kw):
    fg   = BG if accent else TEXT
    bg   = ACCENT if accent else (DANGER if danger else BORDER)
    size = 8 if small else 10
    b = tk.Button(parent, text=text, command=command,
                  bg=bg, fg=fg, activebackground=ACCENT2,
                  activeforeground=BG, relief="flat",
                  font=("Courier New", size, "bold"),
                  cursor="hand2", padx=10, pady=4, **kw)
    b.bind("<Enter>", lambda e, _bg=bg: b.config(
        bg=ACCENT2 if (accent or not danger) else "#ff6060"))
    b.bind("<Leave>", lambda e, _bg=bg: b.config(bg=_bg))
    return b

def styled_spinbox(parent, var, lo, hi, width=7, step=1, **kw):
    return tk.Spinbox(parent, from_=lo, to=hi, increment=step,
                      textvariable=var, width=width,
                      bg=ENTRY_BG, fg=TEXT, buttonbackground=BORDER,
                      relief="flat", font=FONT_UI,
                      insertbackground=ACCENT,
                      highlightbackground=BORDER, highlightcolor=ACCENT,
                      highlightthickness=1, **kw)

def section_header(parent, title):
    frame = tk.Frame(parent, bg=BG)
    frame.pack(fill="x", pady=(14, 3))
    bar = tk.Frame(frame, bg=ACCENT, width=3, height=18)
    bar.pack(side="left", padx=(0, 8))
    bar.pack_propagate(False)
    tk.Label(frame, text=title, font=FONT_SECTION,
             fg=ACCENT, bg=BG).pack(side="left")

def hline(parent):
    tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=6)

def _safe_getext(path):
    try:
        return path.lower().rsplit(".", 1)[-1]
    except Exception:
        return ""


# ──────────────────────────────────────────────
# FilePicker
# ──────────────────────────────────────────────
class FilePicker(tk.Frame):
    def __init__(self, parent, label, filetypes, initial_dir=None, **kw):
        super().__init__(parent, bg=CARD, **kw)
        self.var = tk.StringVar()
        self._ft  = filetypes
        self._id  = initial_dir
        styled_label(self, label, color=SUBTEXT).pack(anchor="w")
        row = tk.Frame(self, bg=CARD); row.pack(fill="x", pady=(2, 0))
        self.entry = styled_entry(row, textvariable=self.var, width=52)
        self.entry.pack(side="left", fill="x", expand=True)
        styled_button(row, " BROWSE", self._browse, small=True
                      ).pack(side="left", padx=(6, 0))

    def _browse(self):
        p = filedialog.askopenfilename(
            initialdir=self._id or str(Path.home()),
            filetypes=self._ft)
        if p: self.var.set(p)

    def get(self):  return self.var.get().strip()
    def set(self, v): self.var.set(v)

# ──────────────────────────────────────────────
# EffectToggle
# ──────────────────────────────────────────────
class EffectToggle(tk.Frame):
    def __init__(self, parent, label, desc="", default=True, **kw):
        super().__init__(parent, bg=CARD, **kw)
        self.var = tk.BooleanVar(value=default)
        inner = tk.Frame(self, bg=CARD, padx=8, pady=0)
        inner.pack(fill="x")
        tk.Checkbutton(inner, variable=self.var, bg=CARD,
                       activebackground=CARD, selectcolor=ENTRY_BG,
                       fg=ACCENT, relief="flat", cursor="hand2"
                       ).pack(side="left")
        col = tk.Frame(inner, bg=CARD); col.pack(side="left")
        tk.Label(col, text=label, font=("Courier New", 9, "bold"),
                 fg=TEXT, bg=CARD).pack(anchor="w")
        if desc:
            tk.Label(col, text=desc, font=("Courier New", 8),
                     fg=SUBTEXT, bg=CARD).pack(anchor="w")

    def get(self): return self.var.get()

# ──────────────────────────────────────────────
# SliderRow  — label + scale + value readout
# ──────────────────────────────────────────────
class SliderRow(tk.Frame):
    def __init__(self, parent, label, var, lo, hi,
                 resolution=0.1, fmt="{:.1f}", length=180, **kw):
        super().__init__(parent, bg=CARD, **kw)
        self.var = var; self.fmt = fmt
        top = tk.Frame(self, bg=CARD); top.pack(fill="x")
        styled_label(top, label, color=SUBTEXT, size=8).pack(side="left")
        self.val_lbl = styled_label(top, self._fv(), color=ACCENT, size=8)
        self.val_lbl.pack(side="right")
        tk.Scale(self, from_=lo, to=hi, resolution=resolution,
                 orient="horizontal", variable=var,
                 length=length, showvalue=False,
                 bg=CARD, fg=TEXT, troughcolor=ENTRY_BG,
                 highlightbackground=CARD, activebackground=ACCENT,
                 sliderlength=14,
                 command=lambda _: self.val_lbl.config(text=self._fv())
                 ).pack(fill="x")

    def _fv(self): return self.fmt.format(self.var.get())

# ──────────────────────────────────────────────
# ColourButton — swatch + choose
# ──────────────────────────────────────────────
class ColourButton(tk.Frame):
    """Combo: entry/combobox + colour-chooser swatch button."""
    def __init__(self, parent, var, presets=None, width=10, **kw):
        super().__init__(parent, bg=CARD, **kw)
        self.var = var
        self.swatch = tk.Label(self, width=2, bg=self._safe_colour(),
                               relief="flat", cursor="hand2")
        self.swatch.pack(side="left", padx=(0, 3))
        self.swatch.bind("<Button-1>", self._choose)
        values = presets or []
        self.combo = ttk.Combobox(self, textvariable=var,
                                  values=values, width=width)
        self.combo.pack(side="left")
        var.trace_add("write", lambda *_: self._refresh())

    def _safe_colour(self):
        c = self.var.get().strip()
        try:
            self.winfo_rgb(c); return c
        except Exception:
            return "#888888"

    def _refresh(self):
        self.swatch.config(bg=self._safe_colour())

    def _choose(self, _=None):
        current = self._safe_colour()
        result  = colorchooser.askcolor(color=current,
                                        title="Choose colour")
        if result and result[1]:
            self.var.set(result[1])

# ──────────────────────────────────────────────
# Main Application
# ──────────────────────────────────────────────
class IntroBuilderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Intro Builder  v1.0")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(860, 820)

        self.base_dir  = Path(__file__).parent.resolve()
        self.audio_dir = self.base_dir / "audio"
        self.bg_dir    = self.base_dir / "backgrounds"
        # Create companion folders if they don't exist yet
        for _d in (self.audio_dir, self.bg_dir):
            try:
                _d.mkdir(parents=False, exist_ok=True)
            except Exception:
                pass

        self.tmp_bg             = "/tmp/prm_bg.mp4"
        self.tmp_audio          = "/tmp/prm_audio.m4a"
        self.tmp_audio_pcm      = "/tmp/prm_audio_pcm.wav"   # safe intermediate
        self.tmp_audio_filtered = "/tmp/prm_audio_fx.m4a"
        self._output_file       = None

        self._ui_queue = queue.Queue()
        self._build_ui()
        self._apply_ttk_style()
        self._poll_ui_queue()

    def _is_animated_gif(self,path):
        if not path or not path.lower().endswith(".gif"): return False
        try:
            pr=subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=nb_frames","-of","default=nokey=1:noprint_wrappers=1",path],capture_output=True,text=True,timeout=8)
            nb=pr.stdout.strip()
            return int(nb)>1 if nb.isdigit() else True
        except Exception: return True

    def _codec_map(self,fmt,preset,crf):
        if fmt=="mp4_h264_aac":
            vcodec=["-c:v","libx264","-preset",preset,"-crf",str(crf),"-pix_fmt","yuv420p","-movflags","+faststart"]; acodec=["-c:a","aac","-b:a","192k"]
        elif fmt=="mp4_h265_aac":
            vcodec=["-c:v","libx265","-preset",preset,"-crf",str(max(18,crf+4)),"-tag:v","hvc1","-pix_fmt","yuv420p","-movflags","+faststart"]; acodec=["-c:a","aac","-b:a","192k"]
        elif fmt=="webm_vp9_opus":
            vcodec=["-c:v","libvpx-vp9","-b:v","0","-crf",str(min(40,max(20,crf)))]; acodec=["-c:a","libopus","-b:a","160k"]
        elif fmt=="mov_prores":
            vcodec=["-c:v","prores_ks","-profile:v","3","-pix_fmt","yuv422p10le"]; acodec=["-c:a","pcm_s16le"]
        elif fmt=="mkv_h265_aac":
            vcodec=["-c:v","libx265","-preset",preset,"-crf",str(max(18,crf+4))]; acodec=["-c:a","aac","-b:a","192k"]
        else:
            vcodec=["-c:v","libx264","-preset",preset,"-crf",str(crf),"-pix_fmt","yuv420p","-movflags","+faststart"]; acodec=["-c:a","aac","-b:a","192k"]
        return vcodec,acodec


    # ── UI scaffold ───────────────────────────────────────────────────
    def _poll_ui_queue(self):
        """Drain pending UI updates on the main thread every 40 ms."""
        try:
            while True:
                self._ui_queue.get_nowait()()
        except queue.Empty:
            pass
        self.after(40, self._poll_ui_queue)

    def _ui(self, fn):
        """Queue fn() for execution on the main thread (thread-safe)."""
        self._ui_queue.put(fn)

    def _make_scrollable_tab(self, nb, title):
        """Return (inner_frame, canvas) for a scrollable notebook tab."""
        outer = tk.Frame(nb, bg=BG)
        nb.add(outer, text=f"  {title}  ")
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0, bd=0)
        vsb    = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner  = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
                   lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e, c=canvas, w=win_id: c.itemconfig(w, width=e.width))
        def _mw(event, c=canvas):
            if event.num == 4:   c.yview_scroll(-1, "units")
            elif event.num == 5: c.yview_scroll(1, "units")
            else:                c.yview_scroll(-1*(event.delta//120), "units")
        canvas.bind("<Enter>",
                    lambda e, c=canvas, fn=_mw: (
                        c.bind_all("<MouseWheel>", fn),
                        c.bind_all("<Button-4>",   fn),
                        c.bind_all("<Button-5>",   fn)))
        canvas.bind("<Leave>",
                    lambda e, c=canvas: (
                        c.unbind_all("<MouseWheel>"),
                        c.unbind_all("<Button-4>"),
                        c.unbind_all("<Button-5>")))
        return inner, canvas

    def _build_ui(self):
        # ── Title bar ─────────────────────────────────────────────────
        tb = tk.Frame(self, bg=BG); tb.pack(fill="x", padx=20, pady=(16, 0))
        tk.Label(tb, text="[>]", font=("Courier New", 20, "bold"),
                 fg=ACCENT, bg=BG).pack(side="left", padx=(0, 10))
        tk.Label(tb, text="INTRO BUILDER",
                 font=FONT_TITLE, fg=TEXT, bg=BG).pack(side="left")
        tk.Label(tb, text="v1.0", font=("Courier New", 8),
                 fg=SUBTEXT, bg=BG).pack(side="left", padx=8, pady=(5, 0))
        styled_button(tb, "[ LOAD SETTINGS FROM FILE ]",
                      self._load_settings_from_file, small=True
                      ).pack(side="right")
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(8, 0))

        # ── Notebook tabs ──────────────────────────────────────────────
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=6, pady=(4, 0))
        self._notebook = nb

        t1, c1 = self._make_scrollable_tab(nb, "Source & Output")
        t2, c2 = self._make_scrollable_tab(nb, "Text & Overlays")
        t3, c3 = self._make_scrollable_tab(nb, "Video & Colour")
        t4, c4 = self._make_scrollable_tab(nb, "Audio")
        # Keep a reference to the first tab canvas for scroll-to-bottom on build
        self._tab_canvases = [c1, c2, c3, c4]

        self._build_form(t1, t2, t3, t4)

        # ── Permanent log panel (always visible below tabs) ────────────
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        self._build_log_panel()
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        self._build_bottom_bar()

    # ── Form (split across four tab parent frames) ────────────────────
    def _build_form(self, t1, t2, t3, t4):
        pad = dict(padx=20)

        # ═ SOURCE FILES ══════════════════════════════════════════════
        section_header(t1, "SOURCE FILES")
        fc = styled_frame(t1, padx=14, pady=12)
        fc.pack(fill="x", **pad, pady=(0, 4))

        self.bg_picker = FilePicker(
            fc, "Background  (video or image: .mp4 .mov .avi .mkv .jpg .png .gif)",
            [("Media", "*.mp4 *.mov *.avi *.mkv *.webm *.jpg *.jpeg *.png *.gif"),
             ("All", "*")],
            initial_dir=str(self.bg_dir) if self.bg_dir.exists() else None)
        self.bg_picker.pack(fill="x", pady=(0, 4))

        # Aspect ratio preserve option (for graphic/image files)
        ar_row = tk.Frame(fc, bg=CARD); ar_row.pack(fill="x", pady=(0, 4))
        self.preserve_ar_var = tk.BooleanVar(value=True)
        tk.Checkbutton(ar_row, variable=self.preserve_ar_var,
                       bg=CARD, fg=ACCENT, selectcolor=ENTRY_BG,
                       activebackground=CARD, cursor="hand2"
                       ).pack(side="left")
        tk.Label(ar_row, text="Preserve aspect ratio",
                 font=("Courier New", 9, "bold"), fg=TEXT, bg=CARD
                 ).pack(side="left")
        # Padding colour — shown only when preserve_ar is ticked
        self._pad_col_lbl  = styled_label(ar_row, "   Padding colour:",
                                          color=SUBTEXT)
        self._pad_col_lbl.pack(side="left")
        self.pad_color_var = tk.StringVar(value="black")
        self._pad_col_btn  = ColourButton(ar_row, self.pad_color_var,
                     presets=["black", "white", "#111111", "#222222",
                               "gray", "#001020", "#200010"],
                     width=8)
        self._pad_col_btn.pack(side="left", padx=(4, 0))

        def _on_preserve_ar(*_):
            if self.preserve_ar_var.get():
                self._pad_col_lbl.pack(side="left")
                self._pad_col_btn.pack(side="left", padx=(4, 0))
            else:
                self._pad_col_lbl.pack_forget()
                self._pad_col_btn.pack_forget()
        self.preserve_ar_var.trace_add("write", _on_preserve_ar)

        # Audio mode — order: background | provided | silent
        # "background" is default for video; "silent" forced for images.
        styled_label(fc, "Audio Source", color=SUBTEXT).pack(anchor="w")
        self.audio_source_var = tk.StringVar(value="background")
        amode_row = tk.Frame(fc, bg=CARD); amode_row.pack(fill="x", padx=8, pady=2)
        self._rb_bg  = tk.Radiobutton(amode_row,
                           text="Original background track", value="background",
                           variable=self.audio_source_var,
                           bg=CARD, fg=TEXT, selectcolor=ENTRY_BG,
                           activebackground=CARD, activeforeground=ACCENT,
                           font=FONT_LABEL, cursor="hand2")
        self._rb_bg.pack(side="left", padx=(0, 16))
        self._rb_prov = tk.Radiobutton(amode_row,
                           text="Provided track", value="provided",
                           variable=self.audio_source_var,
                           bg=CARD, fg=TEXT, selectcolor=ENTRY_BG,
                           activebackground=CARD, activeforeground=ACCENT,
                           font=FONT_LABEL, cursor="hand2")
        self._rb_prov.pack(side="left", padx=(0, 16))
        self._rb_silent = tk.Radiobutton(amode_row,
                           text="Silent (no audio)", value="silent",
                           variable=self.audio_source_var,
                           bg=CARD, fg=TEXT, selectcolor=ENTRY_BG,
                           activebackground=CARD, activeforeground=ACCENT,
                           font=FONT_LABEL, cursor="hand2")
        self._rb_silent.pack(side="left", padx=(0, 16))

        self.audio_picker = FilePicker(
            fc, "Audio file  (.mp3  .wav  .m4a  .aac  .flac)",
            [("Audio", "*.mp3 *.wav *.m4a *.aac *.flac"), ("All", "*")],
            initial_dir=str(self.audio_dir) if self.audio_dir.exists() else None)
        self.audio_picker.pack(fill="x", pady=(6, 0))
        # Auto-select 'Provided track' radio when a file is chosen
        self.audio_picker.var.trace_add(
            "write",
            lambda *_: self.audio_source_var.set("provided")
            if self.audio_picker.get() else None)

        # Auto-update audio mode when background file changes
        self.bg_picker.var.trace_add("write", self._on_bg_changed)
        self.bg_picker.var.trace_add("write", lambda *_: self.after(100, self._probe_bg_duration))

        # ═ DURATION & OUTPUT ══════════════════════════════════════════
        section_header(t1, "DURATION & OUTPUT")
        dc = styled_frame(t1, padx=14, pady=12)
        dc.pack(fill="x", **pad, pady=(0, 4))
        dr = tk.Frame(dc, bg=CARD); dr.pack(fill="x")

        # Duration
        col_dur = tk.Frame(dr, bg=CARD); col_dur.pack(side="left", padx=(0, 24))
        styled_label(col_dur, "Duration (s)", color=SUBTEXT).pack(anchor="w")
        self.duration_var = tk.IntVar(value=8)
        self._dur_spinbox = styled_spinbox(col_dur, self.duration_var, 3, 300, width=6, step=1)
        self._dur_spinbox.pack(anchor="w", pady=(2, 0))

        # Background clip range: Start / End
        col_bgs = tk.Frame(dr, bg=CARD); col_bgs.pack(side="left", padx=(0, 16))
        styled_label(col_bgs, "BG Start (s)", color=SUBTEXT).pack(anchor="w")
        self.seek_var = tk.DoubleVar(value=0.0)
        styled_spinbox(col_bgs, self.seek_var, 0.0, 3600.0, width=7, step=0.5
                       ).pack(anchor="w", pady=(2, 0))

        col_bge = tk.Frame(dr, bg=CARD); col_bge.pack(side="left", padx=(0, 24))
        styled_label(col_bge, "BG End (s)", color=SUBTEXT).pack(anchor="w")
        self.bg_end_var = tk.DoubleVar(value=0.0)
        bge_row = tk.Frame(col_bge, bg=CARD); bge_row.pack(anchor="w", pady=(2, 0))
        styled_spinbox(bge_row, self.bg_end_var, 0.0, 3600.0, width=7, step=0.5
                       ).pack(side="left")
        styled_label(bge_row, "  (0 = full)", color=SUBTEXT, size=8
                     ).pack(side="left")

        col3 = tk.Frame(dr, bg=CARD); col3.pack(side="left", fill="x", expand=True)
        styled_label(col3, "Output Filename", color=SUBTEXT).pack(anchor="w")
        self.out_name_var = tk.StringVar(value="intro_output")
        styled_entry(col3, textvariable=self.out_name_var, width=32
                     ).pack(anchor="w", pady=(2, 0))

        # Provided track range: Start / End — shown only when "Provided track" selected
        self._audio_range_row = tk.Frame(dc, bg=CARD)
        # (not packed yet — hidden until "provided" is selected)
        ar_inner = tk.Frame(self._audio_range_row, bg=CARD)
        ar_inner.pack(fill="x")

        styled_label(ar_inner, "Track Start (s):", color=SUBTEXT
                     ).pack(side="left", padx=(0, 6))
        self.audio_seek_var = tk.DoubleVar(value=0.0)
        styled_spinbox(ar_inner, self.audio_seek_var, 0.0, 3600.0,
                       width=7, step=0.5).pack(side="left", padx=(0, 24))

        styled_label(ar_inner, "Track End (s):", color=SUBTEXT
                     ).pack(side="left", padx=(0, 6))
        self.audio_end_var = tk.DoubleVar(value=0.0)
        styled_spinbox(ar_inner, self.audio_end_var, 0.0, 3600.0,
                       width=7, step=0.5).pack(side="left", padx=(0, 8))
        styled_label(ar_inner, "(0 = play to end / loop to duration)",
                     color=SUBTEXT, size=8).pack(side="left")

        # Show/hide when audio source changes
        def _on_audio_source(*_):
            if self.audio_source_var.get() == "provided":
                self._audio_range_row.pack(fill="x", pady=(8, 0))
            else:
                self._audio_range_row.pack_forget()
        self.audio_source_var.trace_add("write", _on_audio_source)

        self.out_format_var=tk.StringVar(value="mp4_h264_aac")
        fmt_row=tk.Frame(dc,bg=CARD); fmt_row.pack(fill="x",pady=(8,0))
        styled_label(fmt_row,"Output Format",color=SUBTEXT).pack(side="left",padx=(0,6))
        ttk.Combobox(fmt_row,textvariable=self.out_format_var,width=22,values=["mp4_h264_aac","mp4_h265_aac","webm_vp9_opus","mov_prores","mkv_h265_aac","gif_animated"]).pack(side="left")

        # Metadata embed toggle
        meta_row = tk.Frame(dc, bg=CARD); meta_row.pack(fill="x", pady=(6, 0))
        self.save_metadata_var = tk.BooleanVar(value=True)
        tk.Checkbutton(meta_row, variable=self.save_metadata_var,
                       bg=CARD, fg=ACCENT, selectcolor=ENTRY_BG,
                       activebackground=CARD, cursor="hand2"
                       ).pack(side="left")
        tk.Label(meta_row, text="Embed settings in output file",
                 font=("Courier New", 9, "bold"), fg=TEXT, bg=CARD
                 ).pack(side="left")
        styled_label(meta_row,
                     "  (saves all settings as metadata in the output file)",
                     color=SUBTEXT).pack(side="left")

        # ═ TEXT & OVERLAYS ════════════════════════════════════════════
        section_header(t2, "TEXT & OVERLAYS")
        tc = styled_frame(t2, padx=14, pady=12)
        tc.pack(fill="x", **pad, pady=(0, 4))

        styled_label(tc, "Overlay Text", color=SUBTEXT).pack(anchor="w")
        styled_label(tc, "  (multi-line: press Enter for a new line)",
                     color=SUBTEXT, size=8).pack(anchor="w")
        self._text_widget = tk.Text(
            tc, height=3, width=62,
            bg=ENTRY_BG, fg=TEXT, insertbackground=ACCENT,
            relief="flat", font=FONT_UI, wrap="word",
            highlightbackground=BORDER, highlightcolor=ACCENT,
            highlightthickness=1)
        self._text_widget.pack(anchor="w", pady=(2, 8))
        self._text_widget.insert("1.0", "")
        # Compatibility shim: self.text_var.get() still works elsewhere
        class _TextVarShim:
            def __init__(self, widget):
                self._w = widget
            def get(self):
                return self._w.get("1.0", "end-1c")
            def set(self, v):
                self._w.delete("1.0", "end")
                self._w.insert("1.0", v)
        self.text_var = _TextVarShim(self._text_widget)

        # Font row
        fr = tk.Frame(tc, bg=CARD); fr.pack(fill="x")

        col_f = tk.Frame(fr, bg=CARD); col_f.pack(side="left", padx=(0, 16))
        styled_label(col_f, "Font", color=SUBTEXT).pack(anchor="w")
        self.font_var = tk.StringVar(value="Impact")
        avail = sorted(f for f in tkfont.families() if not f.startswith("@"))
        ttk.Combobox(col_f, textvariable=self.font_var,
                     values=avail, width=18).pack(anchor="w", pady=(2, 0))

        col_sz = tk.Frame(fr, bg=CARD); col_sz.pack(side="left", padx=(0, 16))
        styled_label(col_sz, "Size", color=SUBTEXT).pack(anchor="w")
        self.fontsize_var = tk.IntVar(value=180)
        styled_spinbox(col_sz, self.fontsize_var, 10, 500, width=5
                       ).pack(anchor="w", pady=(2, 0))

        col_col = tk.Frame(fr, bg=CARD); col_col.pack(side="left", padx=(0, 16))
        styled_label(col_col, "Colour", color=SUBTEXT).pack(anchor="w")
        self.fontcolor_var = tk.StringVar(value="white")
        ColourButton(col_col, self.fontcolor_var,
                     presets=["white","yellow","cyan","#ff8844",
                               "#88ffcc","red","gold","#eeeeee"],
                     width=9).pack(anchor="w", pady=(2, 0))

        col_bw = tk.Frame(fr, bg=CARD); col_bw.pack(side="left", padx=(0, 16))
        styled_label(col_bw, "Border", color=SUBTEXT).pack(anchor="w")
        self.borderw_var = tk.IntVar(value=5)
        styled_spinbox(col_bw, self.borderw_var, 0, 30, width=4
                       ).pack(anchor="w", pady=(2, 0))

        # Position + opacity
        po_row = tk.Frame(tc, bg=CARD); po_row.pack(fill="x", pady=(10, 0))
        styled_label(po_row, "Position:", color=SUBTEXT).pack(side="left", padx=(0, 8))
        self.pos_var = tk.StringVar(value="Center")
        for p in ["Center", "Top-Center", "Bottom-Center", "Lower-Third"]:
            tk.Radiobutton(po_row, text=p, variable=self.pos_var, value=p,
                           bg=CARD, fg=TEXT, selectcolor=ENTRY_BG,
                           activebackground=CARD, activeforeground=ACCENT,
                           font=FONT_LABEL, cursor="hand2"
                           ).pack(side="left", padx=(0, 8))
        styled_label(po_row, "  Opacity %:", color=SUBTEXT).pack(side="left", padx=(12, 6))
        self.text_opacity_var = tk.IntVar(value=100)
        tk.Scale(po_row, from_=0, to=100, orient="horizontal",
                 variable=self.text_opacity_var, length=110,
                 bg=CARD, fg=TEXT, troughcolor=ENTRY_BG, showvalue=True,
                 sliderlength=14).pack(side="left")

        self.text_fade_enable    = tk.BooleanVar(value=False)
        self.text_fade_in        = tk.DoubleVar(value=0.0)   # fade-in START time
        self.text_fade_in_dur    = tk.DoubleVar(value=1.0)   # fade-in DURATION
        self.text_fade_out_from  = tk.DoubleVar(value=5.0)   # fade-out START time
        self.text_fade_out_dur   = tk.DoubleVar(value=1.0)   # fade-out DURATION

        # Checkbox row — includes live duration reference to avoid tab-switching
        tf_hdr = tk.Frame(tc, bg=CARD); tf_hdr.pack(fill="x", pady=(6, 0))
        tk.Checkbutton(tf_hdr, variable=self.text_fade_enable,
                       bg=CARD, fg=ACCENT, selectcolor=ENTRY_BG,
                       activebackground=CARD, cursor="hand2").pack(side="left")
        tk.Label(tf_hdr, text="Text Fade", font=FONT_LABEL,
                 fg=TEXT, bg=CARD).pack(side="left", padx=(4, 0))
        styled_label(tf_hdr, "  (total duration:", color=SUBTEXT, size=8
                     ).pack(side="left", padx=(8, 0))
        self._tf_dur_lbl = styled_label(tf_hdr,
                                        f"{self.duration_var.get():.1f}s)",
                                        color=ACCENT, size=8)
        self._tf_dur_lbl.pack(side="left", padx=(2, 0))

        def _update_tf_dur_lbl(*_):
            try:
                self._tf_dur_lbl.config(text=f"{float(self.duration_var.get()):.1f}s)")
            except Exception:
                pass
        self.duration_var.trace_add("write", _update_tf_dur_lbl)

        # 4-slider grid  (2 columns x 2 rows)
        tf_grid = tk.Frame(tc, bg=CARD); tf_grid.pack(fill="x", pady=(4, 0))

        def _fade_slider(parent, label, var, default_lbl, cmd):
            blk = tk.Frame(parent, bg=CARD); blk.pack(side="left", padx=(0, 20))
            top = tk.Frame(blk, bg=CARD); top.pack(fill="x")
            styled_label(top, label, color=SUBTEXT, size=8).pack(side="left")
            lbl = styled_label(top, default_lbl, color=ACCENT, size=8)
            lbl.pack(side="right")
            sc = tk.Scale(blk, from_=0.0, to=max(0.1, float(self.duration_var.get())),
                          resolution=0.1, orient="horizontal", variable=var,
                          length=180, showvalue=False,
                          bg=CARD, fg=TEXT, troughcolor=ENTRY_BG, sliderlength=14,
                          command=cmd)
            sc.pack(fill="x")
            return lbl, sc

        # Row 1
        tf_r1 = tk.Frame(tf_grid, bg=CARD); tf_r1.pack(fill="x", pady=(2, 0))
        self._fi_lbl, self._fi_scale = _fade_slider(
            tf_r1, "Fade in after (s):", self.text_fade_in, "0.0s",
            lambda v: self._on_fade_changed())
        self._fid_lbl, self._fid_scale = _fade_slider(
            tf_r1, "Fade in for (s):", self.text_fade_in_dur, "1.0s",
            lambda v: self._on_fade_changed())

        # Row 2
        tf_r2 = tk.Frame(tf_grid, bg=CARD); tf_r2.pack(fill="x", pady=(4, 0))
        self._fof_lbl, self._fof_scale = _fade_slider(
            tf_r2, "Fade out from (s):", self.text_fade_out_from, "5.0s",
            lambda v: self._on_fade_changed())
        self._fod_lbl, self._fod_scale = _fade_slider(
            tf_r2, "Fade out for (s):", self.text_fade_out_dur, "1.0s",
            lambda v: self._on_fade_changed())

        # Keep all slider ranges in sync with duration
        self.duration_var.trace_add("write", self._sync_fade_ranges)

        hline(tc)

        # Lower Third
        lt_row = tk.Frame(tc, bg=CARD); lt_row.pack(fill="x", pady=(0, 4))
        self.ov_lowerthird = tk.BooleanVar(value=False)
        tk.Checkbutton(lt_row, variable=self.ov_lowerthird,
                       bg=CARD, fg=ACCENT, selectcolor=ENTRY_BG,
                       activebackground=CARD, cursor="hand2"
                       ).pack(side="left")
        tk.Label(lt_row, text="Lower Third",
                 font=("Courier New", 9, "bold"), fg=TEXT, bg=CARD
                 ).pack(side="left")
        styled_label(lt_row, "  — title/subtitle bar, auto-sized to text",
                     color=SUBTEXT).pack(side="left")

        lt_f = tk.Frame(tc, bg=CARD, padx=26); lt_f.pack(fill="x", pady=(2, 6))

        # Row 1: Title and Sub text
        lt_text_row = tk.Frame(lt_f, bg=CARD); lt_text_row.pack(fill="x", pady=(0, 4))
        for lbl2, var_name2 in [("Title:", "lt_title_var"), ("Sub:", "lt_sub_var")]:
            styled_label(lt_text_row, lbl2, color=SUBTEXT).pack(side="left", padx=(0, 4))
            v = tk.StringVar()
            setattr(self, var_name2, v)
            styled_entry(lt_text_row, textvariable=v, width=24
                         ).pack(side="left", padx=(0, 14))

        # Row 2: Display from / to
        lt_time_row = tk.Frame(lt_f, bg=CARD); lt_time_row.pack(fill="x", pady=(0, 4))
        styled_label(lt_time_row, "Display from (s):", color=SUBTEXT
                     ).pack(side="left", padx=(0, 6))
        self.lt_from_var = tk.DoubleVar(value=1.0)
        styled_spinbox(lt_time_row, self.lt_from_var, 0.0, 3600.0, width=6, step=0.5
                       ).pack(side="left", padx=(0, 20))
        styled_label(lt_time_row, "Display to (s):", color=SUBTEXT
                     ).pack(side="left", padx=(0, 6))
        self.lt_to_var = tk.DoubleVar(value=6.0)
        styled_spinbox(lt_time_row, self.lt_to_var, 0.0, 3600.0, width=6, step=0.5
                       ).pack(side="left")

        # Row 3: Entry/exit style
        lt_style_row = tk.Frame(lt_f, bg=CARD); lt_style_row.pack(fill="x", pady=(0, 4))
        styled_label(lt_style_row, "Animation:", color=SUBTEXT
                     ).pack(side="left", padx=(0, 8))
        self.lt_style_var = tk.StringVar(value="slide")
        for val, txt in [("slide", "Slide in / slide out"),
                         ("fade",  "Fade in / fade out")]:
            tk.Radiobutton(lt_style_row, text=txt, variable=self.lt_style_var, value=val,
                           bg=CARD, fg=TEXT, selectcolor=ENTRY_BG,
                           activebackground=CARD, font=FONT_LABEL, cursor="hand2"
                           ).pack(side="left", padx=(0, 16))

        # Row 4: Box colour + opacity
        lt_col_row = tk.Frame(lt_f, bg=CARD); lt_col_row.pack(fill="x", pady=(0, 4))
        styled_label(lt_col_row, "Box colour:", color=SUBTEXT
                     ).pack(side="left", padx=(0, 6))
        self.lt_bg_color_var = tk.StringVar(value="#222222")
        ColourButton(lt_col_row, self.lt_bg_color_var,
                     presets=["#222222", "black", "#111111", "#1a1a2e",
                               "#002244", "#220011", "gray"],
                     width=9).pack(side="left", padx=(0, 24))
        styled_label(lt_col_row, "Box opacity:", color=SUBTEXT
                     ).pack(side="left", padx=(0, 6))
        self.lt_box_opacity_var = tk.DoubleVar(value=0.72)
        # Scale + value label side-by-side (label immediately after scale)
        tk.Scale(lt_col_row, from_=0.0, to=1.0, resolution=0.05,
                 orient="horizontal", variable=self.lt_box_opacity_var,
                 length=120, showvalue=False,
                 bg=CARD, fg=TEXT, troughcolor=ENTRY_BG, sliderlength=14,
                 command=lambda v: self._lt_op_lbl.config(text=f"{int(float(v)*100)}%")
                 ).pack(side="left")
        self._lt_op_lbl = styled_label(lt_col_row, "72%", color=ACCENT, size=8)
        self._lt_op_lbl.pack(side="left", padx=(4, 0))

        # Countdown-to-end footer
        cd_row = tk.Frame(tc, bg=CARD); cd_row.pack(fill="x", pady=(0, 4))
        self.ov_countdown = tk.BooleanVar(value=False)
        tk.Checkbutton(cd_row, variable=self.ov_countdown,
                       bg=CARD, fg=ACCENT, selectcolor=ENTRY_BG,
                       activebackground=CARD, cursor="hand2"
                       ).pack(side="left")
        tk.Label(cd_row, text="Countdown Footer",
                 font=("Courier New", 9, "bold"), fg=TEXT, bg=CARD
                 ).pack(side="left")
        styled_label(cd_row,
                     "  — counts DOWN to the end of the video (e.g. 5 4 3 2 1)",
                     color=SUBTEXT).pack(side="left")

        cd_opts = tk.Frame(tc, bg=CARD, padx=26); cd_opts.pack(fill="x", pady=(0, 4))
        styled_label(cd_opts, "Count from:", color=SUBTEXT).pack(side="left", padx=(0, 6))
        self.cd_from_var = tk.IntVar(value=5)
        styled_spinbox(cd_opts, self.cd_from_var, 2, 30, width=4
                       ).pack(side="left", padx=(0, 20))
        styled_label(cd_opts, "Font size:", color=SUBTEXT).pack(side="left", padx=(0, 6))
        self.cd_size_var = tk.IntVar(value=100)
        styled_spinbox(cd_opts, self.cd_size_var, 20, 300, width=4
                       ).pack(side="left", padx=(0, 20))
        styled_label(cd_opts, "Colour:", color=SUBTEXT).pack(side="left", padx=(0, 6))
        self.cd_color_var = tk.StringVar(value="white")
        ColourButton(cd_opts, self.cd_color_var,
                     presets=["white","yellow","red","cyan"], width=8
                     ).pack(side="left", padx=(0, 20))
        styled_label(cd_opts, "Position:", color=SUBTEXT).pack(side="left", padx=(0, 6))
        self.cd_pos_var = tk.StringVar(value="Bottom-Centre")
        ttk.Combobox(cd_opts, textvariable=self.cd_pos_var,
                     values=["Bottom-Centre", "Bottom-Left", "Bottom-Right",
                             "Centre", "Top-Centre"],
                     width=13).pack(side="left")

        # Extras opacity
        eo_row = tk.Frame(tc, bg=CARD); eo_row.pack(fill="x", pady=(8, 0))
        styled_label(eo_row, "Overlay Extras Opacity %:", color=SUBTEXT
                     ).pack(side="left", padx=(0, 8))
        self.extras_opacity_var = tk.IntVar(value=100)
        tk.Scale(eo_row, from_=0, to=100, orient="horizontal",
                 variable=self.extras_opacity_var, length=200,
                 bg=CARD, fg=TEXT, troughcolor=ENTRY_BG, showvalue=True,
                 sliderlength=14).pack(side="left")

        # ═ VIDEO EFFECTS ════════════════════════════════════════════
        section_header(t3, "VIDEO EFFECTS")
        vfx = styled_frame(t3, padx=14, pady=10)
        vfx.pack(fill="x", **pad, pady=(0, 4))

        lc = tk.Frame(vfx, bg=CARD); lc.pack(side="left", fill="both", expand=True, padx=(0, 6))
        rc = tk.Frame(vfx, bg=CARD); rc.pack(side="left", fill="both", expand=True)

        def tog(parent, label, desc="", default=False):
            t = EffectToggle(parent, label, desc, default=default)
            t.pack(fill="x", pady=1); return t

        # Left column: 6 effects
        self.fx_scan      = tog(lc, "Scanline Sweep",   "Animated light bar across frame")
        self.fx_drift     = tog(lc, "Slow Drift",       "Pan gently left to right")
        self.fx_mirror    = tog(lc, "Mirror Tiles",     "2x2 kaleidoscope")
        self.fx_grain     = tog(lc, "Film Grain",       "Analogue noise overlay")
        self.fx_letterbox = tog(lc, "Letterbox",        "Cinematic 2.35:1 black bars")
        self.fx_vignette  = tog(lc, "Vignette",         "Darkened edges for cinema look")
        # Right column: 5 effects
        self.fx_flash     = tog(rc, "Flash Bar",        "Mid-video white flash")
        self.fx_pulse     = tog(rc, "Pulse",            "Rhythmic breathe / zoom")
        self.fx_glitch    = tog(rc, "Glitch",           "Digital corruption flicker")
        self.fx_bloom     = tog(rc, "Bloom",            "Soft glow on highlights")
        self.fx_sharpen   = tog(rc, "Sharpen",          "Crisp edge detail")
        # fx_eq (Colour Grading) and fx_hueshift (Colour Shift) live in Colour Options below

        # Reset button for Video Effects
        vfx_reset_row = tk.Frame(vfx, bg=CARD)
        vfx_reset_row.pack(fill="x", pady=(6, 0), side="bottom")
        styled_button(vfx_reset_row, "Reset Video Effects",
                      self._reset_video_effects, small=True
                      ).pack(side="right")



        # ═ COLOUR OPTIONS ═════════════════════════════════════════════
        section_header(t3, "COLOUR OPTIONS")
        co_card = styled_frame(t3, padx=14, pady=12)
        co_card.pack(fill="x", **pad, pady=(0, 4))

        # ── Sepia / B&W ─────────────────────────────────────────────────
        sep_row = tk.Frame(co_card, bg=CARD); sep_row.pack(fill="x", pady=(0, 6))
        self.fx_sepia_var = tk.BooleanVar(value=False)
        tk.Checkbutton(sep_row, variable=self.fx_sepia_var,
                       bg=CARD, fg=ACCENT, selectcolor=ENTRY_BG,
                       activebackground=CARD, cursor="hand2"
                       ).pack(side="left")
        tk.Label(sep_row, text="Sepia / B&W",
                 font=("Courier New", 9, "bold"), fg=TEXT, bg=CARD
                 ).pack(side="left", padx=(0, 16))
        sep_opts = tk.Frame(sep_row, bg=CARD); sep_opts.pack(side="left")
        self.sepia_mode_var = tk.StringVar(value="sepia")
        for m in ("sepia", "black & white"):
            tk.Radiobutton(sep_opts, text=m, variable=self.sepia_mode_var, value=m,
                           bg=CARD, fg=TEXT, selectcolor=ENTRY_BG,
                           activebackground=CARD, font=FONT_LABEL, cursor="hand2"
                           ).pack(side="left", padx=(0, 10))
        # Wrapper so fx_sepia.var.get() / fx_sepia.get() still works elsewhere
        class _SepiaToggle:
            def __init__(self, var): self.var = var
            def get(self): return self.var.get()
        self.fx_sepia = _SepiaToggle(self.fx_sepia_var)

        hline(co_card)

        # ── Fade to Colour ───────────────────────────────────────────────
        fade_hdr = tk.Frame(co_card, bg=CARD); fade_hdr.pack(fill="x")
        self.fx_fade_col_var = tk.BooleanVar(value=True)
        tk.Checkbutton(fade_hdr, variable=self.fx_fade_col_var,
                       bg=CARD, fg=ACCENT, selectcolor=ENTRY_BG,
                       activebackground=CARD, cursor="hand2"
                       ).pack(side="left")
        tk.Label(fade_hdr, text="Fade to Colour",
                 font=("Courier New", 9, "bold"), fg=TEXT, bg=CARD
                 ).pack(side="left", padx=(0, 16))
        styled_label(fade_hdr, "Colour:", color=SUBTEXT, size=8
                     ).pack(side="left", padx=(0, 6))
        self.fade_color_var = tk.StringVar(value="black")
        ColourButton(fade_hdr, self.fade_color_var,
                     presets=["black","white","red","blue",
                               "green","#ff8800","#220022"],
                     width=10).pack(side="left")

        # Fade duration — full-width slider on its own row
        fade_dur_row = tk.Frame(co_card, bg=CARD, padx=4)
        fade_dur_row.pack(fill="x", pady=(6, 0))
        styled_label(fade_dur_row, "Duration (s):", color=SUBTEXT, size=8
                     ).pack(side="left", padx=(0, 6))
        self.fade_duration_var = tk.DoubleVar(value=1.5)
        self._fade_dur_lbl = styled_label(fade_dur_row, "1.5", color=ACCENT, size=8)
        self._fade_dur_lbl.pack(side="right")
        tk.Scale(fade_dur_row, from_=0.3, to=5.0, resolution=0.1,
                 orient="horizontal", variable=self.fade_duration_var,
                 showvalue=False,
                 bg=CARD, fg=TEXT, troughcolor=ENTRY_BG, sliderlength=14,
                 command=lambda v: self._fade_dur_lbl.config(text=f"{float(v):.1f}")
                 ).pack(fill="x", padx=(0, 4))

        hline(co_card)

        # ── Colour Grading — same alignment as Fade to Colour ─────────────
        cg_hdr = tk.Frame(co_card, bg=CARD); cg_hdr.pack(fill="x", pady=(0, 6))
        _cg_var = tk.BooleanVar(value=False)
        tk.Checkbutton(cg_hdr, variable=_cg_var,
                       bg=CARD, fg=ACCENT, selectcolor=ENTRY_BG,
                       activebackground=CARD, cursor="hand2"
                       ).pack(side="left")
        tk.Label(cg_hdr, text="Colour Grading",
                 font=("Courier New", 9, "bold"), fg=TEXT, bg=CARD
                 ).pack(side="left", padx=(0, 16))
        styled_label(cg_hdr, "Contrast / brightness / saturation",
                     color=SUBTEXT, size=8).pack(side="left")
        class _BoolToggle:
            def __init__(self, var): self.var = var
            def get(self): return self.var.get()
        self.fx_eq = _BoolToggle(_cg_var)

        # ── Colour Shift — same alignment as Fade to Colour ───────────────
        cs_hdr = tk.Frame(co_card, bg=CARD); cs_hdr.pack(fill="x", pady=(0, 6))
        _cs_var = tk.BooleanVar(value=False)
        tk.Checkbutton(cs_hdr, variable=_cs_var,
                       bg=CARD, fg=ACCENT, selectcolor=ENTRY_BG,
                       activebackground=CARD, cursor="hand2"
                       ).pack(side="left")
        tk.Label(cs_hdr, text="Colour Shift",
                 font=("Courier New", 9, "bold"), fg=TEXT, bg=CARD
                 ).pack(side="left", padx=(0, 16))
        styled_label(cs_hdr, "Slow hue rotation",
                     color=SUBTEXT, size=8).pack(side="left")
        self.fx_hueshift = _BoolToggle(_cs_var)

        # ═ AUDIO EFFECTS — TWO COLUMNS ═══════════════════════════════
        section_header(t4, "AUDIO EFFECTS")
        afx_card = styled_frame(t4, padx=14, pady=10)
        afx_card.pack(fill="x", **pad, pady=(0, 4))

        # ── Fade In/Out group (always at top) ───────────────────────────
        fade_grp = tk.Frame(afx_card, bg=CARD); fade_grp.pack(fill="x", pady=(0, 4))
        self.afx_fade = EffectToggle(fade_grp, "Fade In / Out",
                                      "Crossfade at start and end of audio",
                                      default=True)
        self.afx_fade.pack(anchor="w")
        self.fade_dur_var = tk.DoubleVar(value=1.5)
        fade_dur_frame = tk.Frame(afx_card, bg=CARD); fade_dur_frame.pack(fill="x", pady=(0, 8))
        styled_label(fade_dur_frame, "Fade duration (s):", color=SUBTEXT, size=8
                     ).pack(side="left", padx=(0, 6))
        self._fade_audio_lbl = styled_label(fade_dur_frame, "1.5", color=ACCENT, size=8)
        self._fade_audio_lbl.pack(side="right")
        tk.Scale(fade_dur_frame, from_=0.1, to=4.0, resolution=0.1,
                 orient="horizontal", variable=self.fade_dur_var,
                 showvalue=False,
                 bg=CARD, fg=TEXT, troughcolor=ENTRY_BG,
                 sliderlength=14,
                 command=lambda v: self._fade_audio_lbl.config(text=f"{float(v):.1f}")
                 ).pack(fill="x", padx=(0, 4))

        hline(afx_card)

        # ── Master volume ────────────────────────────────────────────────
        vol_outer = tk.Frame(afx_card, bg=CARD); vol_outer.pack(fill="x", pady=(0, 6))
        vol_hdr = tk.Frame(vol_outer, bg=CARD); vol_hdr.pack(fill="x")
        styled_label(vol_hdr, "Master Volume:", color=SUBTEXT).pack(side="left")
        self.master_volume_var = tk.DoubleVar(value=1.0)
        self._vol_lbl = styled_label(vol_hdr, "1.00x", color=ACCENT, size=8)
        self._vol_lbl.pack(side="right")
        tk.Scale(vol_outer, from_=0.0, to=4.0, resolution=0.05,
                 orient="horizontal", variable=self.master_volume_var,
                 showvalue=False,
                 bg=CARD, fg=TEXT, troughcolor=ENTRY_BG,
                 highlightbackground=CARD, activebackground=ACCENT,
                 sliderlength=14,
                 command=lambda v: self._vol_lbl.config(text=f"{float(v):.2f}x")
                 ).pack(fill="x")

        # Two-column toggle area (afx_fade moved to top, excluded here)
        afx_cols = tk.Frame(afx_card, bg=CARD); afx_cols.pack(fill="x")
        al = tk.Frame(afx_cols, bg=CARD)
        al.pack(side="left", fill="both", expand=True, padx=(0, 6))
        ar = tk.Frame(afx_cols, bg=CARD)
        ar.pack(side="left", fill="both", expand=True)

        def atog(parent, label, desc="", default=False):
            t = EffectToggle(parent, label, desc, default=default)
            t.pack(fill="x", pady=1); return t

        # Left column: 5 effects
        self.afx_bass       = atog(al, "Bass Punch",       "Low-frequency EQ boost")
        self.afx_reverb     = atog(al, "Reverb",           "Hall reverb (aecho)")
        self.afx_wide       = atog(al, "Stereo Widener",   "Wider soundstage")
        self.afx_compressor = atog(al, "Compressor",       "Dynamic range control")
        self.afx_echo       = atog(al, "Echo / Delay",     "Slap-back echo effect")
        # Right column: 5 effects
        self.afx_highpass   = atog(ar, "High-Pass Filter", "Remove rumble below cutoff")
        self.afx_lowpass    = atog(ar, "Low-Pass Filter",  "Soften highs above cutoff")
        self.afx_normalize  = atog(ar, "Normalize",        "Auto loudness to -16 LUFS")
        self.afx_tremolo    = atog(ar, "Tremolo",          "Rhythmic volume pulse")
        self.afx_chorus     = atog(ar, "Chorus",           "Rich chorus shimmer")

        # Fine-grained sliders
        hline(afx_card)
        sliders_frame = tk.Frame(afx_card, bg=CARD)
        sliders_frame.pack(fill="x")
        sliders_frame.columnconfigure(0, weight=1, uniform="slcol")
        sliders_frame.columnconfigure(1, weight=1, uniform="slcol")
        sl_l = tk.Frame(sliders_frame, bg=CARD)
        sl_l.grid(row=0, column=0, sticky="nw", padx=(0, 8))
        sl_r = tk.Frame(sliders_frame, bg=CARD)
        sl_r.grid(row=0, column=1, sticky="nw")

        self.bass_freq_var   = tk.DoubleVar(value=80.0)
        self.bass_gain_var   = tk.DoubleVar(value=6.0)
        self.reverb_delay_ms = tk.DoubleVar(value=40.0)
        self.reverb_decay    = tk.DoubleVar(value=0.5)
        self.comp_ratio_var  = tk.DoubleVar(value=4.0)
        self.comp_thr_var    = tk.DoubleVar(value=-18.0)
        self.echo_delay_ms   = tk.DoubleVar(value=80.0)
        self.echo_decay_var  = tk.DoubleVar(value=0.35)
        self.hp_freq_var     = tk.DoubleVar(value=80.0)
        self.lp_freq_var     = tk.DoubleVar(value=12000.0)
        self.tremolo_rate    = tk.DoubleVar(value=5.0)
        self.tremolo_depth   = tk.DoubleVar(value=0.5)

        def mk(parent, label, var, lo, hi, res=0.1, fmt="{:.1f}", length=190):
            SliderRow(parent, label, var, lo, hi,
                      resolution=res, fmt=fmt, length=length
                      ).pack(fill="x", pady=2)

        mk(sl_l, "Bass freq (Hz)",       self.bass_freq_var,   30,   300,  res=5,   fmt="{:.0f}")
        mk(sl_l, "Bass gain (dB)",       self.bass_gain_var,   0.0,  18.0)
        mk(sl_l, "Reverb delay (ms)",    self.reverb_delay_ms, 10,   200,  res=5,   fmt="{:.0f}")
        mk(sl_l, "Reverb decay",         self.reverb_decay,    0.05, 1.0,  res=0.05)
        mk(sl_l, "Comp. threshold (dB)", self.comp_thr_var,   -40.0, 0.0)
        mk(sl_l, "Comp. ratio",          self.comp_ratio_var,  1.0,  20.0)
        mk(sl_r, "High-pass freq (Hz)",  self.hp_freq_var,     20,   800,  res=10,  fmt="{:.0f}")
        mk(sl_r, "Low-pass freq (Hz)",   self.lp_freq_var,   1000, 20000,  res=100, fmt="{:.0f}")
        mk(sl_r, "Echo delay (ms)",      self.echo_delay_ms,   10,   500,  res=5,   fmt="{:.0f}")
        mk(sl_r, "Echo decay",           self.echo_decay_var,  0.1,  0.95, res=0.05)
        mk(sl_r, "Tremolo rate (Hz)",    self.tremolo_rate,    0.5,  20.0)
        mk(sl_r, "Tremolo depth",        self.tremolo_depth,   0.0,   1.0)

        # Reset button spans both columns
        reset_row = tk.Frame(sliders_frame, bg=CARD)
        reset_row.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        styled_button(reset_row, "Reset Audio Effects",
                      self._reset_audio_sliders, small=True
                      ).pack(side="right")

        # ═ QUALITY ════════════════════════════════════════════════════
        section_header(t1, "QUALITY")
        qc = styled_frame(t1, padx=14, pady=12)
        qc.pack(fill="x", **pad, pady=(0, 4))
        qr = tk.Frame(qc, bg=CARD); qr.pack(fill="x")

        styled_label(qr, "CRF:", color=SUBTEXT).pack(side="left", padx=(0, 6))
        # CRF = Constant Rate Factor; lower = higher quality / larger file
        self.crf_var = tk.IntVar(value=18)
        self._crf_lbl = styled_label(qr, "18", color=ACCENT, size=8)
        self._crf_lbl.pack(side="left")
        self._crf_scale = tk.Scale(qr, from_=12, to=30, orient="horizontal",
                 variable=self.crf_var, length=160, showvalue=False,
                 bg=CARD, fg=TEXT, troughcolor=ENTRY_BG, sliderlength=14,
                 command=lambda v: self._crf_lbl.config(text=str(int(float(v))))
                 )
        self._crf_scale.pack(side="left", padx=(2, 10))
        self._crf_hint = styled_label(qr, "H.264 (0-51; lower=better)",
                                      color=SUBTEXT, size=8)
        self._crf_hint.pack(side="left")
        # Wire format selector -> auto-update CRF
        self.out_format_var.trace_add("write", self._on_format_changed)

        styled_label(qr, "Preset:", color=SUBTEXT).pack(side="left", padx=(0, 6))
        self.preset_var = tk.StringVar(value="ultrafast")
        ttk.Combobox(qr, textvariable=self.preset_var,
                     values=["ultrafast","veryfast","fast","medium","slow","veryslow"],
                     width=12).pack(side="left")


    def _build_log_panel(self):
        """Permanent build log panel shown below all tabs."""
        lc2 = styled_frame(self, padx=14, pady=8)
        lc2.pack(fill="x", padx=6)
        log_top = tk.Frame(lc2, bg=CARD); log_top.pack(fill="x", pady=(0, 4))
        styled_label(log_top, "Build Log:", color=SUBTEXT).pack(side="left")
        styled_button(log_top, "Copy Log",  self._copy_log,  small=True
                      ).pack(side="right")
        styled_button(log_top, "Clear Log", self._clear_log, small=True
                      ).pack(side="right", padx=(0, 6))
        self.log_text = tk.Text(
            lc2, height=8, bg="#080810", fg="#66ff66",
            font=FONT_MONO, relief="flat", state="disabled",
            insertbackground=ACCENT,
            highlightbackground=BORDER, highlightthickness=1)
        self.log_text.pack(fill="x")
        self.progress_var = tk.DoubleVar(value=0)
        ttk.Progressbar(lc2, variable=self.progress_var, maximum=100,
                        style="Accent.Horizontal.TProgressbar"
                        ).pack(fill="x", pady=(4, 0))
        self.status_label = styled_label(lc2, "Ready.", color=SUBTEXT)
        self.status_label.pack(anchor="w", pady=(2, 0))

    def _build_bottom_bar(self):
        bar = tk.Frame(self, bg=SURFACE, padx=20, pady=10)
        bar.pack(fill="x")
        self.build_btn = styled_button(
            bar, "[>] BUILD INTRO", self._start_build, accent=True)
        self.build_btn.pack(side="left", padx=(0, 10))
        self.save_btn = styled_button(bar, "[S] SAVE AS", self._save_as)
        self.save_btn.config(state="disabled")
        # Not packed at construction — appears only after a successful build
        self.preview_btn_holder=tk.Frame(bar,bg=SURFACE)
        self.preview_btn_holder.pack(side="left")
        self.preview_btn=styled_button(self.preview_btn_holder,"[P] PREVIEW",self._preview)
        self.preview_btn.config(state="disabled")
        self.preview_btn.pack(side="left")

    def _apply_ttk_style(self):
        s = ttk.Style(self); s.theme_use("clam")
        s.configure("TScrollbar", background=BORDER, troughcolor=BG,
                    arrowcolor=SUBTEXT, borderwidth=0)
        s.configure("Accent.Horizontal.TProgressbar",
                    troughcolor=ENTRY_BG, background=ACCENT,
                    borderwidth=0, darkcolor=ACCENT, lightcolor=ACCENT)
        s.configure("TCombobox", fieldbackground=ENTRY_BG,
                    background=BORDER, foreground=TEXT,
                    selectbackground=ACCENT, selectforeground=BG,
                    arrowcolor=SUBTEXT)
        s.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)])
        # Notebook tab styling
        s.configure("TNotebook", background=BG, borderwidth=0, tabmargins=0)
        s.configure("TNotebook.Tab",
                    background=CARD, foreground=SUBTEXT,
                    font=("Courier New", 9, "bold"),
                    padding=(12, 6), borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", SURFACE), ("active", BORDER)],
              foreground=[("selected", ACCENT), ("active", TEXT)])

    # ── Logging ───────────────────────────────────────────────────────
    def _log(self, msg, color=None):
        def _do():
            self.log_text.config(state="normal")
            if color:
                tag = "c" + color.replace("#", "")
                self.log_text.tag_configure(tag, foreground=color)
                self.log_text.insert("end", msg + "\n", tag)
            else:
                self.log_text.insert("end", msg + "\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        if threading.current_thread() is threading.main_thread():
            _do()
        else:
            self._ui(_do)

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def _copy_log(self):
        self.clipboard_clear()
        self.clipboard_append(self.log_text.get("1.0", "end"))
        self._log("Log copied to clipboard.", SUCCESS)

    def _set_status(self, msg, color=SUBTEXT):
        def _do():
            self.status_label.config(text=msg, fg=color)
        if threading.current_thread() is threading.main_thread():
            _do()
        else:
            self._ui(_do)

    def _set_progress(self, pct):
        def _do():
            self.progress_var.set(pct)
        if threading.current_thread() is threading.main_thread():
            _do()
            self.update_idletasks()
        else:
            self._ui(_do)

    # ── Settings dict ─────────────────────────────────────────────────
    def _get_settings_dict(self):
        return {
            "duration":       self.duration_var.get(),
            "seek":           self.seek_var.get(),
            "bg_end":         self.bg_end_var.get(),
            "text":           self.text_var.get().rstrip("\n"),
            "font":           self.font_var.get(),
            "fontsize":       self.fontsize_var.get(),
            "fontcolor":      self.fontcolor_var.get(),
            "borderw":        self.borderw_var.get(),
            "pos":            self.pos_var.get(),
            "text_opacity":   self.text_opacity_var.get(),
            "extras_opacity": self.extras_opacity_var.get(),
            "text_fade_enable":self.text_fade_enable.get(),
            "text_fade_in":       self.text_fade_in.get(),
            "text_fade_in_dur":   self.text_fade_in_dur.get(),
            "text_fade_out_from": self.text_fade_out_from.get(),
            "text_fade_out_dur":  self.text_fade_out_dur.get(),
            "audio_source":   self.audio_source_var.get(),
            "master_volume":  self.master_volume_var.get(),
            "crf":            self.crf_var.get(),
            "preset":         self.preset_var.get(),
            "fade_duration":  self.fade_duration_var.get(),
            "fade_color":     self.fade_color_var.get(),
            "fx_fade_col":    self.fx_fade_col_var.get(),
            "fx_eq":          self.fx_eq.var.get(),
            "fx_vignette":    self.fx_vignette.var.get(),
            "fx_scan":        self.fx_scan.var.get(),
            "fx_flash":       self.fx_flash.var.get(),
            "fx_drift":       self.fx_drift.var.get(),
            "fx_pulse":       self.fx_pulse.var.get(),
            "fx_mirror":      self.fx_mirror.var.get(),
            "fx_hueshift":    self.fx_hueshift.var.get(),
            "fx_grain":       self.fx_grain.var.get(),
            "fx_glitch":      self.fx_glitch.var.get(),
            "fx_letterbox":   self.fx_letterbox.var.get(),
            "fx_bloom":       self.fx_bloom.var.get(),
            "fx_sepia":       self.fx_sepia.var.get(),
            "fx_sharpen":     self.fx_sharpen.var.get(),
            "sepia_mode":     self.sepia_mode_var.get(),
            "afx_fade":       self.afx_fade.var.get(),
            "afx_bass":       self.afx_bass.var.get(),
            "afx_reverb":     self.afx_reverb.var.get(),
            "afx_wide":       self.afx_wide.var.get(),
            "afx_compressor": self.afx_compressor.var.get(),
            "afx_highpass":   self.afx_highpass.var.get(),
            "afx_lowpass":    self.afx_lowpass.var.get(),
            "afx_normalize":  self.afx_normalize.var.get(),
            "afx_tremolo":    self.afx_tremolo.var.get(),
            "afx_chorus":     self.afx_chorus.var.get(),
            "fade_dur":       self.fade_dur_var.get(),
            "bass_freq":      self.bass_freq_var.get(),
            "bass_gain":      self.bass_gain_var.get(),
            "reverb_delay":   self.reverb_delay_ms.get(),
            "echo_delay":     self.echo_delay_ms.get(),
            "echo_decay":     self.echo_decay_var.get(),
            "afx_echo":       self.afx_echo.var.get(),
            "reverb_decay":   self.reverb_decay.get(),
            "comp_ratio":     self.comp_ratio_var.get(),
            "comp_thr":       self.comp_thr_var.get(),
            "hp_freq":        self.hp_freq_var.get(),
            "lp_freq":        self.lp_freq_var.get(),
            "tremolo_rate":   self.tremolo_rate.get(),
            "tremolo_depth":  self.tremolo_depth.get(),
            "ov_lowerthird":  self.ov_lowerthird.get(),
            "lt_title":       self.lt_title_var.get(),
            "lt_sub":         self.lt_sub_var.get(),
            "lt_from":        self.lt_from_var.get(),
            "lt_to":          self.lt_to_var.get(),
            "lt_style":       getattr(self,"lt_style_var",type("_",(),{"get":lambda s:"slide"})()).get(),
            "lt_bg_color":    getattr(self,"lt_bg_color_var",type("_",(),{"get":lambda s:"#222222"})()).get(),
            "lt_box_opacity": float(getattr(self,"lt_box_opacity_var",type("_",(),{"get":lambda s:0.72})()).get()),
            "ov_countdown":   self.ov_countdown.get(),
            "cd_from":        self.cd_from_var.get(),
            "cd_size":        self.cd_size_var.get(),
            "cd_color":       self.cd_color_var.get(),
            "cd_pos":         self.cd_pos_var.get(),
            "out_format":self.out_format_var.get(),
            "preserve_ar":    self.preserve_ar_var.get(),
            "pad_color":      self.pad_color_var.get(),
            "bg_file":        self.bg_picker.get(),
            "audio_file":     self.audio_picker.get(),
            "audio_seek":     self.audio_seek_var.get(),
            "audio_end":      self.audio_end_var.get(),
            "save_metadata":  self.save_metadata_var.get(),
        }

    def _apply_settings_dict(self, d):
        simple_vars = {
            "duration":       self.duration_var,
            "seek":           self.seek_var,
            "bg_end":         self.bg_end_var,
            "text":           self.text_var,
            "font":           self.font_var,
            "fontsize":       self.fontsize_var,
            "fontcolor":      self.fontcolor_var,
            "borderw":        self.borderw_var,
            "pos":            self.pos_var,
            "text_opacity":   self.text_opacity_var,
            "extras_opacity": self.extras_opacity_var,
            "audio_source":   self.audio_source_var,
            "master_volume":  self.master_volume_var,
            "crf":            self.crf_var,
            "preset":         self.preset_var,
            "fade_duration":  self.fade_duration_var,
            "fade_color":     self.fade_color_var,
            "sepia_mode":     self.sepia_mode_var,
            "fade_dur":       self.fade_dur_var,
            "bass_freq":      self.bass_freq_var,
            "bass_gain":      self.bass_gain_var,
            "reverb_delay":   self.reverb_delay_ms,
            "echo_delay":     self.echo_delay_ms,
            "echo_decay":     self.echo_decay_var,
            "reverb_decay":   self.reverb_decay,
            "comp_ratio":     self.comp_ratio_var,
            "comp_thr":       self.comp_thr_var,
            "hp_freq":        self.hp_freq_var,
            "lp_freq":        self.lp_freq_var,
            "tremolo_rate":   self.tremolo_rate,
            "tremolo_depth":  self.tremolo_depth,
            "lt_title":       self.lt_title_var,
            "lt_sub":         self.lt_sub_var,
            "lt_from":        self.lt_from_var,
            "lt_to":          self.lt_to_var,
            "lt_style":       getattr(self,"lt_style_var",tk.StringVar()),
            "lt_bg_color":    getattr(self,"lt_bg_color_var",tk.StringVar()),
            "lt_box_opacity": getattr(self,"lt_box_opacity_var",tk.DoubleVar()),
            "cd_from":        self.cd_from_var,
            "cd_size":        self.cd_size_var,
            "cd_color":       self.cd_color_var,
            "cd_pos":         self.cd_pos_var,
            "out_format":self.out_format_var,
            "pad_color":  self.pad_color_var,
            "audio_seek": self.audio_seek_var,
            "audio_end":  self.audio_end_var,
        }
        bool_vars = {
            "fx_fade_col":  self.fx_fade_col_var,
            "ov_lowerthird":self.ov_lowerthird,
            "ov_countdown": self.ov_countdown,
            "text_fade_enable":self.text_fade_enable,
            "preserve_ar":  self.preserve_ar_var,
            "save_metadata": self.save_metadata_var,
        }
        toggles = {
            "fx_eq":        self.fx_eq,
            "fx_vignette":  self.fx_vignette,
            "fx_scan":      self.fx_scan,
            "fx_flash":     self.fx_flash,
            "fx_drift":     self.fx_drift,
            "fx_pulse":     self.fx_pulse,
            "fx_mirror":    self.fx_mirror,
            "fx_hueshift":  self.fx_hueshift,
            "fx_grain":     self.fx_grain,
            "fx_glitch":    self.fx_glitch,
            "fx_letterbox": self.fx_letterbox,
            "fx_bloom":     self.fx_bloom,
            "fx_sepia":     self.fx_sepia,
            "fx_sharpen":   self.fx_sharpen,
            "afx_fade":     self.afx_fade,
            "afx_bass":     self.afx_bass,
            "afx_reverb":   self.afx_reverb,
            "afx_wide":     self.afx_wide,
            "afx_compressor":self.afx_compressor,
            "afx_highpass": self.afx_highpass,
            "afx_lowpass":  self.afx_lowpass,
            "afx_normalize":self.afx_normalize,
            "afx_tremolo":  self.afx_tremolo,
            "afx_echo":     self.afx_echo,
            "afx_chorus":   self.afx_chorus,
        }
        for k, var in simple_vars.items():
            if k in d:
                try: var.set(d[k])
                except Exception: pass
        for k, var in bool_vars.items():
            if k in d:
                try: var.set(bool(d[k]))
                except Exception: pass
        for k, tog in toggles.items():
            if k in d:
                try: tog.var.set(bool(d[k]))
                except Exception: pass
        self._crf_lbl.config(text=str(self.crf_var.get()))
        self._vol_lbl.config(text=f"{self.master_volume_var.get():.2f}x")
        # Refresh CRF hint and slider range to match loaded format
        self.after(50, self._on_format_changed)
        for key, var in [("text_fade_in",       self.text_fade_in),
                          ("text_fade_in_dur",   self.text_fade_in_dur),
                          ("text_fade_out_from", self.text_fade_out_from),
                          ("text_fade_out_dur",  self.text_fade_out_dur)]:
            if key in d:
                try: var.set(float(d[key]))
                except Exception: pass
        # Refresh all fade labels and ranges after loading
        self.after(100, self._on_fade_changed)
        if "bg_file" in d and d["bg_file"]:
            try: self.bg_picker.set(d["bg_file"])
            except Exception: pass
        if "audio_file" in d and d["audio_file"]:
            try: self.audio_picker.set(d["audio_file"])
            except Exception: pass

    def _load_settings_from_file(self):
        path = filedialog.askopenfilename(
            title="Select a previously built intro",
            filetypes=[("Video/Media files", "*.mp4 *.mov *.mkv *.webm"),
                       ("All files", "*")])
        if not path: return
        try:
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries",
                 "format_tags=comment",
                 "-of", "default=noprint_wrappers=1:nokey=1", path],
                capture_output=True, text=True)
            comment = probe.stdout.strip()
            if "IB_SETTINGS:" not in comment:
                messagebox.showwarning(
                    "No Metadata",
                    "This file has no Pre-Roll settings embedded.\n"
                    "Only files built with a version with embedded settings enabled.")
                return
            encoded  = comment.split("IB_SETTINGS:")[1]
            settings = json.loads(base64.b64decode(encoded).decode("utf-8"))
            self._apply_settings_dict(settings)
            self._log("Settings loaded from file metadata.", SUCCESS)
            messagebox.showinfo("Loaded", "All settings restored.")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    # ── Build ─────────────────────────────────────────────────────────
    def _on_bg_changed(self, *_):
        """When the background file changes, update audio mode and radio state."""
        path = self.bg_picker.get().strip()
        if not path:
            return
        ext=_safe_getext(path)
        is_img=ext in ("jpg","jpeg","png","bmp","webp","tiff","gif")
        if is_img:
            # Images have no audio — force silent and disable background option
            self.audio_source_var.set("silent")
            self._rb_bg.config(state="disabled")
            self._rb_prov.config(state="normal")
            self._rb_silent.config(state="normal")
        else:
            # Video — re-enable all radio options, then probe for audio track
            self._rb_bg.config(state="normal")
            self._rb_prov.config(state="normal")
            self._rb_silent.config(state="normal")
            import threading as _thr
            _thr.Thread(target=self._probe_bg_audio, args=(path,), daemon=True).start()


    # ── CRF presets keyed by format ──────────────────────────────────────────
    _CRF_PRESETS = {
        "mp4_h264_aac":  (18, 12, 30, "H.264  CRF 0-51  (18 = visually lossless)"),
        "mp4_h265_aac":  (22, 14, 35, "H.265  CRF 0-51  (22 = visually lossless)"),
        "webm_vp9_opus": (24, 15, 40, "VP9    CRF 0-63  (24 = high quality)"),
        "mov_prores":    (None, 0, 0,  "ProRes — lossless; CRF not used"),
        "mkv_h265_aac":  (22, 14, 35, "H.265  CRF 0-51  (22 = visually lossless)"),
        "gif_animated":  (None, 0, 0,  "GIF — palette-based; CRF not used"),
    }

    def _on_format_changed(self, *_):
        """Update CRF slider range, value and hint when output format changes."""
        fmt = self.out_format_var.get()
        preset = self._CRF_PRESETS.get(fmt, (18, 12, 30, "CRF (lower = better quality)"))
        best_crf, lo, hi, hint = preset
        if not hasattr(self, "_crf_scale"):
            return
        if best_crf is None:
            self._crf_scale.config(state="disabled", from_=0, to=1)
            self._crf_lbl.config(text="N/A")
        else:
            self._crf_scale.config(state="normal", from_=lo, to=hi)
            self.crf_var.set(best_crf)
            self._crf_lbl.config(text=str(best_crf))
        if hasattr(self, "_crf_hint"):
            self._crf_hint.config(text=hint)

    def _probe_bg_audio(self, path):
        """Probe video file for audio stream; set radio button on main thread."""
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "a:0",
                 "-show_entries", "stream=codec_type",
                 "-of", "default=noprint_wrappers=1:nokey=1", path],
                capture_output=True, text=True, timeout=10)
            has_audio = r.stdout.strip() == "audio"
        except Exception:
            has_audio = False
        def _apply():
            if has_audio:
                self.audio_source_var.set("background")
            else:
                self.audio_source_var.set("silent")
        self._ui(_apply)

    def _sync_fade_ranges(self, *_):
        """Recalculate all four fade slider maximums when duration changes."""
        try:
            dur = float(self.duration_var.get())
        except Exception:
            return
        self._on_fade_changed(dur=dur)

    def _on_fade_changed(self, _=None, dur=None):
        """Called whenever any fade slider moves — updates labels and caps ranges."""
        try:
            if dur is None:
                dur = float(self.duration_var.get())
            fi_start = float(self.text_fade_in.get())
            fi_dur   = float(self.text_fade_in_dur.get())
            fo_start = float(self.text_fade_out_from.get())
            fo_dur   = float(self.text_fade_out_dur.get())
        except Exception:
            return

        # Clamp: fi_start can be 0..dur
        fi_start = min(fi_start, dur)
        # fi_dur: 0..(dur - fi_start)
        fi_dur_max = max(0.1, dur - fi_start)
        fi_dur = min(fi_dur, fi_dur_max)
        # fo_start: (fi_start+fi_dur)..dur  — can't start before text is visible
        fo_min   = fi_start + fi_dur
        fo_start = max(fo_min, min(fo_start, dur))
        # fo_dur: 0..(dur - fo_start)
        fo_dur_max = max(0.1, dur - fo_start)
        fo_dur = min(fo_dur, fo_dur_max)

        # Apply clamped values
        for var, val in [(self.text_fade_in, fi_start),
                         (self.text_fade_in_dur, fi_dur),
                         (self.text_fade_out_from, fo_start),
                         (self.text_fade_out_dur, fo_dur)]:
            if abs(var.get() - val) > 0.001:
                var.set(round(val, 1))

        # Update slider ranges
        if hasattr(self, "_fi_scale"):
            self._fi_scale.config(to=dur)
        if hasattr(self, "_fid_scale"):
            self._fid_scale.config(to=max(0.1, fi_dur_max))
        if hasattr(self, "_fof_scale"):
            self._fof_scale.config(from_=round(fo_min, 1), to=dur)
        if hasattr(self, "_fod_scale"):
            self._fod_scale.config(to=max(0.1, fo_dur_max))

        # Update value labels
        if hasattr(self, "_fi_lbl"):
            self._fi_lbl.config(text=f"{fi_start:.1f}s")
        if hasattr(self, "_fid_lbl"):
            self._fid_lbl.config(text=f"{fi_dur:.1f}s")
        if hasattr(self, "_fof_lbl"):
            self._fof_lbl.config(text=f"{fo_start:.1f}s")
        if hasattr(self, "_fod_lbl"):
            self._fod_lbl.config(text=f"{fo_dur:.1f}s")

    def _reset_audio_sliders(self):
        """Reset all audio fine-control sliders to defaults and all audio checkboxes to off."""
        defaults = {
            "fade_dur_var":    1.5,
            "bass_freq_var":   80.0,
            "bass_gain_var":   6.0,
            "reverb_delay_ms": 40.0,
            "reverb_decay":    0.5,
            "comp_thr_var":   -18.0,
            "comp_ratio_var":  4.0,
            "hp_freq_var":     80.0,
            "lp_freq_var":     12000.0,
            "echo_delay_ms":   80.0,
            "echo_decay_var":  0.35,
            "tremolo_rate":    5.0,
            "tremolo_depth":   0.5,
            "master_volume_var": 1.0,
        }
        for attr, val in defaults.items():
            if hasattr(self, attr):
                getattr(self, attr).set(val)
        self._vol_lbl.config(text="1.00x")
        # Reset all audio effect checkboxes to off
        for tog in (self.afx_fade, self.afx_bass, self.afx_reverb, self.afx_wide,
                    self.afx_compressor, self.afx_highpass, self.afx_lowpass,
                    self.afx_normalize, self.afx_tremolo, self.afx_echo, self.afx_chorus):
            tog.var.set(False)

    def _reset_video_effects(self):
        """Reset all video effects in the Video Effects section to off."""
        for tog in (self.fx_eq, self.fx_scan, self.fx_drift, self.fx_mirror,
                    self.fx_grain, self.fx_letterbox, self.fx_vignette, self.fx_flash,
                    self.fx_pulse, self.fx_hueshift, self.fx_glitch, self.fx_bloom,
                    self.fx_sharpen):
            tog.var.set(False)

    def _probe_bg_duration(self):
        """Probe the selected background file and update the duration spinbox max."""
        path = self.bg_picker.get().strip()
        if not path or not os.path.isfile(path):
            return
        ext=_safe_getext(path)
        is_animated=(ext=="gif" and self._is_animated_gif(path))
        is_img=ext in ("jpg","jpeg","png","bmp","webp","tiff","gif")
        if is_img:
            return  # images have no duration
        try:
            r = subprocess.run(
                ["ffprobe","-v","error","-show_entries","format=duration",
                 "-of","default=noprint_wrappers=1:nokey=1", path],
                capture_output=True, text=True, timeout=10)
            src_dur = float(r.stdout.strip())
            if src_dur > 0:
                # Set max AND default to source duration
                max_dur = max(3, int(src_dur))
                self._dur_spinbox.config(to=max_dur)
                self.duration_var.set(max_dur)
                self._log(f"  Source duration: {src_dur:.1f}s  (duration set to {max_dur}s)", SUBTEXT)
        except Exception:
            pass

    def _start_build(self):
        bg  = self.bg_picker.get()
        aud = self.audio_picker.get()
        txt = self.text_var.get().strip()

        if not bg or not os.path.isfile(bg):
            messagebox.showwarning("Missing", "Select a background file."); return
        if (self.audio_source_var.get() == "provided"
                and (not aud or not os.path.isfile(aud))):
            messagebox.showwarning("Missing",
                "Select an audio file or change Audio Source mode."); return
        # Blank overlay text is allowed — drawtext is skipped in filter_complex

        self.build_btn.config(state="disabled")
        self.save_btn.pack_forget()
        self.preview_btn.config(state="disabled")
        try: self.preview_btn_holder.pack_forget()
        except Exception: pass
        self._clear_log()
        # Scroll all tab canvases so Build Log (below tabs) is visible
        # The log panel is below the notebook so no canvas scroll needed —
        # just ensure the window bottom is visible by scrolling to end
        self.after(50, lambda: [c.yview_moveto(1.0) for c in getattr(self, "_tab_canvases", [])])
        self._set_progress(0)
        self._output_file = None
        threading.Thread(target=self._build_thread, daemon=True).start()

    def _build_thread(self):
        import time; t0 = time.time()
        try:
            dur     = self.duration_var.get()
            seek    = float(self.seek_var.get())
            bg_end  = float(getattr(self, "bg_end_var",
                                     type("_",(),{"get":lambda s:0.0})()).get())
            text    = self.text_var.get().strip("\n \t")
            crf     = self.crf_var.get()
            preset  = self.preset_var.get()
            fmt=getattr(self,"out_format_var",tk.StringVar(value="mp4_h264_aac")).get()
            base_out=self.out_name_var.get().strip() or "intro_output"
            ext_map={"mp4_h264_aac":".mp4","mp4_h265_aac":".mp4","webm_vp9_opus":".webm","mov_prores":".mov","mkv_h265_aac":".mkv","gif_animated":".gif"}
            out_path=str(self.base_dir/(base_out+ext_map.get(fmt,".mp4")))

            self._log("=" * 52, ACCENT)
            self._log("***  INTRO BUILDER  v1.0  ***", ACCENT)
            self._log("=" * 52, ACCENT)
            self._log(f"  BG      : {self.bg_picker.get()}")
            self._log(f"  Audio   : {self.audio_source_var.get()}"
                      + (f"  /  {self.audio_picker.get()}"
                         if self.audio_source_var.get() == "provided" else ""))
            self._log(f"  Dur     : {dur}s  |  seek={seek}s")
            self._log(f"  Text    : {text}\n")

            # Pre-flight: log source info + available RAM
            try:
                pr = subprocess.run(
                    ["ffprobe","-v","error","-show_entries",
                     "stream=width,height,codec_name",
                     "-of","default=noprint_wrappers=1",
                     self.bg_picker.get()],
                    capture_output=True, text=True, timeout=10)
                for ln in pr.stdout.strip().splitlines():
                    self._log("  src: " + ln, SUBTEXT)
            except Exception: pass
            try:
                avail = [l for l in open("/proc/meminfo")
                         if "MemAvailable" in l]
                if avail: self._log("  RAM: " + avail[0].strip(), SUBTEXT)
            except Exception: pass

            # ── Step 1: Background ──────────────────────────────────
            self._log(">> [1/3] Background...", WARNING)
            self._set_status("1/3 Background...", WARNING)

            src_path=self.bg_picker.get()
            ext=_safe_getext(src_path)
            is_animated=(ext=="gif" and self._is_animated_gif(src_path))
            is_image=ext in ("jpg","jpeg","png","bmp","webp","tiff","gif")
            vf_bg = self._build_bg_vf(dur)
            self._log(f"  vf_bg   : {vf_bg}", WARNING)

            cmd1 = ["ffmpeg", "-y",
                    "-threads", "2"]          # limit decoder threads on Pi
            if seek > 0.0 and not is_image:
                cmd1 += ["-ss", str(seek)]
            if is_image:
                if ext=="gif" and is_animated: cmd1+=["-ignore_loop","0"]
                else: cmd1+=["-loop","1"]
            else:
                cmd1+=["-stream_loop","-1"]
            if vf_bg == "__MIRROR__":
                # Mirror effect needs filter_complex (split/hstack/vstack)
                mirror_fc = (
                    "[0:v]fps=30,scale=960:540,"
                    "split[ka][kb];[kb]hflip[kbf];[ka][kbf]hstack,"
                    "split[kc][kd];[kd]vflip[kdf];[kc][kdf]vstack,"
                    "scale=1920:1080,format=yuv420p[vout]"
                )
                _bg_t_arg = (["-to", str(bg_end)] if bg_end > 0.0
                             else ["-t", str(dur)])
                cmd1 += ["-i", self.bg_picker.get()] + _bg_t_arg + [
                         "-filter_complex", mirror_fc,
                         "-map", "[vout]",
                         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
                         "-threads", "2", "-an", "-movflags", "+faststart",
                         self.tmp_bg]
            else:
                _bg_t_arg = (["-to", str(bg_end)] if bg_end > 0.0
                             else ["-t", str(dur)])
                cmd1 += ["-i", self.bg_picker.get()] + _bg_t_arg + [
                         "-vf", vf_bg,
                         "-c:v", "libx264",
                         "-preset", "ultrafast",  # least RAM usage for intermediate
                         "-crf", "18",
                         "-threads", "2",         # limit encoder threads
                         "-an",
                         "-movflags", "+faststart",
                         self.tmp_bg]
            self._run_ffmpeg(cmd1, "bg")
            self._set_progress(30)

            # ── Step 2: Audio ───────────────────────────────────────
            self._log("\n>> [2/3] Audio...", WARNING)
            self._set_status("2/3 Audio...", WARNING)
            self._process_audio(dur, seek)
            self._set_progress(60)

            # ── Step 3: Composite ───────────────────────────────────
            self._log("\n>> [3/3] Compositing...", WARNING)
            self._set_status("3/3 Compositing...", WARNING)

            fc = self._build_filter_complex(text, dur)
            meta_json = json.dumps(self._get_settings_dict())
            encoded   = base64.b64encode(meta_json.encode()).decode()
            fmt=getattr(self,"out_format_var",tk.StringVar(value="mp4_h264_aac")).get()
            base_out=self.out_name_var.get().strip() or "intro_output"
            if fmt!="gif_animated":
                vcodec,acodec=self._codec_map(fmt,preset,crf)
                meta_args = (["-metadata", f"comment=IB_SETTINGS:{encoded}"]
                             if getattr(self, "save_metadata_var", None)
                             and self.save_metadata_var.get() else [])
                cmd3=(["ffmpeg","-y","-threads","2",
                       "-i",self.tmp_bg,"-i",self.tmp_audio,
                       "-map_metadata","-1",
                       "-filter_complex",fc,
                       "-map","[v]","-map","1:a"]
                      +vcodec+["-threads","2"]+acodec
                      +["-shortest"]+meta_args+[out_path])
                self._run_ffmpeg(cmd3,"composite")
            else:
                mid_mp4=str(self.base_dir/(base_out+".__mid__.mp4"))
                cmd3=["ffmpeg","-y","-threads","2",
                       "-i",self.tmp_bg,"-i",self.tmp_audio,
                       "-map_metadata","-1",
                       "-filter_complex",fc,"-map","[v]","-an",
                       "-c:v","libx264","-preset",preset,"-crf",str(max(16,crf-4)),
                       "-pix_fmt","yuv420p","-movflags","+faststart",mid_mp4]
                self._run_ffmpeg(cmd3,"composite_gif_mid")
                palette=str(self.base_dir/(base_out+".__pal__.png"))
                gif_fps=12
                self._run_ffmpeg(["ffmpeg","-y","-i",mid_mp4,"-vf",f"fps={gif_fps},scale=iw:-1:flags=lanczos,palettegen",palette],"gif_palette")
                self._run_ffmpeg(["ffmpeg","-y","-i",mid_mp4,"-i",palette,"-lavfi",f"fps={gif_fps},scale=iw:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=sierra2_4a","-loop","0",out_path],"gif_encode")
                for _f in (mid_mp4,palette):
                    try: os.remove(_f)
                    except Exception: pass
            self._set_progress(95)

            # Cleanup
            for f in (self.tmp_bg, self.tmp_audio,
                      self.tmp_audio_pcm, self.tmp_audio_filtered):
                try: os.remove(f)
                except Exception: pass

            sz = os.path.getsize(out_path)
            sz_s = (f"{sz/1_048_576:.2f} MB" if sz > 1_048_576
                    else f"{sz/1024:.1f} KB")
            elapsed = time.time() - t0

            self._log(f"\n[OK] Done in {elapsed:.1f}s", SUCCESS)
            self._log(f"     File size : {sz_s}", SUCCESS)
            self._log(f"     Output    : {out_path}", SUCCESS)
            self._set_status(f"[OK] {elapsed:.1f}s  |  {sz_s}", SUCCESS)
            self._set_progress(100)
            self._output_file = out_path
            self._ui(lambda: (
                self.save_btn.pack(side="left", padx=(0, 10)),
                self.save_btn.config(state="normal"),
                self.preview_btn.config(state="normal"),
                self.preview_btn_holder.pack(side="left")))

        except Exception as ex:
            self._log(f"\n[!!] Error: {ex}", DANGER)
            self._set_status(f"Failed: {ex}", DANGER)
        finally:
            self._ui(lambda: self.build_btn.config(state="normal"))

    # ── Audio processing (fixes m4a / mp3 decode issues) ─────────────
    def _process_audio(self, dur, seek):
        """
        Robust audio pipeline:
          1. Decode any source to uncompressed PCM WAV  (fixes m4a/mp3 issues)
          2. Apply audio effects
          3. Re-encode to AAC m4a
        """
        amode = self.audio_source_var.get()

        if amode == "silent":
            cmd = ["ffmpeg", "-y", "-f", "lavfi",
                   "-i", "anullsrc=r=44100:cl=stereo",
                   "-t", str(dur), "-c:a", "aac", "-b:a", "192k",
                   self.tmp_audio]
            self._run_ffmpeg(cmd, "audio_silent")
            return

        # Step 2a: decode to PCM — always works regardless of input codec
        if amode == "background":
            src = self.bg_picker.get()
            dec = ["ffmpeg", "-y"]
            if seek > 0.0:
                dec += ["-ss", str(seek)]
            dec += ["-i", src, "-t", str(dur), "-vn",
                    "-ar", "44100", "-ac", "2",
                    "-c:a", "pcm_s16le", self.tmp_audio_pcm]
        else:
            src = self.audio_picker.get()
            aseek = float(getattr(self, "audio_seek_var",
                                  type("_", (), {"get": lambda s: 0.0})()).get())
            aend  = float(getattr(self, "audio_end_var",
                                  type("_", (), {"get": lambda s: 0.0})()).get())
            dec = ["ffmpeg", "-y",
                   "-stream_loop", "-1"]
            if aseek > 0.0:
                dec += ["-ss", str(aseek)]
            # -to is relative to the file start (before -ss); use -t for duration instead
            # if an end point is set: clip length = aend - aseek (if aend > aseek)
            if aend > 0.0 and aend > aseek:
                clip_len = aend - aseek
                dec += ["-i", src, "-t", str(min(dur, clip_len)),
                        "-ar", "44100", "-ac", "2",
                        "-c:a", "pcm_s16le", self.tmp_audio_pcm]
            else:
                dec += ["-i", src, "-t", str(dur),
                        "-ar", "44100", "-ac", "2",
                        "-c:a", "pcm_s16le", self.tmp_audio_pcm]

        dec += ["-threads", "2"]
        self._run_ffmpeg(dec, "audio_decode")

        # Step 2b: build audio filter chain (v1.8: ordered + limiter)
        af_parts=[]
        fd=float(self.fade_dur_var.get())
        mv=float(self.master_volume_var.get())
        if self.afx_fade.get():
            af_parts+=[f"afade=t=in:st=0:d={fd}",f"afade=t=out:st={max(0,dur-fd)}:d={fd}"]
        if self.afx_highpass.get(): af_parts.append(f"highpass=f={int(self.hp_freq_var.get())}")
        if self.afx_lowpass.get():  af_parts.append(f"lowpass=f={int(self.lp_freq_var.get())}")
        if self.afx_bass.get():
            bf=int(self.bass_freq_var.get()); g=float(self.bass_gain_var.get())
            af_parts.append(f"equalizer=f={bf}:t=o:w={bf}:g={g:.1f}")
        if self.afx_compressor.get():
            r=float(self.comp_ratio_var.get()); thr=float(self.comp_thr_var.get())
            af_parts.append(f"acompressor=threshold={thr}dB:ratio={r:.1f}:attack=5:release=50:makeup=1")
        if self.afx_chorus.get():  af_parts.append("chorus=0.5:0.9:50|60|40:0.4|0.32|0.3:0.25|0.4|0.3:2|2.3|1.3")
        if self.afx_tremolo.get():
            rt=float(self.tremolo_rate.get()); dep=float(self.tremolo_depth.get())
            af_parts.append(f"tremolo=f={rt:.1f}:d={dep:.2f}")
        if getattr(self,"afx_echo",None) and self.afx_echo.get():
            edm=int(self.echo_delay_ms.get()); edc=float(self.echo_decay_var.get())
            af_parts.append(f"aecho=1.0:{edc:.2f}:{edm}:0.35")
        if self.afx_reverb.get():
            dec2=float(self.reverb_decay.get()); d1=int(self.reverb_delay_ms.get()); d2=min(int(d1*1.75),500)
            af_parts.append(f"aecho=0.8:{dec2:.2f}:{d1}|{d2}:0.3|0.2")
        if self.afx_wide.get():      af_parts.append("extrastereo=m=2.0,alimiter=limit=0.9")
        if self.afx_normalize.get(): af_parts.append("loudnorm=I=-16:TP=-1:LRA=11")
        af_parts.append(f"volume={mv:.3f}")
        af_parts.append("alimiter=limit=1.0")
        af_str=",".join(af_parts)

        # Step 2c: apply effects + encode to AAC
        cmd_fx = ["ffmpeg", "-y",
                  "-i", self.tmp_audio_pcm,
                  "-af", af_str,
                  "-c:a", "aac", "-b:a", "192k",
                  self.tmp_audio]
        self._run_ffmpeg(cmd_fx, "audio_fx")

    # ── Background vf chain ───────────────────────────────────────────
    def _build_bg_vf(self, dur):
        if self.fx_mirror.get():
            return "__MIRROR__"

        # Detect whether source is a still/animated graphic
        src_path = self.bg_picker.get()
        ext = _safe_getext(src_path)
        is_animated = (ext == "gif" and self._is_animated_gif(src_path))
        is_img = ext in ("jpg","jpeg","png","bmp","webp","tiff","gif")

        # Build the pad colour (used when preserve_ar is on for images)
        pad_col = "black"
        if getattr(self, "pad_color_var", None):
            pad_col = self.pad_color_var.get().strip() or "black"

        preserve = is_img and getattr(self, "preserve_ar_var", None) and self.preserve_ar_var.get()
        self._log(f"  img={is_img}  preserve_ar={preserve}  pad_col={pad_col}", SUBTEXT)

        parts = []

        if self.fx_drift.get():
            if preserve:
                # Scale to fit within the wider drift canvas preserving AR, pad, then drift-crop
                parts = [
                    "fps=30",
                    "scale=2076:1080:force_original_aspect_ratio=decrease",
                    f"pad=2076:1080:(ow-iw)/2:(oh-ih)/2:{pad_col}",
                    f"crop=1920:1080:'min(t/{dur}*156,156)':0",
                ]
            else:
                parts = [
                    "fps=30",
                    "scale=2076:1080",
                    f"crop=1920:1080:'min(t/{dur}*156,156)':0",
                ]
        else:
            if preserve:
                parts = [
                    "fps=30",
                    "scale=1920:1080:force_original_aspect_ratio=decrease",
                    f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:{pad_col}",
                ]
            else:
                parts = ["fps=30", "scale=1920:1080"]

        if self.fx_pulse.get():
            parts += [
                "scale=2040:1148",
                f"crop=1920:1080"
                f":'60+60*sin(2*PI*t/{max(dur/2,1)})'"
                f":'34+34*sin(2*PI*t/{max(dur/2,1)})'",
            ]
        if self.fx_hueshift.get():
            parts.append(f"hue=h='mod(t/{dur}*120,360)'")
        parts.append("format=yuv420p")
        return ",".join(parts)

    # ── filter_complex for composite ──────────────────────────────────
    def _build_filter_complex(self, text, dur):
        font_path  = self._find_font(self.font_var.get())
        pos        = self.pos_var.get()
        fade_t     = self.fade_duration_var.get()
        fo_start   = max(0.0, dur - fade_t)
        text_op    = self.text_opacity_var.get() / 100.0
        try:
            fi_start = max(0.0, float(self.text_fade_in.get()))
            fi_dur   = max(0.0, float(self.text_fade_in_dur.get()))
            fo_start = max(0.0, float(self.text_fade_out_from.get()))
            fo_dur   = max(0.0, float(self.text_fade_out_dur.get()))
            tf_enabled = bool(self.text_fade_enable.get())
        except Exception:
            fi_start, fi_dur, fo_start, fo_dur, tf_enabled = 0.0, 0.0, dur, 0.0, False
        extras_op  = self.extras_opacity_var.get() / 100.0

        if pos == "Center":         tx,ty = "(w-text_w)/2","(h-text_h)/2"
        elif pos == "Top-Center":   tx,ty = "(w-text_w)/2","80"
        elif pos == "Bottom-Center":tx,ty = "(w-text_w)/2","h-text_h-80"
        else:                       tx,ty = "(w-text_w)/2","h*0.72"

        op = f"{text_op:.3f}"
        if tf_enabled:
            fi_end   = fi_start + max(0.001, fi_dur)     # when fully visible
            fo_end   = fo_start + max(0.001, fo_dur)     # when fully gone
            fo_end   = min(fo_end, dur)
            fo_ramp  = max(0.001, fo_end - fo_start)

            # Build nested if() expression — ffmpeg evaluates left-to-right
            if fi_dur > 0 and fo_dur > 0:
                # invisible → ramp in → hold → ramp out → invisible
                alpha = (f"if(lt(t,{fi_start:.3f}),0,"
                         f"if(lt(t,{fi_end:.3f}),(t-{fi_start:.3f})/{fi_dur:.3f}*{op},"
                         f"if(lt(t,{fo_start:.3f}),{op},"
                         f"if(lt(t,{fo_end:.3f}),({fo_end:.3f}-t)/{fo_ramp:.3f}*{op},"
                         f"0))))")
            elif fi_dur > 0:
                # invisible → ramp in → hold
                alpha = (f"if(lt(t,{fi_start:.3f}),0,"
                         f"if(lt(t,{fi_end:.3f}),(t-{fi_start:.3f})/{fi_dur:.3f}*{op},"
                         f"{op}))")
            elif fo_dur > 0:
                # hold → ramp out → invisible
                alpha = (f"if(lt(t,{fo_start:.3f}),{op},"
                         f"if(lt(t,{fo_end:.3f}),({fo_end:.3f}-t)/{fo_ramp:.3f}*{op},"
                         f"0))")
            else:
                alpha = op
        else:
            alpha = op

        pre, post = [], []

        # Pre-bloom (colour/image)
        if self.fx_eq.get():
            pre.append("eq=contrast=1.12:brightness=0.02:saturation=1.25")
        if self.fx_sepia.get():
            if self.sepia_mode_var.get() == "sepia":
                pre.append("colorchannelmixer="
                           "rr=.393:rg=.769:rb=.189:"
                           "gr=.349:gg=.686:gb=.168:"
                           "br=.272:bg=.534:bb=.131")
            else:
                pre.append("hue=s=0")
        if self.fx_vignette.get():
            pre.append("vignette=PI/6")
        if self.fx_grain.get():
            pre.append("noise=alls=12:allf=t+u")
        if self.fx_sharpen.get():
            pre.append("unsharp=5:5:1.0:5:5:0.0")

        # Post-bloom (draw operations)
        if text:
            lines     = text.split("\n")
            fontsize  = self.fontsize_var.get()
            line_h    = int(fontsize * 1.2)   # approx line height with spacing
            n         = len(lines)
            fontcolor = self.fontcolor_var.get()
            borderw   = self.borderw_var.get()
            # Adjust base y so the block is centred on ty
            # ty expressions like "(h-text_h)/2" apply per-line; we offset each
            for i, line in enumerate(lines):
                if not line.strip():
                    continue   # skip blank lines (still counted for spacing)
                # Vertical offset from the block centre
                offset = int((i - (n - 1) / 2.0) * line_h)
                if ty == "(h-text_h)/2":
                    y_expr = f"(h-text_h)/2+{offset}" if offset != 0 else "(h-text_h)/2"
                elif ty == "80":
                    y_expr = f"80+{i}*{line_h}"
                elif ty == "h-text_h-80":
                    block_top = f"h-text_h-80-{(n-1-i)*line_h}"
                    y_expr = block_top
                else:  # Lower-Third h*0.72
                    y_expr = f"h*0.72+{offset}" if offset != 0 else "h*0.72"
                dt = (f"drawtext=text='{self._esc(line)}'"
                      f":fontcolor={fontcolor}"
                      f":fontsize={fontsize}"
                      f":x={tx}:y={y_expr}"
                      f":alpha='{alpha}'"
                      f":borderw={borderw}:bordercolor=gray")
                if font_path: dt += f":fontfile='{font_path}'"
                post.append(dt)

        if self.fx_scan.get():
            post.append(f"drawbox=x=0:y='mod(t,{dur})*h/{dur}'"
                        f":w=iw:h=6:color=white@0.18:t=fill")
        if self.fx_flash.get():
            h = dur / 2
            post.append(f"drawbox=x=(w/2-400):y=(h/2-10):w=800:h=20"
                        f":color=white@0.15:t=fill"
                        f":enable='between(t,{h},{h+0.25})'")
        if self.fx_glitch.get():
            for gt in [dur*0.25, dur*0.55, dur*0.82]:
                gs, ge = round(gt, 2), round(gt+0.07, 2)
                if ge > dur: continue
                post.append(f"drawbox=x=0:y='h*0.3':w=iw:h=8"
                            f":color=white@0.7:t=fill"
                            f":enable='between(t,{gs},{ge})'")
                post.append(f"drawbox=x=0:y='h*0.65':w=iw:h=4"
                            f":color=cyan@0.5:t=fill"
                            f":enable='between(t,{gs},{ge})'")
        if self.fx_letterbox.get():
            post += ["drawbox=x=0:y=0:w=iw:h=127:color=black:t=fill",
                     "drawbox=x=0:y=ih-127:w=iw:h=127:color=black:t=fill"]

        if self.fx_fade_col_var.get():
            fc  = self.fade_color_var.get().strip() or "black"
            ft  = float(self.fade_duration_var.get())
            fot = max(0.0, dur - ft)
            post += [f"fade=t=in:st=0:d={ft}:color={fc}",
                     f"fade=t=out:st={fot}:d={ft}:color={fc}"]

        # Lower Third
        if self.ov_lowerthird.get():
            ltt_raw = self.lt_title_var.get().strip()
            lts_raw = self.lt_sub_var.get().strip()
            if ltt_raw or lts_raw:
                ltt = self._esc(ltt_raw)
                lts = self._esc(lts_raw)
                lt_from  = float(self.lt_from_var.get())
                lt_to    = float(self.lt_to_var.get())
                lt_style = getattr(self, "lt_style_var", type("_",(),{"get":lambda s:"slide"})()).get()
                box_hex  = getattr(self, "lt_bg_color_var", type("_",(),{"get":lambda s:"#222222"})()).get().strip() or "#222222"
                box_op   = float(getattr(self, "lt_box_opacity_var", type("_",(),{"get":lambda s:0.72})()).get())
                lop      = box_op * extras_op

                # Estimate box width from longest line (approx 17px per char for size-36 title)
                title_chars = len(ltt_raw)
                sub_chars   = len(lts_raw)
                max_chars   = max(title_chars, sub_chars, 1)
                # Title font=36: ~22px avg char width; 60px padding each side
                # Subtitle font=26: slightly narrower so title drives width
                title_w = title_chars * 22 + 120
                sub_w   = sub_chars   * 16 + 120
                box_w   = max(320, title_w, sub_w)
                # Box height: title(~42px) + subtitle(~32px if present) + padding
                box_h       = 96 if lts_raw else 60
                bar_y       = int(1080 * 0.78)
                anim_dur    = min(0.5, (lt_to - lt_from) * 0.25)  # 25% of display time, max 0.5s

                enable = f"between(t,{lt_from:.3f},{lt_to:.3f})"

                # drawbox does NOT support dynamic x/y expressions —
                # workaround: box always fades in/out; text slides for "slide" style.

                slide_in_end  = lt_from + anim_dur
                slide_out_beg = lt_to   - anim_dur
                fade_in_end   = lt_from + anim_dur
                fade_out_beg  = lt_to   - anim_dur

                # Alpha expression used for both box and text in fade mode,
                # and for the box in slide mode (box fades, text slides)
                alpha_expr = (f"if(lt(t,{lt_from:.3f}),0,"
                              f"if(lt(t,{fade_in_end:.3f}),(t-{lt_from:.3f})/{anim_dur:.3f},"
                              f"if(lt(t,{fade_out_beg:.3f}),1,"
                              f"if(lt(t,{lt_to:.3f}),({lt_to:.3f}-t)/{anim_dur:.3f},"
                              f"0))))")

                # Box: always drawn at fixed x=60 with fade alpha
                # (drawbox requires static coordinates)
                box_alpha_val = f"({alpha_expr})*{lop:.3f}"
                # FFmpeg drawbox colour includes opacity in the hex@alpha syntax.
                # We bake the fade into the alpha component via a workaround:
                # Use enable='between' for the static window, and adjust opacity
                # with the full lop value. The fade is handled by letting the
                # box appear/disappear via a very short enable window approximation.
                # Cleanest working approach: fixed box with enable=between, text slides.
                post.append(f"drawbox=x=60:y={bar_y-8}:w={box_w}:h={box_h}"
                            f":color={box_hex}@{lop:.3f}:t=fill"
                            f":enable='{enable}'")

                if lt_style == "slide":
                    # Text slides in from left, box is already in place (faded in above)
                    off = -(box_w + 10)
                    tx = (f"if(lt(t,{lt_from:.3f}),{off},"
                          f"if(lt(t,{slide_in_end:.3f}),{off}+({80-off})*(t-{lt_from:.3f})/{anim_dur:.3f},"
                          f"if(lt(t,{slide_out_beg:.3f}),80,"
                          f"if(lt(t,{lt_to:.3f}),80+({off}-80)*(t-{slide_out_beg:.3f})/{anim_dur:.3f},"
                          f"{off}))))")
                    txt_alpha = f"{extras_op:.3f}"
                else:
                    # Both box and text fade in/out together
                    tx = "80"
                    txt_alpha = f"({alpha_expr})*{extras_op:.3f}"

                if ltt_raw:
                    post.append(f"drawtext=text='{ltt}':fontcolor=white:fontsize=36"
                                f":x='{tx}':y={bar_y+8}"
                                f":alpha='{txt_alpha}':enable='{enable}'")
                if lts_raw:
                    post.append(f"drawtext=text='{lts}':fontcolor=#dddddd:fontsize=26"
                                f":x='{tx}':y={bar_y+50}"
                                f":alpha='{txt_alpha}':enable='{enable}'")

        # Countdown footer — counts DOWN to end of video
        if self.ov_countdown.get():
            cf    = self.cd_from_var.get()
            csz   = self.cd_size_var.get()
            ccol  = self.cd_color_var.get() or "white"
            c_pos = self.cd_pos_var.get()
            cop   = extras_op

            # Work out x/y from position choice
            if c_pos == "Bottom-Centre":
                cdx, cdy = "(w-text_w)/2", f"h-{csz+20}"
            elif c_pos == "Bottom-Left":
                cdx, cdy = "20", f"h-{csz+20}"
            elif c_pos == "Bottom-Right":
                cdx, cdy = f"w-text_w-20", f"h-{csz+20}"
            elif c_pos == "Top-Centre":
                cdx, cdy = "(w-text_w)/2", "20"
            else:  # Centre
                cdx, cdy = "(w-text_w)/2", "(h-text_h)/2"

            # Countdown shows "seconds remaining until end":
            # at t = dur-cf  → shows cf
            # at t = dur-1   → shows 1
            # '0' is excluded intentionally (no flash at end)
            start_t = max(0.0, dur - cf)
            for i in range(cf, 0, -1):   # cf down to 1 (0 excluded)
                ts = round(dur - i, 3)
                te = round(ts + 1.0, 3)
                if ts < 0 or ts >= dur: continue
                te = min(te, dur)
                post.append(
                    f"drawtext=text='{i}'"
                    f":fontcolor={ccol}@{cop:.2f}"
                    f":fontsize={csz}"
                    f":x={cdx}:y={cdy}"
                    f":borderw=3:bordercolor=black@{cop:.2f}"
                    f":enable='between(t,{ts:.2f},{te:.2f})'")

        # Assemble — guard against empty filter list (causes ffmpeg parse error)
        all_filters = pre + post
        if not all_filters:
            all_filters = ["null"]   # no-op passthrough; avoids "[0:v][v]" syntax error

        if self.fx_bloom.get():
            pre_s  = (",".join(pre) + ",") if pre else ""
            post_s = ("," + ",".join(post)) if post else ""
            return (f"[0:v]{pre_s}split[ba][bb];"
                    f"[bb]boxblur=15:2,lutyuv=y='min(val+40,255)'[bg];"
                    f"[ba][bg]blend=all_mode=screen:all_opacity=0.4"
                    f"{post_s}[v]")
        else:
            return "[0:v]" + ",".join(all_filters) + "[v]"

    # ── ffmpeg runner ─────────────────────────────────────────────────
    def _run_ffmpeg(self, cmd, label):
        self._log("  $ " + " ".join(cmd[:6]) + " ...", SUBTEXT)
        try:
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True)
            for line in proc.stdout:
                line = line.rstrip()
                if not line: continue
                if "time=" in line or "frame=" in line:
                    self._parse_progress(line)
                    self._log("  " + line, "#334455")
                elif "error" in line.lower():
                    self._log("  " + line, DANGER)
                else:
                    self._log("  " + line, "#445566")
            proc.wait()
            rc = proc.returncode
            if rc in (-11, 139):
                raise RuntimeError(
                    "ffmpeg SIGSEGV on step '" + label + "' -- "
                    "likely out of memory on Pi.\n"
                    "Try: Preset=ultrafast, lower Duration, "
                    "or pre-scale source to 1080p.")
            if rc != 0:
                raise RuntimeError(
                    "ffmpeg failed for '" + label + "' (exit " + str(rc) + ")")
        except FileNotFoundError:
            raise RuntimeError(
                "ffmpeg not found. Install: sudo apt install ffmpeg")

    def _parse_progress(self, line):
        m = re.search(r"time=(\d+):(\d+):([\d.]+)", line)
        if m:
            h, mn, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            cur = h*3600 + mn*60 + s
            dur = self.duration_var.get()
            base = self.progress_var.get()
            pct  = min(99, base + (cur / max(dur, 1)) * 28)
            self._set_progress(pct)

    def _find_font(self, name):
        dirs = [Path("/usr/share/fonts"), Path("/usr/local/share/fonts"),
                Path.home()/".fonts", Path.home()/".local/share/fonts"]
        safe = name.lower().replace(" ", "")
        for d in dirs:
            if not d.exists(): continue
            for ext in ("*.ttf", "*.otf"):
                for f in d.rglob(ext):
                    if safe in f.stem.lower(): return str(f)
        return None

    def _esc(self, t):
        """Escape text for FFmpeg drawtext.
        Apostrophes/single-quotes are replaced with the Unicode right single
        quotation mark (U+2019) which is visually identical and never breaks
        the FFmpeg filter string parser. Colons are backslash-escaped."""
        return (t.replace("\\", "\\\\")   # escape existing backslashes first
                 .replace("'", "\u2019")         # ' → typographic right quote
                 .replace(":", "\\:"))           # colon escape

    # ── Preview / Save As ─────────────────────────────────────────────
    def _preview(self):
        if not getattr(self, "_output_file", None) or \
                not os.path.isfile(self._output_file):
            messagebox.showerror("No Output", "Build first."); return
        try:
            subprocess.Popen(
                ["vlc", "--avcodec-hw=none", self._output_file],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            messagebox.showerror("VLC Not Found",
                                 "Install: sudo apt install vlc")

    def _save_as(self):
        if not getattr(self, "_output_file", None) or \
                not os.path.isfile(self._output_file):
            messagebox.showerror("No Output", "Build first."); return
        ext=Path(self._output_file).suffix.lower() or ".mp4"
        dest = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=Path(self._output_file).name)
        if dest:
            shutil.copy2(self._output_file, dest)
            self._log(f"Saved to: {dest}", SUCCESS)
            messagebox.showinfo("Saved", f"Saved to:\n{dest}")


# ──────────────────────────────────────────────
if __name__ == "__main__":
    if sys.platform == "win32":
        import ctypes
        try:
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except Exception:
            pass
    IntroBuilderApp().mainloop()