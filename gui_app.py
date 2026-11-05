"""
Aplikasi Desktop GUI Native Modern
Sistem Monitoring Akhlak Siswa (Kelas XII TKJ - SMK Alhadiid)
Dibangun menggunakan pustaka standar Python: tkinter, ttk, json, webbrowser.
Zero External Dependencies.
"""

import json
import os
import sqlite3
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser

from monitoring_akhlak import (
    NAMA_DB_DEFAULT,
    ambil_semua_siswa,
    isi_data_seeder,
    koneksi_db,
    lihat_riwayat,
    ringkasan,
    siapkan_db,
    statistik_global,
    tambah_catatan,
    tambah_siswa,
)

# Palet Warna Dark Minimalist (Zinc / Slate Aesthetic)
BG_MAIN = "#09090b"
BG_CARD = "#121215"
BG_PANEL = "#18181b"
BORDER_COLOR = "#27272a"
TEXT_PRIMARY = "#f4f4f5"
TEXT_MUTED = "#a1a1aa"
TEXT_DIM = "#71717a"
COLOR_BLUE = "#3b82f6"
COLOR_GREEN = "#10b981"
COLOR_RED = "#f43f5e"
COLOR_AMBER = "#f59e0b"


class ModernCard(tk.Frame):
    """Komponen kartu metrik dengan border 1px dan visualisasi angka."""

    def __init__(self, parent, title, value="0", subtitle="", value_color=TEXT_PRIMARY, **kwargs):
        super().__init__(parent, bg=BG_PANEL, highlightbackground=BORDER_COLOR, highlightthickness=1, bd=0, padx=12, pady=10, **kwargs)
        self.lbl_title = tk.Label(self, text=title.upper(), font=("Helvetica", 8, "bold"), fg=TEXT_MUTED, bg=BG_PANEL)
        self.lbl_title.pack(anchor="w")

        self.lbl_val = tk.Label(self, text=value, font=("Helvetica", 18, "bold"), fg=value_color, bg=BG_PANEL)
        self.lbl_val.pack(anchor="w", pady=(3, 1))

        self.lbl_sub = tk.Label(self, text=subtitle, font=("Helvetica", 8), fg=TEXT_DIM, bg=BG_PANEL)
        self.lbl_sub.pack(anchor="w")

    def update_value(self, val):
        self.lbl_val.config(text=str(val))


class MonitoringAkhlakGUI(tk.Tk):
    """Aplikasi utama Desktop GUI Sistem Monitoring Akhlak Siswa."""

    def __init__(self):
        super().__init__()
        self.title("Monitoring Akhlak Siswa | SMK Alhadiid (Kelas XII TKJ)")
        self.geometry("1160x740")
        self.minsize(980, 620)
        self.configure(bg=BG_MAIN)

        siapkan_db()

        self.siswa_terpilih_id = None
        self.siswa_terpilih_nama = None
        self.daftar_cache_siswa = []

        self._atur_style()
        self._bangun_ui()
        self.muat_data_semua()

    def _atur_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Treeview styling
        style.configure(
            "Custom.Treeview",
            background=BG_PANEL,
            foreground=TEXT_PRIMARY,
            fieldbackground=BG_PANEL,
            rowheight=26,
            borderwidth=0,
            font=("Helvetica", 9),
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", "#27272a")],
            foreground=[("selected", "#ffffff")],
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=BG_MAIN,
            foreground=TEXT_MUTED,
            font=("Helvetica", 8, "bold"),
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", BORDER_COLOR)],
            foreground=[("active", TEXT_PRIMARY)],
        )

        # Scrollbar styling
        style.configure(
            "Vertical.TScrollbar",
            background=BG_PANEL,
            troughcolor=BG_MAIN,
            borderwidth=0,
            arrowsize=10,
        )

    def _bangun_ui(self):
        # 1. TOP NAVBAR
        nav = tk.Frame(self, bg=BG_MAIN, height=54, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=16, pady=8)
        nav.pack(fill="x", side="top")

        left_nav = tk.Frame(nav, bg=BG_MAIN)
        left_nav.pack(side="left")

        badge = tk.Label(left_nav, text="XII TKJ", font=("Helvetica", 8, "bold"), fg=COLOR_BLUE, bg="#1e293b", padx=6, pady=2)
        badge.pack(side="left", padx=(0, 10))

        title_lbl = tk.Label(left_nav, text="Sistem Monitoring Akhlak Siswa", font=("Helvetica", 12, "bold"), fg=TEXT_PRIMARY, bg=BG_MAIN)
        title_lbl.pack(side="left")

        subtitle_lbl = tk.Label(left_nav, text=" • SMK Alhadiid (Lab Jaringan)", font=("Helvetica", 9), fg=TEXT_MUTED, bg=BG_MAIN)
        subtitle_lbl.pack(side="left")

        # Right Action Buttons
        right_nav = tk.Frame(nav, bg=BG_MAIN)
        right_nav.pack(side="right")

        btn_seed = tk.Button(right_nav, text="⚡ Seed 10 Siswa", font=("Helvetica", 8, "bold"), fg=COLOR_AMBER, bg=BG_PANEL, activebackground=BORDER_COLOR, activeforeground="#ffffff", bd=0, padx=10, pady=5, cursor="hand2", command=self.aksi_seed)
        btn_seed.pack(side="left", padx=4)

        btn_web = tk.Button(right_nav, text="🌐 Buka Web Dashboard", font=("Helvetica", 8, "bold"), fg=COLOR_BLUE, bg=BG_PANEL, activebackground=BORDER_COLOR, activeforeground="#ffffff", bd=0, padx=10, pady=5, cursor="hand2", command=self.aksi_buka_web)
        btn_web.pack(side="left", padx=4)

        btn_export = tk.Button(right_nav, text="📥 Ekspor JSON", font=("Helvetica", 8), fg=TEXT_MUTED, bg=BG_PANEL, activebackground=BORDER_COLOR, activeforeground="#ffffff", bd=0, padx=10, pady=5, cursor="hand2", command=self.aksi_ekspor_json)
        btn_export.pack(side="left", padx=4)

        # 2. METRIC CARDS ROW
        cards_row = tk.Frame(self, bg=BG_MAIN, padx=16, pady=12)
        cards_row.pack(fill="x", side="top")

        self.card_siswa = ModernCard(cards_row, "Total Siswa", "0", "Kelas XII TKJ Terdata", COLOR_BLUE)
        self.card_siswa.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.card_catatan = ModernCard(cards_row, "Total Catatan", "0", "Rekam Jejak Pembinaan", TEXT_PRIMARY)
        self.card_catatan.pack(side="left", fill="x", expand=True, padx=4)

        self.card_apresiasi = ModernCard(cards_row, "Apresiasi (+1)", "0", "Capaian & Perilaku Baik", COLOR_GREEN)
        self.card_apresiasi.pack(side="left", fill="x", expand=True, padx=4)

        self.card_evaluasi = ModernCard(cards_row, "Evaluasi (-1)", "0", "Pendampingan Aktif", COLOR_RED)
        self.card_evaluasi.pack(side="left", fill="x", expand=True, padx=(6, 0))

        # 3. SPLIT MAIN CONTAINER (Dual-Pane)
        paned = tk.PanedWindow(self, orient="horizontal", bg=BORDER_COLOR, bd=0, sashwidth=2)
        paned.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # === PANEL KIRI: DAFTAR SISWA ===
        panel_kiri = tk.Frame(paned, bg=BG_CARD, padx=12, pady=12)
        paned.add(panel_kiri, minsize=380, width=420)

        top_kiri = tk.Frame(panel_kiri, bg=BG_CARD)
        top_kiri.pack(fill="x", pady=(0, 8))

        lbl_hdr_siswa = tk.Label(top_kiri, text="Daftar Siswa", font=("Helvetica", 10, "bold"), fg=TEXT_PRIMARY, bg=BG_CARD)
        lbl_hdr_siswa.pack(side="left")

        btn_tambah_siswa = tk.Button(top_kiri, text="+ Siswa Baru", font=("Helvetica", 8, "bold"), fg="#ffffff", bg=COLOR_BLUE, activebackground="#2563eb", activeforeground="#ffffff", bd=0, padx=8, pady=3, cursor="hand2", command=self.buka_dialog_tambah_siswa)
        btn_tambah_siswa.pack(side="right")

        # Search Bar
        search_frame = tk.Frame(panel_kiri, bg=BG_MAIN, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=6, pady=4)
        search_frame.pack(fill="x", pady=(0, 8))

        lbl_cari_icon = tk.Label(search_frame, text="🔍", font=("Helvetica", 8), fg=TEXT_DIM, bg=BG_MAIN)
        lbl_cari_icon.pack(side="left", padx=(0, 4))

        self.entry_cari = tk.Entry(search_frame, font=("Helvetica", 9), fg=TEXT_PRIMARY, bg=BG_MAIN, insertbackground=TEXT_PRIMARY, bd=0)
        self.entry_cari.pack(side="left", fill="x", expand=True)
        self.entry_cari.bind("<KeyRelease>", self.filter_siswa_live)

        # Tabel Siswa (Treeview)
        tree_frame_kiri = tk.Frame(panel_kiri, bg=BG_CARD)
        tree_frame_kiri.pack(fill="both", expand=True)

        cols_siswa = ("id", "nama", "catatan", "skor")
        self.tree_siswa = ttk.Treeview(tree_frame_kiri, columns=cols_siswa, show="headings", style="Custom.Treeview", selectmode="browse")
        self.tree_siswa.heading("id", text="ID SISWA")
        self.tree_siswa.heading("nama", text="NAMA SISWA")
        self.tree_siswa.heading("catatan", text="CATATAN")
        self.tree_siswa.heading("skor", text="SKOR")

        self.tree_siswa.column("id", width=90, anchor="w")
        self.tree_siswa.column("nama", width=160, anchor="w")
        self.tree_siswa.column("catatan", width=70, anchor="center")
        self.tree_siswa.column("skor", width=60, anchor="center")

        scroll_kiri = ttk.Scrollbar(tree_frame_kiri, orient="vertical", command=self.tree_siswa.yview, style="Vertical.TScrollbar")
        self.tree_siswa.configure(yscrollcommand=scroll_kiri.set)

        self.tree_siswa.pack(side="left", fill="both", expand=True)
        scroll_kiri.pack(side="right", fill="y")

        self.tree_siswa.bind("<<TreeviewSelect>>", self.saat_siswa_diklik)

        # === PANEL KANAN: DETAIL & RIWAYAT SISWA ===
        panel_kanan = tk.Frame(paned, bg=BG_CARD, padx=14, pady=12)
        paned.add(panel_kanan, minsize=520)

        # Header Siswa Terpilih
        self.header_kanan = tk.Frame(panel_kanan, bg=BG_PANEL, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=12, pady=10)
        self.header_kanan.pack(fill="x", pady=(0, 10))

        self.lbl_detail_id = tk.Label(self.header_kanan, text="PILIH SISWA", font=("Consolas", 9, "bold"), fg=COLOR_BLUE, bg=BG_PANEL)
        self.lbl_detail_id.pack(anchor="w")

        self.lbl_detail_nama = tk.Label(self.header_kanan, text="Silakan klik baris siswa di panel kiri", font=("Helvetica", 12, "bold"), fg=TEXT_PRIMARY, bg=BG_PANEL)
        self.lbl_detail_nama.pack(anchor="w", pady=(2, 2))

        self.lbl_detail_ringkasan = tk.Label(self.header_kanan, text="Pilih salah satu siswa untuk meninjau riwayat dan menambah catatan pembinaan.", font=("Helvetica", 8), fg=TEXT_MUTED, bg=BG_PANEL)
        self.lbl_detail_ringkasan.pack(anchor="w")

        # Action Button Tambah Catatan
        action_bar_kanan = tk.Frame(panel_kanan, bg=BG_CARD)
        action_bar_kanan.pack(fill="x", pady=(0, 8))

        lbl_hdr_riwayat = tk.Label(action_bar_kanan, text="Riwayat Catatan Perilaku & Tindak Lanjut", font=("Helvetica", 10, "bold"), fg=TEXT_PRIMARY, bg=BG_CARD)
        lbl_hdr_riwayat.pack(side="left")

        self.btn_tambah_catatan = tk.Button(action_bar_kanan, text="+ Catat Pembinaan", font=("Helvetica", 8, "bold"), fg="#ffffff", bg=COLOR_GREEN, activebackground="#059669", activeforeground="#ffffff", bd=0, padx=10, pady=4, cursor="hand2", state="disabled", command=self.buka_dialog_tambah_catatan)
        self.btn_tambah_catatan.pack(side="right")

        # Tabel Riwayat Catatan
        tree_frame_kanan = tk.Frame(panel_kanan, bg=BG_CARD)
        tree_frame_kanan.pack(fill="both", expand=True)

        cols_riwayat = ("tanggal", "kategori", "skor", "deskripsi", "tindak_lanjut")
        self.tree_riwayat = ttk.Treeview(tree_frame_kanan, columns=cols_riwayat, show="headings", style="Custom.Treeview")
        self.tree_riwayat.heading("tanggal", text="TANGGAL")
        self.tree_riwayat.heading("kategori", text="KATEGORI")
        self.tree_riwayat.heading("skor", text="SKOR")
        self.tree_riwayat.heading("deskripsi", text="DESKRIPSI FAKTUAL")
        self.tree_riwayat.heading("tindak_lanjut", text="RENCANA TINDAK LANJUT")

        self.tree_riwayat.column("tanggal", width=90, anchor="center")
        self.tree_riwayat.column("kategori", width=110, anchor="w")
        self.tree_riwayat.column("skor", width=65, anchor="center")
        self.tree_riwayat.column("deskripsi", width=220, anchor="w")
        self.tree_riwayat.column("tindak_lanjut", width=200, anchor="w")

        scroll_kanan = ttk.Scrollbar(tree_frame_kanan, orient="vertical", command=self.tree_riwayat.yview, style="Vertical.TScrollbar")
        self.tree_riwayat.configure(yscrollcommand=scroll_kanan.set)

        self.tree_riwayat.pack(side="left", fill="both", expand=True)
        scroll_kanan.pack(side="right", fill="y")

    # =========================================================================
    # DATA LOADING & FILTER LOGIC
    # =========================================================================

    def muat_data_semua(self):
        # 1. Update Metrik Kartu
        stats = statistik_global()
        self.card_siswa.update_value(stats["total_siswa"])
        self.card_catatan.update_value(stats["total_catatan"])
        self.card_apresiasi.update_value(f"+{stats['total_apresiasi']}")
        self.card_evaluasi.update_value(stats["total_evaluasi"])

        # 2. Update Tabel Siswa
        self.daftar_cache_siswa = ambil_semua_siswa()
        self.render_tabel_siswa(self.daftar_cache_siswa)

        # 3. Refresh Detail Siswa Jika Sudah Terpilih
        if self.siswa_terpilih_id:
            self.segarkan_detail_siswa(self.siswa_terpilih_id, self.siswa_terpilih_nama)

    def render_tabel_siswa(self, data):
        self.tree_siswa.delete(*self.tree_siswa.get_children())
        for id_s, nama, jml, skor in data:
            skor_text = f"+{skor}" if skor > 0 else (str(skor) if skor < 0 else "0")
            self.tree_siswa.insert("", "end", values=(id_s, nama, jml, skor_text))

    def filter_siswa_live(self, event=None):
        q = self.entry_cari.get().strip().lower()
        if not q:
            self.render_tabel_siswa(self.daftar_cache_siswa)
            return

        terfilter = [
            s for s in self.daftar_cache_siswa
            if q in s[0].lower() or q in s[1].lower()
        ]
        self.render_tabel_siswa(terfilter)

    def saat_siswa_diklik(self, event=None):
        selected = self.tree_siswa.selection()
        if not selected:
            return

        item = self.tree_siswa.item(selected[0])
        id_siswa = item["values"][0]
        nama_siswa = item["values"][1]
        self.siswa_terpilih_id = str(id_siswa)
        self.siswa_terpilih_nama = str(nama_siswa)

        self.segarkan_detail_siswa(self.siswa_terpilih_id, self.siswa_terpilih_nama)

    def segarkan_detail_siswa(self, id_siswa, nama_siswa):
        total_catatan, total_skor = ringkasan(id_siswa)
        skor_fmt = f"+{total_skor}" if total_skor > 0 else str(total_skor)

        self.lbl_detail_id.config(text=f"ID SISWA: {id_siswa}")
        self.lbl_detail_nama.config(text=nama_siswa)
        self.lbl_detail_ringkasan.config(
            text=f"Total Rekam Jejak: {total_catatan} Catatan  |  Skor Akumulasi: {skor_fmt}  |  Urutan: Kronologis Terbalik (Terbaru)"
        )
        self.btn_tambah_catatan.config(state="normal")

        # Render riwayat
        self.tree_riwayat.delete(*self.tree_riwayat.get_children())
        riwayat = lihat_riwayat(id_siswa)
        for tgl, kat, desk, skor, tindak in riwayat:
            skor_label = f"+1 Apresiasi" if skor > 0 else "-1 Evaluasi"
            self.tree_riwayat.insert("", "end", values=(tgl, kat, skor_label, desk, tindak))

    # =========================================================================
    # DIALOG ACTIONS
    # =========================================================================

    def buka_dialog_tambah_siswa(self):
        dialog = tk.Toplevel(self)
        dialog.title("Tambah Siswa Baru")
        dialog.geometry("420x240")
        dialog.configure(bg=BG_CARD)
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center Dialog
        dialog.geometry("+%d+%d" % (self.winfo_x() + 250, self.winfo_y() + 150))

        tk.Label(dialog, text="FORMULIR PENDAFTARAN SISWA BARU", font=("Helvetica", 10, "bold"), fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=20, pady=(16, 12))

        tk.Label(dialog, text="ID Siswa (Format Contoh: XII-TKJ-11):", font=("Helvetica", 8), fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=20)
        e_id = tk.Entry(dialog, font=("Consolas", 10), bg=BG_MAIN, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, highlightthickness=1, highlightbackground=BORDER_COLOR)
        e_id.pack(fill="x", padx=20, pady=(3, 10))

        tk.Label(dialog, text="Nama Lengkap Siswa:", font=("Helvetica", 8), fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=20)
        e_nama = tk.Entry(dialog, font=("Helvetica", 10), bg=BG_MAIN, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, highlightthickness=1, highlightbackground=BORDER_COLOR)
        e_nama.pack(fill="x", padx=20, pady=(3, 16))

        def simpan():
            id_val = e_id.get().strip()
            nama_val = e_nama.get().strip()
            try:
                tambah_siswa(id_val, nama_val)
                messagebox.showinfo("Berhasil", f"Siswa '{nama_val}' [{id_val}] berhasil didaftarkan.", parent=dialog)
                dialog.destroy()
                self.muat_data_semua()
            except (ValueError, sqlite3.IntegrityError) as err:
                messagebox.showerror("Gagal Menyimpan", f"Data belum tersimpan: {err}", parent=dialog)

        btn_box = tk.Frame(dialog, bg=BG_CARD)
        btn_box.pack(fill="x", padx=20)
        tk.Button(btn_box, text="Simpan Siswa", font=("Helvetica", 9, "bold"), fg="#ffffff", bg=COLOR_BLUE, activebackground="#2563eb", activeforeground="#ffffff", bd=0, padx=14, pady=6, cursor="hand2", command=simpan).pack(side="right")
        tk.Button(btn_box, text="Batal", font=("Helvetica", 9), fg=TEXT_MUTED, bg=BG_PANEL, activebackground=BORDER_COLOR, activeforeground="#ffffff", bd=0, padx=12, pady=6, cursor="hand2", command=dialog.destroy).pack(side="right", padx=6)

    def buka_dialog_tambah_catatan(self):
        if not self.siswa_terpilih_id:
            messagebox.showwarning("Pilih Siswa", "Silakan pilih salah satu siswa terlebih dahulu.", parent=self)
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Catat Pembinaan - [{self.siswa_terpilih_id}] {self.siswa_terpilih_nama}")
        dialog.geometry("520x440")
        dialog.configure(bg=BG_CARD)
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("+%d+%d" % (self.winfo_x() + 200, self.winfo_y() + 100))

        tk.Label(dialog, text=f"CATAT PERILAKU: {self.siswa_terpilih_nama} ({self.siswa_terpilih_id})", font=("Helvetica", 10, "bold"), fg=TEXT_PRIMARY, bg=BG_CARD).pack(anchor="w", padx=20, pady=(14, 8))

        row1 = tk.Frame(dialog, bg=BG_CARD)
        row1.pack(fill="x", padx=20, pady=(0, 8))

        # Kategori Dropdown
        col1 = tk.Frame(row1, bg=BG_CARD)
        col1.pack(side="left", fill="x", expand=True, padx=(0, 6))
        tk.Label(col1, text="Kategori Perilaku:", font=("Helvetica", 8), fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
        cb_kategori = ttk.Combobox(col1, values=["Disiplin", "Tanggung Jawab", "Kepedulian", "Kejujuran"], state="readonly")
        cb_kategori.current(0)
        cb_kategori.pack(fill="x", pady=2)

        # Skor Dropdown
        col2 = tk.Frame(row1, bg=BG_CARD)
        col2.pack(side="right", fill="x", expand=True, padx=(6, 0))
        tk.Label(col2, text="Indikator Skor:", font=("Helvetica", 8), fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w")
        cb_skor = ttk.Combobox(col2, values=["+1 (Apresiasi Capaian Positif)", "-1 (Evaluasi Pembinaan)"], state="readonly")
        cb_skor.current(0)
        cb_skor.pack(fill="x", pady=2)

        # Deskripsi Faktual
        tk.Label(dialog, text="Deskripsi Faktual (Tindakan konkret teramati, bahasa netral):", font=("Helvetica", 8), fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=20)
        txt_desk = tk.Text(dialog, height=4, font=("Helvetica", 9), bg=BG_MAIN, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, highlightthickness=1, highlightbackground=BORDER_COLOR)
        txt_desk.pack(fill="x", padx=20, pady=(2, 10))

        # Rencana Tindak Lanjut
        tk.Label(dialog, text="Rencana Tindak Lanjut & Ruang Klarifikasi:", font=("Helvetica", 8), fg=TEXT_MUTED, bg=BG_CARD).pack(anchor="w", padx=20)
        e_tindak = tk.Entry(dialog, font=("Helvetica", 9), bg=BG_MAIN, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, highlightthickness=1, highlightbackground=BORDER_COLOR)
        e_tindak.pack(fill="x", padx=20, pady=(2, 16))

        def simpan():
            kat = cb_kategori.get().strip()
            skor_raw = cb_skor.get()
            skor_val = 1 if "+1" in skor_raw else -1
            desk_val = txt_desk.get("1.0", "end").strip()
            tindak_val = e_tindak.get().strip()

            try:
                tambah_catatan(self.siswa_terpilih_id, kat, desk_val, skor_val, tindak_val)
                messagebox.showinfo("Berhasil", "Catatan pembinaan berhasil dicatat.", parent=dialog)
                dialog.destroy()
                self.muat_data_semua()
            except (ValueError, sqlite3.IntegrityError) as err:
                messagebox.showerror("Gagal Menyimpan", f"Data belum tersimpan: {err}", parent=dialog)

        btn_box = tk.Frame(dialog, bg=BG_CARD)
        btn_box.pack(fill="x", padx=20)
        tk.Button(btn_box, text="Simpan Catatan", font=("Helvetica", 9, "bold"), fg="#ffffff", bg=COLOR_GREEN, activebackground="#059669", activeforeground="#ffffff", bd=0, padx=14, pady=6, cursor="hand2", command=simpan).pack(side="right")
        tk.Button(btn_box, text="Batal", font=("Helvetica", 9), fg=TEXT_MUTED, bg=BG_PANEL, activebackground=BORDER_COLOR, activeforeground="#ffffff", bd=0, padx=12, pady=6, cursor="hand2", command=dialog.destroy).pack(side="right", padx=6)

    def aksi_seed(self):
        if messagebox.askyesno("Suntik Data Seeder", "Suntikkan 10 data simulasi siswa Kelas XII TKJ beserta rekam jejak pembinaan?"):
            ts, tc = isi_data_seeder()
            messagebox.showinfo("Seeder Selesai", f"Berhasil menambahkan {ts} siswa baru dan {tc} catatan pembinaan.", parent=self)
            self.muat_data_semua()

    def aksi_buka_web(self):
        # Membuka browser ke dashboard web lokal
        webbrowser.open("http://127.0.0.1:8080")

    def aksi_ekspor_json(self):
        students = ambil_semua_siswa()
        export_data = []
        for id_s, nama, jml, skor in students:
            records = lihat_riwayat(id_s)
            export_data.append({
                "id_siswa": id_s,
                "nama": nama,
                "total_catatan": jml,
                "total_skor": skor,
                "riwayat": [
                    {"tanggal": r[0], "kategori": r[1], "deskripsi": r[2], "skor": r[3], "tindak_lanjut": r[4]}
                    for r in records
                ]
            })

        out_path = os.path.abspath("ekspor_monitoring_akhlak.json")
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({"data_ekspor_akhlak_tkj": export_data}, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Ekspor Berhasil", f"Data berhasil diekspor ke:\n{out_path}", parent=self)
        except Exception as e:
            messagebox.showerror("Ekspor Gagal", f"Terjadi kesalahan: {e}", parent=self)


def jalankan_gui():
    """Fungsi pembuka GUI Desktop dengan penanganan display headless yang aman."""
    try:
        app = MonitoringAkhlakGUI()
        app.mainloop()
    except tk.TclError as err:
        print(f"\n[PERINGATAN GUI] Tidak dapat mendeteksi tampilan layar grafis ($DISPLAY): {err}")
        print("Jika menjalankan di server VPS atau remote SSH tanpa layar, gunakan opsi:")
        print("  • Mode Web Dashboard GUI : python monitoring_akhlak.py --web")
        print("  • Mode Terminal Console  : python monitoring_akhlak.py --cli")


if __name__ == "__main__":
    jalankan_gui()
