"""
Web Dashboard GUI & REST API Server - Enterprise Edition
Sistem Monitoring Akhlak Siswa (Kelas XII TKJ - SMK Alhadiid)
Dibangun menggunakan pustaka standar Python: http.server, json, urllib, sqlite3.
Zero External Dependencies • Linear/Raycast Dark Theme • Anti-AI Slop Standards.
"""

import csv
import http.server
import io
import json
import os
import socketserver
import sqlite3
import sys
import urllib.parse

from monitoring_akhlak import (
    NAMA_DB_DEFAULT,
    ambil_analisis_kategori,
    ambil_semua_catatan,
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
  <title>Sistem Monitoring Akhlak Siswa | XII TKJ - SMK Alhadiid</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            zinc: {
              950: '#09090b',
              900: '#121215',
              850: '#18181b',
              800: '#27272a',
              700: '#3f3f46',
              600: '#52525b',
              400: '#a1a1aa',
              300: '#d4d4d8',
              200: '#e4e4e7',
            }
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; }
    code, .font-mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
    
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #09090b; }
    ::-webkit-scrollbar-thumb { background: #27272a; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: #3f3f46; }

    @media print {
      body { background: white !important; color: black !important; font-size: 11px !important; }
      nav, header, #sidebarNav, #topActionBar, .no-print, button, #toast, #commandPalette { display: none !important; }
      #printDossierView { display: block !important; }
      #tab-overview, #tab-students, #tab-logs { display: none !important; }
      table { border-collapse: collapse !important; width: 100% !important; }
      th, td { border: 1px solid #cbd5e1 !important; color: black !important; padding: 5px 8px !important; }
      th { background-color: #f8fafc !important; }
    }
  </style>
</head>
<body class="bg-zinc-950 text-zinc-100 min-h-screen flex antialiased selection:bg-zinc-800 selection:text-white">

  <!-- SIDEBAR NAVIGATION (LINEAR AESTHETIC) -->
  <aside id="sidebarNav" class="w-64 border-r border-zinc-800/80 bg-zinc-950 flex flex-col shrink-0 select-none z-20">
    <div class="h-14 border-b border-zinc-800/80 px-4 flex items-center justify-between">
      <div class="flex items-center gap-2.5">
        <div class="h-7 w-7 rounded-md bg-zinc-900 border border-zinc-800 flex items-center justify-center text-blue-400">
          <i data-lucide="shield" class="w-4 h-4 text-blue-400" stroke-width="1.5"></i>
        </div>
        <div>
          <span class="text-xs font-semibold tracking-tight text-white block">SMK Alhadiid</span>
          <span class="text-[10px] text-zinc-500 font-mono block">XII TKJ • Monitoring</span>
        </div>
      </div>
      <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800">v2.4</span>
    </div>

    <!-- NAVIGATION TABS -->
    <div class="p-3 space-y-1 flex-1">
      <div class="px-2 pb-2 text-[10px] font-semibold tracking-wider text-zinc-500 uppercase">Menu Utama</div>
      
      <button onclick="pindahTab('overview')" id="nav-overview" class="w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium text-white bg-zinc-900 border border-zinc-800/80 transition">
        <div class="flex items-center gap-2.5">
          <i data-lucide="layout-grid" class="w-4 h-4 text-blue-400" stroke-width="1.5"></i>
          <span>Ikhtisar & Analitik</span>
        </div>
        <kbd class="text-[9px] font-mono text-zinc-500 bg-zinc-950 px-1.5 py-0.5 rounded border border-zinc-800">1</kbd>
      </button>

      <button onclick="pindahTab('students')" id="nav-students" class="w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 transition">
        <div class="flex items-center gap-2.5">
          <i data-lucide="users" class="w-4 h-4 text-zinc-400" stroke-width="1.5"></i>
          <span>Data Siswa Kelas</span>
        </div>
        <kbd class="text-[9px] font-mono text-zinc-500 bg-zinc-950 px-1.5 py-0.5 rounded border border-zinc-800">2</kbd>
      </button>

      <button onclick="pindahTab('logs')" id="nav-logs" class="w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 transition">
        <div class="flex items-center gap-2.5">
          <i data-lucide="file-text" class="w-4 h-4 text-zinc-400" stroke-width="1.5"></i>
          <span>Jurnal Seluruh Catatan</span>
        </div>
        <kbd class="text-[9px] font-mono text-zinc-500 bg-zinc-950 px-1.5 py-0.5 rounded border border-zinc-800">3</kbd>
      </button>

      <button onclick="pindahTab('print')" id="nav-print" class="w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 transition">
        <div class="flex items-center gap-2.5">
          <i data-lucide="printer" class="w-4 h-4 text-zinc-400" stroke-width="1.5"></i>
          <span>Dokumen Cetak Resmi</span>
        </div>
        <kbd class="text-[9px] font-mono text-zinc-500 bg-zinc-950 px-1.5 py-0.5 rounded border border-zinc-800">4</kbd>
      </button>

      <div class="pt-4 px-2 pb-2 text-[10px] font-semibold tracking-wider text-zinc-500 uppercase">Aksi Cepat</div>

      <button onclick="bukaModalCatatan()" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-medium text-zinc-300 hover:text-white hover:bg-zinc-900 transition">
        <i data-lucide="plus-circle" class="w-3.5 h-3.5 text-blue-400" stroke-width="1.5"></i>
        <span>Catat Perilaku Baru</span>
      </button>

      <button onclick="bukaModalSiswa()" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-medium text-zinc-300 hover:text-white hover:bg-zinc-900 transition">
        <i data-lucide="user-plus" class="w-3.5 h-3.5 text-zinc-400" stroke-width="1.5"></i>
        <span>Tambah Siswa Baru</span>
      </button>

      <button onclick="suntikSeeder()" class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-medium text-amber-400/90 hover:text-amber-300 hover:bg-zinc-900 transition">
        <i data-lucide="database" class="w-3.5 h-3.5 text-amber-400" stroke-width="1.5"></i>
        <span>Seed 10 Siswa Fiktif</span>
      </button>
    </div>

    <!-- DATABASE ENGINE BADGE -->
    <div class="p-3 border-t border-zinc-800/80 text-[11px] text-zinc-400 bg-zinc-950">
      <div class="flex items-center justify-between text-zinc-500 text-[10px]">
        <span>Storage Engine</span>
        <span class="flex items-center gap-1 text-emerald-400">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>SQLite3 Active</span>
        </span>
      </div>
      <div class="mt-1 text-[10px] text-zinc-400 font-mono truncate">monitoring_akhlak.db</div>
    </div>
  </aside>

  <!-- MAIN VIEWPORT -->
  <div class="flex-1 flex flex-col min-w-0 overflow-y-auto">
    
    <!-- TOP HEADER BAR -->
    <header id="topActionBar" class="h-14 border-b border-zinc-800/80 px-6 flex items-center justify-between bg-zinc-950/80 backdrop-blur sticky top-0 z-10 select-none">
      <div class="flex items-center gap-3">
        <h1 id="topPageTitle" class="text-sm font-semibold text-white tracking-tight">Ikhtisar & Analitik Pembinaan</h1>
        <span class="text-zinc-600">/</span>
        <span class="text-xs text-zinc-400">Lab Jaringan Komputer</span>
      </div>

      <div class="flex items-center gap-2">
        <button onclick="bukaCommandPalette()" class="inline-flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-xs text-zinc-400 hover:text-zinc-200 transition">
          <i data-lucide="search" class="w-3.5 h-3.5 text-zinc-500" stroke-width="1.5"></i>
          <span>Perintah & Cari...</span>
          <kbd class="text-[10px] font-mono px-1 py-0.5 rounded bg-zinc-950 text-zinc-400 border border-zinc-800">⌘K</kbd>
        </button>

        <a href="/api/export/csv" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-xs font-medium text-zinc-300 hover:text-white transition">
          <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-emerald-400" stroke-width="1.5"></i>
          <span>CSV</span>
        </a>

        <a href="/api/export" target="_blank" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-xs font-medium text-zinc-300 hover:text-white transition">
          <i data-lucide="code" class="w-3.5 h-3.5 text-blue-400" stroke-width="1.5"></i>
          <span>JSON</span>
        </a>
      </div>
    </header>

    <!-- CONTENT BODY CONTAINER -->
    <main class="flex-1 p-6 space-y-6 max-w-7xl w-full mx-auto">
      
      <!-- ================================================================= -->
      <!-- TAB 1: IKHTISAR & ANALITIK -->
      <!-- ================================================================= -->
      <section id="tab-overview" class="space-y-6">
        
        <!-- KPI METRICS -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80 space-y-2">
            <div class="flex items-center justify-between text-zinc-400 text-xs">
              <span>Total Siswa Terdaftar</span>
              <i data-lucide="users" class="w-4 h-4 text-zinc-500" stroke-width="1.5"></i>
            </div>
            <div class="flex items-baseline gap-2">
              <span id="kpiSiswa" class="text-2xl font-bold font-mono text-white">-</span>
              <span class="text-[11px] text-zinc-500">Kelas XII TKJ</span>
            </div>
          </div>

          <div class="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80 space-y-2">
            <div class="flex items-center justify-between text-zinc-400 text-xs">
              <span>Total Log Perilaku</span>
              <i data-lucide="activity" class="w-4 h-4 text-zinc-500" stroke-width="1.5"></i>
            </div>
            <div class="flex items-baseline gap-2">
              <span id="kpiCatatan" class="text-2xl font-bold font-mono text-white">-</span>
              <span class="text-[11px] text-zinc-500">Insiden & Apresiasi</span>
            </div>
          </div>

          <div class="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80 space-y-2">
            <div class="flex items-center justify-between text-zinc-400 text-xs">
              <span>Apresiasi Positif (+1)</span>
              <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400" stroke-width="1.5"></i>
            </div>
            <div class="flex items-baseline gap-2">
              <span id="kpiApresiasi" class="text-2xl font-bold font-mono text-emerald-400">-</span>
              <span class="text-[11px] text-zinc-500">Capaian Baik</span>
            </div>
          </div>

          <div class="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80 space-y-2">
            <div class="flex items-center justify-between text-zinc-400 text-xs">
              <span>Evaluasi Pembinaan (-1)</span>
              <i data-lucide="alert-triangle" class="w-4 h-4 text-rose-400" stroke-width="1.5"></i>
            </div>
            <div class="flex items-baseline gap-2">
              <span id="kpiEvaluasi" class="text-2xl font-bold font-mono text-rose-400">-</span>
              <span class="text-[11px] text-zinc-500">Pendampingan</span>
            </div>
          </div>
        </div>

        <!-- ANALYTICS GRID: 4 CATEGORIES & INDEKS PROGRESS -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          <!-- LEFT 2 COLS: CATEGORY DISTRIBUTION -->
          <div class="lg:col-span-2 p-5 rounded-xl bg-zinc-900/50 border border-zinc-800/80 space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-xs font-semibold text-zinc-200 tracking-wide uppercase">Distribusi Dimensi Karakter</h3>
                <p class="text-xs text-zinc-400 mt-0.5">Pemetaan rekam jejak perilaku berdasarkan 4 pilar pembinaan.</p>
              </div>
              <span class="text-[11px] font-mono text-zinc-400 bg-zinc-950 px-2 py-0.5 rounded border border-zinc-800">Disiplin • Tanggung Jawab • Peduli • Jujur</span>
            </div>

            <div class="space-y-3.5 pt-2" id="categoryDistributionContainer">
              <div class="text-xs text-zinc-500 py-6 text-center">Memuat distribusi analitik...</div>
            </div>
          </div>

          <!-- RIGHT 1 COL: INDEKS MORAL KELAS -->
          <div class="p-5 rounded-xl bg-zinc-900/50 border border-zinc-800/80 flex flex-col justify-between space-y-4">
            <div>
              <h3 class="text-xs font-semibold text-zinc-200 tracking-wide uppercase">Indeks Perilaku Positif</h3>
              <p class="text-xs text-zinc-400 mt-0.5">Rasio capaian apresiasi positif dibanding total seluruh rekam jejak.</p>
            </div>

            <div class="py-4 text-center">
              <div class="text-4xl font-extrabold font-mono text-white tracking-tight" id="indeksPersenVal">0.0%</div>
              <p class="text-xs text-zinc-500 mt-1">Standar KKM Pembinaan: 70.0%</p>
              
              <div class="w-full bg-zinc-950 rounded-full h-2 border border-zinc-800 mt-4 overflow-hidden">
                <div id="indeksProgressBar" class="h-full bg-blue-500 transition-all duration-500" style="width: 0%"></div>
              </div>
            </div>

            <div class="p-3 rounded-lg bg-zinc-950 border border-zinc-800/80 text-[11px] text-zinc-400 leading-relaxed">
              <strong class="text-zinc-200 font-medium">Catatan Pedagogis:</strong> Nilai indeks bersifat diagnostik untuk pendidik mengukur efektivitas kultur kelas, bukan angka penentu rapor siswa.
            </div>
          </div>
        </div>

        <!-- RECENT ACTIVITY FEED -->
        <div class="rounded-xl bg-zinc-900/40 border border-zinc-800/80 overflow-hidden">
          <div class="px-5 py-3.5 border-b border-zinc-800/80 flex items-center justify-between">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-zinc-200">Aktivitas Pembinaan Terkini</h3>
            <button onclick="pindahTab('logs')" class="text-xs text-blue-400 hover:text-blue-300 font-medium">Buka Jurnal Seluruhnya →</button>
          </div>
          <div class="divide-y divide-zinc-800/60" id="recentActivityList">
            <div class="p-6 text-center text-xs text-zinc-500">Memuat catatan terkini...</div>
          </div>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- TAB 2: DATA SISWA KELAS -->
      <!-- ================================================================= -->
      <section id="tab-students" class="space-y-4 hidden">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-3">
          <div class="flex items-center gap-2 w-full sm:w-auto">
            <div class="relative w-full sm:w-80">
              <i data-lucide="search" class="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" stroke-width="1.5"></i>
              <input 
                type="text" 
                id="searchStudentInput" 
                onkeyup="filterTabelSiswa()" 
                placeholder="Cari ID siswa atau nama lengkap..." 
                class="w-full pl-9 pr-3 py-1.5 text-xs bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition"
              />
            </div>
            <select id="filterStatusSiswa" onchange="filterTabelSiswa()" class="text-xs bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-300 px-3 py-1.5 focus:outline-none focus:border-blue-500">
              <option value="semua">Semua Status</option>
              <option value="positif">Teladan Aktif (+)</option>
              <option value="evaluasi">Perlu Pembinaan (-)</option>
              <option value="netral">Netral / Nol (0)</option>
            </select>
          </div>

          <div class="flex items-center gap-2 self-end">
            <button onclick="bukaModalSiswa()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-medium text-white transition">
              <i data-lucide="plus" class="w-3.5 h-3.5" stroke-width="1.5"></i>
              <span>Tambah Siswa</span>
            </button>
          </div>
        </div>

        <div class="rounded-xl border border-zinc-800/80 bg-zinc-900/40 overflow-hidden shadow-sm">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="border-b border-zinc-800/80 bg-zinc-950/60 text-zinc-400 font-medium text-[11px] uppercase tracking-wider">
                <th class="py-3 px-4 font-mono">ID Siswa</th>
                <th class="py-3 px-4">Nama Lengkap</th>
                <th class="py-3 px-4 text-center">Catatan</th>
                <th class="py-3 px-4 text-center">Net Skor</th>
                <th class="py-3 px-4 text-center">Status Pembinaan</th>
                <th class="py-3 px-4 text-right">Tindakan</th>
              </tr>
            </thead>
            <tbody id="studentTableBody" class="divide-y divide-zinc-800/60 text-zinc-300">
              <tr>
                <td colspan="6" class="py-12 text-center text-zinc-500">Memuat data siswa...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- TAB 3: JURNAL SELURUH CATATAN (MASTER LOGS) -->
      <!-- ================================================================= -->
      <section id="tab-logs" class="space-y-4 hidden">
        <div class="flex flex-col sm:flex-row items-center justify-between gap-3">
          <div class="flex items-center gap-2 w-full sm:w-auto">
            <div class="relative w-full sm:w-80">
              <i data-lucide="search" class="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" stroke-width="1.5"></i>
              <input 
                type="text" 
                id="searchLogsInput" 
                onkeyup="filterMasterLogs()" 
                placeholder="Cari deskripsi, tindak lanjut, siswa..." 
                class="w-full pl-9 pr-3 py-1.5 text-xs bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition"
              />
            </div>
            <select id="filterKategoriLogs" onchange="filterMasterLogs()" class="text-xs bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-300 px-3 py-1.5 focus:outline-none focus:border-blue-500">
              <option value="semua">Semua Kategori</option>
              <option value="Disiplin">Disiplin</option>
              <option value="Tanggung Jawab">Tanggung Jawab</option>
              <option value="Kepedulian">Kepedulian</option>
              <option value="Kejujuran">Kejujuran</option>
            </select>
          </div>
          <button onclick="bukaModalCatatan()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-medium text-white transition">
            <i data-lucide="plus-circle" class="w-3.5 h-3.5" stroke-width="1.5"></i>
            <span>Catat Perilaku Baru</span>
          </button>
        </div>

        <div class="rounded-xl border border-zinc-800/80 bg-zinc-900/40 overflow-hidden shadow-sm">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="border-b border-zinc-800/80 bg-zinc-950/60 text-zinc-400 font-medium text-[11px] uppercase tracking-wider">
                <th class="py-3 px-4 font-mono">Tanggal</th>
                <th class="py-3 px-4">Siswa</th>
                <th class="py-3 px-4">Kategori</th>
                <th class="py-3 px-4 text-center">Skor</th>
                <th class="py-3 px-4">Deskripsi Faktual</th>
                <th class="py-3 px-4">Rencana Tindak Lanjut</th>
              </tr>
            </thead>
            <tbody id="logsTableBody" class="divide-y divide-zinc-800/60 text-zinc-300">
              <tr>
                <td colspan="6" class="py-12 text-center text-zinc-500">Memuat jurnal master...</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- TAB 4: DOSSIER & RAPORT CETAK RESMI -->
      <!-- ================================================================= -->
      <section id="tab-print" class="space-y-6 hidden">
        <div class="p-4 rounded-xl bg-zinc-900/60 border border-zinc-800 flex items-center justify-between no-print">
          <div>
            <h3 class="text-xs font-semibold text-white uppercase tracking-wide">Pratinjau Lembar Rekapitulasi Pembinaan Resmi</h3>
            <p class="text-xs text-zinc-400 mt-0.5">Format dokumen cetak resmi untuk arsip kurikulum atau pelaporan bimbingan konseling.</p>
          </div>
          <button onclick="window.print()" class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white transition shadow-sm">
            <i data-lucide="printer" class="w-4 h-4" stroke-width="1.5"></i>
            <span>Cetak / Ekspor PDF</span>
          </button>
        </div>

        <!-- PRINT SHEET SURFACE -->
        <div class="bg-white text-black p-8 rounded-xl shadow-xl max-w-4xl mx-auto space-y-6">
          <div class="border-b-2 border-black pb-3 text-center space-y-1">
            <h2 class="text-base font-bold uppercase tracking-wider">SMK ALHADIID 1 CILEUNGSI</h2>
            <h3 class="text-xs font-semibold uppercase tracking-wide">PROGRAM KEAHLIAN TEKNIK KOMPUTER DAN JARINGAN (TKJ)</h3>
            <p class="text-[10px] text-gray-600">Jl. Raya Setu - Cileungsi, Pasirangin, Cileungsi, Bogor, Jawa Barat</p>
            <div class="pt-2 text-xs font-bold uppercase underline tracking-wide">LEMBAR REKAPITULASI PEMBINAAN AKHLAK SISWA KELAS XII TKJ</div>
          </div>

          <div class="flex justify-between text-[11px] text-gray-700">
            <div>
              <p><strong>Tahun Ajaran:</strong> 2026/2027</p>
              <p><strong>Program Keahlian:</strong> Teknik Komputer & Jaringan</p>
            </div>
            <div class="text-right">
              <p><strong>Tanggal Cetak:</strong> <span id="printDossierDate">-</span></p>
              <p><strong>Sifat Dokumen:</strong> Rahasia / Pembinaan Internal</p>
            </div>
          </div>

          <table class="w-full text-[10px] border-collapse border border-gray-300">
            <thead>
              <tr class="bg-gray-100 text-left uppercase font-semibold">
                <th class="p-2 border border-gray-300 w-12 text-center">No</th>
                <th class="p-2 border border-gray-300 w-24">ID Siswa</th>
                <th class="p-2 border border-gray-300">Nama Siswa</th>
                <th class="p-2 border border-gray-300 text-center w-20">Total Log</th>
                <th class="p-2 border border-gray-300 text-center w-20">Net Skor</th>
                <th class="p-2 border border-gray-300 w-32">Keterangan</th>
              </tr>
            </thead>
            <tbody id="printTableBody">
              <!-- Render cetak -->
            </tbody>
          </table>

          <div class="pt-10 flex justify-between text-xs text-center text-gray-800">
            <div class="w-56">
              <p>Mengetahui,</p>
              <p class="font-semibold">Kepala Program TKJ</p>
              <div class="h-16"></div>
              <p class="font-bold underline">( ........................................ )</p>
              <p class="text-[10px] text-gray-500">NIP/NUPTK: -</p>
            </div>
            <div class="w-56">
              <p>Cileungsi, <span id="printDateSign">-</span></p>
              <p class="font-semibold">Wali Kelas XII TKJ</p>
              <div class="h-16"></div>
              <p class="font-bold underline">( ........................................ )</p>
              <p class="text-[10px] text-gray-500">NIP/NUPTK: -</p>
            </div>
          </div>
        </div>
      </section>

    </main>
  </div>

  <!-- =================================================================== -->
  <!-- SLIDE-OVER DRAWER: PROFIL & RIWAYAT SISWA -->
  <!-- =================================================================== -->
  <div id="drawerSiswa" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden select-none">
    <div class="absolute inset-y-0 right-0 max-w-xl w-full bg-zinc-950 border-l border-zinc-800 flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
      
      <!-- DRAWER HEADER -->
      <div class="p-5 border-b border-zinc-800 flex items-start justify-between bg-zinc-900/40">
        <div>
          <div class="flex items-center gap-2">
            <span id="drawerSiswaId" class="text-xs font-mono font-semibold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">XII-TKJ-01</span>
            <span id="drawerStatusPill" class="text-[11px] px-2 py-0.5 rounded border font-medium">Status</span>
          </div>
          <h2 id="drawerSiswaNama" class="text-base font-bold text-white mt-1.5">Nama Siswa</h2>
          <p id="drawerSummaryText" class="text-xs text-zinc-400 mt-0.5 font-mono">0 catatan pembinaan • net skor 0</p>
        </div>
        <button onclick="tutupDrawerSiswa()" class="p-1 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-800 transition">
          <i data-lucide="x" class="w-5 h-5" stroke-width="1.5"></i>
        </button>
      </div>

      <!-- DRAWER BODY: TIMELINE OF RECORDS -->
      <div class="flex-1 overflow-y-auto p-5 space-y-3" id="drawerTimeline">
        <div class="text-center text-xs text-zinc-500 py-10">Memuat catatan...</div>
      </div>

      <!-- DRAWER FOOTER -->
      <div class="p-4 border-t border-zinc-800 bg-zinc-900/40 flex items-center justify-between">
        <button onclick="bukaModalCatatanUntukSiswa()" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-medium text-white transition">
          <i data-lucide="plus" class="w-3.5 h-3.5" stroke-width="1.5"></i>
          <span>Tambah Catatan untuk Siswa Ini</span>
        </button>
        <button onclick="tutupDrawerSiswa()" class="px-3 py-1.5 rounded-lg border border-zinc-800 text-xs text-zinc-400 hover:text-white hover:bg-zinc-800 transition">
          Tutup
        </button>
      </div>
    </div>
  </div>

  <!-- =================================================================== -->
  <!-- MODAL FORM: TAMBAH SISWA BARU -->
  <!-- =================================================================== -->
  <div id="modalSiswa" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-center justify-center p-4">
    <div class="bg-zinc-900 border border-zinc-800 rounded-xl max-w-md w-full p-5 shadow-2xl space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-white flex items-center gap-2">
          <i data-lucide="user-plus" class="w-4 h-4 text-blue-400" stroke-width="1.5"></i>
          <span>Pendaftaran Siswa Baru</span>
        </h3>
        <button onclick="tutupModalSiswa()" class="text-zinc-500 hover:text-zinc-300">
          <i data-lucide="x" class="w-4 h-4" stroke-width="1.5"></i>
        </button>
      </div>
      <form id="formTambahSiswa" onsubmit="simpanSiswa(event)" class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-zinc-400 mb-1">ID Siswa (Format: XII-TKJ-XX)</label>
          <input type="text" id="inputSiswaId" required placeholder="Contoh: XII-TKJ-11" class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:border-blue-500 font-mono" />
        </div>
        <div>
          <label class="block text-xs font-medium text-zinc-400 mb-1">Nama Lengkap Siswa</label>
          <input type="text" id="inputSiswaNama" required placeholder="Contoh: Muhammad Faiz" class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:border-blue-500" />
        </div>
        <div class="pt-2 flex justify-end gap-2">
          <button type="button" onclick="tutupModalSiswa()" class="px-3 py-1.5 rounded-lg border border-zinc-800 text-xs text-zinc-400 hover:bg-zinc-800">Batal</button>
          <button type="submit" class="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-medium text-white transition">Simpan Siswa</button>
        </div>
      </form>
    </div>
  </div>

  <!-- =================================================================== -->
  <!-- MODAL FORM: TAMBAH CATATAN PEMBINAAN -->
  <!-- =================================================================== -->
  <div id="modalCatatan" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-center justify-center p-4">
    <div class="bg-zinc-900 border border-zinc-800 rounded-xl max-w-lg w-full p-5 shadow-2xl space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-white flex items-center gap-2">
          <i data-lucide="file-plus" class="w-4 h-4 text-blue-400" stroke-width="1.5"></i>
          <span>Catat Pembinaan Perilaku</span>
        </h3>
        <button onclick="tutupModalCatatan()" class="text-zinc-500 hover:text-zinc-300">
          <i data-lucide="x" class="w-4 h-4" stroke-width="1.5"></i>
        </button>
      </div>
      <form id="formTambahCatatan" onsubmit="simpanCatatan(event)" class="space-y-3">
        <div>
          <label class="block text-xs font-medium text-zinc-400 mb-1">Pilih Siswa Target</label>
          <select id="inputCatatanSiswaId" required class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:border-blue-500 font-mono">
            <!-- Pilihan Siswa -->
          </select>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Dimensi Karakter</label>
            <select id="inputCatatanKategori" required class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:border-blue-500">
              <option value="Disiplin">Disiplin</option>
              <option value="Tanggung Jawab">Tanggung Jawab</option>
              <option value="Kepedulian">Kepedulian</option>
              <option value="Kejujuran">Kejujuran</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium text-zinc-400 mb-1">Indikator Skor</label>
            <select id="inputCatatanSkor" required class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:border-blue-500 font-medium">
              <option value="1">+1 (Apresiasi Capaian Positif)</option>
              <option value="-1">-1 (Evaluasi Pembinaan Perilaku)</option>
            </select>
          </div>
        </div>
        <div>
          <label class="block text-xs font-medium text-zinc-400 mb-1">Deskripsi Faktual (Tindakan teramati, bahasa netral)</label>
          <textarea id="inputCatatanDeskripsi" required rows="2" placeholder="Catat tindakan konkret yang diamati secara objektif..." class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:border-blue-500"></textarea>
        </div>
        <div>
          <label class="block text-xs font-medium text-zinc-400 mb-1">Rencana Tindak Lanjut & Ruang Klarifikasi</label>
          <input type="text" id="inputCatatanTindakLanjut" required placeholder="Langkah perbaikan/apresiasi yang disepakati..." class="w-full px-3 py-2 text-xs bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200 focus:outline-none focus:border-blue-500" />
        </div>
        <div class="pt-2 flex justify-end gap-2">
          <button type="button" onclick="tutupModalCatatan()" class="px-3 py-1.5 rounded-lg border border-zinc-800 text-xs text-zinc-400 hover:bg-zinc-800">Batal</button>
          <button type="submit" class="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-medium text-white transition">Simpan Catatan</button>
        </div>
      </form>
    </div>
  </div>

  <!-- =================================================================== -->
  <!-- COMMAND PALETTE (RAYCAST / LINEAR STYLE: CTRL+K) -->
  <!-- =================================================================== -->
  <div id="commandPalette" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-start justify-center pt-20 px-4">
    <div class="bg-zinc-900 border border-zinc-800 rounded-xl max-w-lg w-full shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-100">
      <div class="p-3 border-b border-zinc-800 flex items-center gap-2.5">
        <i data-lucide="search" class="w-4 h-4 text-zinc-500" stroke-width="1.5"></i>
        <input 
          type="text" 
          id="cmdInput" 
          onkeyup="filterCommandPalette()" 
          placeholder="Ketik nama siswa atau perintah cepat..." 
          class="w-full bg-transparent text-xs text-zinc-100 placeholder-zinc-500 focus:outline-none"
        />
        <kbd class="text-[9px] font-mono text-zinc-500 bg-zinc-950 px-1.5 py-0.5 rounded border border-zinc-800">ESC</kbd>
      </div>
      <div class="p-2 max-h-72 overflow-y-auto space-y-1" id="cmdResults">
        <!-- Hasil pencarian / perintah cepat -->
      </div>
    </div>
  </div>

  <!-- TOAST NOTIFICATION STACK -->
  <div id="toast" class="fixed bottom-5 right-5 z-50 transform translate-y-20 opacity-0 transition-all duration-200 pointer-events-none px-3.5 py-2 rounded-lg shadow-2xl border text-xs font-medium flex items-center gap-2"></div>

  <!-- =================================================================== -->
  <!-- JAVASCRIPT FRONTEND LOGIC -->
  <!-- =================================================================== -->
  <script>
    let globalStudents = [];
    let globalLogs = [];
    let activeStudentDrawerId = null;

    async function bootstrap() {
      await muatSemuaData();
      inisialisasiShortcut();
    }

    async function muatSemuaData() {
      try {
        const [stats, students, categories, logs] = await Promise.all([
          fetch('/api/stats').then(r => r.json()),
          fetch('/api/students').then(r => r.json()),
          fetch('/api/analytics').then(r => r.json()),
          fetch('/api/all-records').then(r => r.json())
        ]);

        globalStudents = students;
        globalLogs = logs;

        // Render KPI
        document.getElementById('kpiSiswa').innerText = stats.total_siswa;
        document.getElementById('kpiCatatan').innerText = stats.total_catatan;
        document.getElementById('kpiApresiasi').innerText = '+' + stats.total_apresiasi;
        document.getElementById('kpiEvaluasi').innerText = stats.total_evaluasi;
        document.getElementById('indeksPersenVal').innerText = stats.indeks_positif + '%';
        document.getElementById('indeksProgressBar').style.width = Math.min(stats.indeks_positif, 100) + '%';

        // Render Komponen
        renderDistribusiKategori(categories, stats.total_catatan);
        renderRecentActivity(globalLogs.slice(0, 5));
        renderTabelSiswa(globalStudents);
        renderMasterLogs(globalLogs);
        renderPrintDossier(globalStudents);
        updateSelectSiswaOption(globalStudents);

        lucide.createIcons();
      } catch (err) {
        munculkanToast('Gagal memuat data: ' + err, 'error');
      }
    }

    function renderDistribusiKategori(categories, totalCatatan) {
      const container = document.getElementById('categoryDistributionContainer');
      if (!categories || categories.length === 0 || totalCatatan === 0) {
        container.innerHTML = `<div class="text-xs text-zinc-500 py-6 text-center">Belum ada catatan perilaku yang tersimpan.</div>`;
        return;
      }

      container.innerHTML = categories.map(c => {
        const pct = Math.round((c.total / totalCatatan) * 100);
        const posPct = c.total > 0 ? (c.positif / c.total * 100) : 0;
        const evaPct = c.total > 0 ? (c.evaluasi / c.total * 100) : 0;
        return `
          <div class="p-3 rounded-lg bg-zinc-950/80 border border-zinc-800/80 space-y-2">
            <div class="flex items-center justify-between text-xs">
              <span class="font-medium text-zinc-200">${c.kategori}</span>
              <span class="font-mono text-zinc-400">${c.total} log (${pct}%)</span>
            </div>
            <div class="w-full bg-zinc-900 rounded-full h-1.5 overflow-hidden flex">
              <div class="bg-emerald-500 h-1.5" style="width: ${posPct}%"></div>
              <div class="bg-rose-500 h-1.5" style="width: ${evaPct}%"></div>
            </div>
            <div class="flex items-center justify-between text-[10px] text-zinc-500">
              <span class="text-emerald-400 font-mono">+${c.positif} apresiasi</span>
              <span class="text-rose-400 font-mono">${c.evaluasi} evaluasi</span>
            </div>
          </div>
        `;
      }).join('');
    }

    function renderRecentActivity(logs) {
      const el = document.getElementById('recentActivityList');
      if (!logs || logs.length === 0) {
        el.innerHTML = `<div class="p-6 text-center text-xs text-zinc-500">Belum ada aktivitas pembinaan.</div>`;
        return;
      }
      el.innerHTML = logs.map(l => {
        const [idCatatan, idSiswa, nama, tgl, kat, desk, skor, tindak] = l;
        const isPos = skor > 0;
        return `
          <div class="px-5 py-3 flex items-center justify-between hover:bg-zinc-900/40 transition">
            <div class="flex items-center gap-3">
              <span class="px-1.5 py-0.5 rounded text-[10px] font-mono ${isPos ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'} font-semibold">
                ${isPos ? '+1' : '-1'}
              </span>
              <div>
                <div class="text-xs font-medium text-white flex items-center gap-2">
                  <span>${nama}</span>
                  <span class="text-[10px] text-zinc-500 font-mono">(${idSiswa})</span>
                  <span class="text-[10px] text-zinc-400 px-1.5 py-0.2 rounded bg-zinc-800">${kat}</span>
                </div>
                <p class="text-[11px] text-zinc-400 mt-0.5">${desk}</p>
              </div>
            </div>
            <span class="text-[10px] font-mono text-zinc-500">${tgl}</span>
          </div>
        `;
      }).join('');
    }

    function renderTabelSiswa(data) {
      const tbody = document.getElementById('studentTableBody');
      if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="py-12 text-center text-zinc-500">Tidak ada siswa yang cocok dengan filter pencarian.</td></tr>`;
        return;
      }

      tbody.innerHTML = data.map(s => {
        const [id, nama, jml, skor] = s;
        let badgeStatus = '';
        let skorBadge = '';

        if (skor > 0) {
          skorBadge = `<span class="font-mono text-emerald-400 font-semibold">+${skor}</span>`;
          badgeStatus = `<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Teladan Aktif</span>`;
        } else if (skor < 0) {
          skorBadge = `<span class="font-mono text-rose-400 font-semibold">${skor}</span>`;
          badgeStatus = `<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">Dalam Pembinaan</span>`;
        } else {
          skorBadge = `<span class="font-mono text-zinc-400">0</span>`;
          badgeStatus = `<span class="px-2 py-0.5 rounded text-[10px] font-medium bg-zinc-800 text-zinc-400 border border-zinc-700">Stabil / Netral</span>`;
        }

        return `
          <tr class="hover:bg-zinc-900/60 transition group">
            <td class="py-3 px-4 font-mono text-blue-400 text-xs">${id}</td>
            <td class="py-3 px-4 font-medium text-white text-xs">${nama}</td>
            <td class="py-3 px-4 text-center font-mono text-zinc-400">${jml}</td>
            <td class="py-3 px-4 text-center">${skorBadge}</td>
            <td class="py-3 px-4 text-center">${badgeStatus}</td>
            <td class="py-3 px-4 text-right">
              <button onclick="bukaDrawerSiswa('${id}', '${nama}', ${skor}) && event.stopPropagation()" class="px-2.5 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs font-medium transition">
                Profil & Riwayat
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    function renderMasterLogs(logs) {
      const tbody = document.getElementById('logsTableBody');
      if (!logs || logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="py-12 text-center text-zinc-500">Belum ada riwayat catatan di jurnal.</td></tr>`;
        return;
      }
      tbody.innerHTML = logs.map(l => {
        const [idCatatan, idSiswa, nama, tgl, kat, desk, skor, tindak] = l;
        const isPos = skor > 0;
        return `
          <tr class="hover:bg-zinc-900/50 transition">
            <td class="py-2.5 px-4 font-mono text-zinc-400 text-[11px] whitespace-nowrap">${tgl}</td>
            <td class="py-2.5 px-4 font-medium text-white text-xs">
              ${nama} <span class="text-zinc-500 font-mono text-[10px]">(${idSiswa})</span>
            </td>
            <td class="py-2.5 px-4 text-zinc-300 text-xs">
              <span class="px-2 py-0.5 rounded text-[10px] bg-zinc-800 border border-zinc-700/80">${kat}</span>
            </td>
            <td class="py-2.5 px-4 text-center">
              <span class="font-mono text-xs font-semibold ${isPos ? 'text-emerald-400' : 'text-rose-400'}">${isPos ? '+1' : '-1'}</span>
            </td>
            <td class="py-2.5 px-4 text-zinc-300 text-xs leading-relaxed">${desk}</td>
            <td class="py-2.5 px-4 text-zinc-400 text-xs leading-relaxed font-mono">${tindak}</td>
          </tr>
        `;
      }).join('');
    }

    function renderPrintDossier(students) {
      const tbody = document.getElementById('printTableBody');
      tbody.innerHTML = students.map((s, idx) => {
        const [id, nama, jml, skor] = s;
        let ket = 'Stabil';
        if (skor > 1) ket = 'Teladan Positif';
        else if (skor < 0) ket = 'Perlu Bimbingan BK';

        return `
          <tr>
            <td class="p-2 border border-gray-300 text-center">${idx + 1}</td>
            <td class="p-2 border border-gray-300 font-mono">${id}</td>
            <td class="p-2 border border-gray-300 font-semibold">${nama}</td>
            <td class="p-2 border border-gray-300 text-center font-mono">${jml}</td>
            <td class="p-2 border border-gray-300 text-center font-mono font-bold">${skor > 0 ? '+' : ''}${skor}</td>
            <td class="p-2 border border-gray-300">${ket}</td>
          </tr>
        `;
      }).join('');

      const d = new Date();
      const strDate = d.toLocaleDateString('id-ID', { year: 'numeric', month: 'long', day: 'numeric' });
      document.getElementById('printDossierDate').innerText = strDate;
      document.getElementById('printDateSign').innerText = strDate;
    }

    function filterTabelSiswa() {
      const q = document.getElementById('searchStudentInput').value.toLowerCase();
      const status = document.getElementById('filterStatusSiswa').value;

      const filtered = globalStudents.filter(s => {
        const matchesQuery = s[0].toLowerCase().includes(q) || s[1].toLowerCase().includes(q);
        if (!matchesQuery) return false;

        const skor = s[3];
        if (status === 'positif') return skor > 0;
        if (status === 'evaluasi') return skor < 0;
        if (status === 'netral') return skor === 0;
        return true;
      });

      renderTabelSiswa(filtered);
    }

    function filterMasterLogs() {
      const q = document.getElementById('searchLogsInput').value.toLowerCase();
      const kat = document.getElementById('filterKategoriLogs').value;

      const filtered = globalLogs.filter(l => {
        const matchKategori = (kat === 'semua') || (l[4] === kat);
        const matchQuery = l[1].toLowerCase().includes(q) || l[2].toLowerCase().includes(q) || l[5].toLowerCase().includes(q) || l[7].toLowerCase().includes(q);
        return matchKategori && matchQuery;
      });

      renderMasterLogs(filtered);
    }

    function updateSelectSiswaOption(students) {
      const sel = document.getElementById('inputCatatanSiswaId');
      sel.innerHTML = students.map(s => `<option value="${s[0]}">${s[0]} — ${s[1]}</option>`).join('');
    }

    function pindahTab(namaTab) {
      ['overview', 'students', 'logs', 'print'].forEach(t => {
        document.getElementById(`tab-${t}`).classList.add('hidden');
        const navBtn = document.getElementById(`nav-${t}`);
        if (navBtn) {
          navBtn.className = "w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 transition";
        }
      });

      document.getElementById(`tab-${namaTab}`).classList.remove('hidden');
      const activeNav = document.getElementById(`nav-${namaTab}`);
      if (activeNav) {
        activeNav.className = "w-full flex items-center justify-between px-2.5 py-2 rounded-lg text-xs font-medium text-white bg-zinc-900 border border-zinc-800/80 transition";
      }

      const titleMap = {
        'overview': 'Ikhtisar & Analitik Pembinaan',
        'students': 'Data Siswa & Profil Perilaku',
        'logs': 'Jurnal Master Catatan Pembinaan',
        'print': 'Lembar Dokumen Cetak Resmi'
      };
      document.getElementById('topPageTitle').innerText = titleMap[namaTab];
      lucide.createIcons();
    }

    // DRAWER SISWA LOGIC
    async function bukaDrawerSiswa(id, nama, skor) {
      activeStudentDrawerId = id;
      document.getElementById('drawerSiswaId').innerText = id;
      document.getElementById('drawerSiswaNama').innerText = nama;
      
      const pill = document.getElementById('drawerStatusPill');
      if (skor > 0) {
        pill.className = "text-[11px] px-2 py-0.5 rounded border font-medium bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
        pill.innerText = "Teladan Aktif";
      } else if (skor < 0) {
        pill.className = "text-[11px] px-2 py-0.5 rounded border font-medium bg-rose-500/10 text-rose-400 border-rose-500/20";
        pill.innerText = "Dalam Pembinaan";
      } else {
        pill.className = "text-[11px] px-2 py-0.5 rounded border font-medium bg-zinc-800 text-zinc-400 border-zinc-700";
        pill.innerText = "Netral / Stabil";
      }

      const timeline = document.getElementById('drawerTimeline');
      timeline.innerHTML = `<div class="p-8 text-center text-xs text-zinc-500">Mengambil catatan siswa...</div>`;
      document.getElementById('drawerSiswa').classList.remove('hidden');

      try {
        const res = await fetch(`/api/students/${id}/records`).then(r => r.json());
        document.getElementById('drawerSummaryText').innerText = `${res.total_catatan} catatan pembinaan • net skor ${res.total_skor > 0 ? '+' : ''}${res.total_skor}`;

        if (!res.records || res.records.length === 0) {
          timeline.innerHTML = `<div class="p-6 rounded-xl border border-zinc-800/80 bg-zinc-900/40 text-center text-xs text-zinc-500">Belum ada catatan pembinaan yang tersimpan untuk siswa ini.</div>`;
        } else {
          timeline.innerHTML = res.records.map(r => {
            const [tgl, kat, desk, skr, tindak] = r;
            const isPos = skr > 0;
            return `
              <div class="p-3.5 rounded-xl border ${isPos ? 'border-emerald-500/20 bg-emerald-950/10' : 'border-rose-500/20 bg-rose-950/10'} space-y-2">
                <div class="flex items-center justify-between text-xs">
                  <div class="flex items-center gap-2">
                    <span class="px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${isPos ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}">${kat}</span>
                    <span class="text-zinc-500 font-mono text-[11px]">${tgl}</span>
                  </div>
                  <span class="font-mono font-bold text-xs ${isPos ? 'text-emerald-400' : 'text-rose-400'}">${isPos ? '+1 Apresiasi' : '-1 Evaluasi'}</span>
                </div>
                <p class="text-xs text-zinc-200 leading-relaxed">${desk}</p>
                <div class="pt-1.5 border-t border-zinc-800/60 text-[11px] text-zinc-400 flex items-start gap-1.5">
                  <span class="text-zinc-300 font-medium">Tindak Lanjut:</span>
                  <span>${tindak}</span>
                </div>
              </div>
            `;
          }).join('');
        }
        lucide.createIcons();
      } catch (err) {
        timeline.innerHTML = `<div class="text-rose-400 text-xs p-4">Galat: ${err}</div>`;
      }
    }

    function tutupDrawerSiswa() {
      document.getElementById('drawerSiswa').classList.add('hidden');
    }

    function bukaModalCatatanUntukSiswa() {
      if (activeStudentDrawerId) {
        document.getElementById('inputCatatanSiswaId').value = activeStudentDrawerId;
      }
      tutupDrawerSiswa();
      bukaModalCatatan();
    }

    // MODAL DIALOGS
    function bukaModalSiswa() {
      document.getElementById('modalSiswa').classList.remove('hidden');
      document.getElementById('modalSiswa').classList.add('flex');
      document.getElementById('inputSiswaId').focus();
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
        munculkanToast(`Siswa '${nama}' berhasil didaftarkan.`, 'success');
        tutupModalSiswa();
        document.getElementById('formTambahSiswa').reset();
        await muatSemuaData();
      } catch (err) {
        munculkanToast(err.message, 'error');
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
        munculkanToast('Catatan pembinaan berhasil dicatat ke basis data.', 'success');
        tutupModalCatatan();
        document.getElementById('formTambahCatatan').reset();
        await muatSemuaData();
      } catch (err) {
        munculkanToast(err.message, 'error');
      }
    }

    async function suntikSeeder() {
      if (!confirm('Suntikkan 10 data simulasi siswa XII TKJ beserta rekam jejak pembinaan?')) return;
      try {
        const res = await fetch('/api/seed', { method: 'POST' });
        const hasil = await res.json();
        munculkanToast(`Data seeder masuk: +${hasil.siswa_baru} siswa, +${hasil.catatan_baru} catatan.`, 'success');
        await muatSemuaData();
      } catch (err) {
        munculkanToast('Gagal menjalankan seeder: ' + err, 'error');
      }
    }

    // COMMAND PALETTE LOGIC (CTRL+K)
    function bukaCommandPalette() {
      const p = document.getElementById('commandPalette');
      p.classList.remove('hidden');
      p.classList.add('flex');
      const inp = document.getElementById('cmdInput');
      inp.value = '';
      inp.focus();
      renderCommandPaletteResults('');
    }

    function tutupCommandPalette() {
      const p = document.getElementById('commandPalette');
      p.classList.add('hidden');
      p.classList.remove('flex');
    }

    function filterCommandPalette() {
      const q = document.getElementById('cmdInput').value.toLowerCase();
      renderCommandPaletteResults(q);
    }

    function renderCommandPaletteResults(q) {
      const res = document.getElementById('cmdResults');
      const cmds = [
        { label: 'Catat Perilaku Baru', action: () => { tutupCommandPalette(); bukaModalCatatan(); } },
        { label: 'Pendaftaran Siswa Baru', action: () => { tutupCommandPalette(); bukaModalSiswa(); } },
        { label: 'Suntikkan Data Seeder (10 Siswa TKJ)', action: () => { tutupCommandPalette(); suntikSeeder(); } },
        { label: 'Ekspor Data ke Format CSV', action: () => { window.location.href = '/api/export/csv'; } },
        { label: 'Ekspor Database ke JSON', action: () => { window.open('/api/export', '_blank'); } },
        { label: 'Buka Dokumen Cetak Resmi', action: () => { tutupCommandPalette(); pindahTab('print'); } }
      ];

      // Siswa hasil query
      const studentMatches = globalStudents.filter(s => s[0].toLowerCase().includes(q) || s[1].toLowerCase().includes(q));

      let html = '';
      if (q) {
        studentMatches.slice(0, 5).forEach(s => {
          html += `
            <div onclick="tutupCommandPalette(); bukaDrawerSiswa('${s[0]}', '${s[1]}', ${s[3]})" class="px-3 py-2 rounded-lg hover:bg-zinc-800 cursor-pointer flex items-center justify-between text-xs text-zinc-200">
              <span class="font-medium text-white">${s[1]} <span class="text-zinc-500 font-mono text-[10px]">(${s[0]})</span></span>
              <span class="text-[10px] text-blue-400 font-mono">Buka Profil</span>
            </div>
          `;
        });
      }

      cmds.filter(c => c.label.toLowerCase().includes(q)).forEach(c => {
        html += `
          <div onclick="(${c.action.toString()})()" class="px-3 py-2 rounded-lg hover:bg-zinc-800 cursor-pointer flex items-center justify-between text-xs text-zinc-300">
            <span>${c.label}</span>
            <span class="text-[10px] text-zinc-500 font-mono">Perintah</span>
          </div>
        `;
      });

      if (!html) {
        html = `<div class="p-4 text-center text-xs text-zinc-500">Tidak ada perintah atau siswa yang cocok.</div>`;
      }
      res.innerHTML = html;
    }

    function inisialisasiShortcut() {
      document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
          e.preventDefault();
          bukaCommandPalette();
        } else if (e.key === 'Escape') {
          tutupCommandPalette();
          tutupDrawerSiswa();
          tutupModalSiswa();
          tutupModalCatatan();
        } else if (!e.ctrlKey && !e.metaKey && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
          if (e.key === '1') pindahTab('overview');
          if (e.key === '2') pindahTab('students');
          if (e.key === '3') pindahTab('logs');
          if (e.key === '4') pindahTab('print');
        }
      });
    }

    function munculkanToast(msg, tipe) {
      const t = document.getElementById('toast');
      t.innerText = msg;
      t.className = `fixed bottom-5 right-5 z-50 px-3.5 py-2 rounded-lg shadow-2xl border text-xs font-medium flex items-center gap-2 transition-all duration-200 ${
        tipe === 'success' 
          ? 'bg-emerald-950/90 border-emerald-800 text-emerald-200 opacity-100 translate-y-0' 
          : 'bg-rose-950/90 border-rose-800 text-rose-200 opacity-100 translate-y-0'
      }`;
      setTimeout(() => {
        t.className += ' opacity-0 translate-y-20 pointer-events-none';
      }, 3500);
    }

    document.addEventListener('DOMContentLoaded', bootstrap);
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

        if path == "/api/analytics":
            analytics = ambil_analisis_kategori()
            self._kirim_json(200, analytics)
            return

        if path == "/api/students":
            students = ambil_semua_siswa()
            self._kirim_json(200, students)
            return

        if path == "/api/all-records":
            logs = ambil_semua_catatan()
            self._kirim_json(200, logs)
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

        if path == "/api/export/csv":
            # Ekspor database lengkap ke CSV
            students = ambil_semua_siswa()
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID SISWA", "NAMA SISWA", "TOTAL CATATAN", "NET SKOR", "STATUS"])
            for id_s, nama, jml, skor in students:
                status = "Teladan Aktif" if skor > 0 else ("Dalam Pembinaan" if skor < 0 else "Stabil/Netral")
                writer.writerow([id_s, nama, jml, skor, status])

            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=rekap_akhlak_xii_tkj.csv")
            self.end_headers()
            self.wfile.write(output.getvalue().encode("utf-8"))
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
        print(f"◈ Web Dashboard Enterprise aktif di: http://127.0.0.1:{port}")
        print("Tekan Ctrl+C untuk menghentikan server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer Web Dashboard dinonaktifkan.")


if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    jalankan_server(port=port_arg)
