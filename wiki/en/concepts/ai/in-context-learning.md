---
type: concept
domain: ai
lang: en
tags: [in-context-learning, LLM, few-shot-learning, prompt-engineering]
created: 2026-06-02
updated: 2026-06-02
translation: "[[pembelajaran-dalam-konteks]]"
description: A paradigm in natural language processing where a pre-trained language model learns to perform tasks via input-target demonstrations provided inside its prompt, without any parameter updates.
---

# In-Context Learning

**In-Context Learning (ICL)** is a foundational capability of modern large language models (LLMs) that allows them to perform new tasks simply by reading a few examples provided in their input context (prompt), without updating their neural network weights.

## Mechanics

Under the ICL paradigm, a test query is accompanied by a small set of demonstration examples:
$$D = \{(x_1, y_1), (x_2, y_2), \dots, (x_n, y_n)\}$$

The prompt consists of these demonstrations followed by the target input $x_{\text{test}}$. The model completes the prompt by generating the corresponding prediction $y_{\text{test}}$, effectively performing task inference:
$$y_{\text{test}} \approx \arg\max_y P(y \mid D, x_{\text{test}})$$

## Key Attributes

- **Zero Parameter Changes**: The model weights are completely frozen.
- **Task Generalization**: A single model can switch between translation, summarization, and reasoning dynamically just by changing the prompt.
- **Emergent Behavior**: Standard few-shot ICL was popularized by GPT-3 (Brown et al., 2020) and emerges primarily in models above a certain parameter scale.

## Core Variants

- [[many-shot-in-context-learning]] — Providing hundreds or thousands of demonstrations.
- [[demonstration-retrieval-for-icl]] — Dynamically selecting the most relevant examples for each query.
- [[cheat-sheet-icl]] — Compressing demonstration knowledge into a high-level cheat sheet.
- [[chain-of-thought-prompting]] — Augmenting examples with step-by-step reasoning steps.

## Indonesian Counterpart

- [[in-context-learning]] (Indonesian translation note)
