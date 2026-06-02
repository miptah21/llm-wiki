---
type: concept
domain: ai
lang: en
translation: "[[demonstration-retrieval-for-icl-id]]"
tags: [in-context-learning, retrieval, demonstration-selection]
created: 2026-06-02
updated: 2026-06-02
sources: ["[[source-2509.20820v1]]"]
description: A strategy for ICL that retrieves task demonstrations similar to each test input from a larger pool, improving performance while keeping the context short.
---

# Demonstration Retrieval for ICL

**Demonstration retrieval** is an approach to efficient in-context learning that selects a small subset of demonstrations from a large pool based on their similarity to each test input, rather than using all available demonstrations.

## Methods

| Method | Mechanism | Reference |
|--------|-----------|-----------|
| **BM25** | Exact-match term-frequency search | Liu et al. (2022) |
| **Cosine** | Cosine similarity in embedding space (e.g., Sentence-BERT) | Liu et al. (2022); Reimers & Gurevych (2019) |
| **Set-BSR** | BERTScore-based similarity capturing multiple aspects | Gupta et al. (2023) |

## Performance (from Honda et al., 2025)

Across 8 BBH tasks with GPT-4.1, retrieving 8 demonstrations per query:
- **Cosine:** 89.1% avg accuracy
- **Set-BSR:** 89.0%
- **BM25:** 86.9%
- **Cheat-Sheet ICL:** 90.0% (without test-time retrieval)

## Trade-offs vs. Cheat-Sheet ICL

| Aspect | Retrieval ICL | Cheat-Sheet ICL |
|--------|:---:|:---:|
| Per-query retrieval needed | Yes | No |
| Demonstration storage needed | Yes | No |
| Token length at inference | Low | Low |
| One-time setup | Build index | Create cheat sheet |

## See Also

- [[cheat-sheet-icl]]
- [[many-shot-in-context-learning]]
- [[in-context-learning]]
