---
type: concept
domain: ai
lang: en
translation: "[[dropout-regularization-id]]"
tags: [regularization, deep-learning, neural-network, overfitting, ingest]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Krizhevsky-2012]]"]
description: A regularization technique where hidden neurons are randomly zeroed out during training with a specified probability to prevent co-adaptation.
---

# Dropout Regularization

**Dropout** is a powerful regularization technique designed to prevent overfitting in deep neural networks.

## Mechanism

During training, dropout randomly sets the output of each hidden neuron to zero with a probability $p$ (commonly $p=0.5$).
- **Forward Pass**: The dropped-out neurons do not contribute to the forward propagation of activations.
- **Backward Pass**: These neurons do not participate in backpropagation, meaning their weights are not updated for that training step.
- **Weight Sharing**: Every training iteration effectively samples a different network architecture, but all these architectures share weights.
- **Inference/Test Time**: All neurons are active, but their outputs are multiplied by $(1-p)$ (e.g., 0.5) to approximate the geometric mean of the predictions produced by the exponentially many dropout networks.

## Rationale
By disabling random subsets of neurons, dropout prevents neurons from developing complex co-adaptations (where a neuron only learns features that are useful in the presence of specific other neurons). This forces each neuron to learn more robust, independent features that are useful in conjunction with random subsets of other neurons.

In [[source-Krizhevsky-2012]], dropout was applied to the first two fully-connected layers to combat substantial overfitting. While it halved the speed of convergence (doubled the number of iterations required), it was essential for training their 60-million-parameter network without severe overfitting.

## See Also

- [[deep-convolutional-neural-networks]]
- [[relu-nonlinearity]]

## Sources

- [[source-Krizhevsky-2012]]\n