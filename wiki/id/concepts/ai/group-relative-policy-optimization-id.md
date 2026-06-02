---
type: concept
domain: ai
lang: id
translation: "[[group-relative-policy-optimization]]"
tags: [grpo, reinforcement-learning, algorithm, optimization]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-DeepSeek-2025-id]]"]
description: Algoritme reinforcement learning gradien kebijakan yang memperkirakan baseline dari skor rata-rata grup alih-alih mempertahankan jaringan kritikus.
---

# Group Relative Policy Optimization (GRPO)

**Group Relative Policy Optimization (GRPO)** adalah algoritme *reinforcement learning* gradien kebijakan (*policy gradient*) efisien yang diperkenalkan oleh Shao dkk. (2024) dan dipopulerkan oleh DeepSeek-AI (2025) dalam pelatihan DeepSeek-R1. GRPO mengoptimalkan model dengan membandingkan kelompok luaran (*group of outputs*) yang dihasilkan untuk satu prompt tunggal. Algoritme ini meniadakan kebutuhan akan model kritikus (*critic model*) terpisah (yang biasanya berukuran sama dengan model kebijakan/*policy model*), sehingga menghemat memori dan biaya komputasi secara signifikan.

## Formulasi Algoritme

Untuk setiap pertanyaan $q$, GRPO mengambil sampel kelompok luaran $\{o_1, o_2, \dots, o_G\}$ dari kebijakan lama $\pi_{\theta_{\text{old}}}$. Model kebijakan $\pi_\theta$ dioptimalkan dengan memaksimalkan fungsi objektif berikut:

$$\mathcal{J}_{\text{GRPO}}(\theta) = \frac{1}{G} \sum_{i=1}^{G} \left( \min\left(\frac{\pi_\theta(o_i \mid q)}{\pi_{\theta_{\text{old}}}(o_i \mid q)} A_i, \, \text{clip}\left(\frac{\pi_\theta(o_i \mid q)}{\pi_{\theta_{\text{old}}}(o_i \mid q)}, 1-\epsilon, 1+\epsilon\right) A_i\right) - \beta \text{D}_{\text{KL}}\left(\pi_\theta \parallel \pi_{\text{ref}}\right) \right)$$

Di mana:
- $G$ adalah ukuran kelompok (*group size*).
- $\epsilon$ dan $\beta$ adalah hiperparameter.
- $\pi_{\text{ref}}$ adalah kebijakan referensi (biasanya model SFT).
- $\text{D}_{\text{KL}}(\pi_\theta \parallel \pi_{\text{ref}})$ adalah divergensi Kullback-Leibler yang dihitung sebagai:
  $$\text{D}_{\text{KL}}(\pi_\theta \parallel \pi_{\text{ref}}) = \frac{\pi_{\text{ref}}(o_i \mid q)}{\pi_\theta(o_i \mid q)} - \log\frac{\pi_{\text{ref}}(o_i \mid q)}{\pi_\theta(o_i \mid q)} - 1$$
- $A_i$ adalah nilai *advantage* relatif dari luaran $o_i$ di dalam kelompok, yang dihitung berdasarkan kumpulan *reward* $\{r_1, r_2, \dots, r_G\}$:
  $$A_i = \frac{r_i - \text{mean}(\{r_1, r_2, \dots, r_G\})}{\text{std}(\{r_1, r_2, \dots, r_G\})}$$

## Perbandingan dengan PPO

Dalam *Proximal Policy Optimization* ([[proximal-policy-optimization-id]]) standar:
- Jaringan "kritikus" sekunder dilatih untuk memprediksi fungsi nilai (*value function*) dari suatu keadaan (*state*). Fungsi *advantage* kemudian dihitung relatif terhadap fungsi nilai ini.
- Jika model kebijakan memiliki $N$ parameter, model kritikus biasanya juga memiliki $N$ parameter, yang melipatgandakan kebutuhan memori aktif selama pelatihan.

Dalam GRPO:
- Nilai *baseline* ditentukan oleh rata-rata *reward* dari kelompok tersebut.
- Performa relatif (nilai z-score) dari masing-masing luaran di dalam kelompok bertindak sebagai nilai *advantage*.
- Konsumsi memori dapat ditekan secara signifikan, memungkinkan penggunaan ukuran batch yang lebih besar untuk pelatihan LLM skala besar.

## Lihat Juga

- [[proximal-policy-optimization-id]]
- [[reinforcement-learning-dari-umpan-balik-manusia]]
- [[pemodelan-reward]]
