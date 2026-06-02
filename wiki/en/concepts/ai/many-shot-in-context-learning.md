---
type: concept
domain: ai
lang: en
translation: "[[many-shot-in-context-learning-id]]"
tags: [in-context-learning, LLM, few-shot-learning, long-context]
created: 2026-06-02
updated: 2026-06-02
sources: ["[[source-2509.20820v1]]"]
description: An ICL regime that provides LLMs with hundreds or thousands of demonstrations by leveraging extended context windows, yielding superior performance over conventional few-shot ICL on pattern-recognition tasks.
---

# Many-Shot In-Context Learning

**Many-shot in-context learning (ICL)** is a paradigm where LLMs are provided with a large number of task-specific demonstrations (typically 100–1000+) within their context window, as opposed to the conventional few-shot setting (2–32 examples).

## Background

Standard ICL (Brown et al., 2020) conditions the LLM on a few demonstrations $D_n = \{(x_i, y_i)\}_{i=1}^{n}$ alongside the test input to produce predictions. Due to context window limitations, $n$ was traditionally small (few-shot).

With extended context windows in models like Gemini 1.5 Pro (1M+ tokens) and GPT-4.1 (128K+ tokens), $n$ can be increased by orders of magnitude — this is the **many-shot** regime.

## Key Findings (Agarwal et al., 2024; Bertsch et al., 2025)

- Performance improves log-linearly with the number of demonstrations on many tasks.
- Many-shot ICL is **training-free** — no parameter updates required.
- Can be applied to proprietary models that don't support fine-tuning.
- Particularly effective on **pattern-recognition tasks** (e.g., BIG-Bench Hard) rather than tasks requiring general academic knowledge already well-encoded in pretraining.

## Drawbacks

1. **Computational cost:** Processing tens of thousands of input tokens per inference is expensive. Even with prefix caching, decoding must attend over the full long context.
2. **API costs:** Cached prefixes are often evicted after short intervals or require paid persistence.
3. **Format degradation:** Very long contexts can distract the model from output format adherence.
4. **Diminishing returns:** Tasks already well-solved by the model show no gains (e.g., MATH500, GSM8K with GPT-4.1).

## Efficiency Alternatives

- [[demonstration-retrieval-for-icl]] — Select relevant demonstrations per query.
- [[cheat-sheet-icl]] — Distill demonstrations into a compact textual summary.
- Attention modification techniques (Yuan et al., 2024) — Require model parameter access.

## See Also

- [[in-context-learning]]
- [[reinforced-icl]]
- [[chain-of-thought-prompting]]
