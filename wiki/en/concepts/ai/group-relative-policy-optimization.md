---
type: concept
domain: ai
lang: en
translation: "[[group-relative-policy-optimization-id]]"
tags: [grpo, reinforcement-learning, algorithm, optimization]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-DeepSeek-2025]]"]
description: A policy gradient reinforcement learning algorithm that estimates baselines from group average scores instead of maintaining a critic network.
---

# Group Relative Policy Optimization (GRPO)

**Group Relative Policy Optimization (GRPO)** is an efficient policy gradient reinforcement learning algorithm introduced by Shao et al. (2024) and popularized by DeepSeek-AI (2025) during the training of DeepSeek-R1. GRPO optimizes models by comparing a group of outputs generated for a single prompt, eliminating the need for a separate critic model (which is typically of equal size to the policy model), thereby saving significant memory and computational cost.

## Algorithmic Formulation

For each question $q$, GRPO samples a group of outputs $\{o_1, o_2, \dots, o_G\}$ from the old policy $\pi_{\theta_{\text{old}}}$. The policy model $\pi_\theta$ is optimized by maximizing the following objective function:

$$\mathcal{J}_{\text{GRPO}}(\theta) = \frac{1}{G} \sum_{i=1}^{G} \left( \min\left(\frac{\pi_\theta(o_i \mid q)}{\pi_{\theta_{\text{old}}}(o_i \mid q)} A_i, \, \text{clip}\left(\frac{\pi_\theta(o_i \mid q)}{\pi_{\theta_{\text{old}}}(o_i \mid q)}, 1-\epsilon, 1+\epsilon\right) A_i\right) - \beta \text{D}_{\text{KL}}\left(\pi_\theta \parallel \pi_{\text{ref}}\right) \right)$$

Where:
- $G$ is the group size.
- $\epsilon$ and $\beta$ are hyperparameters.
- $\pi_{\text{ref}}$ is the reference policy (usually the SFT model).
- $\text{D}_{\text{KL}}(\pi_\theta \parallel \pi_{\text{ref}})$ is the Kullback-Leibler divergence computed as:
  $$\text{D}_{\text{KL}}(\pi_\theta \parallel \pi_{\text{ref}}) = \frac{\pi_{\text{ref}}(o_i \mid q)}{\pi_\theta(o_i \mid q)} - \log\frac{\pi_{\text{ref}}(o_i \mid q)}{\pi_\theta(o_i \mid q)} - 1$$
- $A_i$ is the relative advantage of output $o_i$ within the group, calculated based on the rewards $\{r_1, r_2, \dots, r_G\}$:
  $$A_i = \frac{r_i - \text{mean}(\{r_1, r_2, \dots, r_G\})}{\text{std}(\{r_1, r_2, \dots, r_G\})}$$

## Comparison to PPO

In standard [[proximal-policy-optimization]] (PPO):
- A secondary "critic" network is trained to predict the value function of a state. The advantage function is calculated relative to this value function.
- If the policy model has $N$ parameters, the critic model usually has another $N$ parameters, doubling the active memory requirements.

In GRPO:
- The baseline is the average reward of the group.
- The relative performance (z-score) of each output in the group acts as the advantage.
- Memory consumption is significantly reduced, allowing for larger batch sizes and large-scale training of LLMs.

## See Also

- [[proximal-policy-optimization]]
- [[reinforcement-learning-from-human-feedback]]
- [[reward-modeling]]
