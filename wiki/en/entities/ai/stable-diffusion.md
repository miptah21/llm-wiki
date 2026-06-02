---
type: entity
category: model
domain: ai
lang: en
translation: "[[stable-diffusion-id]]"
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Rombach-2022]]"]
tags: [stable-diffusion, compvis, generative-ai, text-to-image]
---

# Stable Diffusion

**Stable Diffusion** is a widely popularized open-weights latent text-to-image diffusion model. Originally released in August 2022, the model is based on the research paper *High-Resolution Image Synthesis with Latent Diffusion Models* (Rombach et al., 2022) developed by [[compvis]] (LMU Munich), Runway ML, and Stability AI.

## Architecture and Technology

Stable Diffusion operates within the framework of [[latent-diffusion-models]]. Rather than generating images directly in pixel space, it runs the diffusion denoising process in a compressed latent space:
1. **Autoencoder (VAE)**: Compresses images into a latent space with a downsampling factor $f = 8$, reducing a $512 \times 512$ image to a $64 \times 64$ latent representation.
2. **Text Encoder**: Projects user-defined text prompts into a latent representation using the pre-trained CLIP text encoder (developed by OpenAI).
3. **U-Net**: A time-conditional network equipped with cross-attention layers that iteratively denoises the latent representation, guided by the text embedding.

## Impact and Release

Unlike previous state-of-the-art text-to-image generators (such as OpenAI's DALL-E 2 or Google's Imagen), which were kept closed-source, Stable Diffusion was released with open weights. This permitted developers and researchers to run high-resolution image synthesis locally on consumer-grade GPUs, triggering a massive wave of open-source generative AI tools, community fine-tunes (such as ControlNet and LoRAs), and commercial applications.

## See Also

- [[compvis]]
- [[latent-diffusion-models]]
- [[perceptual-image-compression]]
