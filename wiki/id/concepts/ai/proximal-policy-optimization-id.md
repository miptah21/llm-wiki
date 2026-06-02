---
type: concept
domain: ai
lang: id
translation: "[[proximal-policy-optimization]]"
tags: [ppo, reinforcement-learning, algorithm, optimization]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Ouyang-2022-id]]"]
description: Algoritme reinforcement learning gradien kebijakan yang menggunakan fungsi objektif terpotong untuk memastikan pembaruan kebijakan yang stabil dan inkremental.
---

# Proximal Policy Optimization (PPO)

**Proximal Policy Optimization (PPO)** adalah algoritme pembelajaran penguatan (*reinforcement learning*) berbasis kebijakan (*policy-based*) yang populer dikembangkan oleh OpenAI (Schulman dkk., 2017). Algoritme ini dirancang untuk melakukan pembaruan gradien yang stabil dan hemat sampel pada jaringan kebijakan (*policy networks*) dengan mencegah kebijakan baru menyimpang terlalu jauh dari kebijakan lama.

## Clipped Objective Function (Fungsi Objektif Terpotong)

PPO mencapai pelatihan yang stabil dengan menggunakan fungsi objektif proksi terpotong (*clipped surrogate objective function*). Untuk kebijakan $\pi_\phi$ dengan parameter $\phi$, fungsi objektif membatasi pembaruan kebijakan ke wilayah terpercaya (*trusted region*):

$$L^{\text{CLIP}}(\phi) = \hat{\mathbb{E}}_t \left[ \min\left(r_t(\phi)\hat{A}_t, \, \text{clip}(r_t(\phi), 1-\epsilon, 1+\epsilon)\hat{A}_t\right) \right]$$

Di mana:
- $r_t(\phi) = \frac{\pi_\phi(a_t \mid s_t)}{\pi_{\phi_{\text{old}}}(a_t \mid s_t)}$ adalah rasio probabilitas antara tindakan di bawah kebijakan baru dan kebijakan lama.
- $\hat{A}_t$ adalah nilai *advantage* yang diperkirakan pada langkah waktu $t$, yang mengukur seberapa jauh lebih baik tindakan yang dipilih dibandingkan dengan ekspektasi rata-rata kebijakan.
- $\epsilon$ adalah hiperparameter pemotongan (*clipping*, biasanya bernilai antara $0.1$ dan $0.2$) yang membatasi rasio $r_t(\phi)$.
- Operator $\min$ memastikan kebijakan tidak menerima *reward* berlebih akibat melakukan pembaruan di luar rentang yang terpotong.

## Peran dalam Penyelarasan LLM (RLHF)

Dalam *Reinforcement Learning dari Umpan Balik Manusia* (RLHF), PPO digunakan untuk mengoptimalkan parameter model bahasa (kebijakan/*policy*) guna menghasilkan penyelesaian (*completions*) yang mendapatkan skor tinggi dari jaringan [[pemodelan-reward]].

Selama pelatihan:
- Keadaan (*state* $s$) adalah prompt masukan.
- Tindakan (*action* $a$) adalah urutan respon yang dihasilkan model.
- Nilai *reward* ditentukan oleh *reward model*, yang ditambah dengan penalti divergensi KL per-token untuk mencegah model mengeksploitasi kelemahan *reward model* (dikenal sebagai *reward hacking*).

## Lihat Juga

- [[reinforcement-learning-dari-umpan-balik-manusia]]
- [[pemodelan-reward]]
- [[pajak-penyelarasan]]
