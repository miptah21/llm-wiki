---
type: source
source_file: "raw/papers/Rombach-2022.pdf"
sha256: "5e2b3a5c07d5ed193d5d115270c8a601732c6d8a25dc25fa0c9448dac53c9a82"
created: 2026-06-03
updated: 2026-06-03
translation: "[[source-Rombach-2022-id]]"
tags: [ingested, diffusion, LDM, image-synthesis, generative-ai]
---

# Source Summary: High-Resolution Image Synthesis with Latent Diffusion Models

**High-Resolution Image Synthesis with Latent Diffusion Models** (Rombach et al., 2022) is the foundational paper from [[compvis]] that introduces **Latent Diffusion Models (LDMs)**, which later became commercially known as **Stable Diffusion**. The paper presents a novel two-stage generative modeling approach that separates perceptual compression from semantic generation, dramatically reducing the computational resources required to train and run diffusion models.

## Overview

Although traditional diffusion models (DMs) achieve state-of-the-art results in image synthesis, they are computationally expensive because they operate directly in pixel space, requiring massive training times (hundreds of GPU days) and costly iterative evaluations during inference.

Rombach et al. address this by training diffusion models within the lower-dimensional latent space of a powerful, pre-trained autoencoder. By abstracting away imperceptible, high-frequency details during the autoencoding stage, the diffusion model can focus its capacity on learning the semantic composition of the data. To enable flexible, multi-modal generation (such as text-to-image), they integrate cross-attention layers into the UNet backbone of the diffusion model.

## Core Methodology

The LDM framework divides training into two distinct phases:

### 1. Perceptual Image Compression (Stage 1)
An autoencoder consisting of an encoder $\mathcal{E}$ and a decoder $\mathcal{D}$ is trained on a large dataset.
- **Encoder Mapping**: Converts an image $x \in \mathbb{R}^{H \times W \times 3}$ into a latent representation $z = \mathcal{E}(x) \in \mathbb{R}^{h \times w \times c}$, reducing spatial dimensions by a downsampling factor $f = H/h = W/w$.
- **Loss Function**: Combined perceptual loss and a patch-based adversarial objective to enforce local realism on reconstructed images $\tilde{x} = \mathcal{D}(z)$.
- **Regularization**: To prevent high-variance latent spaces, they utilize either:
  - *KL-reg*: Imposes a mild Kullback-Leibler penalty towards a standard normal distribution (similar to a VAE).
  - *VQ-reg*: Imposes a vector quantization layer within the decoder (similar to a VQGAN).

### 2. Latent Diffusion Models (Stage 2)
The diffusion model is trained within the learned, frozen latent space $z$.
- **Objective Function**: Optimized using a reweighted denoising score-matching objective:
  $$\mathcal{L}_{\text{LDM}} := \mathbb{E}_{\mathcal{E}(x), \epsilon \sim \mathcal{N}(0,1), t} \left[ \|\epsilon - \epsilon_\theta(z_t, t)\|^2_2 \right]$$
  where $z_t$ is the noisy latent at timestep $t$, and $\epsilon_\theta$ is the UNet-based denoising autoencoder.

### 3. Multi-Modal Conditioning (Cross-Attention)
To support conditioning inputs $y$ (such as text prompts, semantic maps, or layouts), the UNet backbone is augmented with cross-attention layers:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d}}\right) \cdot V$$
where $Q = W_Q^{(i)} \cdot \phi_i(z_t)$ represents flattened intermediate UNet states, and $K = W_K^{(i)} \cdot \tau_\theta(y)$ and $V = W_V^{(i)} \cdot \tau_\theta(y)$ project the conditioned features via a domain-specific encoder $\tau_\theta$.

The conditional objective is:
$$\mathcal{L}_{\text{LDM-cond}} := \mathbb{E}_{\mathcal{E}(x), y, \epsilon \sim \mathcal{N}(0,1), t} \left[ \|\epsilon - \epsilon_\theta(z_t, t, \tau_\theta(y))\|_2^2 \right]$$

## Key Findings & Benchmark Performance

- **Optimal Compression Ratios**: The authors evaluate downsampling factors $f \in \{1, 2, 4, 8, 16, 32\}$ and find that LDM-4 and LDM-8 offer the optimal balance between high-fidelity reconstruction and efficient sampling speed.
- **Unconditional Synthesis**: Achieves a new state-of-the-art FID of **5.11 on CelebA-HQ**, outperforming prior GANs and joint likelihood-based models like LSGM.
- **Text-to-Image Synthesis**: Conditioned on language prompts via a BERT-tokenizer and transformer, the LDM outperforms larger autoregressive models (like DALL-E and CogView) on MS-COCO benchmarks, scoring an **FID of 12.61** with classifier-free guidance.

## Core Concepts

- [[latent-diffusion-models]]
- [[perceptual-image-compression]]

## Core Entities

- [[compvis]]
- [[stable-diffusion]]
