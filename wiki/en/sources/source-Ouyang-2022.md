---
type: source
source_file: "raw/papers/Ouyang-2022.pdf"
sha256: "c1984bb50a5b90fddb895fdc3a0f72e5bc977148c9f63ef6040cbe7a3e1f0d98"
created: 2026-06-03
updated: 2026-06-03
translation: "[[source-Ouyang-2022-id]]"
tags: [ingested, RLHF, alignment, instructgpt]
---

# Source Summary: Training Language Models to Follow Instructions with Human Feedback

**Training Language Models to Follow Instructions with Human Feedback** (Ouyang et al., 2022) is the seminal paper from [[openai]] that introduces **InstructGPT**, a set of large language models aligned using **Reinforcement Learning from Human Feedback (RLHF)**. The paper demonstrates that optimizing language models for user intent rather than simply predicting the next token yields models that are safer, more helpful, and more honest, even at much smaller parameter scales.

## Overview

Traditional large language models (LMs), such as GPT-3, are trained to predict the next token on a massive corpus of web text. While capable of diverse tasks, these models are frequently misaligned with user intent: they may fabricate facts, generate toxic or biased outputs, or simply fail to follow instructions.

Ouyang et al. address this misalignment by using a three-step RLHF framework to align the GPT-3 baseline models with human preferences, culminating in the creation of InstructGPT. In human evaluations, outputs from a 1.3B parameter InstructGPT policy are preferred to those of the 175B parameter GPT-3 base model, despite having 100x fewer parameters.

## Core Methodology

The paper outlines a three-step reinforcement learning pipeline:

1. **Supervised Fine-Tuning (SFT)**: 
   Collect demonstration data from trained human contractors answering high-quality, diverse instruction prompts. Fine-tune the base GPT-3 model on this dataset using supervised learning.
   - *Detail*: SFT models tend to overfit validation loss after 1 epoch, but training for more epochs (up to 16) improves RM score and human preference ratings.

2. **Reward Modeling (RM)**:
   Generate multiple outputs ($K = 4$ to $K = 9$) from the SFT model for a single prompt. Have human labelers rank these outputs. Train a Reward Model (using a 6B parameter architecture for efficiency and stability) to predict human preference rankings.
   - *Loss function formulation*:
     $$\text{loss}(\theta) = -\frac{1}{\binom{K}{2}} \mathbb{E}_{(x, y_w, y_l) \sim D} \left[ \log\left(\sigma\left(r_\theta(x, y_w) - r_\theta(x, y_l)\right)\right) \right]$$
     where $r_\theta(x, y)$ is the scalar output of the RM, $y_w$ is the preferred output, and $y_l$ is the less preferred output.

3. **Reinforcement Learning via Proximal Policy Optimization (PPO)**:
   Fine-tune the SFT model in a bandit environment using PPO to maximize the reward predicted by the RM. A per-token KL divergence penalty from the SFT model is added to the reward to prevent over-optimization of the reward model.
   - *Objective Function (PPO-ptx)*:
     $$\text{objective}(\phi) = \mathbb{E}_{(x, y) \sim D_{\pi_{\text{RL}}}} \left[ r_\theta(x, y) - \beta \log \left( \frac{\pi_{\text{RL}}^\phi(y \mid x)}{\pi_{\text{SFT}}(y \mid x)} \right) \right] + \gamma \mathbb{E}_{x \sim D_{\text{pretrain}}} \left[ \log\left(\pi_{\text{RL}}^\phi(x)\right) \right]$$
     Here, the KL penalty coefficient $\beta$ restricts the policy divergence from SFT, while the pretraining loss coefficient $\gamma$ mitigates the [[alignment-tax]] on public NLP benchmarks.

## Key Findings & Contributions

- **Human Preference Validation**: InstructGPT outputs are highly preferred over GPT-3 baselines. The 175B InstructGPT model outputs are preferred to 175B GPT-3 outputs $85 \pm 3\%$ of the time.
- **Truthfulness and Toxicity**: On benchmarks like TruthfulQA, InstructGPT generates truthful and informative answers twice as often as GPT-3. Toxicity is reduced by approximately 25% when prompted to be respectful.
- **Generalization**: InstructGPT models generalize to instructions outside their direct training distribution (e.g., code execution, non-English prompts), showing that the model learns the generalized intent of "instruction following."
- **Alignment Tax Mitigation**: Reinforcement learning purely on RM feedback leads to regressions on standard NLP benchmarks (e.g., SQuAD, HellaSwag). Incorporating pretraining gradients (PPO-ptx) effectively preserves downstream capabilities while maintaining human alignment.

## Core Concepts

- [[reinforcement-learning-from-human-feedback]]
- [[supervised-fine-tuning]]
- [[reward-modeling]]
- [[alignment-tax]]

## Core Entities

- [[openai]]
- [[instructgpt]]
