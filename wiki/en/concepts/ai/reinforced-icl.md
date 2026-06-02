---
type: concept
domain: ai
lang: en
translation: "[[reinforced-icl-id]]"
tags: [in-context-learning, rationale-augmentation, chain-of-thought]
created: 2026-06-02
updated: 2026-06-02
sources: ["[[source-2509.20820v1]]"]
description: An improved ICL baseline that augments demonstrations with model-generated chain-of-thought rationales, selecting correct reasoning paths to boost performance across shot counts.
---

# Reinforced ICL

**Reinforced ICL** (Agarwal et al., 2024) is an enhanced in-context learning baseline that augments each demonstration with a model-generated rationale — a chain-of-thought reasoning path that leads to the correct answer.

## Mechanism

1. For each demonstration $(x_i, y_i)$, sample multiple chain-of-thought (CoT) reasoning paths from the LLM.
2. Select only the paths that arrive at the correct answer $y_i$.
3. The augmented demonstration set becomes $\hat{D}_n = \{(x_i, \hat{r}_i, y_i)\}_{i=1}^{n}$.

## X-ICL Efficiency Improvement

He et al. (2024) proposed a more efficient rationale augmentation method used in the cheat-sheet ICL paper:
- Instead of sampling multiple paths and filtering, condition the LLM on both the input $x_i$ **and** the correct label $y_i$ when generating the explanation $\hat{r}$.
- This produces a correct rationale with a single sampling, avoiding wasted generations.

## Impact

Reinforced ICL was shown to outperform vanilla ICL across a broad range of shot counts. It serves as the baseline for all ICL variants in Honda et al. (2025), including [[cheat-sheet-icl]], [[many-shot-in-context-learning]], and [[demonstration-retrieval-for-icl]].

## See Also

- [[chain-of-thought-prompting]]
- [[in-context-learning]]
