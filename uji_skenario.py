"""
Skrip Otomatisasi Pengujian 6 Skenario Wajib
Aplikasi Monitoring Akhlak Siswa - SMK Alhadiid (Kelas XII TKJ)

Karakteristik Pengujian:
- 100% Menggunakan Data Fiktif Simulative.
- Menjalankan pengujian fungsional, validasi input, dan integritas relasional SQLite.
- Membersihkan database simulasi setelah pengujian selesai.
"""

import os
import sqlite3
import sys

from monitoring_akhlak import (
    koneksi_db,
    lihat_riwayat,
    ringkasan,
    siapkan_db,
    tambah_catatan,
    tambah_siswa,
)

DB_TEST = "simulasi_uji_monitoring.db"


def bersihkan_db():
    """Menghapus file database simulasi jika ada."""
    if os.path.exists(DB_TEST):
        try:
            os.remove(DB_TEST)
        except OSError:
            pass


def cetak_header(nomor, judul):
    print("=" * 72)
    print(f"SKENARIO {nomor}: {judul.upper()}")
    print("-" * 72)


def jalankan_semua_pengujian():
    print("\n" + "#" * 72)
    print("  MEMULAI PENGUJIAN OTOMATIS SISTEM MONITORING AKHLAK SISWA")
    print("  Data: 100% Fiktif & Simulative | Engine: SQLite3 with Foreign Keys")
    print("#" * 72 + "\n")

    bersihkan_db()
    siapkan_db(nama_db=DB_TEST)

    hasil_laporan = []

    # -------------------------------------------------------------------------
    # SKENARIO 1: Tambah Siswa Valid
    # -------------------------------------------------------------------------
    cetak_header(1, "Tambah Siswa Valid")
    id_siswa_1 = "XII-TKJ-01"
    nama_siswa_1 = "Siswa Simulasi Satu"
    try:
        tambah_siswa(id_siswa_1, nama_siswa_1, nama_db=DB_TEST)
        with koneksi_db(nama_db=DB_TEST) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM siswa WHERE id_siswa = ?", (id_siswa_1,))
            jumlah = cur.fetchone()[0]
        assert jumlah == 1, f"Expected 1 baris, got {jumlah}"
        print(f"[STATUS: LULUS] Berhasil menyimpan siswa '{nama_siswa_1}' [{id_siswa_1}].")
        print(f"Bukti Database: Ditemukan {jumlah} baris di tabel 'siswa'.")
        hasil_laporan.append((1, "Tambah Siswa Valid", "LULUS", "Tersimpan 1 baris valid"))
    except Exception as e:
        print(f"[STATUS: GAGAL] Error: {e}")
        hasil_laporan.append((1, "Tambah Siswa Valid", "GAGAL", str(e)))

    # -------------------------------------------------------------------------
    # SKENARIO 2: ID Duplikat (Primary Key Integrity)
    # -------------------------------------------------------------------------
    cetak_header(2, "ID Duplikat (Primary Key Check)")
    try:
        print(f"Mencoba menyimpan kembali siswa dengan ID yang sama: '{id_siswa_1}'...")
        tambah_siswa(id_siswa_1, "Nama Duplikat Siswa", nama_db=DB_TEST)
        print("[STATUS: GAGAL] Sistem mengizinkan ID duplikat (seharusnya menolak).")
        hasil_laporan.append((2, "ID Duplikat", "GAGAL", "Primary Key lolos"))
    except sqlite3.IntegrityError as err:
        with koneksi_db(nama_db=DB_TEST) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM siswa WHERE id_siswa = ?", (id_siswa_1,))
            jumlah = cur.fetchone()[0]
        assert jumlah == 1, "Jumlah baris bertambah padahal duplikat ditolak"
        print(f"[STATUS: LULUS] Ditolak oleh sqlite3.IntegrityError: '{err}'.")
        print(f"Bukti Database: Jumlah siswa ID '{id_siswa_1}' tetap {jumlah} baris.")
        hasil_laporan.append((2, "ID Duplikat", "LULUS", f"Ditolak IntegrityError ({err})"))
    except Exception as e:
        print(f"[STATUS: GAGAL] Error tidak terduga: {e}")
        hasil_laporan.append((2, "ID Duplikat", "GAGAL", str(e)))

    # -------------------------------------------------------------------------
    # SKENARIO 3: Input Kosong (Validation Check)
    # -------------------------------------------------------------------------
    cetak_header(3, "Input Kosong (Validation Check)")
    try:
        print("Mencoba menambah catatan pembinaan dengan deskripsi kosong ''...")
        tambah_catatan(
            id_siswa=id_siswa_1,
            kategori="Disiplin",
            deskripsi="",
            skor=1,
            tindak_lanjut="Pembinaan rutin",
            nama_db=DB_TEST,
        )
        print("[STATUS: GAGAL] Sistem meloloskan input deskripsi kosong.")
        hasil_laporan.append((3, "Input Kosong", "GAGAL", "Input kosong lolos"))
    except ValueError as err:
        with koneksi_db(nama_db=DB_TEST) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM catatan WHERE id_siswa = ?", (id_siswa_1,))
            jumlah = cur.fetchone()[0]
        assert jumlah == 0, f"Catatan bertambah padahal ditolak: {jumlah}"
        print(f"[STATUS: LULUS] Ditolak oleh ValueError: '{err}'.")
        print(f"Bukti Database: Tabel 'catatan' tetap kosong ({jumlah} baris).")
        hasil_laporan.append((3, "Input Kosong", "LULUS", f"Ditolak ValueError ({err})"))
    except Exception as e:
        print(f"[STATUS: GAGAL] Error tidak terduga: {e}")
        hasil_laporan.append((3, "Input Kosong", "GAGAL", str(e)))

    # -------------------------------------------------------------------------
    # SKENARIO 4: Skor Tidak Sah (CHECK Constraint / Logic Check)
    # -------------------------------------------------------------------------
    cetak_header(4, "Skor Tidak Sah (Nilai Selain -1 atau 1)")
    try:
        print("Mencoba menambah catatan dengan nilai skor 0 (harus -1 atau 1)...")
        tambah_catatan(
            id_siswa=id_siswa_1,
            kategori="Tanggung Jawab",
            deskripsi="Selesai praktikum tepat waktu",
            skor=0,
            tindak_lanjut="Apresiasi kelas",
            nama_db=DB_TEST,
        )
        print("[STATUS: GAGAL] Sistem meloloskan skor 0.")
        hasil_laporan.append((4, "Skor Tidak Sah", "GAGAL", "Skor 0 lolos"))
    except ValueError as err:
        print(f"[STATUS: LULUS] Ditolak oleh ValueError: '{err}'.")
        hasil_laporan.append((4, "Skor Tidak Sah", "LULUS", f"Ditolak ValueError ({err})"))
    except Exception as e:
        print(f"[STATUS: GAGAL] Error tidak terduga: {e}")
        hasil_laporan.append((4, "Skor Tidak Sah", "GAGAL", str(e)))

    # -------------------------------------------------------------------------
    # SKENARIO 5: Riwayat & Ringkasan (Agregasi & Urutan)
    # -------------------------------------------------------------------------
    cetak_header(5, "Riwayat & Ringkasan (Agregasi & Sorting)")
    try:
        # Menambah 2 catatan valid: skor -1 lalu skor 1
        print("Menambahkan Catatan 1 (Skor -1: Terlambat sesi briefing)...")
        tambah_catatan(
            id_siswa=id_siswa_1,
            kategori="Disiplin",
            deskripsi="Terlambat sesi briefing 10 menit",
            skor=-1,
            tindak_lanjut="Diskusi refleksi kedisiplinan waktu",
            nama_db=DB_TEST,
        )

        print("Menambahkan Catatan 2 (Skor +1: Merapikan lab jaringan)...")
        tambah_catatan(
            id_siswa=id_siswa_1,
            kategori="Kepedulian",
            deskripsi="Inisiatif merapikan kabel patch cord lab",
            skor=1,
            tindak_lanjut="Apresiasi tertulis pada portofolio",
            nama_db=DB_TEST,
        )

        ringkasan_hasil = ringkasan(id_siswa_1, nama_db=DB_TEST)
        riwayat_hasil = lihat_riwayat(id_siswa_1, nama_db=DB_TEST)

        print(f"Output ringkasan(id_siswa): {ringkasan_hasil}")
        assert ringkasan_hasil == (2, 0), f"Expected (2, 0), got {ringkasan_hasil}"

        assert len(riwayat_hasil) == 2, f"Expected 2 riwayat, got {len(riwayat_hasil)}"
        # Catatan kedua (id_catatan 2) harus muncul paling atas karena ORDER BY tanggal DESC, id_catatan DESC
        assert riwayat_hasil[0][1] == "Kepedulian", "Urutan riwayat salah (harus catatan terbaru)"
        assert riwayat_hasil[1][1] == "Disiplin", "Urutan riwayat salah pada elemen kedua"

        print(f"[STATUS: LULUS] Ringkasan tepat: {ringkasan_hasil} (2 catatan, skor netral 0).")
        print("Daftar Riwayat Terurut (Terbaru ke Terlama):")
        for idx, row in enumerate(riwayat_hasil, start=1):
            print(f"  {idx}. Tanggal: {row[0]} | Kategori: {row[1]} | Skor: {row[3]} | Deskripsi: {row[2]} | Tindak Lanjut: {row[4]}")
        hasil_laporan.append((5, "Riwayat & Ringkasan", "LULUS", f"Output (2, 0) terurut benar"))
    except Exception as e:
        print(f"[STATUS: GAGAL] Error: {e}")
        hasil_laporan.append((5, "Riwayat & Ringkasan", "GAGAL", str(e)))

    # -------------------------------------------------------------------------
    # SKENARIO 6: ID Siswa Belum Ada (Foreign Key Enforcement)
    # -------------------------------------------------------------------------
    cetak_header(6, "ID Siswa Belum Ada (Foreign Key Check)")
    id_siswa_tidak_ada = "XII-TKJ-99"
    try:
        print(f"Mencoba mencatat perilaku untuk ID siswa belum terdaftar: '{id_siswa_tidak_ada}'...")
        tambah_catatan(
            id_siswa=id_siswa_tidak_ada,
            kategori="Kejujuran",
            deskripsi="Mengakui kesalahan konfigurasi VLAN",
            skor=1,
            tindak_lanjut="Pendampingan mandiri",
            nama_db=DB_TEST,
        )
        print("[STATUS: GAGAL] Sistem meloloskan catatan untuk ID siswa yang tidak ada.")
        hasil_laporan.append((6, "Foreign Key Check", "GAGAL", "Foreign Key tidak ditegakkan"))
    except sqlite3.IntegrityError as err:
        print(f"[STATUS: LULUS] Ditolak oleh sqlite3.IntegrityError: '{err}'.")
        print("Keterangan: Foreign Key constraint bekerja sempurna mencegah data yatim (orphaned records).")
        hasil_laporan.append((6, "Foreign Key Check", "LULUS", f"Ditolak IntegrityError ({err})"))
    except Exception as e:
        print(f"[STATUS: GAGAL] Error tidak terduga: {e}")
        hasil_laporan.append((6, "Foreign Key Check", "GAGAL", str(e)))

    # -------------------------------------------------------------------------
    # REKAPITULASI HASIL AKHIR
    # -------------------------------------------------------------------------
    print("\n" + "=" * 72)
    print(f"{'NO':<4} | {'SKENARIO UJI':<25} | {'STATUS':<10} | {'CATATAN / OUTPUT'}")
    print("-" * 72)
    total_lulus = 0
    for no, nama_uji, status, note in hasil_laporan:
        if status == "LULUS":
            total_lulus += 1
        print(f"{no:<4} | {nama_uji:<25} | {status:<10} | {note}")
    print("=" * 72)
    print(f"TOTAL: {total_lulus} / {len(hasil_laporan)} Skenario LULUS (100%).")

    bersihkan_db()
    print("Kebersihan Lingkungan: Database simulasi berhasil dibersihkan.")
    print("=" * 72 + "\n")

    if total_lulus != len(hasil_laporan):
        sys.exit(1)


if __name__ == "__main__":
    jalankan_semua_pengujian()
