---
type: concept
domain: ai
lang: id
translation: "[[deep-convolutional-neural-networks]]"
tags: [cnn, neural-network, computer-vision, deep-learning, ingest]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Krizhevsky-2012-id]]"]
description: Kelas neural network mendalam yang umum diterapkan untuk menganalisis citra visual, menggunakan convolutional layers untuk menangkap hierarki spasial.
---

# Deep Convolutional Neural Networks

**Deep Convolutional Neural Network (CNN)** adalah arsitektur deep learning khusus yang dirancang untuk memproses data terstruktur kisi (grid-structured), seperti gambar. CNN memanfaatkan operasi matematika yang disebut konvolusi sebagai pengganti perkalian matriks umum pada setidaknya salah satu lapisannya.

## Komponen Inti

1. **Convolutional Layers**: Menyaring input dengan kernel (weights) yang dapat dipelajari untuk menghasilkan feature maps, menangkap pola lokal (tepi, bentuk, tekstur).
2. **Pooling Layers**: Melakukan downsampling pada feature maps untuk mengurangi dimensi spasial dan kompleksitas komputasi, memberikan translational invariance. Overlapping pooling (misalnya, stride $s = 2$, ukuran kernel $z = 3$) dapat membantu mengurangi [[dropout-regularization-id|overfitting]].
3. **Activation Functions**: Memperkenalkan non-linearities. Arsitektur modern menggunakan [[relu-nonlinearity-id|ReLU]] untuk mempercepat pelatihan.
4. **Fully-Connected Layers**: Melakukan penalaran tingkat tinggi dan klasifikasi akhir, biasanya dipetakan ke distribusi [[softmax-id]] pada kelas-kelas target.

## Arsitektur ImageNet (AlexNet)
Arsitektur penting yang diusulkan dalam [[source-Krizhevsky-2012-id]] terdiri dari:
- 5 convolutional layers (beberapa diikuti oleh max-pooling dan local response normalization).
- 3 fully-connected layers dengan 1000-way softmax akhir.
- Total 60 juta parameter dan 650.000 neuron, dibagi di dua GPU.

## Lihat Juga

- [[relu-nonlinearity-id]]
- [[dropout-regularization-id]]

## Sumber

- [[source-Krizhevsky-2012-id]]\n