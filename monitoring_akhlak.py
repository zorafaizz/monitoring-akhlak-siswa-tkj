"""
Aplikasi Monitoring Akhlak Siswa (Modul Proyek Kelas XII TKJ - SMK Alhadiid)
Dibangun menggunakan pustaka standar Python: sqlite3 dan datetime.
Dapat dijalankan langsung di Spyder IDE maupun terminal.
"""

import sqlite3
from datetime import date

NAMA_DB_DEFAULT = "monitoring_akhlak.db"


def koneksi_db(nama_db=NAMA_DB_DEFAULT):
    """
    Membuka koneksi ke database SQLite dan mengaktifkan penegakan Foreign Key.
    """
    conn = sqlite3.connect(nama_db)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def siapkan_db(nama_db=NAMA_DB_DEFAULT):
    """
    Menyiapkan tabel relasional 'siswa' dan 'catatan' dengan skema yang ketat.
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


def tampilkan_menu():
    """
    Menampilkan panduan prinsip pembinaan dan menu utama konsol.
    """
    print("=" * 72)
    print("  SISTEM MONITORING AKHLAK SISWA | KELAS XII TKJ - SMK ALHADIID")
    print("=" * 72)
    print("[PANDUAN & PRINSIP PEMBINAAN]")
    print("- Kategori Contoh: Disiplin, Tanggung Jawab, Kepedulian, Kejujuran")
    print("- Deskripsi      : Wajib faktual, objektif, dan menggunakan bahasa netral.")
    print("- Indikator Skor : (-1 / +1) adalah pembimbing pembinaan, BUKAN penentu")
    print("                   mutlak karakter maupun capaian akademik siswa.")
    print("- Kolaborasi     : Wajib mencantumkan tindak lanjut dan ruang klarifikasi.")
    print("-" * 72)
    print("MENU UTAMA:")
    print("1. Tambah Siswa")
    print("2. Tambah Catatan Pembinaan")
    print("3. Lihat Riwayat & Ringkasan")
    print("4. Keluar")
    print("=" * 72)


def main():
    """
    Fungsi utama penggerak CLI dengan penanganan error yang ramah dan konsisten.
    """
    siapkan_db()

    while True:
        tampilkan_menu()
        try:
            pilihan = input("Pilih menu (1-4): ").strip()

            if pilihan == "1":
                print("\n--- [1] TAMBAH SISWA BARU ---")
                id_siswa = input("ID Siswa (contoh: XII-TKJ-01): ")
                nama = input("Nama Lengkap Siswa           : ")
                tambah_siswa(id_siswa, nama)
                print(f"Sukses: Siswa '{nama.strip()}' [{id_siswa.strip()}] berhasil disimpan.\n")

            elif pilihan == "2":
                print("\n--- [2] TAMBAH CATATAN PEMBINAAN ---")
                id_siswa = input("ID Siswa                     : ")
                print("Panduan Kategori: Disiplin | Tanggung Jawab | Kepedulian | Kejujuran")
                kategori = input("Kategori                     : ")
                deskripsi = input("Deskripsi (faktual/netral)   : ")
                skor_input = input("Skor (-1 evaluasi, 1 positif): ")
                try:
                    skor = int(skor_input.strip())
                except ValueError:
                    raise ValueError("Skor harus -1 atau 1")

                tindak_lanjut = input("Rencana Tindak Lanjut        : ")
                tambah_catatan(id_siswa, kategori, deskripsi, skor, tindak_lanjut)
                print(f"Sukses: Catatan untuk siswa [{id_siswa.strip()}] berhasil disimpan.\n")

            elif pilihan == "3":
                print("\n--- [3] RIWAYAT & RINGKASAN SISWA ---")
                id_siswa = input("Masukkan ID Siswa yang dicari: ")
                total_catatan, total_skor = ringkasan(id_siswa)
                print(f"Jumlah catatan, skor ringkas: ({total_catatan}, {total_skor})")

                riwayat = lihat_riwayat(id_siswa)
                if not riwayat:
                    print(f"Informasi: Belum ada catatan pembinaan untuk siswa [{id_siswa.strip()}].\n")
                else:
                    print("-" * 72)
                    print(f"{'Tanggal':<12} | {'Kategori':<15} | {'Skor':<5} | {'Deskripsi':<18} | {'Tindak Lanjut'}")
                    print("-" * 72)
                    for tgl, kat, desk, skr, tndk in riwayat:
                        skor_str = f"+{skr}" if skr > 0 else str(skr)
                        print(f"{tgl:<12} | {kat:<15} | {skor_str:<5} | {desk:<18} | {tndk}")
                    print("-" * 72 + "\n")

            elif pilihan == "4":
                print("\nSistem ditutup dengan aman. Terima kasih atas dedikasi pembinaannya.")
                break

            else:
                print("\nPilihan menu tidak valid. Silakan pilih angka 1 sampai 4.\n")

        except (ValueError, sqlite3.IntegrityError) as err:
            print(f"Data belum tersimpan: {err}\n")
        except KeyboardInterrupt:
            print("\n\nSistem dihentikan oleh pengguna.")
            break


if __name__ == "__main__":
    main()
