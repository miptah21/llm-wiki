# Design Specification: Split-Screen Scrollytelling Interface for LLM Wiki Dashboards

*   **Tanggal:** 2026-06-03
*   **Status:** Menunggu Review Pengguna (Diperbarui untuk Kompilasi Dinamis Penuh)
*   **Topik:** Migrasi dashboard tab statis ke sistem *scrollytelling* dinamis (split-screen) tanpa hardcoding teks spesifik makalah.

---

## 1. Pendahuluan & Tujuan
Spesifikasi ini diperbarui untuk menghapus semua formatting teks statis dan teks penjelasan hardcoded (seperti Many-Shot ICL/Cheat Sheet) dari skrip `scripts/html_generator.py`. Skrip kompilator harus bersifat sepenuhnya generik, sehingga dapat digunakan untuk makalah atau artikel apa pun di masa mendatang. 

Konten penjelasan pada kartu overlay visualizer kanan akan dipanen secara dinamis dari teks sumber markdown kiri selama proses kompilasi.

---

## 2. Pemanenan Konten Dinamis (Dynamic Content Harvesting)

### 2.1 Penguraian Bagian (Sectioning)
Skrip Python akan membaca berkas markdown ringkasan terjemahan Bahasa Indonesia, memotongnya berdasarkan heading tingkat 2 (`##`), dan melakukan pembersihan teks:
*   Mengekstrak **Judul Section** (`## Judul`).
*   Mengekstrak **Deskripsi Visual Dinamis** dari paragraf pertama (atau 2 kalimat pertama) dari isi section, lalu membersihkan sintaks markdown (seperti wikilinks `[[...]]`, bold `**...**`, dll.) agar aman disimpan dalam atribut HTML.

### 2.2 Atribut Elemen HTML Dinamis
Setiap `<section>` di kolom narasi kiri akan dibuat secara dinamis dengan atribut berikut:
```html
<section class="narrative-section" 
         data-visual-mode="[intro|compression|vector|graph|sandbox]" 
         data-ratio="[0|100]" 
         data-description="[Teks deskripsi ringkas hasil panen Python]"
         id="section-narrative-[index]">
    <h2>[Judul Section]</h2>
    <div class="section-body">
        [Konten HTML hasil parsing markdown]
    </div>
</section>
```

---

## 3. Sinkronisasi JS Engine Generik

Ketika bagian narasi aktif melewati Intersection Observer:
1.  **Judul:** Diperbarui menggunakan `activeSection.querySelector('h2').innerText`.
2.  **Deskripsi:** Diperbarui menggunakan `activeSection.getAttribute('data-description')`.
3.  **Transisi Visualizer:** Diperbarui menggunakan `activeSection.getAttribute('data-visual-mode')` dan `data-ratio`.
Hal ini meniadakan kebutuhan hardcoding string teks di dalam logika JavaScript.

---

## 4. Rencana Verifikasi (Verification Plan)

### 4.1 Pengujian Lintas Dokumen (Cross-document Testing)
Kita akan memverifikasi kompilator dengan dua dokumen yang sangat berbeda untuk membuktikan kegenerikannya:
1.  **Makalah Riset:** `raw/papers/2509.20820v1.pdf` (Menghasilkan dashboard scrollytelling visual Many-Shot/Cheat-Sheet).
2.  **Artikel Wiki:** `raw/articles/The_Unreasonable_Effectiveness_Of_HTML.md` (Menghasilkan dashboard scrollytelling visual generik dengan data deskripsi artikel HTML tersebut, bukan Many-Shot).

### 4.2 Uji Mutu Fungsional
*   Membuka kedua dashboard di browser untuk memastikan deskripsi visualizer kanan memperlihatkan teks yang relevan dengan masing-masing dokumen.
*   Memastikan tidak ada error JavaScript di console browser.
