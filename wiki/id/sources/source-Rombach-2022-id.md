---
type: source
source_file: "raw/papers/Rombach-2022.pdf"
sha256: "5e2b3a5c07d5ed193d5d115270c8a601732c6d8a25dc25fa0c9448dac53c9a82"
created: 2026-06-03
updated: 2026-06-03
translation: "[[source-Rombach-2022]]"
tags: [ingested, diffusion, LDM, image-synthesis, generative-ai]
---

# Ringkasan Sumber: High-Resolution Image Synthesis with Latent Diffusion Models

**High-Resolution Image Synthesis with Latent Diffusion Models** (Rombach et al., 2022) adalah makalah ilmiah fundamental dari [[compvis-id]] yang memperkenalkan **Latent Diffusion Models (LDMs)**, yang kemudian secara komersial dikenal sebagai **Stable Diffusion**. Makalah ini menyajikan pendekatan pemodelan generatif dua tahap baru yang memisahkan kompresi perseptual dari pembangkitan semantik, sehingga menekan kebutuhan sumber daya komputasi secara drastis untuk melatih dan menjalankan model difusi.

## Tinjauan Umum (Overview)

Meskipun model difusi (*diffusion models* - DMs) tradisional mencapai hasil terbaik (*state-of-the-art*) dalam sintesis gambar, model-model ini sangat mahal secara komputasi karena beroperasi langsung di ruang piksel (*pixel space*). Hal ini memerlukan waktu pelatihan yang masif (ratusan hari GPU) dan evaluasi iteratif yang lambat selama proses inferensi.

Rombach dkk. mengatasi masalah ini dengan melatih model difusi di dalam ruang laten (*latent space*) berdimensi lebih rendah menggunakan autoencoder yang tangguh dan telah dilatih sebelumnya (*pre-trained*). Dengan mengaburkan detail frekuensi tinggi yang tidak terlihat oleh persepsi manusia selama tahap autoencoding, model difusi dapat memfokuskan kapasitasnya untuk mempelajari komposisi semantik dari data. Untuk memungkinkan pembangkitan multi-modal yang fleksibel (seperti teks-ke-gambar), mereka mengintegrasikan lapisan *cross-attention* ke dalam tulang punggung UNet dari model difusi.

## Metodologi Inti

Kerangka kerja LDM membagi pelatihan menjadi dua fase yang berbeda:

### 1. Kompresi Gambar Perseptual (Perceptual Image Compression - Tahap 1)
Sebuah autoencoder yang terdiri dari encoder $\mathcal{E}$ dan decoder $\mathcal{D}$ dilatih pada dataset gambar yang besar.
- **Pemetaan Encoder**: Mengubah gambar $x \in \mathbb{R}^{H \times W \times 3}$ menjadi representasi laten $z = \mathcal{E}(x) \in \mathbb{R}^{h \times w \times c}$, mengurangi dimensi spasial dengan faktor downsampling $f = H/h = W/w$.
- **Fungsi Kerugian (Loss Function)**: Gabungan dari *perceptual loss* dan target *adversarial* berbasis petak (*patch-based adversarial objective*) untuk memaksakan realisme lokal pada gambar hasil rekonstruksi $\tilde{x} = \mathcal{D}(z)$.
- **Regularisasi**: Untuk menghindari ruang laten dengan varians yang terlalu tinggi, mereka menggunakan salah satu dari:
  - *KL-reg*: Memaksakan penalti KL ringan terhadap distribusi normal standar (mirip dengan VAE).
  - *VQ-reg*: Memaksakan lapisan kuantisasi vektor (*vector quantization*) di dalam decoder (mirip dengan VQGAN).

### 2. Latent Diffusion Models (Tahap 2)
Model difusi dilatih di dalam ruang laten $z$ yang telah dipelajari dan dibekukan (*frozen*).
- **Fungsi Objektif**: Dioptimalkan menggunakan fungsi *denoising score-matching* yang ditimbang kembali:
  $$\mathcal{L}_{\text{LDM}} := \mathbb{E}_{\mathcal{E}(x), \epsilon \sim \mathcal{N}(0,1), t} \left[ \|\epsilon - \epsilon_\theta(z_t, t)\|^2_2 \right]$$
  di mana $z_t$ adalah laten bising pada langkah waktu $t$, dan $\epsilon_\theta$ adalah autoencoder penghilang bising (*denoising autoencoder*) berbasis UNet.

### 3. Pengondisian Multi-Modal (Cross-Attention)
Untuk mendukung masukan pengondisian $y$ (seperti prompt teks, peta semantik, atau tata letak), arsitektur UNet diperluas dengan lapisan *cross-attention*:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d}}\right) \cdot V$$
di mana $Q = W_Q^{(i)} \cdot \phi_i(z_t)$ mewakili keadaan tengah UNet yang diratakan, sedangkan $K = W_K^{(i)} \cdot \tau_\theta(y)$ dan $V = W_V^{(i)} \cdot \tau_\theta(y)$ memproyeksikan fitur kondisi melalui encoder khusus domain $\tau_\theta$.

Fungsi objektif bersyaratnya adalah:
$$\mathcal{L}_{\text{LDM-cond}} := \mathbb{E}_{\mathcal{E}(x), y, \epsilon \sim \mathcal{N}(0,1), t} \left[ \|\epsilon - \epsilon_\theta(z_t, t, \tau_\theta(y))\|_2^2 \right]$$

## Temuan Utama & Performa Benchmark

- **Rasio Kompresi Optimal**: Evaluasi faktor downsampling $f \in \{1, 2, 4, 8, 16, 32\}$ menunjukkan bahwa LDM-4 dan LDM-8 memberikan keseimbangan terbaik antara hasil rekonstruksi berkualitas tinggi dan kecepatan sampel yang efisien.
- **Sintesis Tanpa Kondisi (Unconditional)**: Meraih rekor FID terbaik sebesar **5.11 pada CelebA-HQ**, mengungguli model berbasis GAN sebelumnya dan model berbasis kemungkinan bersama (*joint likelihood-based*) seperti LSGM.
- **Sintesis Teks-ke-Gambar**: Dengan pengondisian prompt teks menggunakan tokeniser BERT dan transformer, LDM mengungguli model autoregresif yang lebih besar (seperti DALL-E dan CogView) pada benchmark MS-COCO, meraih **skor FID 12.61** menggunakan *classifier-free guidance*.

## Konsep Inti

- [[model-difusi-laten]]
- [[perceptual-image-compression-id]]

## Entitas Inti

- [[compvis-id]]
- [[stable-diffusion-id]]
