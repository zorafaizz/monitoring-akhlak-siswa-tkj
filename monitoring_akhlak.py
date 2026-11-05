"""
Aplikasi Monitoring Akhlak Siswa (Modul Proyek Kelas XII TKJ - SMK Alhadiid)
Dibangun menggunakan pustaka standar Python: sqlite3, datetime, dan sys.
Kompatibel langsung di Spyder IDE maupun terminal modern.
Zero external dependencies.
"""

import os
import sqlite3
import sys
from datetime import date

NAMA_DB_DEFAULT = "monitoring_akhlak.db"

# ANSI styling untuk antarmuka technical-minimalist
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_CYAN = "\033[36m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_RED = "\033[31m"
C_BLUE = "\033[34m"
C_MAGENTA = "\033[35m"


def koneksi_db(nama_db=NAMA_DB_DEFAULT):
    """
    Membuka koneksi ke database SQLite dan mengaktifkan penegakan Foreign Key.
    """
    conn = sqlite3.connect(nama_db)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def siapkan_db(nama_db=NAMA_DB_DEFAULT):
    """
    Menyiapkan tabel relasional 'siswa' dan 'catatan' dengan skema yang ketat
    dan menambahkan indeks untuk optimasi performa query.
    """
    with koneksi_db(nama_db) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS siswa (
                id_siswa TEXT PRIMARY KEY,
                nama TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS catatan (
                id_catatan INTEGER PRIMARY KEY AUTOINCREMENT,
                id_siswa TEXT NOT NULL,
                tanggal TEXT NOT NULL,
                kategori TEXT NOT NULL,
                deskripsi TEXT NOT NULL,
                skor INTEGER NOT NULL CHECK(skor IN (-1, 1)),
                tindak_lanjut TEXT NOT NULL,
                FOREIGN KEY (id_siswa) REFERENCES siswa(id_siswa)
            )
            """
        )
        # Indeks untuk efisiensi kueri relasional dan filter waktu
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_catatan_id_siswa ON catatan(id_siswa)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_catatan_tanggal ON catatan(tanggal)"
        )


def tambah_siswa(id_siswa, nama, nama_db=NAMA_DB_DEFAULT):
    """
    Menambahkan data siswa baru ke tabel siswa.
    Memvalidasi agar ID dan nama tidak kosong.
    """
    if not isinstance(id_siswa, str) or not isinstance(nama, str):
        raise ValueError("ID dan nama wajib diisi")

    id_siswa_bersih = id_siswa.strip()
    nama_bersih = nama.strip()

    if not id_siswa_bersih or not nama_bersih:
        raise ValueError("ID dan nama wajib diisi")

    with koneksi_db(nama_db) as conn:
        conn.execute(
            "INSERT INTO siswa (id_siswa, nama) VALUES (?, ?)",
            (id_siswa_bersih, nama_bersih),
        )


def tambah_catatan(
    id_siswa, kategori, deskripsi, skor, tindak_lanjut, nama_db=NAMA_DB_DEFAULT
):
    """
    Menambahkan catatan pembinaan perilaku siswa ke tabel catatan.
    Memvalidasi skor (-1 atau 1) serta kelengkapan seluruh teks.
    """
    if type(skor) is not int or skor not in (-1, 1):
        raise ValueError("Skor harus -1 atau 1")

    if not all(
        isinstance(val, str)
        for val in (id_siswa, kategori, deskripsi, tindak_lanjut)
    ):
        raise ValueError(
            "ID siswa, kategori, deskripsi, dan tindak lanjut wajib diisi"
        )

    id_siswa_bersih = id_siswa.strip()
    kategori_bersih = kategori.strip()
    deskripsi_bersih = deskripsi.strip()
    tindak_lanjut_bersih = tindak_lanjut.strip()

    if not (
        id_siswa_bersih
        and kategori_bersih
        and deskripsi_bersih
        and tindak_lanjut_bersih
    ):
        raise ValueError(
            "ID siswa, kategori, deskripsi, dan tindak lanjut wajib diisi"
        )

    tanggal_hari_ini = date.today().isoformat()

    with koneksi_db(nama_db) as conn:
        conn.execute(
            """
            INSERT INTO catatan (id_siswa, tanggal, kategori, deskripsi, skor, tindak_lanjut)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                id_siswa_bersih,
                tanggal_hari_ini,
                kategori_bersih,
                deskripsi_bersih,
                skor,
                tindak_lanjut_bersih,
            ),
        )


def lihat_riwayat(id_siswa, nama_db=NAMA_DB_DEFAULT):
    """
    Mengambil seluruh riwayat catatan pembinaan siswa terurut dari yang terbaru.
    """
    id_siswa_bersih = id_siswa.strip() if isinstance(id_siswa, str) else ""
    with koneksi_db(nama_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT tanggal, kategori, deskripsi, skor, tindak_lanjut
            FROM catatan
            WHERE id_siswa = ?
            ORDER BY tanggal DESC, id_catatan DESC
            """,
            (id_siswa_bersih,),
        )
        return cursor.fetchall()


def ringkasan(id_siswa, nama_db=NAMA_DB_DEFAULT):
    """
    Mengambil agregasi jumlah catatan dan total skor perilaku siswa.
    """
    id_siswa_bersih = id_siswa.strip() if isinstance(id_siswa, str) else ""
    with koneksi_db(nama_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*), COALESCE(SUM(skor), 0)
            FROM catatan
            WHERE id_siswa = ?
            """,
            (id_siswa_bersih,),
        )
        return cursor.fetchone()


# =============================================================================
# FITUR ANALITIK TINGKAT LANJUT & SEEDER DATABASE
# =============================================================================

def ambil_semua_siswa(nama_db=NAMA_DB_DEFAULT):
    """
    Mengambil daftar seluruh siswa lengkap dengan agregasi jumlah catatan dan skor.
    """
    with koneksi_db(nama_db) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                s.id_siswa, 
                s.nama, 
                COUNT(c.id_catatan) AS total_catatan, 
                COALESCE(SUM(c.skor), 0) AS total_skor
            FROM siswa s
            LEFT JOIN catatan c ON s.id_siswa = c.id_siswa
            GROUP BY s.id_siswa, s.nama
            ORDER BY s.id_siswa ASC
            """
        )
        return cursor.fetchall()


def statistik_global(nama_db=NAMA_DB_DEFAULT):
    """
    Menghitung statistik global untuk pemantauan keseluruhan kelas.
    """
    with koneksi_db(nama_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM siswa")
        total_siswa = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM catatan")
        total_catatan = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM catatan WHERE skor = 1")
        total_apresiasi = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM catatan WHERE skor = -1")
        total_evaluasi = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(skor), 0) FROM catatan")
        net_skor = cursor.fetchone()[0]

        indeks_positif = (
            round((total_apresiasi / total_catatan) * 100, 1)
            if total_catatan > 0
            else 0.0
        )

        return {
            "total_siswa": total_siswa,
            "total_catatan": total_catatan,
            "total_apresiasi": total_apresiasi,
            "total_evaluasi": total_evaluasi,
            "net_skor": net_skor,
            "indeks_positif": indeks_positif,
        }


def isi_data_seeder(nama_db=NAMA_DB_DEFAULT):
    """
    Menyuntikkan data simulasi fiktif 10 siswa Kelas XII TKJ beserta rekam jejak
    pembinaan perilaku faktual untuk keperluan demonstrasi dan verifikasi sistem.
    """
    siapkan_db(nama_db)

    daftar_siswa = [
        ("XII-TKJ-01", "Ahmad Fauzi"),
        ("XII-TKJ-02", "Bagas Pratama"),
        ("XII-TKJ-03", "Cindy Claudia"),
        ("XII-TKJ-04", "Dimas Wahyu"),
        ("XII-TKJ-05", "Eka Rahmawati"),
        ("XII-TKJ-06", "Fajar Hidayat"),
        ("XII-TKJ-07", "Gilang Ramadhan"),
        ("XII-TKJ-08", "Hanafi Saputra"),
        ("XII-TKJ-09", "Indah Permata"),
        ("XII-TKJ-10", "Jaka Satria"),
    ]

    catatan_simulasi = [
        ("XII-TKJ-01", "Tanggung Jawab", "Menyelesaikan konfigurasi routing OSPF pada router mikrotik lab tepat waktu", 1, "Apresiasi kinerja dan ditunjuk sebagai tutor sebaya"),
        ("XII-TKJ-01", "Kepedulian", "Membantu rekan sekelompok merapikan kabel UTP pada rak server", 1, "Catatan apresiasi positif pada portofolio kejuruan"),
        ("XII-TKJ-02", "Disiplin", "Terlambat memasuki ruang praktikum jaringan 15 menit tanpa surat izin", -1, "Refleksi kedisiplinan dan piket inventaris lab"),
        ("XII-TKJ-02", "Kejujuran", "Mengakui kesalahan konfigurasi IP yang menyebabkan IP conflict di lab", 1, "Apresiasi integritas dan bimbingan teknik subnetting"),
        ("XII-TKJ-02", "Tanggung Jawab", "Menuntaskan perbaikan konfigurasi switch managed sebelum jam lab selesai", 1, "Pujian lisan di hadapan instruktur"),
        ("XII-TKJ-03", "Disiplin", "Selalu hadir 10 menit sebelum jam praktikum dan menyiapkan workstation lab", 1, "Apresiasi keteladanan kedisiplinan"),
        ("XII-TKJ-03", "Kepedulian", "Mengumpulkan modul ajar yang tertinggal dan menyerahkan ke meja instruktur", 1, "Ucapan terima kasih resmi instruktur"),
        ("XII-TKJ-04", "Disiplin", "Meninggalkan sampah pembungkus konektor RJ-45 di meja kerja praktikum", -1, "Edukasi kebersihan lab kerja dan membersihkan meja"),
        ("XII-TKJ-04", "Tanggung Jawab", "Melakukan crimping ulang kabel LAN hingga lulus uji cable tester", 1, "Apresiasi ketekunan teknis"),
        ("XII-TKJ-05", "Kejujuran", "Menyerahkan flashdisk milik rekan yang tertinggal di PC server lab", 1, "Apresiasi integritas karakter"),
        ("XII-TKJ-06", "Disiplin", "Makan snack di dalam ruang server saat praktikum berlangsung", -1, "Peringatan aturan K3 laboratorium dan pembersihan ruang"),
        ("XII-TKJ-06", "Tanggung Jawab", "Lupa mematikan (shutdown) server virtual setelah sesi pembelajaran usai", -1, "Pendampingan SOP penutupan lab dan penugasan checklist K3"),
        ("XII-TKJ-07", "Kepedulian", "Inisiatif memperbaiki crimping kabel koneksi akses poin yang kendur", 1, "Pencatatan poin keaktifan lab"),
        ("XII-TKJ-08", "Disiplin", "Tidak menggunakan wearpack lengkap saat sesi instalasi jaringan luar", -1, "Peringatan keselamatan kerja (K3) dan penggunaan APD"),
        ("XII-TKJ-08", "Tanggung Jawab", "Meminjam alat ukur OTDR dan mengembalikan dalam kondisi bersih & lengkap", 1, "Apresiasi kepatuhan prosedur peminjaman alat"),
        ("XII-TKJ-09", "Kepedulian", "Mendampingi rekan yang mengalami kesulitan dalam instalasi Debian Server", 1, "Apresiasi jiwa kolaboratif"),
        ("XII-TKJ-10", "Tanggung Jawab", "Menyusun dokumentasi topologi jaringan kelas secara terstruktur", 1, "Portofolio terpilih untuk bahan pameran karya"),
        ("XII-TKJ-10", "Kejujuran", "Melaporkan adanya port switch yang rusak fisik sebelum digunakan praktikum", 1, "Apresiasi ketelitian dan kejujuran pelaporan"),
    ]

    total_siswa_baru = 0
    total_catatan_baru = 0

    with koneksi_db(nama_db) as conn:
        for id_s, nama in daftar_siswa:
            try:
                conn.execute(
                    "INSERT INTO siswa (id_siswa, nama) VALUES (?, ?)", (id_s, nama)
                )
                total_siswa_baru += 1
            except sqlite3.IntegrityError:
                pass

    for id_s, kat, desk, skor, tindak in catatan_simulasi:
        try:
            tambah_catatan(id_s, kat, desk, skor, tindak, nama_db=nama_db)
            total_catatan_baru += 1
        except Exception:
            pass

    return total_siswa_baru, total_catatan_baru


# =============================================================================
# TAMPILAN ANTARMUKA KONSOL (CLI MODERN TECHNICAL)
# =============================================================================

def cetak_kotak_header():
    """Mencetak header aplikasi dengan aksen technical modern."""
    print(f"\n{C_CYAN}┌────────────────────────────────────────────────────────────────────────┐{C_RESET}")
    print(f"{C_CYAN}│{C_RESET} {C_BOLD}◈ SISTEM MONITORING AKHLAK SISWA | KELAS XII TKJ - SMK ALHADIID{C_RESET}        {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}│{C_RESET}   {C_DIM}Arsitektur SQLite Relasional • Parameterized • Zero External Deps{C_RESET}     {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}└────────────────────────────────────────────────────────────────────────┘{C_RESET}")


def cetak_panduan_pembinaan():
    """Mencetak panduan etika pencatatan dan kategori pembinaan."""
    print(f"{C_YELLOW}[PANDUAN ETIKA & PRINSIP PEMBINAAN]{C_RESET}")
    print(" • Kategori Contoh : Disiplin | Tanggung Jawab | Kepedulian | Kejujuran")
    print(" • Prinsip Deskripsi: Wajib faktual, objektif, netral (hindari label subjektif).")
    print(f" • Fungsi Skor     : {C_GREEN}[+1 Apresiasi]{C_RESET} / {C_RED}[-1 Pembinaan]{C_RESET} adalah indikator tren pendampingan,")
    print("                     BUKAN vonis tunggal atas moral atau prestasi akademik.")
    print(" • Hak Siswa       : Wajib mencantumkan tindak lanjut & ruang klarifikasi dua arah.")
    print(f"{C_DIM}────────────────────────────────────────────────────────────────────────{C_RESET}")


def tampilkan_menu():
    """
    Menampilkan menu navigasi utama CLI dengan opsi yang diperkaya.
    """
    cetak_kotak_header()
    cetak_panduan_pembinaan()
    print(f"{C_BOLD}NAVIGASI SISTEM:{C_RESET}")
    print(f"  {C_CYAN}1.{C_RESET} Tambah Siswa Baru")
    print(f"  {C_CYAN}2.{C_RESET} Tambah Catatan Pembinaan Perilaku")
    print(f"  {C_CYAN}3.{C_RESET} Lihat Riwayat & Ringkasan Siswa")
    print(f"  {C_CYAN}4.{C_RESET} {C_BOLD}Dashboard & Statistik Global Kelas XII TKJ{C_RESET}")
    print(f"  {C_CYAN}5.{C_RESET} Suntikkan Data Seeder Simulasi Fiktif (10 Siswa TKJ)")
    print(f"  {C_CYAN}6.{C_RESET} {C_GREEN}Buka Web Dashboard GUI (Browser / Modern SPA){C_RESET}")
    print(f"  {C_CYAN}7.{C_RESET} Keluar dari Aplikasi")
    print(f"{C_CYAN}────────────────────────────────────────────────────────────────────────{C_RESET}")


def cetak_dashboard_global():
    """Mencetak visualisasi kartu metrik dan tabel performa siswa di terminal."""
    stats = statistik_global()
    siswa_list = ambil_semua_siswa()

    print(f"\n{C_BOLD}{C_CYAN}┌─ METRIK GLOBAL PEMBINAAN SISWA KELAS XII TKJ ──────────────────────────┐{C_RESET}")
    print(f"{C_CYAN}│{C_RESET} Total Siswa Terdaftar : {C_BOLD}{stats['total_siswa']:<4}{C_RESET} │ Total Catatan       : {C_BOLD}{stats['total_catatan']:<4}{C_RESET} {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}│{C_RESET} Apresiasi Positif (+1): {C_GREEN}{stats['total_apresiasi']:<4}{C_RESET} │ Evaluasi Pembinaan  : {C_RED}{stats['total_evaluasi']:<4}{C_RESET} {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}│{C_RESET} Net Total Skor Akumulasi: {C_BOLD}{stats['net_skor']:<2}{C_RESET}    │ Indeks Perilaku Positif: {C_CYAN}{stats['indeks_positif']}%{C_RESET}  {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}└────────────────────────────────────────────────────────────────────────┘{C_RESET}")

    if not siswa_list:
        print(f"{C_YELLOW}Belum ada data siswa. Gunakan Menu 1 atau Menu 5 untuk mengisi data.{C_RESET}\n")
        return

    print(f"\n{C_BOLD}DAFTAR SISWA & AGREGASI AKHLAK:{C_RESET}")
    print("┌───────────────┬──────────────────────────┬──────────┬────────────┐")
    print("│ ID SISWA      │ NAMA LENGKAP             │ CATATAN  │ SKOR NET   │")
    print("├───────────────┼──────────────────────────┼──────────┼────────────┤")
    for id_s, nama, jml, skr in siswa_list:
        skr_label = f"+{skr}" if skr > 0 else (str(skr) if skr < 0 else " 0")
        warna_skor = C_GREEN if skr > 0 else (C_RED if skr < 0 else C_DIM)
        print(f"│ {id_s:<13} │ {nama:<24} │ {jml:<8} │ {warna_skor}{skr_label:<10}{C_RESET} │")
    print("└───────────────┴──────────────────────────┴──────────┴────────────┘\n")


def jalankan_server_web_lokal(port=8080):
    """
    Menjalankan Web Dashboard GUI terintegrasi langsung dari file server_web.py.
    """
    print(f"\n{C_CYAN}⚡ Memulai Web Dashboard GUI Server pada port {port}...{C_RESET}")
    try:
        from server_web import jalankan_server
        jalankan_server(port=port)
    except ImportError:
        print(f"{C_RED}Modul server_web.py tidak ditemukan. Pastikan file ada di direktori proyek.{C_RESET}")


def main():
    """
    Fungsi utama penggerak CLI dengan penanganan error terpusat dan ramah.
    """
    siapkan_db()

    # Opsi flag CLI untuk eksekusi langsung
    if len(sys.argv) > 1:
        flag = sys.argv[1].strip()
        if flag in ("--web", "-w"):
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
            jalankan_server_web_lokal(port=port)
            return
        elif flag in ("--seed", "-s"):
            ts, tc = isi_data_seeder()
            print(f"Data seeder disuntikkan: +{ts} Siswa, +{tc} Catatan.")
            return

    while True:
        tampilkan_menu()
        try:
            pilihan = input(f"{C_BOLD}Pilih opsi menu (1-7): {C_RESET}").strip()

            if pilihan == "1":
                print(f"\n{C_CYAN}--- [1] FORM TAMBAH DATA SISWA BARU ---{C_RESET}")
                id_siswa = input("ID Siswa (contoh: XII-TKJ-11) : ")
                nama = input("Nama Lengkap Siswa            : ")
                tambah_siswa(id_siswa, nama)
                print(f"{C_GREEN}✓ Sukses: Siswa '{nama.strip()}' [{id_siswa.strip()}] berhasil disimpan ke database.{C_RESET}\n")

            elif pilihan == "2":
                print(f"\n{C_CYAN}--- [2] FORM CATATAN PEMBINAAN PERILAKU ---{C_RESET}")
                id_siswa = input("ID Siswa Target               : ")
                print(f"{C_DIM}Kategori Rekomendasi: Disiplin | Tanggung Jawab | Kepedulian | Kejujuran{C_RESET}")
                kategori = input("Kategori Pembinaan            : ")
                deskripsi = input("Deskripsi Kejadian (Faktual)  : ")
                skor_input = input("Skor (-1 Evaluasi, 1 Positif) : ")
                try:
                    skor = int(skor_input.strip())
                except ValueError:
                    raise ValueError("Skor harus berupa angka bulat (-1 atau 1)")

                tindak_lanjut = input("Rencana Tindak Lanjut         : ")
                tambah_catatan(id_siswa, kategori, deskripsi, skor, tindak_lanjut)
                print(f"{C_GREEN}✓ Sukses: Catatan pembinaan untuk siswa [{id_siswa.strip()}] berhasil dicatat.{C_RESET}\n")

            elif pilihan == "3":
                print(f"\n{C_CYAN}--- [3] LIHAT RIWAYAT & RINGKASAN SISWA ---{C_RESET}")
                id_siswa = input("Masukkan ID Siswa yang dicari: ").strip()
                total_catatan, total_skor = ringkasan(id_siswa)
                print(f"\n{C_BOLD}Jumlah catatan, skor ringkas: ({total_catatan}, {total_skor}){C_RESET}")

                riwayat = lihat_riwayat(id_siswa)
                if not riwayat:
                    print(f"{C_YELLOW}Informasi: Belum ada catatan pembinaan untuk siswa [{id_siswa}].{C_RESET}\n")
                else:
                    print("┌────────────┬─────────────────┬───────┬────────────────────────────┬────────────────────────────┐")
                    print("│ TANGGAL    │ KATEGORI        │ SKOR  │ DESKRIPSI KEJADIAN         │ TINDAK LANJUT              │")
                    print("├────────────┼─────────────────┼───────┼────────────────────────────┼────────────────────────────┤")
                    for tgl, kat, desk, skr, tndk in riwayat:
                        skr_badge = f"{C_GREEN}+1{C_RESET}" if skr > 0 else f"{C_RED}-1{C_RESET}"
                        d_disp = (desk[:26] + "..") if len(desk) > 28 else desk
                        t_disp = (tndk[:26] + "..") if len(tndk) > 28 else tndk
                        print(f"│ {tgl:<10} │ {kat:<15} │ {skr_badge:<14} │ {d_disp:<26} │ {t_disp:<26} │")
                    print("└────────────┴─────────────────┴───────┴────────────────────────────┴────────────────────────────┘\n")

            elif pilihan == "4":
                cetak_dashboard_global()

            elif pilihan == "5":
                print(f"\n{C_CYAN}Menyuntikkan data seeder simulasi Kelas XII TKJ...{C_RESET}")
                ts, tc = isi_data_seeder()
                print(f"{C_GREEN}✓ Data Seeder Selesai: {ts} siswa baru ditambahkan, {tc} catatan pembinaan tercatat.{C_RESET}\n")

            elif pilihan == "6":
                jalankan_server_web_lokal()

            elif pilihan == "7":
                print(f"\n{C_GREEN}Sistem ditutup dengan aman. Terima kasih atas dedikasi pembinaannya.{C_RESET}")
                break

            else:
                print(f"\n{C_RED}Pilihan menu tidak valid. Silakan pilih angka 1 sampai 7.{C_RESET}\n")

        except (ValueError, sqlite3.IntegrityError) as err:
            print(f"{C_RED}Data belum tersimpan: {err}{C_RESET}\n")
        except KeyboardInterrupt:
            print(f"\n\n{C_YELLOW}Sistem dihentikan oleh pengguna.{C_RESET}")
            break


if __name__ == "__main__":
    main()
