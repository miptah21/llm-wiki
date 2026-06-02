---
type: concept
domain: ai
lang: id
translation: "[[relu-nonlinearity]]"
tags: [activation-function, deep-learning, neural-network, ingest]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Krizhevsky-2012-id]]"]
description: Fungsi aktivasi non-saturating yang didefinisikan sebagai f(x) = max(0, x) yang mempercepat pelatihan neural network.
---

# ReLU Nonlinearity

**Rectified Linear Unit (ReLU)** adalah fungsi aktivasi non-saturating yang digunakan secara luas dalam deep neural networks. Secara matematis, ia didefinisikan sebagai:
$$f(x) = \max(0, x)$$

## Keunggulan dibanding Saturating Functions

Fungsi aktivasi tradisional seperti sigmoid logistik ($f(x) = (1 + e^{-x})^{-1}$) atau tangen hiperbolik ($f(x) = \tanh(x)$) mengalami saturasi untuk input yang besar, yang berarti gradiennya menjadi sangat dekat dengan nol. Hal ini memicu masalah vanishing gradient, yang secara signifikan memperlambat pelatihan model.

Sebaliknya, ReLU:
- **Tidak mengalami saturasi** pada domain positif (gradien selalu 1 untuk $x > 0$), sehingga memitigasi masalah vanishing gradient.
- **Memungkinkan sparse activation**, karena setiap input negatif dipetakan tepat ke nol.
- **Membutuhkan komputasi minimal** dibandingkan dengan fungsi eksponensial, mempercepat langkah forward dan backward.

Dalam [[source-Krizhevsky-2012-id]], penggunaan ReLU memungkinkan convolutional neural network empat lapis mencapai tingkat kesalahan pelatihan 25% pada dataset CIFAR-10 tiga hingga enam kali lebih cepat daripada jaringan setara yang menggunakan unit tanh.

## Lihat Juga

- [[deep-convolutional-neural-networks-id]]
- [[dropout-regularization-id]]

## Sumber

- [[source-Krizhevsky-2012-id]]\n