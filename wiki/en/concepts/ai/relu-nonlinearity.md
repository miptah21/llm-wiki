---
type: concept
domain: ai
lang: en
translation: "[[relu-nonlinearity-id]]"
tags: [activation-function, deep-learning, neural-network, ingest]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Krizhevsky-2012]]"]
description: A non-saturating activation function defined as f(x) = max(0, x) that accelerates neural network training.
---

# ReLU Nonlinearity

The **Rectified Linear Unit (ReLU)** is a non-saturating activation function widely used in deep neural networks. Mathematically, it is defined as:
$$f(x) = \max(0, x)$$

## Advantages over Saturating Functions

Traditional activation functions like the logistic sigmoid ($f(x) = (1 + e^{-x})^{-1}$) or hyperbolic tangent ($f(x) = \tanh(x)$) saturate for large inputs, meaning their gradients become extremely close to zero. This leads to the vanishing gradient problem, which significantly slows down training.

In contrast, ReLU:
- **Does not saturate** in the positive domain (gradient is always 1 for $x > 0$), which mitigates vanishing gradients.
- **Enables sparse activation**, as any negative input maps to exactly zero.
- **Requires minimal computation** compared to exponentials, accelerating forward and backward passes.

In [[source-Krizhevsky-2012]], using ReLUs allowed a four-layer convolutional neural network to reach a 25% training error rate on CIFAR-10 six times faster than an equivalent network using tanh units.

## See Also

- [[deep-convolutional-neural-networks]]
- [[dropout-regularization]]

## Sources

- [[source-Krizhevsky-2012]]\n