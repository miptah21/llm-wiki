---
type: concept
domain: ai
lang: id
translation: "[[softmax]]"
tags: [activation-function, deep-learning, neural-network]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Krizhevsky-2012-id]]"]
description: Fungsi aktivasi yang menormalisasi vektor berisi K bilangan riil menjadi distribusi probabilitas yang terdiri dari K probabilitas.
---

# Softmax Function

**Softmax** (juga dikenal sebagai softargmax atau normalized exponential function) adalah fungsi matematika yang menerima input berupa vektor berisi $K$ bilangan riil, dan menormalisasinya menjadi distribusi probabilitas yang terdiri dari $K$ probabilitas yang proporsional dengan eksponensial dari setiap angka input.

Secara matematis, fungsi ini didefinisikan sebagai:
$$\\sigma(\\mathbf{z})_i = \\frac{e^{z_i}}{\\sum_{j=1}^{K} e^{z_j}}$$
untuk $i = 1, \\dotsc, K$ dan $\\mathbf{z} = (z_1, \\dotsc, z_K) \\in \\mathbb{R}^K$.

## Kegunaan

Dalam deep learning:
- **Output Layer Activation**: Softmax biasanya diterapkan pada lapisan output dari neural network klasifikasi multi-kelas (seperti [[source-Krizhevsky-2012-id]]) untuk memetakan skor logit mentah menjadi probabilitas dengan total nilai 1.
- **Cross-Entropy Loss**: Fungsi ini sangat praktis jika dipasangkan dengan cross-entropy loss untuk menghitung gradien selama pelatihan model.

## Lihat Juga

- [[deep-convolutional-neural-networks-id]]
- [[relu-nonlinearity-id]]

## Sumber

- [[source-Krizhevsky-2012-id]]
