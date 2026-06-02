---
type: concept
domain: ai
lang: en
translation: "[[pajak-penyelarasan]]"
tags: [alignment-tax, alignment, safety, evaluation]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Ouyang-2022]]"]
description: The performance cost or regression observed on standard NLP benchmarks when aligning a model to human preferences.
---

# Alignment Tax

The **Alignment Tax** refers to the performance cost or capabilities regression observed when a machine learning model is aligned to human preferences (such as safety and instruction following), compared to its unaligned, raw pretrained counterpart. 

## Context and Causes

When training a large language model using Reinforcement Learning from Human Feedback (RLHF), the model is optimized for human preference rankings on a specific distribution of prompts. Because this preference-maximizing objective differs from the raw pretraining objective (which maximizes the log likelihood of web text), it can cause the model to perform worse on generic, non-interactive NLP tasks.

In Ouyang et al. (2022), the baseline PPO models trained on the human prompt distribution suffered significant regressions on public NLP benchmarks, including:
- **SQuAD** (Question Answering)
- **DROP** (Reading Comprehension)
- **HellaSwag** (Common Sense Reasoning)
- **WMT 2015 French to English translation**

## Mitigation: The PPO-ptx Objective

To minimize this alignment tax, researchers proposed a modified PPO objective called **PPO-ptx**. This approach mixes gradients from the pretraining distribution back into the PPO updates.

The combined objective function is:

$$\text{objective}(\phi) = \mathbb{E}_{(x, y) \sim D_{\pi_{\text{RL}}}} \left[ r_\theta(x, y) - \beta \log \left( \frac{\pi_{\text{RL}}^\phi(y \mid x)}{\pi_{\text{SFT}}(y \mid x)} \right) \right] + \gamma \mathbb{E}_{x \sim D_{\text{pretrain}}} \left[ \log\left(\pi_{\text{RL}}^\phi(x)\right) \right]$$

Where:
- $\pi_{\text{RL}}^\phi$ is the learned RL policy.
- $\pi_{\text{SFT}}$ is the supervised fine-tuned model.
- $D_{\text{pretrain}}$ is the pretraining data distribution.
- $\beta$ controls the strength of the KL divergence penalty.
- $\gamma$ controls the weight of the pretraining gradients.

By setting a non-zero value for $\gamma$, the model is forced to maintain high log likelihood on pretraining text, effectively mitigating performance regression on downstream NLP tasks while preserving instruction-following improvements.

## See Also

- [[reinforcement-learning-from-human-feedback]]
- [[supervised-fine-tuning]]
- [[reward-modeling]]
