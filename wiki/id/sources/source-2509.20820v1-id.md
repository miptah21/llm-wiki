---
type: source
source_file: "raw/papers/2509.20820v1.pdf"
sha256: "A38AACFB331D25131C9B66BAD3225FECE1D64BF4B8FA897C219E48B963BAAF75"
translation: "[[source-2509.20820v1]]"
created: 2026-06-02
updated: 2026-06-02
tags: [in-context-learning, prompt-engineering, LLM-efficiency, knowledge-distillation, many-shot-ICL]
---

# Distilling Many-Shot In-Context Learning into a Cheat Sheet (Mendistilasi Many-Shot ICL menjadi Lembar Panduan Tekstual)

**Penulis:** Ukyo Honda, Soichiro Murakami, Peinan Zhang
**Afiliasi:** CyberAgent, Tokyo, Jepang
**Publikasi:** 2025-09-25 (arXiv:2509.20820v1 [cs.CL])
**Kode Sumber:** https://github.com/CyberAgentAILab/cheat-sheet-icl

---

## Abstrak (Abstract)

Makalah penelitian ini mengusulkan **cheat-sheet ICL**, sebuah metode yang mendistilasi contoh demonstrasi **Many-Shot In-Context Learning (ICL)** menjadi ringkasan tekstual ringkas yang padat (sebuah "cheat sheet") untuk menggantikan seluruh rangkaian demonstrasi asli pada saat inferensi kueri uji. Pada tugas penalaran menantang **BIG-Bench Hard (BBH)**, **cheat-sheet ICL** mencapai kinerja yang sebanding atau bahkan lebih baik daripada Many-Shot ICL konvensional dengan menggunakan token yang jauh lebih sedikit, dan menyamai performa ICL berbasis pencarian (*retrieval-based ICL*) tanpa memerlukan proses pencarian saat uji (*test-time retrieval*).

---

## Pernyataan Masalah (Problem Statement)

Many-shot ICL mencapai performa tinggi dengan menyediakan ratusan contoh demonstrasi ke dalam *context window* LLM yang diperluas, namun membutuhkan biaya komputasi yang sangat mahal: setiap proses inferensi harus memproses puluhan ribu token masukan. ICL berbasis pencarian (*retrieval-based ICL*) memitigasi hal ini dengan memilih contoh relevan per kueri, tetapi memerlukan operasi pencarian (*retrieval*) untuk setiap masukan uji tunggal. Kedua pendekatan ini sangat mahal pada saat waktu inferensi kueri berlangsung.

---

## Metode Inti (Core Method)

### 1. Pembuatan Cheat-Sheet (Satu Kali Preprocessing)
1. Mulai dengan kumpulan lengkap demonstrasi many-shot $\hat{D}_n = \{(x_i, \hat{r}_i, y_i)\}_{n}^{i=1}$, yang telah diperkaya dengan penalaran penjelasan yang dihasilkan oleh model (mengikuti metode X-ICL / reinforced ICL).
2. Sajikan $\hat{D}_n$ ke LLM menggunakan prompt terstruktur khusus yang menginstruksikan model untuk:
   - Membaca semua contoh demonstrasi dan mengidentifikasi contoh paling sulit.
   - Membuat cheat sheet ringkas yang hanya mencakup poin spesifik dan detail untuk memecahkan kasus menantang tersebut, serta mengecualikan konten yang mudah.
3. Hasil keluaran LLM berupa teks $S$ yang merupakan cheat sheet — sebuah rangkuman tekstual mengenai pola pemecahan tugas.

### 2. Proses Inferensi (Inference)
- Cukup sediakan LLM dengan: cheat sheet $S$ + dua contoh instruksi format $\hat{D}_2$ + masukan uji $x_{\text{test}}$.
- Penentuan keputusan: 
$$y^* = \arg\max_{y \in Y} P(y \mid S, \hat{D}_2, x_{\text{test}})$$

---

## Hasil Eksperimen Utama (Key Experimental Results)

### Kumpulan Data (Datasets)
Dipilih delapan tugas **BIG-Bench Hard (BBH)** di mana Many-Shot ICL mengungguli Few-Shot ICL sebesar >1 persentase poin: *Boolean Expressions, Causal Judgement, Disambiguation QA, Geometric Shapes, Movie Recommendation, Salient Translation Error Detection, Sports Understanding, Word Sorting*.

### Temuan Utama (GPT-4.1)
- **7 dari 8 tugas:** Cheat-sheet ICL mengungguli few-shot ICL dengan anggaran token yang sama atau lebih kecil.
- **vs. Many-Shot ICL:** Kinerja sebanding atau lebih baik dengan menggunakan **~18× token masukan lebih sedikit** (misalnya, ~1,300 vs. ~24,000 token pada tugas Boolean Expressions).
- **vs. Metode Pencarian (Retrieval):** Cheat-sheet ICL (rata-rata 90.0%) menyamai Cosine retrieval (89.1%) dan Set-BSR (89.0%), serta mengungguli BM25 (86.9%), semuanya dengan panjang token yang setara.
- **Biaya:** Biaya cheat-sheet ICL sebanding dengan 8-shot ($0.065 vs. $0.064 per set uji) sedangkan 150-shot membutuhkan biaya $1.196.

### Kemampuan Transfer Lintas Model (Gemini 2.0 Flash)
- Cheat sheet yang dihasilkan menggunakan GPT-4.1 dapat ditransfer secara efektif ke Gemini 2.0 Flash pada sebagian besar tugas penalaran.
- Pengecualian hanya terjadi pada tugas di mana Many-Shot ICL sendiri tidak memberikan peningkatan performa pada model tersebut.

### Ketangguhan (Robustness)
- Tetap efektif meskipun tanpa diperkaya dengan penalaran penjelasan (*rationale augmentation*).
- Tangguh terhadap variasi prompt pembuatan cheat-sheet.
- Kompatibel dengan metode decoding self-consistency.

---

## Analisis Kesalahan & Interpretabilitas

Karena cheat sheet ditulis dalam teks yang dapat dibaca manusia, praktisi dapat melakukan debugging terarah:
- Pada tugas Disambiguation QA, cheat sheet sempat salah merekomendasikan penggunaan penalaran pengetahuan umum padahal jawaban seharusnya adalah "ambiguous."
- Secara terarah menghapus bagian tersebut dan menambahkan instruksi kontra eksplisit meningkatkan akurasi dari 87.0 $\to$ 89.7.
- Intervensi terarah semacam ini tidak mungkin dilakukan pada daftar demonstrasi many-shot konvensional yang buram (*opaque*).

---

## Batasan (Limitations)

1. **Cakupan:** Baru dievaluasi pada tugas penalaran; tugas kreatif atau percakapan belum diuji.
2. **Prasyarat:** Tugas harus terbukti mendapat manfaat dari Many-Shot ICL (yakni, Few-Shot ICL terbukti tidak memadai).
3. **Persyaratan Model:** Memerlukan LLM dengan kemampuan konteks panjang (*long-context*) untuk langkah pembuatan cheat-sheet awal (hingga ~250K token).
4. **Commonsense Override:** Aturan yang bertentangan dengan pengetahuan umum awal sulit dirangkum secara efektif oleh LLM.

---

## Koneksi Penelitian Terkait (Related Work)

- **Many-shot ICL:** [[many-shot-in-context-learning-id]] (Agarwal et al., 2024; Bertsch et al., 2025)
- **Demonstration Retrieval:** [[demonstration-retrieval-for-icl-id]] (Liu et al., 2022; Gupta et al., 2023)
- **Rationale Augmentation:** [[reinforced-icl-id]] dan [[x-icl-id]] (He et al., 2024)
- **Prompt Compression:** [[kompresi-prompt]] (Li et al., 2025)
- **Knowledge Distillation:** [[distilasi-pengetahuan]] (Hinton et al., 2015; West et al., 2022)
- **Chain-of-Thought:** [[chain-of-thought-prompting-id]] (Wei et al., 2022)
- **Benchmarks:** [[big-bench-hard-id]]

## Entitas Terkait

- [[cyberagent-id]]
- [[gpt-4.1-id]]
- [[gemini-2.0-flash-id]]

---

## Padanan Bahasa Inggris

- [[source-2509.20820v1]] (Catatan Bahasa Inggris)
