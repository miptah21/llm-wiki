---
type: concept
domain: ai
lang: id
tags: [in-context-learning, retrieval, demonstration-selection]
created: 2026-06-02
updated: 2026-06-02
translation: "[[demonstration-retrieval-for-icl]]"
sources: ["[[source-2509.20820v1-id]]"]
description: Strategi untuk ICL yang mengambil contoh demonstrasi tugas serupa dengan setiap masukan uji dari kumpulan data yang lebih besar, meningkatkan kinerja sekaligus menjaga konteks tetap singkat.
---

# Demonstration Retrieval untuk ICL

**Demonstration retrieval** (pencarian contoh demonstrasi) adalah pendekatan untuk efisiensi Pembelajaran dalam Konteks (**In-Context Learning**) yang memilih subset kecil contoh demonstrasi dari kumpulan data besar (*pool*) berdasarkan kemiripannya dengan setiap masukan uji, alih-alih menggunakan semua demonstrasi yang tersedia.

## Metode

| Metode | Mekanisme | Referensi |
|--------|-----------|-----------|
| **BM25** | Pencarian frekuensi kata kecocokan-persis (*exact-match term-frequency*) | Liu et al. (2022) |
| **Cosine** | Kemiripan kosinus dalam ruang embedding (*embedding space*, misalnya Sentence-BERT) | Liu et al. (2022); Reimers & Gurevych (2019) |
| **Set-BSR** | Kemiripan berbasis BERTScore yang menangkap beberapa aspek | Gupta et al. (2023) |

## Performa (dari Penelitian Honda et al., 2025)

Pada 8 tugas BBH menggunakan GPT-4.1, dengan mengambil 8 demonstrasi per kueri:
- **Cosine:** Akurasi rata-rata 89.1%
- **Set-BSR:** Akurasi rata-rata 89.0%
- **BM25:** Akurasi rata-rata 86.9%
- **Cheat-Sheet ICL:** Akurasi rata-rata 90.0% (tanpa memerlukan pencarian/retrieval saat inferensi uji)

## Perbandingan: Retrieval ICL vs. Cheat-Sheet ICL

| Aspek | Retrieval ICL | Cheat-Sheet ICL |
|--------|:---:|:---:|
| Memerlukan Pencarian per Kueri | **Ya** | Tidak |
| Memerlukan Penyimpanan Contoh | **Ya** | Tidak |
| Panjang Token saat Inferensi | Rendah | Rendah |
| Setup Satu Kali | Build Index | Pembuatan Cheat Sheet |

## Padanan Bahasa Inggris

- [[demonstration-retrieval-for-icl]] (Catatan Bahasa Inggris)
