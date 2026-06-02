---
type: concept
domain: ai
lang: en
translation: "[[model-difusi-laten]]"
tags: [diffusion, latent-diffusion, generative-model, image-synthesis]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Rombach-2022]]"]
description: A class of diffusion probabilistic models that operate within the lower-dimensional latent space of a pre-trained autoencoder to generate high-resolution data efficiently.
---

# Latent Diffusion Model (LDM)

A **Latent Diffusion Model (LDM)** is a type of generative model that applies a diffusion process inside the latent space of a pre-trained autoencoder rather than directly on high-dimensional pixel space. Introduced by Rombach et al. (2022), LDMs separate the training of generative models into two phases: perceptual compression (handled by the autoencoder) and semantic generation (handled by the diffusion process).

## Mechanics and Architecture

The training of an LDM is divided into two distinct steps:

1. **Perceptual Compression (Autoencoder)**: An autoencoder composed of an encoder $\mathcal{E}$ and a decoder $\mathcal{D}$ is trained. The encoder projects high-dimensional raw data $x$ (such as pixels) into a lower-dimensional latent representation $z = \mathcal{E}(x)$. The decoder is trained to reconstruct the original input from the latent code: $\tilde{x} = \mathcal{D}(z) \approx x$.
2. **Latent Diffusion (Score-Matching Prior)**: A diffusion model is trained within the learned latent space $z$. The model learns to reverse a forward diffusion process (which progressively adds noise to the latent representation) using a denoising autoencoder network $\epsilon_\theta$ implemented as a time-conditional UNet:
   $$\mathcal{L}_{\text{LDM}} := \mathbb{E}_{\mathcal{E}(x), \epsilon \sim \mathcal{N}(0,1), t} \left[ \|\epsilon - \epsilon_\theta(z_t, t)\|^2_2 \right]$$

## Advantages of Latent Space Diffusion

- **Computational Efficiency**: Because the diffusion process operates on a compressed latent representation, the spatial dimensions of the network evaluations are significantly reduced (e.g., downsampled by $f=4$ or $f=8$). This makes training and sampling exponentially faster.
- **Focus on Semantic Prior**: Pixel-based diffusion models spend significant capacity modeling high-frequency details (e.g., individual texture grains). By using a pre-trained autoencoder to filter out imperceptible high-frequency noise, the LDM can focus its parameter capacity on learning the high-level semantic layout and composition of the data.
- **Flexible Conditioning**: LDMs incorporate cross-attention layers in the UNet backbone, allowing the model to be conditioned on diverse modalities such as text descriptions (via text encoders like CLIP or BERT), bounding boxes, or semantic maps.

## See Also

- [[perceptual-image-compression]]
- [[stable-diffusion]]
- [[compvis]]
