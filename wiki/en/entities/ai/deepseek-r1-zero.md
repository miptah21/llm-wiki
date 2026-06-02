---
type: entity
category: model
domain: ai
lang: en
translation: "[[deepseek-r1-zero-id]]"
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-DeepSeek-2025]]"]
tags: [deepseek, deepseek-r1-zero, llm, reasoning, RL]
---

# DeepSeek-R1-Zero

**DeepSeek-R1-Zero** is an experimental large language model developed by DeepSeek-AI (2025) that exhibits advanced reasoning capabilities trained purely via reinforcement learning (RL) without any prior Supervised Fine-Tuning (SFT) or cold-start data.

## Training and Mechanics

DeepSeek-R1-Zero was initialized directly from the `DeepSeek-V3-Base` model and optimized using the **Group Relative Policy Optimization (GRPO)** algorithm. 
- **Objectives**: Rather than using neural reward models (which are prone to reward hacking), training relied on deterministic rule-based rewards:
  - *Accuracy reward*: Verification of answers via compiler feedback (for coding tasks) or format validation (for mathematical derivations).
  - *Formatting reward*: Enforcing the model to put its reasoning process between `<think>` and `</think>` tags.
- **Emergent Chain-of-Thought (CoT)**: Over thousands of RL training steps, the model naturally learned to think longer, developing behaviors like reflection, backtracking, and self-correction. 
- **The "Aha Moment"**: Researchers observed a fascinating transition stage where the model learned to pause, identify errors in its own math calculations, and restart its derivation using anthropomorphic internal dialogue (e.g., writing "Wait, wait. That's an error...").

## Drawbacks

While demonstrating high reasoning scores (e.g., 71.0% on AIME 2024), DeepSeek-R1-Zero suffered from:
- **Poor Readability**: The thinking process was often unstructured or difficult for humans to read.
- **Language Mixing**: The model would frequently mix English, Chinese, and other languages in its Chain-of-Thought, especially when prompted with multilingual queries.

These limitations prompted the development of its successor, [[deepseek-r1]].

## See Also

- [[deepseek-r1]]
- [[group-relative-policy-optimization]]
- [[reinforcement-learning-from-human-feedback]]
