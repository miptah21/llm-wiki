---
type: concept
domain: ai
lang: id
tags: [in-context-learning, LLM, few-shot-learning, long-context]
created: 2026-06-02
updated: 2026-06-02
translation: "[[many-shot-in-context-learning]]"
sources: ["[[source-2509.20820v1-id]]"]
description: Rezim ICL yang memberikan ratusan atau ribuan contoh demonstrasi ke LLM dengan memanfaatkan context window yang diperluas, menghasilkan kinerja yang unggul dibandingkan few-shot ICL konvensional pada tugas pengenalan pola.
---

# Many-Shot In-Context Learning

**Many-shot in-context learning (ICL)** adalah paradigma pembelajaran dalam konteks di mana LLM diberikan sejumlah besar contoh demonstrasi spesifik tugas (biasanya 100–1000+ contoh) di dalam *context window* mereka, berbeda dengan skenario few-shot konvensional (biasanya 2–32 contoh).

## Latar Belakang

Few-Shot ICL standar (Brown et al., 2020) mengkondisikan LLM pada beberapa contoh demonstrasi:
$$D_n = \{(x_i, y_i)\}_{i=1}^{n}$$

bersama dengan masukan uji untuk menghasilkan prediksi. Karena keterbatasan ukuran *context window* pada model terdahulu, $n$ secara tradisional berukuran kecil (few-shot).

Dengan tersedianya *context window* yang sangat panjang pada model-model modern seperti Gemini 1.5 Pro (1M+ token) dan GPT-4.1 (128K+ token), nilai $n$ dapat ditingkatkan hingga beberapa kali lipat — inilah yang disebut sebagai rezim **many-shot**.

## Temuan Utama (Agarwal et al., 2024; Bertsch et al., 2025)

- Performa model meningkat secara log-linear seiring dengan bertambahnya jumlah demonstrasi pada banyak tugas.
- Many-shot ICL bersifat **training-free** (bebas pelatihan) — tidak memerlukan pembaruan parameter model sama sekali.
- Dapat diterapkan langsung pada model kepemilikan (*proprietary models*) yang tidak mendukung penyetelan halus (*fine-tuning*).
- Sangat efektif pada **pattern-recognition tasks** (tugas pengenalan pola, seperti pada BIG-Bench Hard) dibandingkan tugas-tugas yang membutuhkan pengetahuan akademik umum yang telah diserap dengan baik selama tahap prabayar (*pretraining*).

## Batasan & Kekurangan

1. **Biaya Komputasi (Computational cost):** Memproses puluhan ribu token masukan per inferensi sangatlah mahal. Bahkan dengan fitur pencadangan prefiks (*prefix caching*), dekoder tetap harus menghadiri seluruh konteks panjang.
2. **Biaya API:** Prefiks yang dicadangkan sering kali dihapus setelah interval singkat atau membutuhkan biaya persistensi berbayar.
3. **Penurunan Format:** Konteks yang sangat panjang dapat mendistrak model untuk mematuhi format luaran yang diminta.
4. **Diminishing Returns (Hasil yang Menyusut):** Tugas-tugas yang sudah berhasil diselesaikan dengan baik oleh model tidak menunjukkan peningkatan (misalnya, MATH500, GSM8K dengan GPT-4.1).

## Alternatif Efisiensi

- [[demonstration-retrieval-for-icl-id]] — Memilih demonstrasi paling relevan per kueri.
- [[cheat-sheet-icl-id]] — Mendistilasi contoh demonstrasi menjadi ringkasan aturan tekstual yang padat.
- Teknik modifikasi atensi (Yuan et al., 2024) — Membutuhkan akses ke parameter model.

## Padanan Bahasa Inggris

- [[many-shot-in-context-learning]] (Catatan Bahasa Inggris)
