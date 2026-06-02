---
type: concept
domain: ai
lang: id
translation: "[[dropout-regularization]]"
tags: [regularization, deep-learning, neural-network, overfitting, ingest]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Krizhevsky-2012-id]]"]
description: Teknik regularisasi di mana neuron tersembunyi secara acak disetel ke nol selama pelatihan dengan probabilitas tertentu untuk mencegah co-adaptation.
---

# Dropout Regularization

**Dropout** adalah teknik regularisasi kuat yang dirancang untuk mencegah overfitting dalam deep neural networks.

## Mekanisme

Selama pelatihan, dropout secara acak menyetel output dari setiap neuron tersembunyi ke nol dengan probabilitas $p$ (umumnya $p=0.5$).
- **Forward Pass**: Neuron yang dikeluarkan (dropped out) tidak berkontribusi pada perambatan maju (forward propagation) aktivasi.
- **Backward Pass**: Neuron-neuron ini tidak berpartisipasi dalam backpropagation, yang berarti bobotnya tidak diperbarui untuk langkah pelatihan tersebut.
- **Weight Sharing**: Setiap iterasi pelatihan secara efektif mengambil sampel arsitektur jaringan yang berbeda, tetapi semua arsitektur ini berbagi bobot (share weights).
- **Inference/Test Time**: Semua neuron aktif, tetapi outputnya dikalikan dengan $(1-p)$ (misalnya, 0.5) untuk memperkirakan rata-rata geometris dari prediksi yang dihasilkan oleh jaringan dropout yang berjumlah eksponensial.

## Rasional
Dengan menonaktifkan subset acak neuron, dropout mencegah neuron mengembangkan co-adaptations yang kompleks (di mana sebuah neuron hanya mempelajari fitur yang berguna dengan kehadiran neuron spesifik lainnya). Hal ini memaksa setiap neuron untuk mempelajari fitur independen yang lebih tangguh (robust) yang berguna dalam kombinasi dengan berbagai subset acak dari neuron lain.

Dalam [[source-Krizhevsky-2012-id]], dropout diterapkan pada dua fully-connected layers pertama untuk mengatasi overfitting yang substansial. Meskipun teknik ini memotong kecepatan konvergensi menjadi setengahnya (menggandakan jumlah iterasi yang diperlukan), ia sangat penting untuk melatih jaringan dengan 60 juta parameter tanpa overfitting yang parah.

## Lihat Juga

- [[deep-convolutional-neural-networks-id]]
- [[relu-nonlinearity-id]]

## Sumber

- [[source-Krizhevsky-2012-id]]\n