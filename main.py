"""
Unified Launcher - Sistem Monitoring Akhlak Siswa
SMK Alhadiid | Kelas XII TKJ
Mendukung 3 Mode Operasional:
1. Desktop Native GUI (Tkinter Dark Modern)
2. Web Dashboard Modern (Single-Page Application Browser)
3. Terminal Technical Console (TUI Dashboard)
"""

import os
import sys
import webbrowser

from monitoring_akhlak import (
    NAMA_DB_DEFAULT,
    isi_data_seeder,
    main as jalankan_cli,
    siapkan_db,
)


def cetak_banner_launcher():
    print("\033[36m┌────────────────────────────────────────────────────────────────────────┐\033[0m")
    print("\033[36m│\033[0m \033[1m◈ SISTEM MONITORING AKHLAK SISWA | KELAS XII TKJ - SMK ALHADIID\033[0m        \033[36m│\033[0m")
    print("\033[36m│\033[0m   \033[2mPusat Kontrol Operasional • Desktop GUI • Web SPA • Terminal TUI\033[0m     \033[36m│\033[0m")
    print("\033[36m└────────────────────────────────────────────────────────────────────────┘\033[0m")
    print("PILIH MODE OPERASIONAL APLIKASI:")
    print("  \033[36m[1]\033[0m \033[1mAplikasi Desktop GUI\033[0m (Native Window - Dark Professional)")
    print("  \033[36m[2]\033[0m \033[1;32mWeb Dashboard Interaktif\033[0m (Modern Browser SPA / Zero Dependency)")
    print("  \033[36m[3]\033[0m \033[1;34mTerminal Technical Console\033[0m (TUI Box-Drawing Dashboard)")
    print("  \033[36m[4]\033[0m \033[33mSuntik Data Seeder Simulasi\033[0m (10 Siswa Fiktif XII TKJ)")
    print("  \033[36m[5]\033[0m \033[35mJalankan Otomatisasi Pengujian\033[0m (6 Skenario Wajib)")
    print("  \033[36m[0]\033[0m Keluar dari Sistem")
    print("\033[36m────────────────────────────────────────────────────────────────────────\033[0m")


def luncurkan_gui():
    print("\n\033[36m⚡ Mempersiapkan Aplikasi Desktop GUI...\033[0m")
    try:
        from gui_app import jalankan_gui
        jalankan_gui()
    except Exception as err:
        print(f"\033[31mGagal meluncurkan GUI Desktop: {err}\033[0m")
        print("Beralih ke mode Web Dashboard atau Terminal...")


def luncurkan_web(port=8080):
    print(f"\n\033[32m⚡ Menyalakan Server Web Dashboard pada port {port}...\033[0m")
    try:
        webbrowser.open(f"http://127.0.0.1:{port}")
    except Exception:
        pass
    from server_web import jalankan_server
    jalankan_server(port=port)


def luncurkan_pengujian():
    print("\n\033[35m⚡ Menjalankan Otomatisasi Pengujian 6 Skenario Wajib...\033[0m")
    from uji_skenario import jalankan_semua_pengujian
    jalankan_semua_pengujian()


def menu_utama():
    siapkan_db()

    # Cek argumen CLI langsung
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip().lower()
        if arg in ("--gui", "-g"):
            luncurkan_gui()
            return
        elif arg in ("--web", "-w"):
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
            luncurkan_web(port=port)
            return
        elif arg in ("--cli", "-c"):
            jalankan_cli()
            return
        elif arg in ("--seed", "-s"):
            ts, tc = isi_data_seeder()
            print(f"Data seeder disuntikkan: {ts} siswa baru, {tc} catatan pembinaan.")
            return
        elif arg in ("--test", "-t"):
            luncurkan_pengujian()
            return

    while True:
        cetak_banner_launcher()
        try:
            pilihan = input("\033[1mMasukkan nomor pilihan (0-5): \033[0m").strip()
            if pilihan == "1":
                luncurkan_gui()
                break
            elif pilihan == "2":
                luncurkan_web()
                break
            elif pilihan == "3":
                jalankan_cli()
                break
            elif pilihan == "4":
                ts, tc = isi_data_seeder()
                print(f"\n\033[32m✓ Sukses: +{ts} Siswa baru ditambahkan, +{tc} Catatan pembinaan disimpan.\033[0m\n")
            elif pilihan == "5":
                luncurkan_pengujian()
            elif pilihan == "0":
                print("\n\033[32mTerima kasih. Sistem monitoring akhlak ditutup dengan aman.\033[0m")
                break
            else:
                print("\n\033[31mPilihan tidak valid. Silakan pilih angka 0 sampai 5.\033[0m\n")
        except KeyboardInterrupt:
            print("\n\nSistem dihentikan oleh pengguna.")
            break


if __name__ == "__main__":
    menu_utama()
