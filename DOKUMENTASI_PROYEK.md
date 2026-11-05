# DOKUMENTASI PROYEK PENGEMBANGAN SISTEM
# APLIKASI MONITORING AKHLAK SISWA
### Modul Proyek Kelas XII Teknik Komputer dan Jaringan (TKJ) — SMK Alhadiid

---

## DAFTAR ISI
1. [BAB I: METODOLOGI 5 TAHAPAN PROYEK](#bab-i-metodologi-5-tahapan-proyek)
   - [01 Analisis](#01-analisis)
   - [02 Rancang](#02-rancang)
   - [03 Bangun (CLI & Web GUI SPA)](#03-bangun)
   - [04 Verifikasi & Hasil Pengujian](#04-verifikasi--hasil-pengujian)
   - [05 Evaluasi](#05-evaluasi)
2. [BAB II: ETIKA DAN PRIVASI DATA SISWA](#bab-ii-etika-dan-privasi-data-siswa)
3. [BAB III: JAWABAN KOMPREHENSIF PERTANYAAN REFLEKSI](#bab-iii-jawaban-komprehensif-pertanyaan-refleksi)

---

## BAB I: METODOLOGI 5 TAHAPAN PROYEK

### 01 Analisis

#### 1. Latar Belakang & Permasalahan
Di lingkungan pendidikan kejuruan (SMK), khususnya program keahlian Teknik Komputer dan Jaringan (TKJ), pembentukan karakter profesional, kedisiplinan laboratorium, etika penggunaan teknologi, dan tanggung jawab kerja sama kelompok sama krusialnya dengan kemampuan teknis (*hard skills*). Selama ini, pencatatan pelanggaran maupun capaian positif siswa seringkali menghadapi beberapa kelemahan fundamental:
- **Pencatatan Manual Konvensional**: Menggunakan buku catatan fisik yang rentan hilang, rusak, atau tercecer antar wali kelas dan guru BK.
- **Bias Subjektif & Penghakiman**: Catatan seringkali hanya berfokus pada pelanggaran (aspek negatif) tanpa mengapresiasi perilaku positif, serta minim ruang dialog dan klarifikasi.
- **Kompleksitas Perangkat Lunak Berlebih**: Sistem informasi berbasis web komersial umumnya membutuhkan instalasi web server eksternal berat (Apache/Nginx), basis data enterprise (MySQL/PostgreSQL), koneksi internet aktif, dan ratusan megabyte dependensi `npm`/`pip`, menyulitkan implementasi cepat di laboratorium sekolah yang berbasis lingkungan offline/lokal.

#### 2. Kebutuhan Sistem
Berdasarkan analisis tersebut, dirumuskan kebutuhan sistem perangkat lunak yang:
- **Mandiri & Ringan (*Zero External Dependencies*)**: Dapat dijalankan seketika di lingkungan Python standar (Spyder IDE maupun terminal bawaan OS) tanpa instalasi dependensi pihak ketiga (`pip`).
- **Penyimpanan Terstruktur & Terindeks**: Menggunakan basis data relasional lokal SQLite3 dengan integritas referensial antar entitas, penegakan foreign key, dan indeks kueri.
- **Validasi Ketat & Aman**: Memvalidasi setiap input pengguna secara defensif serta kebal terhadap celah injeksi SQL (*SQL Injection*).
- **Pengalaman Pengguna Modern (*Modern UI/UX*)**: Menyediakan antarmuka ganda: Terminal Technical Dashboard (TUI) dan Web Dashboard GUI (SPA) berbasis peramban modern (*Anti-AI Slop*, palet dark zinc-950, live search, drawer riwayat, dan ekspor JSON).

---

### 02 Rancang

Tahap perancangan menitikberatkan pada kesederhanaan arsitektur (*KISS principle*) dan ketangguhan struktur data (*robustness*).

#### 1. Perancangan Skema Basis Data Relasional & Indeks
Sistem memodelkan hubungan *One-to-Many* (Satu siswa dapat memiliki banyak catatan pembinaan perilaku).

1. **Tabel `siswa`**
   - `id_siswa` (`TEXT PRIMARY KEY`): Nomor Induk Siswa atau format identifikasi unik kelas (contoh: `XII-TKJ-01`). Memastikan tidak ada duplikasi data siswa.
   - `nama` (`TEXT NOT NULL`): Nama lengkap siswa.

2. **Tabel `catatan`**
   - `id_catatan` (`INTEGER PRIMARY KEY AUTOINCREMENT`): Kunci utama unik setiap insiden catatan.
   - `id_siswa` (`TEXT NOT NULL`): Kunci asing (*Foreign Key*) yang terhubung ke `siswa(id_siswa)`.
   - `tanggal` (`TEXT NOT NULL`): Tanggal pencatatan otomatis menggunakan standar ISO-8601 (`YYYY-MM-DD`).
   - `kategori` (`TEXT NOT NULL`): Dimensi karakter (Disiplin, Tanggung Jawab, Kepedulian, Kejujuran).
   - `deskripsi` (`TEXT NOT NULL`): Catatan fakta kejadian objektif.
   - `skor` (`INTEGER NOT NULL CHECK(skor IN (-1, 1))`): Nilai pembinaan yang dibatasi secara ketat hanya bernilai `-1` (evaluasi/pembinaan) atau `1` (apresiasi positif).
   - `tindak_lanjut` (`TEXT NOT NULL`): Rencana pendampingan atau langkah solutif yang disepakati.
   - *Relational Rule*: `FOREIGN KEY (id_siswa) REFERENCES siswa(id_siswa)` dengan penegakan wajib `PRAGMA foreign_keys = ON;`.

3. **Optimasi Indeks Kueri**
   - `CREATE INDEX IF NOT EXISTS idx_catatan_id_siswa ON catatan(id_siswa);`
   - `CREATE INDEX IF NOT EXISTS idx_catatan_tanggal ON catatan(tanggal);`

#### 2. Perancangan Arsitektur Multi-Antarmuka Terpadu
1. **Desktop Native GUI (`gui_app.py`)**:
   - Berbasis pustaka grafis bawaan Python (`tkinter` & `ttk`).
   - Tampilan tema dark zinc profesional, kartu metrik KPI, dual-pane layout, real-time search, dan dialog pop-up validasi.
2. **Web Dashboard GUI SPA (`server_web.py`)**:
   - Digerakkan oleh server HTTP bawaan Python (`http.server` & `socketserver`).
   - Frontend modern bergaya Linear/Vercel: Dark mode zinc-950, Lucide icons, live search siswa, drawer riwayat terurut, analitik distribusi kategori, modal form validasi instan, ekspor data JSON resmi, dan layout cetak resmi ber-kop surat.
3. **Terminal Technical Dashboard (`monitoring_akhlak.py`)**:
   - Navigasi menu interaktif dengan pewarnaan ANSI 256 dan pembingkaian box-drawing Unicode.
   - Fitur ikhtisar analitik global dan seeder simulasi 10 siswa TKJ.
4. **Unified Interactive Launcher (`main.py`)**:
   - Titik masuk operasional tunggal yang menyajikan seleksi mode aplikasi saat pertama kali dimulai.

---

### 03 Bangun

Aplikasi dikonstruksi ke dalam arsitektur modular Python murni:
1. `main.py`: Launcher interaktif terpadu dan router argumen baris perintah (`--gui`, `--web`, `--cli`, `--seed`, `--test`).
2. `gui_app.py`: Aplikasi Desktop GUI native berbasis Tkinter dengan antarmuka dual-pane dan visualisasi metrik.
3. `server_web.py`: Server Web GUI SPA dan RESTful API handler berbasis pustaka standar (`http.server`).
4. `monitoring_akhlak.py`: Modul inti SQLite, logika bisnis, analitik global, seeder data simulasi, dan CLI Technical Dashboard.
5. `uji_skenario.py`: Skrip pengujian otomatis 6 skenario wajib.

#### 1. Implementasi Keamanan & Integritas Data
- **Parameterized Queries**: Seluruh pernyataan SQL (`INSERT`, `SELECT`) menggunakan placeholder tanda tanya (`?`) dan *tuple* parameter untuk mengeliminasi risiko *SQL Injection*.
- **Database Context Manager**: Menggunakan `with koneksi_db() as conn:` untuk menjamin transaksi berjalan secara atomik (*commit* otomatis saat sukses, dan *rollback* aman jika terjadi galat).
- **Defensive Input Validation**:
  - Pengecekan tipe dan pembersihan spasi menggunakan `.strip()`.
  - Pengecekan string kosong pada seluruh parameter wajib.
  - Validasi tipe ketat untuk `skor` dengan memastikan `type(skor) is int and skor in (-1, 1)`.
- **Penanganan Kesalahan Terpusat**: Loop utama dibungkus dalam blok penanganan `try...except (ValueError, sqlite3.IntegrityError) as err:` dengan pesan ramah: `"Data belum tersimpan: <pesan error>"`.

---

### 04 Verifikasi & Hasil Pengujian

Pengujian dilakukan menggunakan skrip uji otomatis `uji_skenario.py` yang mencakup 6 skenario kritis. Seluruh data yang diuji adalah 100% data fiktif.

#### 1. Tabel Matriks Hasil Pengujian 6 Skenario

| No | Skenario Pengujian | Input yang Diuji | Ekspektasi Sistem | Hasil Aktual | Status |
|:--:|:---|:---|:---|:---|:---:|
| 1 | **Tambah Siswa Valid** | ID: `XII-TKJ-01`<br>Nama: `Siswa Simulasi Satu` | Data berhasil disimpan, jumlah baris bertambah 1 | Data tersimpan, `COUNT(*)` = 1 | **LULUS** |
| 2 | **ID Siswa Duplikat** | ID: `XII-TKJ-01` (diulang)<br>Nama: `Nama Duplikat Siswa` | Menolak penyimpanan, memicu `sqlite3.IntegrityError`, baris tidak bertambah | Ditolak `UNIQUE constraint failed: siswa.id_siswa`, baris tetap 1 | **LULUS** |
| 3 | **Input Deskripsi Kosong** | ID: `XII-TKJ-01`<br>Deskripsi: `""` | Menolak penyimpanan, memicu `ValueError`, tidak ada catatan bertambah | Ditolak `ValueError`, tabel catatan tetap 0 baris | **LULUS** |
| 4 | **Skor Tidak Sah** | ID: `XII-TKJ-01`<br>Skor: `0` (bukan -1 atau 1) | Menolak penyimpanan, memicu `ValueError` | Ditolak `ValueError: Skor harus -1 atau 1` | **LULUS** |
| 5 | **Riwayat & Ringkasan** | 2 Catatan berturut-turut:<br>1. Skor `-1` (Disiplin)<br>2. Skor `+1` (Kepedulian) | `ringkasan()` = `(2, 0)`. `lihat_riwayat()` menampilkan 2 baris terurut dari yang terbaru | Output `(2, 0)`, urutan riwayat menampilkan Kepedulian terlebih dahulu, lalu Disiplin | **LULUS** |
| 6 | **ID Siswa Belum Terdaftar** | ID: `XII-TKJ-99` (belum ada di tabel `siswa`) | Ditolak oleh `sqlite3.IntegrityError` karena pelanggaran relasi Foreign Key | Ditolak `FOREIGN KEY constraint failed`, data yatim dicegah | **LULUS** |

#### 2. Log Keluaran Konsol Pengujian Otomatis Asli (Verbatim Execution Output)

```text
########################################################################
  MEMULAI PENGUJIAN OTOMATIS SISTEM MONITORING AKHLAK SISWA
  Data: 100% Fiktif & Simulative | Engine: SQLite3 with Foreign Keys
########################################################################

========================================================================
SKENARIO 1: TAMBAH SISWA VALID
------------------------------------------------------------------------
[STATUS: LULUS] Berhasil menyimpan siswa 'Siswa Simulasi Satu' [XII-TKJ-01].
Bukti Database: Ditemukan 1 baris di tabel 'siswa'.
========================================================================
SKENARIO 2: ID DUPLIKAT (PRIMARY KEY CHECK)
------------------------------------------------------------------------
Mencoba menyimpan kembali siswa dengan ID yang sama: 'XII-TKJ-01'...
[STATUS: LULUS] Ditolak oleh sqlite3.IntegrityError: 'UNIQUE constraint failed: siswa.id_siswa'.
Bukti Database: Jumlah siswa ID 'XII-TKJ-01' tetap 1 baris.
========================================================================
SKENARIO 3: INPUT KOSONG (VALIDATION CHECK)
------------------------------------------------------------------------
Mencoba menambah catatan pembinaan dengan deskripsi kosong ''...
[STATUS: LULUS] Ditolak oleh ValueError: 'ID siswa, kategori, deskripsi, dan tindak lanjut wajib diisi'.
Bukti Database: Tabel 'catatan' tetap kosong (0 baris).
========================================================================
SKENARIO 4: SKOR TIDAK SAH (NILAI SELAIN -1 ATAU 1)
------------------------------------------------------------------------
Mencoba menambah catatan dengan nilai skor 0 (harus -1 atau 1)...
[STATUS: LULUS] Ditolak oleh ValueError: 'Skor harus -1 atau 1'.
========================================================================
SKENARIO 5: RIWAYAT & RINGKASAN (AGREGASI & SORTING)
------------------------------------------------------------------------
Menambahkan Catatan 1 (Skor -1: Terlambat sesi briefing)...
Menambahkan Catatan 2 (Skor +1: Merapikan lab jaringan)...
Output ringkasan(id_siswa): (2, 0)
[STATUS: LULUS] Ringkasan tepat: (2, 0) (2 catatan, skor netral 0).
Daftar Riwayat Terurut (Terbaru ke Terlama):
  1. Tanggal: 2026-11-05 | Kategori: Kepedulian | Skor: 1 | Deskripsi: Inisiatif merapikan kabel patch cord lab | Tindak Lanjut: Apresiasi tertulis pada portofolio
  2. Tanggal: 2026-11-05 | Kategori: Disiplin | Skor: -1 | Deskripsi: Terlambat sesi briefing 10 menit | Tindak Lanjut: Diskusi refleksi kedisiplinan waktu
========================================================================
SKENARIO 6: ID SISWA BELUM ADA (FOREIGN KEY CHECK)
------------------------------------------------------------------------
Mencoba mencatat perilaku untuk ID siswa belum terdaftar: 'XII-TKJ-99'...
[STATUS: LULUS] Ditolak oleh sqlite3.IntegrityError: 'FOREIGN KEY constraint failed'.
Keterangan: Foreign Key constraint bekerja sempurna mencegah data yatim (orphaned records).

========================================================================
NO   | SKENARIO UJI              | STATUS     | CATATAN / OUTPUT
------------------------------------------------------------------------
1    | Tambah Siswa Valid        | LULUS      | Tersimpan 1 baris valid
2    | ID Duplikat               | LULUS      | Ditolak IntegrityError (UNIQUE constraint failed: siswa.id_siswa)
3    | Input Kosong              | LULUS      | Ditolak ValueError (ID siswa, kategori, deskripsi, dan tindak lanjut wajib diisi)
4    | Skor Tidak Sah            | LULUS      | Ditolak ValueError (Skor harus -1 atau 1)
5    | Riwayat & Ringkasan       | LULUS      | Output (2, 0) terurut benar
6    | Foreign Key Check         | LULUS      | Ditolak IntegrityError (FOREIGN KEY constraint failed)
========================================================================
TOTAL: 6 / 6 Skenario LULUS (100%).
Kebersihan Lingkungan: Database simulasi berhasil dibersihkan.
========================================================================
```

---

### 05 Evaluasi

#### 1. Keunggulan Arsitektur
- **Portabilitas Sempurna Tanpa Setup Rumit**: Berjalan di sistem operasi apa pun hanya dengan Python 3 murni tanpa ketergantungan paket luar.
- **Integritas Basis Data Kuat & Terindeks**: Penegakan `PRAGMA foreign_keys = ON`, `CHECK constraint`, dan indeks SQLite menjamin konsistensi data dan kecepatan kueri.
- **Fleksibilitas Antarmuka**: Pengguna dapat memilih antarmuka terminal technical minimalist maupun antarmuka web GUI responsif berstandar modern.

#### 2. Keterbatasan & Peluang Pengembangan
- **Lingkungan Single-User**: Pada model lokal, aplikasi dirancang untuk penggunaan satu operator pada satu workstation.
- **Ketiadaan Autentikasi Pengguna**: Belum ada pemisahan kredensial login antara peran Guru BK, Wali Kelas, dan Siswa.
- **Rekomendasi Skalabilitas**: Untuk penerapan tingkat sekolah menyeluruh, arsitektur dapat ditingkatkan menjadi sistem multi-user dengan autentikasi berbasis token JWT dan enkripsi database tingkat lanjut (SQLCipher).

---

## BAB II: ETIKA DAN PRIVASI DATA SISWA

Pencatatan perilaku dan karakter siswa menyangkut privasi dan masa depan peserta didik. Oleh karena itu, sistem ini menetapkan protokol etika data yang ketat:

1. **Penggunaan Data Fiktif (*Synthetic Data Principle*)**:
   Seluruh data dalam pengembangan, pengujian unit, demonstrasi kelas, maupun pengujian otomatis diwajibkan 100% menggunakan identitas fiktif (misal: `XII-TKJ-01` dengan nama `Ahmad Fauzi`). Dilarang keras menggunakan nama atau NIS nyata siswa sekolah.
2. **Larangan Unggah Data Nyata ke Repositori Publik**:
   Repositori publik di platform seperti GitHub HANYA boleh berisi kode program, skema pengujian, dan dokumentasi. File basis data lokal (`*.db`, `*.sqlite3`) serta file kredensial/lingkungan (`.env`) wajib diblokir secara permanen melalui file konfigurasi `.gitignore`.
3. **Prinsip Pembatasan Hak Akses (*Principle of Least Privilege*)**:
   Data catatan pembinaan hanya boleh diakses oleh pihak yang berwenang langsung dalam proses pedagogis (Wali Kelas, Guru Bimbingan Konseling / BK, dan Kepala Program Kejuruan). Siswa hanya berhak melihat riwayat miliknya sendiri melalui sesi konseling transparan.
4. **Masa Simpan Data (*Data Retention & Purging Lifecycle*)**:
   Catatan pembinaan perilaku bersifat dinamis dan bertujuan mendidik. Catatan evaluasi tidak boleh disimpan selamanya yang berpotensi menjadi stigma permanen bagi siswa. Setelah siswa menyelesaikan masa studi (lulus dari SMK Alhadiid), data catatan perilaku wajib diarsipkan secara terenkripsi atau dihapus secara aman (*secure wiping*).

---

## BAB III: JAWABAN KOMPREHENSIF PERTANYAAN REFLEKSI

### 1. Bagian mana dari aplikasi yang paling membantu proses pembinaan? Mengapa?
**Jawaban Analitis:**
Bagian yang paling esensial dalam membantu proses pembinaan bukanlah skor agregat, melainkan **kolom `deskripsi` yang faktual dan kolom `tindak_lanjut`**. 

*Alasan Pedagogis & Teknis:*
- Angka skor (misalnya total skor `0` atau `-1`) hanyalah indikator komputasional yang tidak memiliki makna pembinaan tanpa konteks.
- Kolom `deskripsi` yang ditulis secara objektif memberikan kejelasan peristiwa riil tanpa distorsi opini.
- Kolom `tindak_lanjut` mengubah sistem dari sekadar "alat penghukum" menjadi "alat resolusi masalah". Guru dan siswa tidak berfokus pada kesalahan masa lalu, melainkan menyepakati tindakan perbaikan konkret (misalnya pendampingan praktikum jaringan, konseling manajemen waktu, atau tugas restoratif positif). Inilah esensi utama dari *restorative justice* di lingkungan pendidikan.

---

### 2. Bagaimana memastikan catatan bersifat faktual, adil, dan memberi ruang klarifikasi?
**Jawaban Analitis:**
Untuk memastikan catatan adil dan objektif, sistem menerapkan 3 pilar operasional:
1. **Standar Penulisan Berbasis Fakta Observasi (*Observable Behavior*)**:
   Deskripsi hanya mencatat apa yang dilihat, didengar, atau diukur secara langsung. Contoh yang faktual: *"Terlambat hadir pada sesi pengkabelan lab selama 15 menit"* (fakta). Hindari catatan subjektif seperti: *"Siswa malas dan tidak menghargai pelajaran"* (opini/labeling).
2. **Prinsip Tabulasi Dua Sisi**:
   Sistem mencakup kategori apresiasi bernilai positif (`+1`), bukan hanya pelanggaran (`-1`). Hal ini menuntut pendidik untuk aktif melihat kebaikan dan kontribusi siswa, menciptakan rekam jejak yang adil dan seimbang.
3. **Mekanisme Ruang Klarifikasi & Verifikasi**:
   Sebelum data disimpan secara permanen ke basis data, proses bisnis mewajibkan guru melakukan konfirmasi langsung dengan siswa yang bersangkutan. Kolom `tindak_lanjut` mendokumentasikan hasil kesepakatan dua arah antara guru dan siswa, sehingga siswa merasa didengar dan diperlakukan secara terhormat.

---

### 3. Apa risiko jika skor dipakai sebagai satu-satunya dasar penilaian siswa?
**Jawaban Analitis:**
Menggunakan skor sebagai satu-satunya tolok ukur evaluasi akhlak siswa menghadirkan risiko fatal, baik secara psikologis maupun metodologis:
1. **Reduksionisme Karakter & Pelabelan Moral (*Moral Stigmatization*)**:
   Karakter manusia adalah dinamika multidimensi yang dipengaruhi latar belakang keluarga, kondisi ekonomi, dan tekanan emosional. Mereduksi akhlak menjadi sekadar angka tunggal (misal: "siswa bernilai -5") akan melahirkan stigma negatif yang menghancurkan kepercayaan diri siswa.
2. **Hukum Goodhart (*Goodhart's Law*)**:
   *"Ketika sebuah ukuran dijadikan sebagai target tunggal, ukuran tersebut berhenti menjadi ukuran yang baik."* Jika skor menjadi penentu mutlak, siswa akan bertindak manipulatif atau berpura-pura baik hanya demi mengejar akumulasi skor positif di depan guru, bukan karena kesadaran moral intrinsik.
3. **Pengabaian Konteks Situasional**:
   Siswa yang terlambat karena harus merawat orang tua yang sakit akan mendapatkan skor `-1` yang setara dengan siswa yang terlambat karena begadang bermain game. Tanpa analisis kualitatif terhadap konteks, sistem skor tunggal menjadi instrumen yang tidak adil dan tidak manusiawi.

---

### 4. Bagaimana menjaga database lokal agar tidak dibuka atau tersebar tanpa izin?
**Jawaban Analitis:**
Keamanan basis data lokal (`monitoring_akhlak.db`) harus dilindungi melalui pendekatan pertahanan berlapis (*Defense-in-Depth*):
1. **Proteksi Hak Akses Berkas Sistem Operasi (*File Permissions*)**:
   Pada sistem operasi Linux/UNIX, hak akses berkas basis data harus dibatasi secara ketat sehingga hanya akun pengguna pemilik (*owner*) yang dapat membaca dan menulis:
   ```bash
   chmod 600 monitoring_akhlak.db
   ```
2. **Penyaringan Repositori Git (`.gitignore`)**:
   Menjaga agar berkas basis data tidak pernah terunggah ke repositori publik dengan mencantumkan pola `*.db` dan `*.sqlite3` pada berkas `.gitignore`.
3. **Enkripsi Penyimpanan (*Storage Encryption*)**:
   Memanfaatkan enkripsi tingkat volume/disk (seperti BitLocker di Windows atau LUKS di Linux) pada perangkat komputer yang menyimpan database. Untuk keamanan tingkat basis data, pustaka dapat ditingkatkan menggunakan modul **SQLCipher** guna mengenkripsi seluruh isi file SQLite dengan algoritma AES-256.
4. **Isolasi Workstation & Penjadwalan Backup Terenkripsi**:
   Komputer yang digunakan untuk pengoperasian sistem harus memiliki penguncian layar otomatis (*auto lock screen*) dan salinan cadangan (*backup*) berkala yang disimpan dalam media terenkripsi di luar perangkat utama.

---

### 5. Fitur atau perbaikan apa yang paling penting sebelum aplikasi dipakai di luar simulasi kelas?
**Jawaban Analitis:**
Sebelum aplikasi ini diimplementasikan pada skala produksi di luar laboratorium kelas, terdapat 4 perbaikan kritis yang wajib dibangun:
1. **Sistem Autentikasi & Otorisasi Berbasis Peran (*Role-Based Access Control / RBAC*)**:
   Menyediakan gerbang login terautentikasi dengan peran spesifik:
   - *Guru Mata Pelajaran/Wali Kelas*: Hanya dapat menginput catatan dan melihat kelas bimbingannya.
   - *Guru Bimbingan Konseling (BK)*: Memiliki wewenang analisis mendalam dan tindak lanjut psikologis.
   - *Siswa*: Hanya memiliki akses baca (*read-only*) untuk riwayat catatan pribadinya sendiri.
2. **Jejak Audit Mutlak (*Audit Trail / Immutable History*)**:
   Menambahkan tabel log sistem yang mencatat identitas pencatat, waktu pencatatan (*timestamp*), serta riwayat pengubahan (*edit history*) untuk mencegah manipulasi catatan secara sepihak.
3. **Transformasi Menjadi Arsitektur Klien-Server / Web Terpusat**:
   Mengemas fungsi logika menjadi RESTful API terpusat sehingga database tidak tersebar di banyak PC laboratorium, melainkan tersimpan di server sekolah yang terkelola secara aman dan terpadu.
4. **Fitur Ekspor & Notifikasi Terpadu**:
   Menyediakan fungsi ekspor laporan bimbingan ke format dokumen resmi (.pdf/.xlsx) serta sistem pemberitahuan berkala kepada orang tua/wali murid sebagai wujud transparansi dan kolaborasi pendidikan antara sekolah dan keluarga.

---
*Dokumen ini disusun sebagai wujud dedikasi rekayasa perangkat lunak berstandar profesional untuk modul kejuruan Kelas XII TKJ - SMK Alhadiid.*
