---
type: concept
domain: ai
lang: en
translation: "[[big-bench-hard-id]]"
tags: [benchmark, reasoning, LLM-evaluation]
created: 2026-06-02
updated: 2026-06-02
sources: ["[[source-2509.20820v1]]"]
description: A suite of challenging reasoning tasks derived from BIG-Bench, specifically curated to be difficult enough that chain-of-thought prompting is needed to improve performance.
---

# BIG-Bench Hard

**BIG-Bench Hard (BBH)** (Suzgun et al., 2023) is a subset of the BIG-Bench benchmark (Srivastava et al., 2023) consisting of tasks that are particularly challenging for LLMs — specifically, tasks where prior models performed below average human raters.

## Role in Cheat-Sheet ICL Research

Honda et al. (2025) selected 8 BBH tasks where many-shot ICL outperformed few-shot ICL by >1 percentage point, making them a suitable testbed for evaluating whether cheat-sheet ICL can preserve many-shot performance with fewer tokens.

### Selected Tasks
1. **Boolean Expressions** — Evaluate boolean expressions with True/False, and/or/not.
2. **Causal Judgement** — Determine whether a typical person would agree with a causation claim.
3. **Disambiguation QA** — Identify pronoun antecedents or answer "ambiguous."
4. **Geometric Shapes** — Identify geometric shapes from SVG path elements.
5. **Movie Recommendation** — Select similar movies from a list.
6. **Salient Translation Error Detection** — Classify translation errors (German→English).
7. **Sports Understanding** — Judge plausibility of sports-related sentences.
8. **Word Sorting** — Alphabetically sort a list of words.

## Key Characteristic

BBH tasks are oriented toward **pattern recognition within datasets** rather than testing general academic knowledge. This makes them particularly suited for many-shot ICL evaluation with strong modern LLMs, since tasks requiring only general knowledge (e.g., MATH500, GSM8K) show no many-shot gains.

## See Also

- [[many-shot-in-context-learning]]
- [[cheat-sheet-icl]]
