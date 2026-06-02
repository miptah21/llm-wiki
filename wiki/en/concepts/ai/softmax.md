---
type: concept
domain: ai
lang: en
translation: "[[softmax-id]]"
tags: [activation-function, deep-learning, neural-network]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Krizhevsky-2012]]"]
description: An activation function that normalizes a vector of K real numbers into a probability distribution of K probabilities.
---

# Softmax Function

The **Softmax** function (also known as softargmax or normalized exponential function) is a mathematical function that takes as input a vector of $K$ real numbers, and normalizes it into a probability distribution consisting of $K$ probabilities proportional to the exponentials of the input numbers. 

Mathematically, it is defined as:
$$\\sigma(\\mathbf{z})_i = \\frac{e^{z_i}}{\\sum_{j=1}^{K} e^{z_j}}$$
for $i = 1, \\dotsc, K$ and $\\mathbf{z} = (z_1, \\dotsc, z_K) \\in \\mathbb{R}^K$.

## Use Cases

In deep learning:
- **Output Layer Activation**: Softmax is typically applied to the output layer of multi-class classification neural networks (e.g., [[source-Krizhevsky-2012]]) to map raw logit scores into probabilities that sum to 1.
- **Cross-Entropy Loss**: It is mathematically convenient when paired with cross-entropy loss for computing gradients during training.

## See Also

- [[deep-convolutional-neural-networks]]
- [[relu-nonlinearity]]

## Sources

- [[source-Krizhevsky-2012]]
