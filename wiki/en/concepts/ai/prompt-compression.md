---
type: concept
domain: ai
lang: en
translation: "[[kompresi-prompt]]"
tags: [prompting, reasoning, LLM]
created: 2026-06-02
updated: 2026-06-02
sources: ["[[source-2509.20820v1]]"]
description: Techniques for reducing the length of LLM prompts while preserving their informational content, covering both demonstration compression and RAG input compression.
---

# Prompt Compression

**Prompt compression** refers to a family of techniques that reduce the token length of LLM inputs (prompts) while attempting to preserve the task-relevant information needed for accurate outputs.

## Categories

### Demonstration-Oriented Compression
- **[[cheat-sheet-icl]]:** Distills many-shot demonstrations into a concise textual summary in a single pass.
- **Instruction Induction:** Automatically generates task instructions from few-shot examples (Honovich et al., 2023; Zhou et al., 2023). Predates the many-shot regime and was not designed for efficiency under large demonstration sets.

### Knowledge/RAG Input Compression
- Focuses on shrinking retrieved documents or lengthy knowledge sources rather than demonstration sets.
- Often requires costly architectural or parameter changes, or iterative optimization over small subsets (Li et al., 2025).

## Cheat-Sheet ICL vs. Prior Work

Unlike most prior prompt compression methods, cheat-sheet ICL:
- Operates in a **single pass** without iterative optimization.
- Requires **no training or model modifications**.
- Targets **many-shot demonstration sets** specifically.
- Is evaluated against **many-shot ICL baselines** rather than zero-/few-shot benchmarks.

## See Also

- [[cheat-sheet-icl]]
- [[knowledge-distillation]]
- [[many-shot-in-context-learning]]
