---
type: source
source_file: "C:/Users/mifta/Documents/Obsidian Vault/remote-blog/01-TODO/2026/My-Wiki/raw/papers/NIPS-2017-attention-is-all-you-need-Paper.pdf"
sha256: d87d482d5ae7960e2e43d7dd6d21377e60e73e8fce1bf2a01aff7aca8a08c537
created: 2026-06-03
updated: 2026-06-03
translation: "[[source-NIPS-2017-attention-is-all-you-need-Paper]]"
tags: [ingested, paper, transformer, attention, deep-learning]
---

# Ringkasan Sumber: Attention Is All You Need (NIPS 2017)

## Tinjauan

- **Judul**: Attention Is All You Need
- **Penulis**: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin
- **Publikasi**: Advances in Neural Information Processing Systems (NIPS) 2017
- **Kontribusi Utama**: Memperkenalkan [[transformer-architecture-id]], arsitektur model sekuens-ke-sekuens yang didasarkan sepenuhnya pada [[self-attention-mechanism-id]], menghilangkan penggunaan arsitektur rekuren (RNN) maupun konvolusi (CNN).

## Ringkasan Bagian Kunci

### 1. Pendahuluan & Latar Belakang
Secara tradisional, model transduksi sekuens mengandalkan model rekuren (LSTMs, GRUs) atau CNN. Model rekuren memproses input secara berurutan, sehingga menghambat proses *parallelization* selama *training*. Transformer menghilangkan rekurensi secara keseluruhan, menghitung representasi input dan output secara paralel menggunakan *self-attention*.

### 2. Arsitektur
Model ini menggunakan arsitektur *encoder-decoder*:
- **Encoder**: Terdiri dari $N = 6$ lapisan identik. Setiap lapisan memiliki sub-lapisan *multi-head self-attention* diikuti oleh *position-wise feed-forward network*.
- **Decoder**: Terdiri dari $N = 6$ lapisan identik. Mencakup lapisan *masked self-attention* (mencegah aliran informasi ke kiri untuk mempertahankan sifat *auto-regressive*) dan lapisan *encoder-decoder attention* yang memperhatikan output dari *encoder*.

### 3. Mekanisme Atensi
- **Scaled Dot-Product Attention**: $\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$. Faktor skala $\frac{1}{\sqrt{d_k}}$ mencegah *gradient* yang terlalu kecil ketika $d_k$ bernilai besar.
- **Multi-Head Attention**: Melakukan proyeksi *queries*, *keys*, dan *values* ke subruang berdimensi lebih rendah sebanyak $h$ kali secara paralel. Hal ini memungkinkan model memperhatikan informasi dari subruang representasi yang berbeda secara bersamaan.

### 4. Positional Encoding
Karena model tidak mengandung rekurensi atau konvolusi, fungsi sinus dan kosinus dari frekuensi yang berbeda ditambahkan ke *input embeddings* untuk menyuntikkan informasi posisi (*positional information*):
$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)$$
$$PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)$$

### 5. Hasil Percobaan
- Mencapai BLEU score terbaik sebesar $28.4$ pada tugas penerjemahan WMT 2014 English-to-German.
- Mencapai BLEU score sebesar $41.0$ pada penerjemahan WMT 2014 English-to-French, dengan biaya komputasi *training* jauh lebih kecil dibanding model-model sebelumnya.

## Konsep Inti

- [[transformer-architecture-id]]
- [[self-attention-mechanism-id]]
