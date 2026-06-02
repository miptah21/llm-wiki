---
type: concept
domain: ai
lang: en
translation: "[[perceptual-image-compression-id]]"
tags: [compression, autoencoder, latent-space, computer-vision]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Rombach-2022]]"]
description: A two-stage autoencoding method that projects images into a perceptually equivalent lower-dimensional space, removing high-frequency details while preserving semantic structure.
---

# Perceptual Image Compression

**Perceptual Image Compression** is a methodology in computer vision and deep learning that uses neural autoencoders to compress high-dimensional raw images into a lower-dimensional representation. Unlike standard compression algorithms (which minimize pixel-level error), perceptual compression aims to preserve the underlying semantic layout and visual realism of an image while discarding high-frequency noise that is imperceptible to the human eye.

## Architecture and Objectives

The system utilizes an encoder $\mathcal{E}$ and a decoder $\mathcal{D}$ trained on large datasets. To ensure that reconstructions are confined to the image manifold, the model combines three main losses during Stage 1 training:
1. **Pixel-Space Loss**: $L_1$ or $L_2$ differences between the original image $x$ and reconstruction $\tilde{x} = \mathcal{D}(\mathcal{E}(x))$.
2. **Perceptual Loss**: Comparison of deep feature representations extracted from pre-trained networks (e.g., VGG).
3. **Adversarial Loss**: A patch-based discriminator that enforces local realism, preventing blurriness.

## Regularization Strategies

To prevent the encoder from learning an arbitrary, high-variance latent space that is difficult for generative priors (like diffusion models) to learn, two forms of regularization are typically employed:
- **KL Regularization (KL-reg)**: Imposes a mild Kullback-Leibler divergence penalty towards a standard normal distribution on the latent space (similar to a Variational Autoencoder).
- **VQ Regularization (VQ-reg)**: Incorporates a vector quantization (VQ) codebook layer, mapping continuous latent codes to discrete indices (similar to VQGAN).

## Role in Generative Modeling

In two-stage generative modeling (such as [[latent-diffusion-models]] or VQGAN), perceptual image compression acts as the first stage. By abstracting away imperceptible noise, it allows the second stage generative model (e.g., a diffusion model or transformer) to train in a much smaller spatial dimension (e.g., downsampled by a factor $f = 4$ or $f = 8$), reducing training costs and increasing inference speeds.

## See Also

- [[latent-diffusion-models]]
- [[stable-diffusion]]
