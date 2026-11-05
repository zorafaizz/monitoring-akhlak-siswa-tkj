"""
Web Dashboard GUI & REST API Server
Sistem Monitoring Akhlak Siswa (Kelas XII TKJ - SMK Alhadiid)
Dibangun murni dengan pustaka standar Python: http.server, json, urllib, sqlite3.
Zero External Dependencies.
"""

import http.server
import json
import os
import socketserver
import sqlite3
import sys
import urllib.parse

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

HTML_PAGE = """<!DOCTYPE html>
<html lang="id" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Monitoring Akhlak Siswa | XII TKJ - SMK Alhadiid</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: '#3b82f6',
            zinc: {
              950: '#09090b',
              900: '#121215',
              850: '#18181b',
              800: '#27272a',
              700: '#3f3f46',
            }
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #09090b; }
    ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #3f3f46; }
  </style>
</head>
<body class="bg-zinc-950 text-zinc-100 min-h-screen flex flex-col antialiased selection:bg-zinc-800 selection:text-zinc-200">

  <!-- TOP NAVIGATION BAR -->
  <header class="border-b border-zinc-800/80 bg-zinc-950/70 backdrop-blur sticky top-0 z-30">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="h-9 w-9 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-blue-400 font-bold text-sm tracking-wider shadow-inner">
          <i data-lucide="shield-check" class="w-5 h-5 text-blue-400"></i>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-sm font-semibold tracking-tight text-white">Sistem Monitoring Akhlak</span>
            <span class="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">XII TKJ</span>
          </div>
          <p class="text-xs text-zinc-400 font-medium">SMK Alhadiid • Lab Jaringan Komputer</p>
        </div>
      </div>
      <div class="flex items-center gap-2.5">
        <button onclick="suntikSeeder()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-xs font-medium text-zinc-300 hover:text-white transition">
          <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-400"></i>
          <span>Seed 10 Siswa</span>
        </button>
        <button onclick="bukaModalSiswa()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-xs font-medium text-zinc-300 hover:text-white transition">
          <i data-lucide="user-plus" class="w-3.5 h-3.5 text-zinc-400"></i>
          <span>Tambah Siswa</span>
        </button>
        <button onclick="bukaModalCatatan()" class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-md bg-blue-600 hover:bg-blue-500 text-xs font-medium text-white transition shadow-sm">
          <i data-lucide="plus-circle" class="w-3.5 h-3.5"></i>
          <span>Catat Pembinaan</span>
        </button>
      </div>
    </div>
  </header>

  <!-- MAIN CONTAINER -->
  <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    
    <!-- BANNER PANDUAN PEMBINAAN POSITIF -->
    <div class="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div class="flex items-start gap-3">
        <div class="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 mt-0.5">
          <i data-lucide="compass" class="w-4 h-4"></i>
        </div>
        <div>
          <h2 class="text-xs font-semibold text-zinc-200 tracking-wide uppercase">Prinsip Pendampingan Karakter</h2>
          <p class="text-xs text-zinc-400 mt-0.5 leading-relaxed">
            Deskripsi wajib mencatat fakta yang teramati secara objektif. Skor <span class="text-emerald-400 font-mono">+1</span> dan <span class="text-rose-400 font-mono">-1</span> merupakan indikator tren bimbingan, bukan vonis mutlak karakter atau penentu tunggal nilai akademik.
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2 shrink-0">
        <a href="/api/export" target="_blank" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-xs font-medium text-zinc-400 hover:text-zinc-200 transition">
          <i data-lucide="download" class="w-3.5 h-3.5"></i>
          <span>Ekspor JSON</span>
        </a>
      </div>
    </div>

    <!-- METRIC CARDS -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4" id="statsGrid">
      <div class="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 relative overflow-hidden">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-zinc-400">Total Siswa Terdata</span>
          <i data-lucide="users" class="w-4 h-4 text-zinc-500"></i>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
          <span class="text-2xl font-bold tracking-tight text-white" id="statTotalSiswa">-</span>
          <span class="text-xs text-zinc-500">Kelas XII TKJ</span>
        </div>
      </div>

      <div class="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 relative overflow-hidden">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-zinc-400">Total Catatan Pembinaan</span>
          <i data-lucide="clipboard-list" class="w-4 h-4 text-zinc-500"></i>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
          <span class="text-2xl font-bold tracking-tight text-white" id="statTotalCatatan">-</span>
          <span class="text-xs text-zinc-500">Insiden & Apresiasi</span>
        </div>
      </div>

      <div class="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 relative overflow-hidden">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-zinc-400">Apresiasi Positif (+1)</span>
          <i data-lucide="heart-handshake" class="w-4 h-4 text-emerald-400"></i>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
          <span class="text-2xl font-bold tracking-tight text-emerald-400" id="statApresiasi">-</span>
          <span class="text-xs text-zinc-500">Capaian Baik</span>
        </div>
      </div>

      <div class="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 relative overflow-hidden">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-zinc-400">Evaluasi Pembinaan (-1)</span>
          <i data-lucide="alert-circle" class="w-4 h-4 text-rose-400"></i>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
          <span class="text-2xl font-bold tracking-tight text-rose-400" id="statEvaluasi">-</span>
          <span class="text-xs text-zinc-500">Pendampingan</span>
        </div>
      </div>
    </div>

    <!-- MAIN CONTENT: TABLE & SEARCH -->
    <div class="rounded-xl border border-zinc-800/80 bg-zinc-900/30 overflow-hidden shadow-sm">
      <div class="p-4 border-b border-zinc-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 bg-zinc-900/40">
        <div class="flex items-center gap-2 w-full sm:w-auto">
          <h2 class="text-sm font-semibold text-white">Daftar Siswa & Profil Pembinaan</h2>
          <span id="badgeJumlahSiswa" class="text-xs px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 border border-zinc-700/60 font-mono">0 siswa</span>
        </div>
        <div class="w-full sm:w-72 relative">
          <i data-lucide="search" class="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none"></i>
          <input 
            type="text" 
            id="searchInput" 
            onkeyup="filterSiswa()" 
            placeholder="Cari ID atau nama siswa..." 
            class="w-full pl-9 pr-3 py-1.5 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 placeholder-zinc-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition"
          />
        </div>
      </div>

      <!-- TABLE -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse text-xs">
          <thead>
            <tr class="border-b border-zinc-800/80 bg-zinc-950/40 text-zinc-400 uppercase tracking-wider font-medium text-[11px]">
              <th class="py-3 px-4 font-mono">ID Siswa</th>
              <th class="py-3 px-4">Nama Siswa</th>
              <th class="py-3 px-4 text-center">Jumlah Catatan</th>
              <th class="py-3 px-4 text-center">Skor Akumulasi</th>
              <th class="py-3 px-4 text-center">Status Pembinaan</th>
              <th class="py-3 px-4 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody id="studentTableBody" class="divide-y divide-zinc-800/50 text-zinc-300">
            <tr>
              <td colspan="6" class="py-12 text-center text-zinc-500">Memuat data siswa...</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </main>

  <!-- MODAL DETAIL RIWAYAT SISWA (DRAWER) -->
  <div id="modalRiwayat" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-center justify-center p-4">
    <div class="bg-zinc-900 border border-zinc-800 rounded-2xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
      <div class="p-5 border-b border-zinc-800 flex items-center justify-between bg-zinc-950/50">
        <div>
          <div class="flex items-center gap-2">
            <span id="modalSiswaId" class="text-xs font-mono font-semibold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">XII-TKJ-01</span>
            <h3 id="modalSiswaNama" class="text-base font-bold text-white">Nama Siswa</h3>
          </div>
          <p id="modalRingkasanBadge" class="text-xs text-zinc-400 mt-1">Jumlah Catatan: 0 | Skor: 0</p>
        </div>
        <button onclick="tutupModalRiwayat()" class="p-1 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <div class="p-5 overflow-y-auto space-y-3 flex-1" id="timelineRiwayat">
        <!-- Riwayat akan di-render di sini -->
      </div>

      <div class="p-4 border-t border-zinc-800 bg-zinc-950/40 flex items-center justify-between">
        <span class="text-[11px] text-zinc-500">Urutan terurut: Tanggal Terbaru ke Terlama</span>
        <button onclick="tutupModalRiwayat()" class="px-4 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-xs font-medium text-zinc-200 transition">
          Tutup
        </button>
      </div>
    </div>
  </div>

  <!-- MODAL TAMBAH SISWA -->
  <div id="modalSiswa" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-center justify-center p-4">
    <div class="bg-zinc-900 border border-zinc-800 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-white flex items-center gap-2">
          <i data-lucide="user-plus" class="w-4 h-4 text-blue-400"></i>
          <span>Tambah Siswa Baru</span>
        </h3>
        <button onclick="tutupModalSiswa()" class="text-zinc-500 hover:text-zinc-300">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>
      <form id="formTambahSiswa" onsubmit="simpanSiswa(event)" class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-zinc-400 mb-1">ID Siswa (Unik)</label>
          <input type="text" id="inputSiswaId" required placeholder="Contoh: XII-TKJ-11" class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono" />
        </div>
        <div>
          <label class="block text-xs font-medium text-zinc-400 mb-1">Nama Lengkap Siswa</label>
          <input type="text" id="inputSiswaNama" required placeholder="Contoh: Muhammad Faiz" class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500" />
        </div>
        <div class="pt-2 flex justify-end gap-2">
          <button type="button" onclick="tutupModalSiswa()" class="px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-xs text-zinc-400">Batal</button>
          <button type="submit" class="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-medium text-white transition">Simpan Siswa</button>
        </div>
      </form>
    </div>
  </div>

  <!-- MODAL TAMBAH CATATAN PEMBINAAN -->
  <div id="modalCatatan" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-center justify-center p-4">
    <div class="bg-zinc-900 border border-zinc-800 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-white flex items-center gap-2">
          <i data-lucide="file-plus" class="w-4 h-4 text-blue-400"></i>
          <span>Catat Pembinaan Perilaku</span>
        </h3>
        <button onclick="tutupModalCatatan()" class="text-zinc-500 hover:text-zinc-300">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>
      <form id="formTambahCatatan" onsubmit="simpanCatatan(event)" class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-zinc-400 mb-1">Pilih Siswa</label>
          <select id="inputCatatanSiswaId" required class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500 font-mono">
            <!-- Pilihan siswa akan dimuat dinamis -->
          </select>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Kategori Perilaku</label>
            <select id="inputCatatanKategori" required class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500">
              <option value="Disiplin">Disiplin</option>
              <option value="Tanggung Jawab">Tanggung Jawab</option>
              <option value="Kepedulian">Kepedulian</option>
              <option value="Kejujuran">Kejujuran</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Indikator Skor</label>
            <select id="inputCatatanSkor" required class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500">
              <option value="1">+1 (Apresiasi Capaian Positif)</option>
              <option value="-1">-1 (Evaluasi Pembinaan Perilaku)</option>
            </select>
          </div>
        </div>
        <div>
          <label class="block text-xs font-medium text-zinc-400 mb-1">Deskripsi Faktual (Observasi Riil)</label>
          <textarea id="inputCatatanDeskripsi" required rows="2" placeholder="Catat tindakan konkret yang diamati (bahasa objektif & netral)..." class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500"></textarea>
        </div>
        <div>
          <label class="block text-xs font-medium text-zinc-400 mb-1">Rencana Tindak Lanjut & Ruang Klarifikasi</label>
          <input type="text" id="inputCatatanTindakLanjut" required placeholder="Langkah perbaikan/apresiasi yang disepakati bersama siswa..." class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:ring-1 focus:ring-blue-500" />
        </div>
        <div class="pt-2 flex justify-end gap-2">
          <button type="button" onclick="tutupModalCatatan()" class="px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-xs text-zinc-400">Batal</button>
          <button type="submit" class="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-medium text-white transition">Simpan Catatan</button>
        </div>
      </form>
    </div>
  </div>

  <!-- TOAST NOTIFICATION -->
  <div id="toast" class="fixed bottom-5 right-5 z-50 transform translate-y-20 opacity-0 transition-all duration-300 pointer-events-none px-4 py-2.5 rounded-lg shadow-xl border text-xs font-medium flex items-center gap-2"></div>

  <!-- JAVASCRIPT LOGIC -->
  <script>
    let semuaSiswa = [];

    async function loadData() {
      try {
        const [resStats, resStudents] = await Promise.all([
          fetch('/api/stats').then(r => r.json()),
          fetch('/api/students').then(r => r.json())
        ]);

        document.getElementById('statTotalSiswa').innerText = resStats.total_siswa;
        document.getElementById('statTotalCatatan').innerText = resStats.total_catatan;
        document.getElementById('statApresiasi').innerText = '+' + resStats.total_apresiasi;
        document.getElementById('statEvaluasi').innerText = resStats.total_evaluasi;

        semuaSiswa = resStudents;
        document.getElementById('badgeJumlahSiswa').innerText = `${semuaSiswa.length} siswa`;
        renderTable(semuaSiswa);
        updateSelectSiswa(semuaSiswa);
      } catch (err) {
        showToast('Gagal memuat data dari server: ' + err, 'error');
      }
    }

    function renderTable(data) {
      const tbody = document.getElementById('studentTableBody');
      if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="py-12 text-center text-zinc-500">Belum ada siswa terdata. Klik tombol "Seed 10 Siswa" di kanan atas.</td></tr>`;
        return;
      }

      tbody.innerHTML = data.map(s => {
        const [id, nama, jml, skor] = s;
        let skorBadge = '';
        let statusBadge = '';

        if (skor > 0) {
          skorBadge = `<span class="font-mono text-emerald-400 font-semibold">+${skor}</span>`;
          statusBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Teladan Aktif</span>`;
        } else if (skor < 0) {
          skorBadge = `<span class="font-mono text-rose-400 font-semibold">${skor}</span>`;
          statusBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">Dalam Pembinaan</span>`;
        } else {
          skorBadge = `<span class="font-mono text-zinc-400">0</span>`;
          statusBadge = `<span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-zinc-800 text-zinc-400 border border-zinc-700">Stabil / Netral</span>`;
        }

        return `
          <tr class="hover:bg-zinc-900/60 transition group">
            <td class="py-3 px-4 font-mono text-blue-400">${id}</td>
            <td class="py-3 px-4 font-medium text-white">${nama}</td>
            <td class="py-3 px-4 text-center font-mono text-zinc-400">${jml}</td>
            <td class="py-3 px-4 text-center">${skorBadge}</td>
            <td class="py-3 px-4 text-center">${statusBadge}</td>
            <td class="py-3 px-4 text-right">
              <button onclick="bukaRiwayat('${id}', '${nama}')" class="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition">
                <span>Riwayat</span>
                <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
              </button>
            </td>
          </tr>
        `;
      }).join('');

      lucide.createIcons();
    }

    function filterSiswa() {
      const q = document.getElementById('searchInput').value.toLowerCase();
      const filtered = semuaSiswa.filter(s => s[0].toLowerCase().includes(q) || s[1].toLowerCase().includes(q));
      renderTable(filtered);
    }

    function updateSelectSiswa(data) {
      const sel = document.getElementById('inputCatatanSiswaId');
      sel.innerHTML = data.map(s => `<option value="${s[0]}">${s[0]} — ${s[1]}</option>`).join('');
    }

    async function bukaRiwayat(id, nama) {
      document.getElementById('modalSiswaId').innerText = id;
      document.getElementById('modalSiswaNama').innerText = nama;
      const timeline = document.getElementById('timelineRiwayat');
      timeline.innerHTML = `<div class="py-8 text-center text-zinc-500">Mengambil catatan pembinaan...</div>`;
      document.getElementById('modalRiwayat').classList.remove('hidden');
      document.getElementById('modalRiwayat').classList.add('flex');

      try {
        const res = await fetch(`/api/students/${id}/records`).then(r => r.json());
        document.getElementById('modalRingkasanBadge').innerText = `Jumlah Catatan: ${res.total_catatan} | Skor Netral: ${res.total_skor > 0 ? '+' : ''}${res.total_skor}`;

        if (!res.records || res.records.length === 0) {
          timeline.innerHTML = `<div class="p-6 rounded-xl border border-zinc-800 bg-zinc-950/40 text-center text-zinc-500 text-xs">Belum ada catatan pembinaan yang tersimpan untuk siswa ini.</div>`;
        } else {
          timeline.innerHTML = res.records.map(r => {
            const [tgl, kat, desk, skor, tindak] = r;
            const isPos = skor > 0;
            return `
              <div class="p-3.5 rounded-xl border ${isPos ? 'border-emerald-500/20 bg-emerald-950/10' : 'border-rose-500/20 bg-rose-950/10'} space-y-2">
                <div class="flex items-center justify-between text-xs">
                  <div class="flex items-center gap-2">
                    <span class="px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${isPos ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">${kat}</span>
                    <span class="text-zinc-500 font-mono text-[11px]">${tgl}</span>
                  </div>
                  <span class="font-mono font-bold text-xs ${isPos ? 'text-emerald-400' : 'text-rose-400'}">${isPos ? '+1 Apresiasi' : '-1 Evaluasi'}</span>
                </div>
                <p class="text-xs text-zinc-200 leading-relaxed font-normal">${desk}</p>
                <div class="pt-1.5 border-t border-zinc-800/60 flex items-start gap-1.5 text-[11px] text-zinc-400">
                  <i data-lucide="arrow-right-circle" class="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5"></i>
                  <span><strong class="text-zinc-300">Tindak Lanjut:</strong> ${tindak}</span>
                </div>
              </div>
            `;
          }).join('');
        }
        lucide.createIcons();
      } catch (err) {
        timeline.innerHTML = `<div class="text-red-400 text-xs">Gagal mengambil riwayat: ${err}</div>`;
      }
    }

    function tutupModalRiwayat() {
      document.getElementById('modalRiwayat').classList.add('hidden');
      document.getElementById('modalRiwayat').classList.remove('flex');
    }

    function bukaModalSiswa() {
      document.getElementById('modalSiswa').classList.remove('hidden');
      document.getElementById('modalSiswa').classList.add('flex');
    }
    function tutupModalSiswa() {
      document.getElementById('modalSiswa').classList.add('hidden');
      document.getElementById('modalSiswa').classList.remove('flex');
    }

    function bukaModalCatatan() {
      document.getElementById('modalCatatan').classList.remove('hidden');
      document.getElementById('modalCatatan').classList.add('flex');
    }
    function tutupModalCatatan() {
      document.getElementById('modalCatatan').classList.add('hidden');
      document.getElementById('modalCatatan').classList.remove('flex');
    }

    async function simpanSiswa(e) {
      e.preventDefault();
      const id = document.getElementById('inputSiswaId').value;
      const nama = document.getElementById('inputSiswaNama').value;
      try {
        const res = await fetch('/api/students', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ id_siswa: id, nama: nama })
        });
        const hasil = await res.json();
        if (!res.ok) throw new Error(hasil.error || 'Gagal menyimpan');
        showToast('Siswa ' + nama + ' berhasil didaftarkan.', 'success');
        tutupModalSiswa();
        document.getElementById('formTambahSiswa').reset();
        loadData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    }

    async function simpanCatatan(e) {
      e.preventDefault();
      const payload = {
        id_siswa: document.getElementById('inputCatatanSiswaId').value,
        kategori: document.getElementById('inputCatatanKategori').value,
        skor: parseInt(document.getElementById('inputCatatanSkor').value),
        deskripsi: document.getElementById('inputCatatanDeskripsi').value,
        tindak_lanjut: document.getElementById('inputCatatanTindakLanjut').value,
      };

      try {
        const res = await fetch('/api/records', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const hasil = await res.json();
        if (!res.ok) throw new Error(hasil.error || 'Gagal menyimpan');
        showToast('Catatan pembinaan berhasil dicatat ke basis data.', 'success');
        tutupModalCatatan();
        document.getElementById('formTambahCatatan').reset();
        loadData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    }

    async function suntikSeeder() {
      if (!confirm('Suntikkan 10 data simulasi siswa fiktif XII TKJ beserta rekam jejak pembinaan?')) return;
      try {
        const res = await fetch('/api/seed', { method: 'POST' });
        const hasil = await res.json();
        showToast(`Berhasil menambahkan ${hasil.siswa_baru} siswa dan ${hasil.catatan_baru} catatan baru.`, 'success');
        loadData();
      } catch (err) {
        showToast('Gagal menjalankan seeder: ' + err, 'error');
      }
    }

    function showToast(msg, tipe) {
      const t = document.getElementById('toast');
      t.innerText = msg;
      t.className = `fixed bottom-5 right-5 z-50 px-4 py-2.5 rounded-lg shadow-xl border text-xs font-medium flex items-center gap-2 transition-all duration-300 ${
        tipe === 'success' 
          ? 'bg-emerald-950 border-emerald-800 text-emerald-200 opacity-100 translate-y-0' 
          : 'bg-rose-950 border-rose-800 text-rose-200 opacity-100 translate-y-0'
      }`;
      setTimeout(() => {
        t.className += ' opacity-0 translate-y-20 pointer-events-none';
      }, 3500);
    }

    document.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      loadData();
    });
  </script>
</body>
</html>
"""


class MonitoringRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    HTTP Request Handler berbasis standard library Python yang melayani SPA Web
    dan endpoint RESTful API.
    """

    def _kirim_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
            return

        if path == "/api/stats":
            stats = statistik_global()
            self._kirim_json(200, stats)
            return

        if path == "/api/students":
            students = ambil_semua_siswa()
            self._kirim_json(200, students)
            return

        if path.startswith("/api/students/") and path.endswith("/records"):
            # Format: /api/students/<id>/records
            parts = path.strip("/").split("/")
            if len(parts) == 4:
                id_siswa = urllib.parse.unquote(parts[2])
                total_catatan, total_skor = ringkasan(id_siswa)
                records = lihat_riwayat(id_siswa)
                self._kirim_json(
                    200,
                    {
                        "id_siswa": id_siswa,
                        "total_catatan": total_catatan,
                        "total_skor": total_skor,
                        "records": records,
                    },
                )
                return

        if path == "/api/export":
            # Ekspor database lengkap ke JSON
            students = ambil_semua_siswa()
            export_data = []
            for id_s, nama, jml, skor in students:
                records = lihat_riwayat(id_s)
                export_data.append(
                    {
                        "id_siswa": id_s,
                        "nama": nama,
                        "total_catatan": jml,
                        "total_skor": skor,
                        "riwayat": [
                            {
                                "tanggal": r[0],
                                "kategori": r[1],
                                "deskripsi": r[2],
                                "skor": r[3],
                                "tindak_lanjut": r[4],
                            }
                            for r in records
                        ],
                    }
                )
            self._kirim_json(200, {"data_ekspor_akhlak_tkj": export_data})
            return

        self._kirim_json(404, {"error": "Endpoint tidak ditemukan"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"

        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._kirim_json(400, {"error": "Payload JSON tidak valid"})
            return

        if path == "/api/students":
            id_siswa = payload.get("id_siswa", "")
            nama = payload.get("nama", "")
            try:
                tambah_siswa(id_siswa, nama)
                self._kirim_json(201, {"pesan": f"Siswa {nama} berhasil didaftarkan"})
            except (ValueError, sqlite3.IntegrityError) as err:
                self._kirim_json(400, {"error": str(err)})
            return

        if path == "/api/records":
            id_siswa = payload.get("id_siswa", "")
            kategori = payload.get("kategori", "")
            deskripsi = payload.get("deskripsi", "")
            skor = payload.get("skor", 0)
            tindak_lanjut = payload.get("tindak_lanjut", "")

            try:
                tambah_catatan(id_siswa, kategori, deskripsi, skor, tindak_lanjut)
                self._kirim_json(201, {"pesan": "Catatan pembinaan berhasil disimpan"})
            except (ValueError, sqlite3.IntegrityError) as err:
                self._kirim_json(400, {"error": str(err)})
            return

        if path == "/api/seed":
            ts, tc = isi_data_seeder()
            self._kirim_json(
                200,
                {
                    "pesan": "Data seeder berhasil dimasukkan",
                    "siswa_baru": ts,
                    "catatan_baru": tc,
                },
            )
            return

        self._kirim_json(404, {"error": "Endpoint POST tidak ditemukan"})

    def log_message(self, format, *args):
        # Mencegah log flooding terminal kecuali ada error
        if args and str(args[1]) != "200":
            sys.stderr.write(f"[WebGUI] {args[0]} - {args[1]}\n")


def jalankan_server(port=8080):
    siapkan_db()
    handler = MonitoringRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"◈ Web Dashboard aktif di: http://127.0.0.1:{port}")
        print("Tekan Ctrl+C untuk menghentikan server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer Web Dashboard dinonaktifkan.")


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    jalankan_server(port=port_arg)
