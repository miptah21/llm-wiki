---
type: source
source_file: "raw/papers/DeepSeek-2025.pdf"
sha256: "52d8ca3ac93e88cef9944e1fd03b0e04aec5954495a8250fb2fadf8fa20a4dad"
created: 2026-06-03
updated: 2026-06-03
translation: "[[source-DeepSeek-2025-id]]"
tags: [ingested, RL, reasoning, deepseek, grpo]
---

# Source Summary: DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning

**DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning** (DeepSeek-AI, 2025) is a landmark paper that explores the development of advanced reasoning capabilities in large language models using large-scale reinforcement learning (RL). It introduces **DeepSeek-R1-Zero**, a model trained purely via RL without supervised fine-tuning (SFT) as a cold start, and **DeepSeek-R1**, which incorporates a multi-stage training pipeline (SFT + RL) to improve readability, eliminate language mixing, and align with human preferences.

## Overview

Historically, reasoning models have relied heavily on supervised data. DeepSeek-AI demonstrates that reasoning capabilities (such as self-verification, reflection, and long Chain-of-Thought generation) can emerge purely through reinforcement learning on base models. 

To achieve this efficiently, they use the **Group Relative Policy Optimization (GRPO)** algorithm, which estimates reinforcement learning baselines from group scores rather than maintaining a large critic model. The paper also validates the power of **knowledge distillation**, showing that the reasoning patterns discovered by frontier models can be directly distilled into smaller dense models (1.5B to 70B parameter models based on Qwen and Llama), making them highly competitive with closed-source models.

## Core Methodology

The paper presents two main models and a distillation pipeline:

### 1. DeepSeek-R1-Zero (Pure RL)
Directly applies RL to `DeepSeek-V3-Base` without a preliminary SFT cold-start phase.
- **Reward Signal**: Evaluated using rule-based metrics:
  - *Accuracy rewards*: Program compilers for coding (e.g., LeetCode) and format checkers/match checkers for math deterministic answers.
  - *Format rewards*: Restricts outputs to place thinking processes between `<think>` and `</think>` tags.
- **Emergent Behaviors**: Naturally develops reflection, backtracking, self-correction, and an "aha moment" where the model re-evaluates its reasoning steps mid-generation.
- **Drawbacks**: Suffers from poor readability, structural chaos, and language mixing.

### 2. DeepSeek-R1 (Multi-Stage Pipeline)
To overcome DeepSeek-R1-Zero's limitations, DeepSeek-R1 is trained using a four-stage pipeline:
1. **Cold Start**: Fine-tune `DeepSeek-V3-Base` on thousands of human-in-the-loop and model-generated long CoT reasoning demonstrations to bootstrap the RL process.
2. **Reasoning-oriented RL**: Apply RL using GRPO. An accuracy reward is combined with a *language consistency reward* to prevent language mixing in the CoT.
3. **Rejection Sampling & SFT**: Perform rejection sampling on the Stage 2 checkpoint to gather 600k high-quality reasoning trajectories. Combine these with 200k non-reasoning samples (writing, QA, translation) from `DeepSeek-V3`'s dataset. Fine-tune the base model on this combined 800k dataset for two epochs.
4. **RL for all Scenarios**: A second RL stage using GRPO that aligns the model with human preferences on helpfulness (evaluated on the final summary) and harmlessness (evaluated on both CoT and summary).

### 3. Distillation
Distills the 800k curated SFT reasoning dataset from DeepSeek-R1 to smaller open-source base models (Qwen2.5 and Llama3). This direct SFT distillation yields superior results compared to applying RL directly on the smaller models.

## Key Findings & Benchmark Performance

- **Reasoning Capabilities**: DeepSeek-R1 achieves a **79.8% Pass@1 on AIME 2024** and **97.3% on MATH-500**, matching or slightly exceeding OpenAI-o1-1217.
- **Coding Elo**: Achieves a **2,029 Elo rating on Codeforces**, outperforming 96.3% of human participants.
- **Distilled Efficiency**: DeepSeek-R1-Distill-Qwen-32B achieves 72.6% on AIME 2024, significantly outperforming other open-source models and matching o1-mini.

## Core Concepts

- [[group-relative-policy-optimization]]
- [[reinforcement-learning-from-human-feedback]]
- [[knowledge-distillation]]

## Core Entities

- [[deepseek-r1-zero]]
- [[deepseek-r1]]
