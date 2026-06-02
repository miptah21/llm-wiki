---
type: concept
domain: ai
lang: en
tags: [x-icl, ICL, reinforced-icl, rationales, few-shot-learning]
created: 2026-06-02
updated: 2026-06-02
translation: "[[x-icl-id]]"
description: An in-context learning framework that augments few-shot or many-shot demonstrations with step-by-step rationales, leveraging reinforcement signals to select or refine the demonstrations.
---

# X-ICL (Rationale-Augmented In-Context Learning)

**X-ICL** refers to advanced variations of In-Context Learning where demonstrations are augmented with detailed explanation rationales (similar to Chain-of-Thought but reinforced or systematically selected). 

## Core Principles

Standard ICL maps inputs directly to targets:
$$x_i \to y_i$$

X-ICL introduces an intermediate rationale $r_i$ representing the thinking process:
$$x_i \to r_i \to y_i$$

By structuring demonstrations with high-quality, verified rationales, the LLM is guided to output similar rationales for the test input, dramatically improving reasoning performance on multi-step tasks.

## Relationship with Reinforced ICL

X-ICL is frequently paired with **Reinforced ICL** frameworks, where:
1. Explanations are drafted by a generator model.
2. A reward signal (e.g., accuracy on a development set) evaluates the quality of the explanation.
3. The prompt demonstrations are iteratively updated or pruned to maximize task performance.

Distilled versions of these configurations are used in methods like [[cheat-sheet-icl]], where rationales are summarized into a singular, human-debuggable rule sheet.

## Indonesian Counterpart

- [[x-icl]] (Indonesian translation note)
