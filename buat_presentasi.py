"""
Skrip Generator Presentasi PowerPoint (.pptx)
Aplikasi Monitoring Akhlak Siswa (Kelas XII TKJ - SMK Alhadiid)
Menggunakan library python-pptx dengan layout Widescreen 16:9,
desain profesional dark slate/navy, kartu kontras tinggi, dan 7 slide lengkap.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# ==============================================================================
# PALET WARNA PROFESIONAL (DARK SLATE / NAVY WITH ACCENTS)
# ==============================================================================
C_BG = RGBColor(15, 23, 42)          # Slate 900 (Dark Navy Background)
C_CARD_BG = RGBColor(30, 41, 59)     # Slate 800 (Card Panel)
C_CARD_BORDER = RGBColor(51, 65, 85) # Slate 700
C_PRIMARY = RGBColor(59, 130, 246)   # Blue Accent (500)
C_CYAN = RGBColor(14, 165, 233)      # Sky Blue (500)
C_GREEN = RGBColor(16, 185, 129)     # Emerald Green (500)
C_RED = RGBColor(244, 63, 94)        # Rose Red (500)
C_AMBER = RGBColor(245, 158, 11)     # Amber (500)
C_WHITE = RGBColor(255, 255, 255)    # White
C_GRAY_LIGHT = RGBColor(226, 232, 240)# Slate 200
C_GRAY_MUTED = RGBColor(148, 163, 184)# Slate 400
C_GRAY_DARK = RGBColor(100, 116, 139) # Slate 500

FONT_HEADING = "Helvetica"
FONT_BODY = "Helvetica"
FONT_MONO = "Courier New"


def buat_background_slide(slide, prs):
    """Membuat latar belakang slide gelap konsisten."""
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = C_BG
    bg_shape.line.color.rgb = C_BG


def tambah_header_slide(slide, nomor_slide, judul_slide, kategori="MODUL PROYEK XII TKJ - SMK ALHADIID"):
    """Menambahkan badge kategori dan judul slide yang elegan."""
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.9))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    # Badge Kategori
    p_kat = tf.paragraphs[0]
    p_kat.text = f"SLIDE {nomor_slide:02d} • {kategori.upper()}"
    p_kat.font.name = FONT_HEADING
    p_kat.font.size = Pt(10)
    p_kat.font.bold = True
    p_kat.font.color.rgb = C_CYAN
    p_kat.space_after = Pt(2)

    # Judul Slide
    p_judul = tf.add_paragraph()
    p_judul.text = judul_slide
    p_judul.font.name = FONT_HEADING
    p_judul.font.size = Pt(20)
    p_judul.font.bold = True
    p_judul.font.color.rgb = C_WHITE


def tambah_kartu(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_CARD_BORDER):
    """Menambahkan panel kartu dengan border halus."""
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1)
    return card


def bangun_presentasi():
    prs = Presentation()
    # Atur widescreen 16:9
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]

    # ==========================================================================
    # SLIDE 1: JUDUL & LATAR BELAKANG MASALAH
    # ==========================================================================
    slide1 = prs.slides.add_slide(blank_slide_layout)
    buat_background_slide(slide1, prs)

    # Banner Header Utama
    tambah_kartu(slide1, Inches(0.8), Inches(0.8), Inches(11.733), Inches(2.2), bg_color=RGBColor(24, 34, 53), border_color=C_PRIMARY)
    title_box = slide1.shapes.add_textbox(Inches(1.1), Inches(1.0), Inches(11.1), Inches(1.8))
    tf1 = title_box.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "LAPORAN RESMI PROYEK KEJURUAN KELAS XII TKJ"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN

    p1 = tf1.add_paragraph()
    p1.text = "Aplikasi Monitoring Akhlak Siswa Berbasis Python dengan Spyder"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(24)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.space_after = Pt(4)

    p2 = tf1.add_paragraph()
    p2.text = "SMK Alhadiid 1 Cileungsi • Program Keahlian Teknik Komputer dan Jaringan • Arsitektur SQLite Relasional"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_GRAY_MUTED

    # Kolom Kiri: Latar Belakang & Masalah
    tambah_kartu(slide1, Inches(0.8), Inches(3.2), Inches(5.7), Inches(3.7))
    box_masalah = slide1.shapes.add_textbox(Inches(1.0), Inches(3.4), Inches(5.3), Inches(3.3))
    tf_m = box_masalah.text_frame
    tf_m.word_wrap = True

    pm_t = tf_m.paragraphs[0]
    pm_t.text = "Latar Belakang & Permasalahan Riil"
    pm_t.font.size = Pt(14)
    pm_t.font.bold = True
    pm_t.font.color.rgb = C_AMBER
    pm_t.space_after = Pt(8)

    items_masalah = [
        "Catatan manual konvensional di buku fisik rentan tercecer antar wali kelas dan guru BK.",
        "Bias subjektif dan labeling negatif sering terjadi tanpa pencatatan fakta kejadian yang konkret.",
        "Apresiasi perilaku positif sering terlewat dan tidak terdokumentasi secara adil.",
        "Software berbasis web server komersial rumit di-setup dan bergantung koneksi internet luar."
    ]
    for m in items_masalah:
        p = tf_m.add_paragraph()
        p.text = "• " + m
        p.font.size = Pt(10)
        p.font.color.rgb = C_GRAY_LIGHT
        p.space_after = Pt(6)

    # Kolom Kanan: 4 Kebutuhan Fitur Guru
    tambah_kartu(slide1, Inches(6.8), Inches(3.2), Inches(5.733), Inches(3.7))
    box_fitur = slide1.shapes.add_textbox(Inches(7.0), Inches(3.4), Inches(5.3), Inches(3.3))
    tf_f = box_fitur.text_frame
    tf_f.word_wrap = True

    pf_t = tf_f.paragraphs[0]
    pf_t.text = "4 Kebutuhan Fungsional Guru Pembina"
    pf_t.font.size = Pt(14)
    pf_t.font.bold = True
    pf_t.font.color.rgb = C_GREEN
    pf_t.space_after = Pt(8)

    fitur_guru = [
        ("1. Tambah Siswa Baru", "Mendaftarkan identitas siswa unik (NIS/ID) ke dalam basis data."),
        ("2. Catat Perilaku Siswa", "Mencatat kejadian faktual, kategori karakter, skor indikator (+1 / -1), & tindak lanjut."),
        ("3. Lihat Riwayat Terurut", "Menampilkan kronologis catatan pembinaan dari yang paling mutakhir (DESC)."),
        ("4. Ringkasan Skor Otomatis", "Agregasi instan jumlah log dan total akumulasi skor bimbingan.")
    ]
    for judul, ket in fitur_guru:
        p = tf_f.add_paragraph()
        p.text = f"✔ {judul}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p_sub = tf_f.add_paragraph()
        p_sub.text = f"   {ket}"
        p_sub.font.size = Pt(9.5)
        p_sub.font.color.rgb = C_GRAY_MUTED
        p_sub.space_after = Pt(4)

    # ==========================================================================
    # SLIDE 2: ALUR KERJA SISTEM & PRINSIP DESAIN
    # ==========================================================================
    slide2 = prs.slides.add_slide(blank_slide_layout)
    buat_background_slide(slide2, prs)
    tambah_header_slide(slide2, 2, "Alur Kerja Sistem (Flowchart) & 4 Prinsip Desain Pembinaan")

    # Kolom Kiri: Alur Logika Eksekusi
    tambah_kartu(slide2, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.4))
    box_alur = slide2.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(5.0))
    tf_a = box_alur.text_frame
    tf_a.word_wrap = True

    pa_t = tf_a.paragraphs[0]
    pa_t.text = "Siklus Alur Kerja Aplikasi (CLI & GUI)"
    pa_t.font.size = Pt(14)
    pa_t.font.bold = True
    pa_t.font.color.rgb = C_PRIMARY
    pa_t.space_after = Pt(10)

    tahapan_alur = [
        ("1. Inisialisasi Database", "Membuka koneksi SQLite3 dan wajib mengaktifkan 'PRAGMA foreign_keys = ON'."),
        ("2. Pilih Menu Operasional", "Pengguna memilih aksi (Tambah Siswa, Catat Perilaku, Lihat Riwayat, Dashboard)."),
        ("3. Input Data & Sanitasi", "Pengambilan masukan pengguna dengan pembersihan spasi menggunakan '.strip()'."),
        ("4. Validasi Ketat Berlapis", "Memastikan input tidak kosong dan skor berada pada domain (-1, 1)."),
        ("5. Transaksi Aman SQLite", "Penyimpanan via Parameterized Query ('?'). Jika gagal -> Rollback aman."),
        ("6. Umpan Balik Instan", "Jika tidak valid, tampilkan error ramah dan kembali ke menu tanpa menyimpan data cacat.")
    ]
    for judul, desc in tahapan_alur:
        p = tf_a.add_paragraph()
        p.text = judul
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p_d = tf_a.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = C_GRAY_MUTED
        p_d.space_after = Pt(4)

    # Kolom Kanan: 4 Prinsip Desain Pembinaan
    tambah_kartu(slide2, Inches(6.8), Inches(1.5), Inches(5.733), Inches(5.4))
    box_prinsip = slide2.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(5.0))
    tf_p = box_prinsip.text_frame
    tf_p.word_wrap = True

    pp_t = tf_p.paragraphs[0]
    pp_t.text = "4 Pilar Etika & Prinsip Desain Pembinaan"
    pp_t.font.size = Pt(14)
    pp_t.font.bold = True
    pp_t.font.color.rgb = C_GREEN
    pp_t.space_after = Pt(10)

    prinsip_desain = [
        ("1. Fakta yang Dapat Diamati (Observable)", "Catatan hanya mendokumentasikan tindakan nyata teramati (contoh: 'terlambat 10 menit', 'merapikan lab'). Menolak asumsi atau opini subjektif."),
        ("2. Bahasa Netral & Profesional", "Menghindari kata-kata penghakiman moral (seperti 'anak nakal', 'pemalas'). Mengedepankan narasi deskriptif yang mendidik dan objektif."),
        ("3. Ruang Klarifikasi & Dialog Dua Arah", "Setiap insiden memberi ruang bagi siswa untuk menyampaikan konteks sebelum tindakan bimbingan diputuskan."),
        ("4. Tindak Lanjut Nyata oleh Manusia", "Skor bukan vonis robotik. Kolom 'tindak_lanjut' mewajibkan adanya rencana aksi pendampingan konkret guru dan siswa.")
    ]
    for judul, desc in prinsip_desain:
        p = tf_p.add_paragraph()
        p.text = judul
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_CYAN
        p_d = tf_p.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_GRAY_LIGHT
        p_d.space_after = Pt(8)

    # ==========================================================================
    # SLIDE 3: DESAIN DATABASE SQLITE & RELASI TABEL
    # ==========================================================================
    slide3 = prs.slides.add_slide(blank_slide_layout)
    buat_background_slide(slide3, prs)
    tambah_header_slide(slide3, 3, "Desain Database SQLite3 & Struktur Relasional One-to-Many")

    # Kartu Tabel SISWA
    tambah_kartu(slide3, Inches(0.8), Inches(1.5), Inches(5.7), Inches(3.2))
    box_ts = slide3.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(2.8))
    tf_ts = box_ts.text_frame
    tf_ts.word_wrap = True

    pts_t = tf_ts.paragraphs[0]
    pts_t.text = "Tabel Parent: SISWA"
    pts_t.font.size = Pt(13)
    pts_t.font.bold = True
    pts_t.font.color.rgb = C_PRIMARY

    ts_fields = [
        ("id_siswa", "TEXT PRIMARY KEY", "Nomor identifikasi unik siswa (NIS/Kelas). Mencegah duplikasi."),
        ("nama", "TEXT NOT NULL", "Nama lengkap resmi peserta didik.")
    ]
    for f_name, f_type, f_desc in ts_fields:
        p = tf_ts.add_paragraph()
        p.text = f"• {f_name} [{f_type}]"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p_d = tf_ts.add_paragraph()
        p_d.text = f"   {f_desc}"
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = C_GRAY_MUTED
        p_d.space_after = Pt(4)

    # Kartu Tabel CATATAN
    tambah_kartu(slide3, Inches(6.8), Inches(1.5), Inches(5.733), Inches(4.3))
    box_tc = slide3.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(3.9))
    tf_tc = box_tc.text_frame
    tf_tc.word_wrap = True

    ptc_t = tf_tc.paragraphs[0]
    ptc_t.text = "Tabel Child: CATATAN"
    ptc_t.font.size = Pt(13)
    ptc_t.font.bold = True
    ptc_t.font.color.rgb = C_GREEN

    tc_fields = [
        ("id_catatan", "INTEGER PRIMARY KEY AUTOINCREMENT", "Kunci identifikasi unik setiap log."),
        ("id_siswa", "TEXT NOT NULL (FK)", "Kunci asing ke siswa(id_siswa)."),
        ("tanggal", "TEXT NOT NULL", "Format standar ISO-8601 (YYYY-MM-DD)."),
        ("kategori", "TEXT NOT NULL", "Disiplin, Tanggung Jawab, Peduli, Jujur."),
        ("deskripsi", "TEXT NOT NULL", "Catatan observasi kejadian objektif."),
        ("skor", "INTEGER CHECK(skor IN (-1, 1))", "Ketat dibatasi hanya -1 atau +1."),
        ("tindak_lanjut", "TEXT NOT NULL", "Rencana aksi resolusi dan apresiasi.")
    ]
    for f_name, f_type, f_desc in tc_fields:
        p = tf_tc.add_paragraph()
        p.text = f"• {f_name} ({f_type}): {f_desc}"
        p.font.size = Pt(9)
        p.font.color.rgb = C_GRAY_LIGHT
        p.space_after = Pt(2)

    # Kartu Bawah: Penjelasan Integritas & PRAGMA Foreign Keys
    tambah_kartu(slide3, Inches(0.8), Inches(4.9), Inches(5.7), Inches(2.0), bg_color=RGBColor(24, 34, 53), border_color=C_CYAN)
    box_rel = slide3.shapes.add_textbox(Inches(1.0), Inches(5.0), Inches(5.3), Inches(1.8))
    tf_rel = box_rel.text_frame
    tf_rel.word_wrap = True

    prel_t = tf_rel.paragraphs[0]
    prel_t.text = "Karakteristik Integritas Relasional"
    prel_t.font.size = Pt(11)
    prel_t.font.bold = True
    prel_t.font.color.rgb = C_CYAN

    items_rel = [
        "Relasi 1-ke-Banyak: Satu data siswa memiliki banyak catatan rekam jejak bimbingan.",
        "Wajib 'PRAGMA foreign_keys = ON;': SQLite menolak catatan jika ID siswa tidak ada (mencegah data yatim/orphaned).",
        "Penambahan Indeks Relasional: 'idx_catatan_id_siswa' untuk akselerasi kueri."
    ]
    for r in items_rel:
        p = tf_rel.add_paragraph()
        p.text = "✔ " + r
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_GRAY_LIGHT
        p.space_after = Pt(2)

    # Kartu Bawah Kanan: Info Indeks
    tambah_kartu(slide3, Inches(6.8), Inches(6.0), Inches(5.733), Inches(0.9), bg_color=RGBColor(24, 34, 53), border_color=C_CARD_BORDER)
    box_ik = slide3.shapes.add_textbox(Inches(7.0), Inches(6.1), Inches(5.3), Inches(0.7))
    tf_ik = box_ik.text_frame
    tf_ik.word_wrap = True
    pik = tf_ik.paragraphs[0]
    pik.text = "Query Optimization Index:"
    pik.font.size = Pt(10)
    pik.font.bold = True
    pik.font.color.rgb = C_WHITE
    pik2 = tf_ik.add_paragraph()
    pik2.text = "CREATE INDEX IF NOT EXISTS idx_catatan_id_siswa ON catatan(id_siswa);"
    pik2.font.size = Pt(8.5)
    pik2.font.name = FONT_MONO
    pik2.font.color.rgb = C_GREEN

    # ==========================================================================
    # SLIDE 4: ARSITEKTUR KODE, KEAMANAN & CARA MENJALANKAN
    # ==========================================================================
    slide4 = prs.slides.add_slide(blank_slide_layout)
    buat_background_slide(slide4, prs)
    tambah_header_slide(slide4, 4, "Arsitektur Kode Python, Keamanan Parameterized, & Eksekusi")

    # Kolom 1: Cara Menjalankan
    tambah_kartu(slide4, Inches(0.8), Inches(1.5), Inches(3.7), Inches(5.4))
    box_c1 = slide4.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(3.3), Inches(5.0))
    tf_c1 = box_c1.text_frame
    tf_c1.word_wrap = True

    pc1_t = tf_c1.paragraphs[0]
    pc1_t.text = "Cara Menjalankan Aplikasi"
    pc1_t.font.size = Pt(13)
    pc1_t.font.bold = True
    pc1_t.font.color.rgb = C_PRIMARY
    pc1_t.space_after = Pt(8)

    instruksi = [
        ("1. Spyder IDE (Anaconda)", "Buka file 'monitoring_akhlak.py' di editor Spyder, lalu tekan tombol F5 (Run File). Menu langsung aktif di IPython Console."),
        ("2. Terminal Standar (Linux/Win)", "Jalankan perintah:\npython3 monitoring_akhlak.py\n(Server Web & Browser otomatis terbuka)."),
        ("3. Tanpa Dependensi Eksternal", "100% menggunakan library standar bawaan Python: sqlite3 & datetime."),
        ("4. Mode GUI Desktop & Web", "Tersedia peluncur mandiri untuk Desktop Window maupun Web Dashboard.")
    ]
    for j, d in instruksi:
        p = tf_c1.add_paragraph()
        p.text = j
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p_d = tf_c1.add_paragraph()
        p_d.text = d
        p_d.font.size = Pt(8.5)
        p_d.font.color.rgb = C_GRAY_MUTED
        p_d.space_after = Pt(6)

    # Kolom 2: Parameterized Query
    tambah_kartu(slide4, Inches(4.8), Inches(1.5), Inches(3.7), Inches(5.4))
    box_c2 = slide4.shapes.add_textbox(Inches(5.0), Inches(1.7), Inches(3.3), Inches(5.0))
    tf_c2 = box_c2.text_frame
    tf_c2.word_wrap = True

    pc2_t = tf_c2.paragraphs[0]
    pc2_t.text = "Keamanan SQL Injection"
    pc2_t.font.size = Pt(13)
    pc2_t.font.bold = True
    pc2_t.font.color.rgb = C_GREEN
    pc2_t.space_after = Pt(8)

    p_sqli_1 = tf_c2.add_paragraph()
    p_sqli_1.text = "Kebal Terhadap SQL Injection:"
    p_sqli_1.font.size = Pt(9.5)
    p_sqli_1.font.bold = True
    p_sqli_1.font.color.rgb = C_WHITE

    p_sqli_code = tf_c2.add_paragraph()
    p_sqli_code.text = "conn.execute(\n  'INSERT INTO siswa VALUES (?, ?)',\n  (id_siswa, nama)\n)"
    p_sqli_code.font.name = FONT_MONO
    p_sqli_code.font.size = Pt(8.5)
    p_sqli_code.font.color.rgb = C_CYAN
    p_sqli_code.space_after = Pt(6)

    penjelasan_sqli = [
        "Seluruh input dikirim terpisah sebagai tuple data, bukan digabung via string formatting (+ atau f-string).",
        "Karakter berbahaya seperti ' OR 1=1 -- akan diperlakukan sebagai teks biasa oleh engine SQLite.",
        "Mencegah manipulasi tabel dan pembobolan data secara absolut."
    ]
    for item in penjelasan_sqli:
        p = tf_c2.add_paragraph()
        p.text = "• " + item
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_GRAY_LIGHT
        p.space_after = Pt(4)

    # Kolom 3: Penanganan Error Terpusat
    tambah_kartu(slide4, Inches(8.8), Inches(1.5), Inches(3.733), Inches(5.4))
    box_c3 = slide4.shapes.add_textbox(Inches(9.0), Inches(1.7), Inches(3.3), Inches(5.0))
    tf_c3 = box_c3.text_frame
    tf_c3.word_wrap = True

    pc3_t = tf_c3.paragraphs[0]
    pc3_t.text = "Penanganan Error Terpusat"
    pc3_t.font.size = Pt(13)
    pc3_t.font.bold = True
    pc3_t.font.color.rgb = C_AMBER
    pc3_t.space_after = Pt(8)

    p_err_code = tf_c3.add_paragraph()
    p_err_code.text = "try:\n    # Proses transaksi\nexcept (ValueError,\n        sqlite3.IntegrityError) as err:\n    print(f'Data belum tersimpan: {err}')"
    p_err_code.font.name = FONT_MONO
    p_err_code.font.size = Pt(8)
    p_err_code.font.color.rgb = C_AMBER
    p_err_code.space_after = Pt(8)

    poin_error = [
        "Aplikasi tidak akan pernah crash saat pengguna salah memasukkan tipe data.",
        "Menangkap pelanggaran Primary Key (duplikasi ID siswa).",
        "Menangkap pelanggaran Foreign Key (ID siswa belum terdaftar).",
        "Menyajikan pesan umpan balik ramah kepada guru."
    ]
    for pe in poin_error:
        p = tf_c3.add_paragraph()
        p.text = "✔ " + pe
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_GRAY_LIGHT
        p.space_after = Pt(4)

    # ==========================================================================
    # SLIDE 5: HASIL PENGUJIAN 6 SKENARIO & SIMULASI OUTPUT
    # ==========================================================================
    slide5 = prs.slides.add_slide(blank_slide_layout)
    buat_background_slide(slide5, prs)
    tambah_header_slide(slide5, 5, "Hasil Verifikasi 6 Skenario Wajib & Bukti Eksekusi Konsol")

    # Kolom Kiri: Tabel 6 Skenario
    tambah_kartu(slide5, Inches(0.8), Inches(1.5), Inches(6.5), Inches(5.4))
    box_sken = slide5.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(6.1), Inches(5.0))
    tf_sk = box_sken.text_frame
    tf_sk.word_wrap = True

    psk_t = tf_sk.paragraphs[0]
    psk_t.text = "Matriks Hasil Uji Otomatis (uji_skenario.py)"
    psk_t.font.size = Pt(13)
    psk_t.font.bold = True
    psk_t.font.color.rgb = C_CYAN
    psk_t.space_after = Pt(6)

    skenario_list = [
        ("1. Tambah Siswa Valid", "Input XII-TKJ-01", "Tersimpan 1 baris valid", "LULUS"),
        ("2. ID Duplikat", "XII-TKJ-01 diulang", "Ditolak IntegrityError", "LULUS"),
        ("3. Input Kosong", "Deskripsi ''", "Ditolak ValueError", "LULUS"),
        ("4. Skor Tidak Sah", "Skor = 0", "Ditolak ValueError", "LULUS"),
        ("5. Riwayat & Ringkasan", "Catatan -1 & +1", "Output (2, 0) terurut DESC", "LULUS"),
        ("6. ID Belum Terdaftar", "Catat XII-TKJ-99", "Ditolak IntegrityError (FK)", "LULUS")
    ]
    for no_j, inp, eks, stat in skenario_list:
        p = tf_sk.add_paragraph()
        p.text = f"• {no_j} [{stat}]"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_GREEN
        p_d = tf_sk.add_paragraph()
        p_d.text = f"   Uji: {inp} ➔ Hasil: {eks}"
        p_d.font.size = Pt(8.5)
        p_d.font.color.rgb = C_GRAY_LIGHT
        p_d.space_after = Pt(2)

    p_tot = tf_sk.add_paragraph()
    p_tot.text = "\nTOTAL HASIL: 6 / 6 SKENARIO LULUS SEMPURNA (100%)"
    p_tot.font.size = Pt(10.5)
    p_tot.font.bold = True
    p_tot.font.color.rgb = C_WHITE

    # Kolom Kanan: Log Konsol Verbatim
    tambah_kartu(slide5, Inches(7.5), Inches(1.5), Inches(5.033), Inches(5.4), bg_color=RGBColor(9, 9, 11), border_color=C_CARD_BORDER)
    box_log = slide5.shapes.add_textbox(Inches(7.7), Inches(1.7), Inches(4.6), Inches(5.0))
    tf_log = box_log.text_frame
    tf_log.word_wrap = True

    plog_t = tf_log.paragraphs[0]
    plog_t.text = "Cuplikan Log Terminal (100% Data Fiktif)"
    plog_t.font.size = Pt(11)
    plog_t.font.bold = True
    plog_t.font.color.rgb = C_AMBER
    plog_t.space_after = Pt(4)

    log_lines = [
        ">>> python3 uji_skenario.py",
        "[STATUS: LULUS] Berhasil menyimpan XII-TKJ-01.",
        "[STATUS: LULUS] Ditolak: UNIQUE constraint failed.",
        "[STATUS: LULUS] Ditolak: ID & deskripsi wajib diisi.",
        "[STATUS: LULUS] Ditolak: Skor harus -1 atau 1.",
        "Output ringkasan(id_siswa): (2, 0)",
        "Riwayat Terurut:",
        " 1. 2026-11-05 | Kepedulian | +1 | Rapikan kabel LAN",
        " 2. 2026-11-05 | Disiplin   | -1 | Terlambat 10 menit",
        "[STATUS: LULUS] Ditolak: FOREIGN KEY constraint failed.",
        "----------------------------------------",
        "HASIL AKHIR: 6 / 6 Skenario LULUS (100%).",
        "Status: Database simulasi otomatis dibersihkan."
    ]
    for line in log_lines:
        p = tf_log.add_paragraph()
        p.text = line
        p.font.name = FONT_MONO
        p.font.size = Pt(8)
        p.font.color.rgb = C_GRAY_LIGHT if "STATUS" not in line else C_GREEN
        p.space_after = Pt(1)

    # ==========================================================================
    # SLIDE 6: BATASAN APLIKASI, ETIKA, & PRIVASI DATA
    # ==========================================================================
    slide6 = prs.slides.add_slide(blank_slide_layout)
    buat_background_slide(slide6, prs)
    tambah_header_slide(slide6, 6, "Batasan Aplikasi, Tata Kelola Etika, & Privasi Data Siswa")

    # Kolom Kiri: Batasan Peran Skor & Pedagogi
    tambah_kartu(slide6, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.4))
    box_b = slide6.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(5.0))
    tf_b = box_b.text_frame
    tf_b.word_wrap = True

    pb_t = tf_b.paragraphs[0]
    pb_t.text = "Batasan Fungsional Skor Perilaku"
    pb_t.font.size = Pt(13)
    pb_t.font.bold = True
    pb_t.font.color.rgb = C_RED
    pb_t.space_after = Pt(8)

    batasan_points = [
        ("Bukan Penentu Tunggal Karakter", "Skor akumulasi (+1 atau -1) hanyalah indikator bimbingan pendidik untuk mendeteksi tren perubahan perilaku, bukan vonis moral mutlak siswa."),
        ("Dilarang Menjadi Dasar Vonis Hukuman", "Sistem tidak boleh digunakan untuk menjatuhkan sanksi otomatis tanpa asesmen kontekstual dan konseling langsung."),
        ("Skor Terpisah dari Nilai Akademik", "Nilai karakter tidak boleh langsung mengurangi atau mendikte nilai capaian kompetensi teknis TKJ pada buku rapor."),
        ("Bahaya Reduksionisme Moral", "Mereduksi akhlak menjadi sekadar angka memicu tindakan manipulatif siswa (Goodhart's Law) demi mengejar poin semu.")
    ]
    for j, d in batasan_points:
        p = tf_b.add_paragraph()
        p.text = f"⚠ {j}"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p_d = tf_b.add_paragraph()
        p_d.text = f"   {d}"
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = C_GRAY_LIGHT
        p_d.space_after = Pt(6)

    # Kolom Kanan: Kebijakan Privasi Data
    tambah_kartu(slide6, Inches(6.8), Inches(1.5), Inches(5.733), Inches(5.4))
    box_priv = slide6.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(5.0))
    tf_priv = box_priv.text_frame
    tf_priv.word_wrap = True

    ppriv_t = tf_priv.paragraphs[0]
    ppriv_t.text = "Protokol Keamanan & Privasi Data Siswa"
    ppriv_t.font.size = Pt(13)
    ppriv_t.font.bold = True
    ppriv_t.font.color.rgb = C_GREEN
    ppriv_t.space_after = Pt(8)

    privasi_points = [
        ("1. Prinsip 100% Data Fiktif", "Seluruh simulasi, demonstrasi pengujian, dan contoh slide wajib menggunakan nama dan nomor induk fiktif (contoh: XII-TKJ-01 Siswa Simulasi Satu)."),
        ("2. Larangan Upload Database Nyata", "File '*.db' dan data riil dilarang keras diunggah ke repositori GitHub publik. Dibatasi secara mutlak via konfigurasi '.gitignore'."),
        ("3. Perlindungan Hak Akses Berkas Lokal", "File database lokal di komputer lab diamankan dengan restriksi hak akses sistem operasi ('chmod 600 monitoring_akhlak.db')."),
        ("4. Siklus Retensi Data (Purging)", "Setelah siswa menyelesaikan studi/lulus dari SMK Alhadiid, catatan rekam jejak perilaku wajib diarsipkan terenkripsi atau dihapus permanen agar tidak meninggalkan stigma sosial.")
    ]
    for j, d in privasi_points:
        p = tf_priv.add_paragraph()
        p.text = f"🛡 {j}"
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_CYAN
        p_d = tf_priv.add_paragraph()
        p_d.text = f"   {d}"
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = C_GRAY_LIGHT
        p_d.space_after = Pt(6)

    # ==========================================================================
    # SLIDE 7: JAWABAN 5 REFLEKSI & PENGEMBANGAN LANJUTAN
    # ==========================================================================
    slide7 = prs.slides.add_slide(blank_slide_layout)
    buat_background_slide(slide7, prs)
    tambah_header_slide(slide7, 7, "Ringkasan 5 Pertanyaan Refleksi & Roadmap Pengembangan")

    # Kolom Kiri: 5 Jawaban Refleksi
    tambah_kartu(slide7, Inches(0.8), Inches(1.5), Inches(6.8), Inches(5.4))
    box_ref = slide7.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(6.4), Inches(5.0))
    tf_r = box_ref.text_frame
    tf_r.word_wrap = True

    pr_t = tf_r.paragraphs[0]
    pr_t.text = "Jawaban Komprehensif 5 Pertanyaan Refleksi Modul"
    pr_t.font.size = Pt(12.5)
    pr_t.font.bold = True
    pr_t.font.color.rgb = C_AMBER
    pr_t.space_after = Pt(6)

    refleksi_items = [
        ("Q1: Fitur Paling Membantu Pembinaan?", "Kolom 'deskripsi' dan 'tindak_lanjut'. Memberi kejelasan fakta kejadian dan menyepakati solusi konkret daripada sekadar angka hukuman."),
        ("Q2: Memastikan Catatan Faktual & Adil?", "Standar penulisan berbasis fakta observasi teramati, tabulasi dua sisi (apresiasi +1 dan bimbingan -1), serta dialog klarifikasi sebelum simpan."),
        ("Q3: Risiko Skor Sebagai Penentu Tunggal?", "Terjadi pelabelan moral negatif (stigma), manipulasi perilaku demi poin semu (Goodhart's Law), dan pengabaian konteks kesulitan hidup siswa."),
        ("Q4: Menjaga Keamanan Database Lokal?", "Proteksi izin berkas OS ('chmod 600'), filter Git (.gitignore), workstation lock otomatis, dan enkripsi storage/SQLCipher."),
        ("Q5: Perbaikan Sebelum Dipakai Luas?", "Penerapan autentikasi multi-peran (RBAC untuk Guru, BK, Siswa), jejak audit log permanen, dan arsitektur web client-server terpusat.")
    ]
    for q, a in refleksi_items:
        p = tf_r.add_paragraph()
        p.text = q
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p_a = tf_r.add_paragraph()
        p_a.text = a
        p_a.font.size = Pt(8.5)
        p_a.font.color.rgb = C_GRAY_LIGHT
        p_a.space_after = Pt(3)

    # Kolom Kanan: Rencana Pengembangan Lanjutan
    tambah_kartu(slide7, Inches(7.8), Inches(1.5), Inches(4.733), Inches(5.4))
    box_dev = slide7.shapes.add_textbox(Inches(8.0), Inches(1.7), Inches(4.3), Inches(5.0))
    tf_dev = box_dev.text_frame
    tf_dev.word_wrap = True

    pd_t = tf_dev.paragraphs[0]
    pd_t.text = "Roadmap Pengembangan Lanjutan"
    pd_t.font.size = Pt(12.5)
    pd_t.font.bold = True
    pd_t.font.color.rgb = C_PRIMARY
    pd_t.space_after = Pt(8)

    roadmap_items = [
        ("1. Desktop & Web GUI Terintegrasi", "Aplikasi kini telah dilengkapi Desktop GUI Native (Tkinter) dan Web Dashboard SPA modern bertema Linear/Raycast."),
        ("2. Filter Lanjutan & Ekspor Laporan", "Fitur filter instan multi-status, pencarian live debounced, dan tombol ekspor langsung ke format resmi CSV dan JSON."),
        ("3. Lembar Raport Siap Cetak (A4)", "Template dossier cetak ber-kop resmi SMK Alhadiid dengan kolom tanda tangan wali kelas dan kepala program TKJ."),
        ("4. Keamanan Multi-User & Token JWT", "Pengembangan REST API terpusat untuk integrasi aplikasi mobile wali murid sekolah.")
    ]
    for j, d in roadmap_items:
        p = tf_dev.add_paragraph()
        p.text = f"🚀 {j}"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_CYAN
        p_d = tf_dev.add_paragraph()
        p_d.text = d
        p_d.font.size = Pt(8.5)
        p_d.font.color.rgb = C_GRAY_MUTED
        p_d.space_after = Pt(6)

    # ==========================================================================
    # SIMPAN PRESENTASI
    # ==========================================================================
    output_nama = "Presentasi_Monitoring_Akhlak_XII_TKJ.pptx"
    prs.save(output_nama)
    print(f"✓ Berhasil membuat file presentasi: {output_nama}")
    print(f"  Format: Widescreen 16:9 | Total Slide: {len(prs.slides)}")


if __name__ == "__main__":
    bangun_presentasi()
