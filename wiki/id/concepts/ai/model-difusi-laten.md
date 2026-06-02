---
type: concept
domain: ai
lang: id
translation: "[[latent-diffusion-models]]"
tags: [diffusion, latent-diffusion, generative-model, image-synthesis]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Rombach-2022-id]]"]
description: Kelas model difusi probabilistik yang beroperasi di dalam ruang laten berdimensi lebih rendah dari autoencoder yang telah dilatih sebelumnya untuk menghasilkan data resolusi tinggi secara efisien.
---

# Model Difusi Laten (Latent Diffusion Model - LDM)

**Model Difusi Laten (Latent Diffusion Model - LDM)** adalah jenis model generatif yang menerapkan proses difusi di dalam ruang laten (*latent space*) dari autoencoder yang telah dilatih sebelumnya (*pre-trained*), alih-alih langsung pada ruang piksel berdimensi tinggi. Diperkenalkan oleh Rombach dkk. (2022), LDM membagi pelatihan model generatif menjadi dua fase: kompresi perseptual (ditangani oleh autoencoder) dan pembangkitan semantik (ditangani oleh proses difusi).

## Mekanisme dan Arsitektur

Pelatihan LDM dibagi menjadi dua langkah utama yang berbeda:

1. **Kompresi Perseptual (Autoencoder)**: Sebuah autoencoder yang terdiri dari encoder $\mathcal{E}$ dan decoder $\mathcal{D}$ dilatih terlebih dahulu. Encoder memproyeksikan data mentah berdimensi tinggi $x$ (seperti piksel gambar) ke representasi laten berdimensi lebih rendah $z = \mathcal{E}(x)$. Decoder dilatih untuk merekonstruksi masukan asli dari kode laten tersebut: $\tilde{x} = \mathcal{D}(z) \approx x$.
2. **Difusi Laten (Latent Diffusion)**: Model difusi dilatih di dalam ruang laten $z$ yang telah dipelajari. Model ini belajar membalikkan proses difusi maju (yang secara bertahap menambahkan derau bising ke representasi laten) dengan menggunakan jaringan autoencoder penghilang derau (*denoising autoencoder*) $\epsilon_\theta$ yang diimplementasikan sebagai UNet kondisional waktu:
   $$\mathcal{L}_{\text{LDM}} := \mathbb{E}_{\mathcal{E}(x), \epsilon \sim \mathcal{N}(0,1), t} \left[ \|\epsilon - \epsilon_\theta(z_t, t)\|^2_2 \right]$$

## Keunggulan Difusi Ruang Laten

- **Keunggulan Komputasi**: Karena proses difusi beroperasi pada representasi laten yang terkompresi, dimensi spasial dari evaluasi jaringan berkurang secara signifikan (misalnya, diperkecil dengan faktor $f=4$ atau $f=8$). Hal ini membuat proses pelatihan dan pengambilan sampel (*sampling*) menjadi jauh lebih cepat.
- **Fokus pada Prior Semantik**: Model difusi berbasis piksel menghabiskan banyak kapasitas untuk memodelkan detail frekuensi tinggi (seperti butiran tekstur individual). Dengan menggunakan autoencoder untuk menyaring derau bising frekuensi tinggi yang tidak terlihat, LDM dapat memfokuskan kapasitas parameternya untuk mempelajari tata letak semantik tingkat tinggi dan komposisi data.
- **Pengondisian Fleksibel**: LDM mengintegrasikan lapisan *cross-attention* ke dalam tulang punggung UNet, memungkinkan model dikondisikan pada berbagai modalitas seperti deskripsi teks (melalui encoder teks seperti CLIP atau BERT), kotak pembatas (*bounding boxes*), atau peta semantik.

## Lihat Juga

- [[perceptual-image-compression-id]]
- [[stable-diffusion-id]]
- [[compvis-id]]
