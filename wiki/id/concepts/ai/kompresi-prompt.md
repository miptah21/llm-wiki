---
type: concept
domain: ai
lang: id
tags: [prompt-engineering, LLM-efficiency, compression]
created: 2026-06-02
updated: 2026-06-02
translation: "[[prompt-compression]]"
sources: ["[[source-2509.20820v1-id]]"]
description: Teknik untuk mengurangi panjang prompt LLM sambil mempertahankan konten informasionalnya, mencakup kompresi demonstrasi dan kompresi masukan RAG.
---

# Kompresi Prompt (Prompt Compression)

**Kompresi Prompt (Prompt Compression)** merujuk pada rumpun teknik yang mengurangi panjang token dari masukan LLM (prompt) dengan tetap berupaya mempertahankan informasi relevan dengan tugas yang diperlukan untuk menghasilkan keluaran yang akurat.

## Kategori

### 1. Kompresi Berorientasi Demonstrasi (Demonstration-Oriented Compression)
- **[[cheat-sheet-icl-id]]:** Mendistilasi contoh demonstrasi many-shot menjadi ringkasan aturan tekstual yang padat dalam satu langkah tunggal (*single pass*).
- **Instruction Induction:** Menghasilkan instruksi tugas secara otomatis dari contoh few-shot (Honovich et al., 2023; Zhou et al., 2023). Metode ini mendahului kemunculan era many-shot dan tidak dirancang untuk efisiensi di bawah kumpulan demonstrasi yang sangat besar.

### 2. Kompresi Masukan Pengetahuan/RAG (Knowledge/RAG Input Compression)
- Berfokus pada penyusutan dokumen yang diambil (*retrieved documents*) atau sumber pengetahuan yang sangat panjang, alih-alih berfokus pada kumpulan contoh demonstrasi.
- Seringkali memerlukan perubahan arsitektur atau parameter model yang mahal, atau optimasi iteratif atas subset kecil (Li et al., 2025).

## Perbandingan: Cheat-Sheet ICL vs. Penelitian Sebelumnya

Berbeda dengan sebagian besar metode kompresi prompt sebelumnya, Cheat-Sheet ICL:
- Beroperasi dalam **satu pass tunggal** tanpa memerlukan proses optimasi iteratif yang memakan waktu.
- Memerlukan **nol pelatihan atau modifikasi model** (*no training or model modifications*).
- Menargetkan **kumpulan demonstrasi many-shot** secara khusus.
- Dievaluasi langsung terhadap baseline **Many-Shot ICL** yang kuat, bukan terhadap benchmark zero-shot atau few-shot yang sederhana.

## Padanan Bahasa Inggris

- [[prompt-compression]] (Catatan Bahasa Inggris)
