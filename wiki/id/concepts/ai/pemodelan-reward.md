---
type: concept
domain: ai
lang: id
translation: "[[reward-modeling]]"
tags: [rm, reward-model, alignment, preference-learning]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Ouyang-2022-id]]"]
description: Melatih model untuk menghasilkan skor skalar yang mewakili peringkat preferensi manusia untuk pasangan input-output tertentu.
---

# Pemodelan Reward (Reward Modeling)

**Pemodelan Reward (Reward Modeling - RM)** adalah fase penting dalam *Reinforcement Learning from Human Feedback* (RLHF) di mana jaringan saraf dilatih untuk bertindak sebagai perwakilan (proksi) bagi evaluator manusia. *Reward model* menerima prompt dan calon penyelesaian (*candidate completion*) sebagai masukan, lalu menghasilkan nilai skalar yang mewakili kualitas atau tingkat preferensi yang diprediksi menurut evaluator manusia.

## Loss Function & Pelatihan

Daripada meminta evaluator manusia untuk memberikan skor numerik absolut pada luaran model (yang sangat subjektif dan tidak konsisten), para evaluator diminta untuk mengurutkan (*rank*) peringkat dari beberapa luaran ($K = 4$ hingga $K = 9$) untuk satu prompt tunggal. Hal ini menghasilkan data perbandingan berpasangan (*pairwise comparison*).

Untuk melatih *reward model*, Ouyang dkk. (2022) menggunakan fungsi kerugian (*loss function*) *cross-entropy* berpasangan. Untuk sebuah prompt $x$, penyelesaian yang lebih disukai $y_w$, dan penyelesaian yang kurang disukai $y_l$:

$$\text{loss}(\theta) = -\frac{1}{\binom{K}{2}} \mathbb{E}_{(x, y_w, y_l) \sim D} \left[ \log\left(\sigma\left(r_\theta(x, y_w) - r_\theta(x, y_l)\right)\right) \right]$$

Di mana:
- $r_\theta(x, y)$ adalah skor skalar yang dihasilkan oleh *reward model* dengan parameter $\theta$ untuk prompt $x$ dan penyelesaian $y$.
- $\sigma(z) = \frac{1}{1 + \exp(-z)}$ adalah fungsi sigmoid.
- $\binom{K}{2}$ adalah jumlah perbandingan berpasangan yang diperoleh dari pemeringkatan $K$ penyelesaian.
- $D$ adalah dataset perbandingan.

## Efisiensi Sistem & Overfitting

- **Batching Comparisons**: Melatih model dengan semua $\binom{K}{2}$ kombinasi berpasangan dari satu prompt dalam satu batch tunggal terbukti efisien secara komputasi. Dibandingkan melakukan $K(K-1)$ *forward pass*, *reward model* hanya memerlukan satu *forward pass* untuk $K$ penyelesaian, kemudian perbedaan logitnya dihitung secara terpisah.
- **Menghindari Overfitting**: Jika perbandingan berpasangan diacak secara independen di berbagai batch, model cenderung mengalami *overfitting* pada penyelesaian yang berulang. Menjaga semua perbandingan dari satu prompt tetap berada dalam batch yang sama terbukti mencegah perilaku *overfitting* ini.
- **Tradeoffs Skala**: Dalam praktiknya, *reward model* yang lebih kecil (misalnya, 6B parameter, alih-alih 175B) sering kali digunakan untuk menghemat sumber daya komputasi dan meningkatkan stabilitas pelatihan selama tahap *reinforcement learning* berikutnya.

## Lihat Juga

- [[reinforcement-learning-dari-umpan-balik-manusia]]
- [[supervised-fine-tuning-id]]
- [[pajak-penyelarasan]]
