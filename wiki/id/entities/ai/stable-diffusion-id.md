---
type: entity
category: model
domain: ai
lang: id
translation: "[[stable-diffusion]]"
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Rombach-2022-id]]"]
tags: [stable-diffusion, compvis, generative-ai, text-to-image]
---

# Stable Diffusion

**Stable Diffusion** adalah model difusi teks-ke-gambar (*text-to-image*) sumber terbuka dengan bobot terbuka (*open-weights*) yang sangat populer. Diluncurkan pertama kali pada Agustus 2022, model ini didasarkan pada makalah penelitian *High-Resolution Image Synthesis with Latent Diffusion Models* (Rombach dkk., 2022) yang dikembangkan oleh [[compvis-id]] (LMU Munich), Runway ML, dan Stability AI.

## Arsitektur dan Teknologi

Stable Diffusion beroperasi menggunakan kerangka kerja [[model-difusi-laten]]. Alih-alih menghasilkan gambar secara langsung di ruang piksel, model ini menjalankan proses penghilangan bising (*denoising*) difusi dalam ruang laten terkompresi:
1. **Autoencoder (VAE)**: Mengompresi gambar ke dalam ruang laten dengan faktor downsampling $f = 8$, memperkecil gambar $512 \times 512$ piksel menjadi representasi laten berdimensi $64 \times 64$.
2. **Text Encoder**: Memproyeksikan prompt teks masukan pengguna ke representasi laten menggunakan encoder teks CLIP yang dilatih sebelumnya (dikembangkan oleh OpenAI).
3. **U-Net**: Jaringan kondisional waktu yang dilengkapi dengan lapisan *cross-attention* untuk menghilangkan bising representasi laten secara iteratif dengan dipandu oleh *embedding* teks.

## Dampak dan Peluncuran

Berbeda dengan model teks-ke-gambar terkemuka sebelumnya (seperti DALL-E 2 dari OpenAI atau Imagen dari Google) yang tertutup bagi publik, Stable Diffusion dirilis dengan bobot model terbuka. Hal ini memungkinkan para pengembang dan peneliti untuk menjalankan sintesis gambar resolusi tinggi secara lokal pada GPU kelas konsumen, memicu gelombang besar alat kecerdasan buatan generatif sumber terbuka, adaptasi komunitas (seperti ControlNet dan LoRA), serta aplikasi komersial di seluruh dunia.

## Lihat Juga

- [[compvis-id]]
- [[model-difusi-laten]]
- [[perceptual-image-compression-id]]
