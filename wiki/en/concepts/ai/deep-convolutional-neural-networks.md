---
type: concept
domain: ai
lang: en
translation: "[[deep-convolutional-neural-networks-id]]"
tags: [cnn, neural-network, computer-vision, deep-learning, ingest]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Krizhevsky-2012]]"]
description: A class of deep neural networks commonly applied to analyzing visual imagery, using convolutional layers to capture spatial hierarchies.
---

# Deep Convolutional Neural Networks

A **Deep Convolutional Neural Network (CNN)** is a specialized deep learning architecture designed to process grid-structured data, such as images. CNNs utilize a mathematical operation called convolution in place of general matrix multiplication in at least one of their layers.

## Core Components

1. **Convolutional Layers**: Filter the input with learnable kernels (weights) to produce feature maps, capturing local patterns (edges, shapes, textures).
2. **Pooling Layers**: Downsample the feature maps to reduce spatial dimensionality and computational complexity, providing translational invariance. Overlapping pooling (e.g., stride $s = 2$, kernel size $z = 3$) can help reduce [[dropout-regularization|overfitting]].
3. **Activation Functions**: Introduce non-linearities. Modern architectures utilize [[relu-nonlinearity|ReLU]] to accelerate training.
4. **Fully-Connected Layers**: Perform final high-level reasoning and classification, typically mapped to a [[softmax]] distribution over classes.

## ImageNet Architecture (AlexNet)
The landmark architecture proposed in [[source-Krizhevsky-2012]] consists of:
- 5 convolutional layers (some followed by max-pooling and local response normalization).
- 3 fully-connected layers with a final 1000-way softmax.
- A total of 60 million parameters and 650,000 neurons, split across two GPUs.

## See Also

- [[relu-nonlinearity]]
- [[dropout-regularization]]

## Sources

- [[source-Krizhevsky-2012]]\n