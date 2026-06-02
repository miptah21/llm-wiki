---
type: source
source_file: "raw/papers/Krizhevsky-2012.pdf"
sha256: "90137160c57217953d5f61857e64ca58e85f06e1b13b4f475c918b1b582b9771"
created: 2026-06-03
updated: 2026-06-03
translation: "[[source-Krizhevsky-2012-id]]"
tags: [ingested, Krizhevsky-2012, cnn, relu, dropout, imagenet]
---

# Source Summary: ImageNet Classification with Deep Convolutional Neural Networks

This paper (often referred to as **AlexNet**) trained a large, deep convolutional neural network (CNN) to classify the 1.2 million high-resolution images in the ImageNet LSVRC-2010 contest into the 1000 different classes. On the test data, it achieved top-1 and top-5 error rates of 37.5% and 17.0%, significantly outperforming the previous state-of-the-art.

### Key Contributions & Architecture
- **ReLU Nonlinearity**: Replaces saturating activation functions (tanh, sigmoid) with non-saturating $\max(0, x)$, training six times faster.
- **Multi-GPU Training**: Spreads network parameters and computation across two GPUs with cross-GPU communication restrictions.
- **Local Response Normalization (LRN)**: A lateral inhibition mechanism that improves generalization.
- **Overlapping Pooling**: Overlapping pooling windows reduce overfitting.
- **Dropout**: Setting hidden neuron outputs to zero with probability 0.5 during training to prevent co-adaptation and overfitting.
- **Data Augmentation**: Reducing overfitting via image translations, horizontal reflections, and PCA-based RGB intensity adjustments.

## Core Concepts

- [[deep-convolutional-neural-networks]]
- [[relu-nonlinearity]]
- [[dropout-regularization]]

## Related Entities

- [[alex-krizhevsky]]
- [[ilya-sutskever]]
- [[geoffrey-hinton]]
- [[imagenet-dataset]]
- [[cuda-convnet]]