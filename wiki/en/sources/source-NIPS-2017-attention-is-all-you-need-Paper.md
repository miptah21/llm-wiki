---
type: source
source_file: "C:/Users/mifta/Documents/Obsidian Vault/remote-blog/01-TODO/2026/My-Wiki/raw/papers/NIPS-2017-attention-is-all-you-need-Paper.pdf"
sha256: d87d482d5ae7960e2e43d7dd6d21377e60e73e8fce1bf2a01aff7aca8a08c537
created: 2026-06-03
updated: 2026-06-03
translation: "[[source-NIPS-2017-attention-is-all-you-need-Paper-id]]"
tags: [ingested, paper, transformer, attention, deep-learning]
---

# Source Summary: Attention Is All You Need (NIPS 2017)

## Overview

- **Title**: Attention Is All You Need
- **Authors**: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, Illia Polosukhin
- **Venue**: Advances in Neural Information Processing Systems (NIPS) 2017
- **Core Contribution**: Introduces the [[transformer-architecture]], a sequence-to-sequence model built entirely on [[self-attention-mechanism]]s, discarding recurrent (RNN) and convolutional (CNN) architectures.

## Key Sections Summary

### 1. Introduction & Background
Traditionally, sequence transduction models rely on recurrent models (LSTMs, GRUs) or CNNs. Recurrent models process inputs sequentially, hindering parallelization during training. The Transformer eliminates recurrence entirely, computing representations of inputs and outputs in parallel using self-attention.

### 2. Architecture
The model utilizes an encoder-decoder architecture:
- **Encoder**: $N = 6$ identical layers. Each layer has a multi-head self-attention sub-layer followed by a position-wise feed-forward network.
- **Decoder**: $N = 6$ identical layers. It includes a masked self-attention layer (preventing leftward information flow to preserve auto-regressive properties) and an encoder-decoder attention layer that attends over the encoder outputs.

### 3. Attention Mechanisms
- **Scaled Dot-Product Attention**: $\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$. The scale factor $\frac{1}{\sqrt{d_k}}$ prevents small gradients when $d_k$ is large.
- **Multi-Head Attention**: Performs projection of queries, keys, and values to lower-dimensional subspaces $h$ times in parallel. This allows the model to attend to information from different representation subspaces.

### 4. Positional Encoding
Since the model contains no recurrence or convolution, sine and cosine functions of different frequencies are added to the input embeddings to inject positional information:
$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)$$
$$PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)$$

### 5. Results
- Achieved state-of-the-art BLEU score of $28.4$ on WMT 2014 English-to-German translation.
- Achieved $41.0$ BLEU score on WMT 2014 English-to-French translation, training for a fraction of the cost of previous models.

## Core Concepts

- [[transformer-architecture]]
- [[self-attention-mechanism]]
