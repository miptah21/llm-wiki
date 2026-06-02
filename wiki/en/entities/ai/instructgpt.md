---
type: entity
category: model
domain: ai
lang: en
translation: "[[instructgpt-id]]"
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Ouyang-2022]]"]
tags: [instructgpt, gpt-3, openai, llm]
---

# InstructGPT

**InstructGPT** is a family of large language models developed by [[openai]] that are fine-tuned using Reinforcement Learning from Human Feedback (RLHF) to follow instructions. First introduced in the paper *Training language models to follow instructions with human feedback* (Ouyang et al., 2022), InstructGPT represents the direct predecessor of ChatGPT.

## Development and Architecture

InstructGPT models use the GPT-3 transformer architecture and were trained in three sizes: 1.3B, 6B, and 175B parameters. Unlike standard GPT-3 models, which are optimized only for next-token prediction, InstructGPT is optimized using:
1. **Supervised Fine-Tuning (SFT)** on prompt-response pairs written by humans.
2. **Reward Modeling** on human preference rankings.
3. **Proximal Policy Optimization (PPO)** utilizing the reward model.

## Validation and Impact

InstructGPT demonstrated that optimizing for human preference ratings significantly improves usability. Despite having 100x fewer parameters, outputs from the 1.3B parameter InstructGPT model were preferred by human evaluators over the outputs of the 175B parameter base GPT-3 model. InstructGPT also showed substantial reductions in hallucination rates and toxic outputs.

## See Also

- [[openai]]
- [[reinforcement-learning-from-human-feedback]]
- [[supervised-fine-tuning]]
- [[reward-modeling]]
