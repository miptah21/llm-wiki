---
type: concept
domain: ai
lang: en
translation: "[[proximal-policy-optimization-id]]"
tags: [ppo, reinforcement-learning, algorithm, optimization]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Ouyang-2022]]"]
description: A policy gradient reinforcement learning algorithm that uses a clipped objective function to ensure stable, incremental policy updates.
---

# Proximal Policy Optimization (PPO)

**Proximal Policy Optimization (PPO)** is a popular model-free reinforcement learning algorithm developed by OpenAI (Schulman et al., 2017). It is designed to perform stable, sample-efficient gradient updates on policy networks by preventing the new policy from deviating too far from the old policy.

## Clipped Objective Function

PPO achieves stable training by utilizing a clipped surrogate objective function. For a policy $\pi_\phi$ parameterized by $\phi$, the objective function restricts policy updates to a trusted region:

$$L^{\text{CLIP}}(\phi) = \hat{\mathbb{E}}_t \left[ \min\left(r_t(\phi)\hat{A}_t, \, \text{clip}(r_t(\phi), 1-\epsilon, 1+\epsilon)\hat{A}_t\right) \right]$$

Where:
- $r_t(\phi) = \frac{\pi_\phi(a_t \mid s_t)}{\pi_{\phi_{\text{old}}}(a_t \mid s_t)}$ is the probability ratio between the action under the new policy and the old policy.
- $\hat{A}_t$ is the estimated advantage at time step $t$, which measures how much better a chosen action is compared to the policy's average expectation.
- $\epsilon$ is a clipping hyperparameter (typically set between $0.1$ and $0.2$) that bounds the ratio $r_t(\phi)$.
- The $\min$ operator ensures that the policy does not receive excessive rewards for taking updates outside the clipped range.

## Role in LLM Alignment (RLHF)

In Reinforcement Learning from Human Feedback (RLHF), PPO is used to optimize the language model's parameters (the policy) to output completions that receive high scores from the [[reward-modeling]] network. 

During training:
- The state $s$ is the prompt.
- The action $a$ is the generated response sequence.
- The reward is determined by the reward model, augmented with a per-token KL divergence penalty to prevent the model from exploiting the reward model's flaws (known as "reward hacking").

## See Also

- [[reinforcement-learning-from-human-feedback]]
- [[reward-modeling]]
- [[alignment-tax]]
