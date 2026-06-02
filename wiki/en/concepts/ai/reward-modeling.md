---
type: concept
domain: ai
lang: en
translation: "[[pemodelan-reward]]"
tags: [rm, reward-model, alignment, preference-learning]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Ouyang-2022]]"]
description: Training a model to output a scalar score representing the human preference rating for a given input-output pair.
---

# Reward Modeling (RM)

**Reward Modeling (RM)** is a phase in Reinforcement Learning from Human Feedback (RLHF) where a neural network is trained to act as a proxy for human evaluators. The reward model takes a prompt and a candidate completion as input and outputs a scalar value representing the predicted quality or desirability of that completion to a human evaluator.

## Loss Function & Training

Rather than asking human evaluators to assign absolute numerical scores to model outputs (which is highly subjective and inconsistent), evaluators are asked to rank multiple completions ($K = 4$ to $K = 9$) for a single prompt. This generates pairwise comparison data.

To train the reward model, Ouyang et al. (2022) utilize a pairwise cross-entropy loss function. For a prompt $x$, a preferred completion $y_w$, and a less-preferred completion $y_l$:

$$\text{loss}(\theta) = -\frac{1}{\binom{K}{2}} \mathbb{E}_{(x, y_w, y_l) \sim D} \left[ \log\left(\sigma\left(r_\theta(x, y_w) - r_\theta(x, y_l)\right)\right) \right]$$

Where:
- $r_\theta(x, y)$ is the scalar score output by the reward model with parameters $\theta$ for prompt $x$ and completion $y$.
- $\sigma(z) = \frac{1}{1 + \exp(-z)}$ is the sigmoid function.
- $\binom{K}{2}$ is the number of pairwise comparisons derived from ranking $K$ completions.
- $D$ is the comparison dataset.

## System Efficiency & Overfitting

- **Batching Comparisons**: Training on all $\binom{K}{2}$ pairwise combinations from a single prompt in a single batch is computationally efficient. Instead of running $K(K-1)$ forward passes, the reward model only needs a single forward pass for the $K$ completions, after which the differences in logits are computed.
- **Overfitting Avoidance**: If pairwise comparisons are shuffled independently across batches, the model overfits on repeated completions. Keeping all comparisons from a single prompt within the same batch prevents this overfitting behavior.
- **Scaling Tradeoffs**: In practice, a smaller reward model (e.g., 6B parameters instead of 175B) is often used to save compute and improve training stability during the downstream reinforcement learning stage.

## See Also

- [[reinforcement-learning-from-human-feedback]]
- [[supervised-fine-tuning]]
- [[alignment-tax]]
