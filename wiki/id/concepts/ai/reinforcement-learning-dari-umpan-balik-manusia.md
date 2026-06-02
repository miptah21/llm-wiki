---
type: concept
domain: ai
lang: id
translation: "[[reinforcement-learning-from-human-feedback]]"
tags: [rlhf, machine-learning, alignment, optimization]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Ouyang-2022-id]]"]
description: Paradigma optimasi yang menggunakan peringkat preferensi manusia sebagai sinyal reward untuk menyelaraskan model pembelajaran mesin dengan nilai dan niat manusia.
---

# Reinforcement Learning dari Umpan Balik Manusia (Reinforcement Learning from Human Feedback - RLHF)

**Reinforcement Learning dari Umpan Balik Manusia (Reinforcement Learning from Human Feedback - RLHF)** adalah paradigma pembelajaran mesin yang menyempurnakan perilaku model menggunakan umpan balik dari evaluator manusia. Alih-alih hanya bergantung pada *loss function* matematis yang telah ditentukan sebelumnya (seperti *cross-entropy*) atau metrik berbasis aturan (seperti BLEU atau ROUGE), RLHF melatih model sekunder (*reward model*) untuk meniru preferensi manusia dan menggunakan model ini sebagai fungsi *reward* untuk mengoptimalkan agen utama melalui *reinforcement learning*.

## Pipa Pemrosesan Utama (Core Pipeline)

Dalam konteks penyelarasan (*alignment*) model bahasa besar, RLHF biasanya mengikuti proses tiga tahap:

1. **Supervised Fine-Tuning (SFT)**: Melakukan *fine-tuning* pada model bahasa yang telah dilatih sebelumnya (*pretrained model*) dengan demonstrasi perilaku target berkualitas tinggi yang dikurasi oleh manusia.
2. **Reward Modeling (RM)**: Melatih jaringan saraf (*neural network*) untuk mengevaluasi hasil penyelesaian model (*completions*). Evaluator manusia mengurutkan beberapa luaran yang dihasilkan untuk satu prompt tunggal, dan *reward model* dioptimalkan untuk memberikan skor skalar yang lebih tinggi pada luaran yang lebih disukai.
3. **Reinforcement Learning (RL)**: Mengoptimalkan kebijakan model SFT menggunakan algoritme *reinforcement learning* (seperti [[proximal-policy-optimization-id]]) terhadap *reward* skalar yang dihasilkan oleh *reward model*.

## Formulasi Matematis

Selama tahap RL, tujuannya adalah memaksimalkan *expected reward* sekaligus memberikan penalti kepada kebijakan (*policy*) agar tidak menyimpang terlalu jauh dari kebijakan awal SFT. Regularisasi ini diimplementasikan menggunakan penalti *KL divergence* (Kullback-Leibler):

$$\text{Reward}(x, y) = R_\theta(x, y) - \beta \text{D}_{\text{KL}}\left(\pi_{\text{RL}}(y \mid x) \parallel \pi_{\text{SFT}}(y \mid x)\right)$$

Di mana:
- $R_\theta(x, y)$ adalah luaran skalar dari *reward model* untuk prompt $x$ dan penyelesaian $y$.
- $\pi_{\text{RL}}$ dan $\pi_{\text{SFT}}$ masing-masing adalah kebijakan *reinforcement learning* dan model *supervised fine-tuned*.
- $\beta$ adalah hiperparameter penskalaan yang mengontrol kekuatan penalti *KL divergence*.

## Aplikasi

RLHF dipopulerkan secara luas oleh model InstructGPT yang dikembangkan oleh [[openai-id]] dan menjadi fondasi utama bagi model bahasa instruksi modern termasuk ChatGPT, Claude, dan Gemini.

## Lihat Juga

- [[supervised-fine-tuning-id]]
- [[pemodelan-reward]]
- [[pajak-penyelarasan]]
- [[proximal-policy-optimization-id]]
