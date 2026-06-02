---
type: concept
domain: ai
lang: en
translation: "[[supervised-fine-tuning-id]]"
tags: [sft, fine-tuning, training, deep-learning]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Ouyang-2022]]"]
description: The process of fine-tuning a pretrained language model on a high-quality dataset of prompt-demonstration pairs using supervised learning.
---

# Supervised Fine-Tuning (SFT)

**Supervised Fine-Tuning (SFT)** is the first step in the alignment process of large language models (LLMs). It transitions a raw, next-token-prediction pretrained model into a policy that can follow user instructions, answer questions, and perform specific tasks by training it on a curated dataset of prompt-response pairs.

## Methodology

During SFT, the model's parameters are updated using standard supervised learning. The training set consists of input prompts $x$ paired with gold-standard demonstration responses $y$ written by human annotators:

$$D_{\text{SFT}} = \{(x_1, y_1), (x_2, y_2), \dots, (x_n, y_n)\}$$

The model is optimized using a standard autoregressive cross-entropy loss, computed only on the tokens of the target sequence $y$:

$$\mathcal{L}_{\text{SFT}}(\theta) = -\sum_{i=1}^{|y|} \log P_\theta(y_i \mid y_{<i}, x)$$

## Key Characteristics & Challenges

- **Overfitting**: During SFT, LLMs tend to overfit on the validation loss quickly (often after just 1 epoch). However, training for more epochs (e.g., up to 16 epochs in Ouyang et al., 2022) is often beneficial for downstream human evaluation ratings and reward model scores, despite the nominal validation loss regression.
- **Data Quality over Quantity**: High-quality, diverse demonstrations (written by skilled annotators) are far more effective for instruction alignment than massive amounts of scraped or synthetic data.
- **Limitation**: While SFT yields high-quality outputs, it remains limited to replicating the exact style of demonstrations and does not scale efficiently to capture complex human preferences or complex multi-objective tradeoffs. Hence, SFT is typically followed by [[reward-modeling]] and reinforcement learning.

## See Also

- [[reinforcement-learning-from-human-feedback]]
- [[reward-modeling]]
- [[alignment-tax]]
