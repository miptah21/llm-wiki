---
type: concept
domain: ai
lang: id
tags: [in-context-learning, LLM, few-shot-learning, prompt-engineering]
created: 2026-06-02
updated: 2026-06-02
translation: "[[in-context-learning]]"
description: Paradigma dalam pemrosesan bahasa alami di mana model bahasa besar belajar melakukan tugas melalui contoh demonstrasi masukan-target yang disediakan dalam promptnya, tanpa ada pembaruan parameter.
---

# Pembelajaran dalam Konteks (In-Context Learning)

**Pembelajaran dalam Konteks (In-Context Learning - ICL)** adalah kemampuan mendasar dari model bahasa besar (LLM) modern yang memungkinkan mereka melakukan tugas-tugas baru hanya dengan membaca beberapa contoh yang disediakan dalam konteks masukan (prompt), tanpa memperbarui bobot jaringan saraf mereka.

## Mekanisme

Di bawah paradigma ICL, kueri uji disertai dengan serangkaian contoh demonstrasi kecil:
$$D = \{(x_1, y_1), (x_2, y_2), \dots, (x_n, y_n)\}$$

Prompt terdiri dari demonstrasi-demonstrasi ini diikuti oleh masukan target $x_{\text{test}}$. Model menyelesaikan prompt dengan menghasilkan prediksi yang sesuai $y_{\text{test}}$, secara efektif melakukan inferensi tugas:
$$y_{\text{test}} \approx \arg\max_y P(y \mid D, x_{\text{test}})$$

## Fitur Utama

- **Nol Perubahan Parameter**: Bobot model sepenuhnya dibekukan selama proses berlangsung.
- **Generalisasi Tugas**: Satu model tunggal dapat beralih antara penerjemahan, peringkasan, dan penalaran secara dinamis hanya dengan mengubah promptnya.
- **Perilaku Emergent**: ICL beberapa contoh (few-shot) standar dipopulerkan oleh GPT-3 (Brown et al., 2020) dan muncul terutama pada model di atas skala parameter tertentu.

## Variasi Utama

- [[many-shot-in-context-learning-id]] — Menyediakan ratusan atau ribuan demonstrasi.
- [[demonstration-retrieval-for-icl-id]] — Memilih contoh yang paling relevan secara dinamis untuk setiap kueri.
- [[cheat-sheet-icl-id]] — Mengompresi pengetahuan demonstrasi menjadi lembar petunjuk tingkat tinggi.
- [[chain-of-thought-prompting-id]] — Melengkapi contoh dengan langkah penalaran demi langkah.

## Padanan Bahasa Inggris

- [[in-context-learning]] (Catatan terjemahan Bahasa Inggris)
