---
type: concept
domain: ai
lang: id
translation: "[[perceptual-image-compression]]"
tags: [compression, autoencoder, latent-space, computer-vision]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Rombach-2022-id]]"]
description: Metode autoencoding dua tahap yang memproyeksikan gambar ke dalam ruang dimensi rendah yang setara secara persepsi, menghilangkan detail frekuensi tinggi sambil mempertahankan struktur semantik.
---

# Kompresi Gambar Perseptual (Perceptual Image Compression)

**Kompresi Gambar Perseptual (Perceptual Image Compression)** adalah metodologi dalam visi komputer dan pembelajaran mendalam (deep learning) yang menggunakan *neural autoencoders* untuk mengompresi gambar mentah berdimensi tinggi menjadi representasi berdimensi lebih rendah. Berbeda dengan algoritme kompresi standar (yang meminimalkan kesalahan tingkat piksel), kompresi perseptual bertujuan untuk mempertahankan tata letak semantik dasar dan realisme visual gambar sembari membuang derau bising frekuensi tinggi yang tidak terlihat oleh mata manusia.

## Arsitektur dan Fungsi Tujuan (Objectives)

Sistem ini menggunakan encoder $\mathcal{E}$ dan decoder $\mathcal{D}$ yang dilatih pada dataset besar. Untuk memastikan hasil rekonstruksi tetap berada pada manifol gambar, model ini menggabungkan tiga fungsi kerugian utama selama pelatihan Tahap 1:
1. **Fungsi Kerugian Ruang Piksel (Pixel-Space Loss)**: Selisih $L_1$ atau $L_2$ antara gambar asli $x$ dan rekonstruksi $\tilde{x} = \mathcal{D}(\mathcal{E}(x))$.
2. **Fungsi Kerugian Perseptual (Perceptual Loss)**: Perbandingan representasi fitur mendalam yang diekstrak dari jaringan yang telah dilatih sebelumnya (seperti VGG).
3. **Fungsi Kerugian Adversarial (Adversarial Loss)**: Diskriminator berbasis petak (*patch-based discriminator*) yang memaksakan realisme lokal, mencegah efek kabur (*blurriness*).

## Strategi Regularisasi

Untuk mencegah encoder mempelajari ruang laten yang acak dan bervarians tinggi (yang akan menyulitkan model prior generatif selanjutnya), dua jenis regularisasi biasanya digunakan:
- **KL Regularization (KL-reg)**: Memaksakan penalti *Kullback-Leibler divergence* yang ringan terhadap distribusi normal standar pada ruang laten (mirip dengan Variational Autoencoder).
- **VQ Regularization (VQ-reg)**: Mengintegrasikan lapisan buku kode kuantisasi vektor (*vector quantization codebook*), memetakan kode laten berkelanjutan ke indeks diskrit (mirip dengan VQGAN).

## Peran dalam Pemodelan Generatif

Dalam pemodelan generatif dua tahap (seperti [[model-difusi-laten]] atau VQGAN), kompresi gambar perseptual bertindak sebagai tahap pertama. Dengan mengaburkan derau bising yang tidak terlihat, ia memungkinkan model generatif tahap kedua (seperti model difusi atau transformer) untuk berlatih dalam dimensi spasial yang jauh lebih kecil (misalnya, diperkecil dengan faktor $f = 4$ atau $f = 8$), menekan biaya pelatihan dan meningkatkan kecepatan inferensi.

## Lihat Juga

- [[model-difusi-laten]]
- [[stable-diffusion-id]]
