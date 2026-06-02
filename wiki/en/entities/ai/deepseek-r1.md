---
type: entity
category: model
domain: ai
lang: en
translation: "[[deepseek-r1-id]]"
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-DeepSeek-2025]]"]
tags: [deepseek, deepseek-r1, llm, reasoning, RL]
---

# DeepSeek-R1

**DeepSeek-R1** is a state-of-the-art reasoning large language model developed by DeepSeek-AI (2025). Trained using a multi-stage pipeline combining Supervised Fine-Tuning (SFT) and Group Relative Policy Optimization (GRPO), DeepSeek-R1 demonstrates reasoning performance on par with closed-source models such as OpenAI-o1.

## Training Pipeline

DeepSeek-R1 resolves the readability and language-mixing issues of [[deepseek-r1-zero]] by employing a four-stage training methodology:

1. **Cold Start SFT**: Fine-tuning the base model (`DeepSeek-V3-Base`) on thousands of high-quality long Chain-of-Thought (CoT) reasoning demonstrations to establish readability and structure.
2. **Reasoning-Oriented RL**: Large-scale RL using GRPO. In addition to accuracy rewards, a *language consistency reward* is added to ensure the model thinks in the target language specified by the prompt.
3. **Rejection Sampling & SFT**: When RL converges, rejection sampling is used to generate 600k high-quality reasoning trajectories. These are merged with 200k non-reasoning SFT tasks (creative writing, translation, general QA) from the DeepSeek-V3 corpus. The base model is retrained on this 800k dataset for 2 epochs.
4. **RL for all Scenarios**: A final GRPO stage optimizing for helpfulness (evaluating the summary output) and harmlessness (evaluating both the CoT and summary).

## Performance and Knowledge Distillation

DeepSeek-R1 achieves exceptional results across standard reasoning benchmarks, scoring **79.8% Pass@1 on AIME 2024** and **97.3% on MATH-500**. 

The paper also shows that the reasoning patterns of DeepSeek-R1 can be distilled into smaller models. DeepSeek-AI released six distilled models (1.5B, 7B, 8B, 14B, 32B, 70B parameters) based on Qwen and Llama architectures. Notably, the distilled **Qwen-32B model achieves 72.6% on AIME 2024**, outperforming other open-source models and performing comparably to OpenAI-o1-mini.

## See Also

- [[deepseek-r1-zero]]
- [[group-relative-policy-optimization]]
- [[knowledge-distillation]]
