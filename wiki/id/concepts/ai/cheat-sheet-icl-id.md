---
type: concept
domain: ai
lang: id
tags: [in-context-learning, prompt-engineering, LLM-efficiency, knowledge-distillation]
created: 2026-06-02
updated: 2026-06-02
translation: "[[cheat-sheet-icl]]"
sources: ["[[source-2509.20820v1-id]]"]
description: Metode yang mereduksi demonstrasi Many-Shot ICL menjadi ringkasan tekstual ringkas (cheat sheet) untuk digunakan sebagai konteks saat inferensi, mencapai kinerja sebanding dengan token yang jauh lebih sedikit.
---

# Cheat-Sheet ICL

**Cheat-sheet ICL** adalah paradigma pembuatan prompt yang diperkenalkan oleh Honda et al. (2025). Metode ini mengompresi pengetahuan yang terkandung dalam demonstrasi **Many-Shot In-Context Learning** menjadi sebuah ringkasan tekstual ringkas yang dapat dibaca manusia — sebuah "cheat sheet" (lembar contekan) — analog dengan cara siswa merangkum materi ujian ke dalam satu lembar referensi kecil.

## Cara Kerja

### 1. Tahap Pembuatan (Satu Kali Preprocessing)
1. Mengumpulkan set lengkap demonstrasi many-shot, secara opsional dilengkapi dengan penalaran penalaran yang dihasilkan model (**Rationale-Augmented Demonstrations** menggunakan [[reinforced-icl-id]]).
2. Menyajikan seluruh demonstrasi tersebut ke LLM dengan prompt yang menginstruksikannya untuk:
   - Mengidentifikasi contoh-contoh demonstrasi yang paling sulit.
   - Mengekstrak poin khusus dan mendalam yang diperlukan untuk memecahkan kasus-kasus menantang tersebut.
3. Hasil keluarannya adalah cheat sheet tekstual yang ringkas $S$.

### 2. Tahap Inferensi (Per-Kueri)
- Menyediakan LLM dengan: cheat sheet $S$ + 2 contoh format instruksi + kueri uji.
- Tidak memerlukan proses pencarian (*retrieval*), tidak memerlukan konteks many-shot yang besar — hanya menggunakan ringkasan ringkas tersebut.

## Keunggulan Utama

| Properti | Many-Shot ICL | Retrieval ICL | Cheat-Sheet ICL |
|----------|:---:|:---:|:---:|
| Biaya Token saat Inferensi | Sangat Tinggi | Rendah | **Rendah** |
| Memerlukan Pencarian per Kueri | Tidak | Ya | **Tidak** |
| Preprocessing Satu Kali | Tidak | Index Building | **Pembuatan Cheat-Sheet** |
| Konteks yang Dapat Ditafsirkan | Tidak | Sebagian | **Ya** |
| Dapat Ditransfer Lintas Model | N/A | Terbatas | **Ya** |

## Performa

Pada 8 tugas BIG-Bench Hard menggunakan GPT-4.1:
- Menyamai atau melampaui 150-shot ICL pada 7/8 tugas dengan menggunakan **~18× token lebih sedikit**.
- Menyamai metode berbasis pencarian (*retrieval-based*) seperti Cosine dan Set-BSR tanpa melakukan pencarian saat inferensi uji.
- Biaya operasional sebanding dengan 8-shot ICL ($0.065 vs. $1.196 untuk 150-shot).

## Keunggulan Interpretabilitas

Karena cheat sheet berupa teks yang dapat dibaca manusia, praktisi dapat:
- Mendiagnosis kegagalan model dengan membaca isi cheat sheet.
- Mengedit bagian tertentu secara langsung (misalnya, menghapus heuristik yang menyesatkan meningkatkan akurasi tugas Disambiguation QA dari 87.0 $\to$ 89.7).
- Hal ini tidak mungkin dilakukan pada daftar demonstrasi few-shot/many-shot konvensional yang buram (*opaque*).

## Batasan

- Hanya divalidasi pada tugas penalaran di mana Many-Shot ICL menunjukkan keunggulan dibanding few-shot.
- Aturan yang bertentangan dengan pengetahuan umum awal (*commonsense priors*) sulit disaring oleh LLM.
- Memerlukan LLM dengan kemampuan konteks panjang (*long-context*) untuk langkah pembuatan cheat-sheet awal.

## Padanan Bahasa Inggris

- [[cheat-sheet-icl]] (Catatan Bahasa Inggris)
