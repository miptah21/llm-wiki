---
type: concept
domain: ai
lang: en
translation: "[[chain-of-thought-prompting-id]]"
tags: [prompting, reasoning, LLM]
created: 2026-06-02
updated: 2026-06-02
sources: ["[[source-2509.20820v1]]"]
description: A prompting technique that elicits step-by-step reasoning from LLMs by including intermediate reasoning steps in demonstrations, significantly improving performance on complex tasks.
---

# Chain-of-Thought Prompting

**Chain-of-thought (CoT) prompting** (Wei et al., 2022) is a technique that improves LLM reasoning by providing demonstrations that include explicit intermediate reasoning steps — a "chain of thought" — rather than just input-output pairs.

## Core Idea

Instead of:
```
Q: Roger has 5 tennis balls...
A: 11
```

CoT prompting uses:
```
Q: Roger has 5 tennis balls...
A: Roger started with 5. He bought 2 cans of 3 = 6. 5 + 6 = 11. The answer is 11.
```

This encourages the model to decompose complex problems into step-by-step reasoning before arriving at the final answer.

## Role in Cheat-Sheet ICL

In Honda et al. (2025), all ICL methods use **rationale-augmented demonstrations** following [[reinforced-icl]]:
- Each demonstration includes a model-generated CoT rationale.
- The cheat-sheet creation prompt receives these rationale-augmented demonstrations.
- Even cheat-sheet ICL without rationale augmentation remains effective, demonstrating robustness.

## Extensions

- **Self-consistency** (Wang et al., 2023): Sample multiple CoT paths and take majority vote.
- **[[reinforced-icl]]**: Filter CoT paths to keep only those leading to correct answers.

## See Also

- [[reinforced-icl]]
- [[cheat-sheet-icl]]
- [[in-context-learning]]
