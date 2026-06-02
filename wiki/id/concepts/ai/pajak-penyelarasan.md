---
type: concept
domain: ai
lang: id
translation: "[[alignment-tax]]"
tags: [alignment-tax, alignment, safety, evaluation]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Ouyang-2022-id]]"]
description: Penurunan performa atau regresi kemampuan pada tolok ukur NLP standar yang terjadi akibat proses penyelarasan model dengan preferensi manusia.
---

# Pajak Penyelarasan (Alignment Tax)

**Pajak Penyelarasan (Alignment Tax)** mengacu pada biaya penurunan performa (*performance cost*) atau regresi kemampuan yang teramati ketika model pembelajaran mesin diselaraskan dengan preferensi manusia (seperti keselamatan dan kepatuhan instruksi), dibandingkan dengan model *pretraining* mentah sebelum diselaraskan.

## Konteks dan Penyebab

Saat melatih model bahasa besar menggunakan *Reinforcement Learning from Human Feedback* (RLHF), model dioptimalkan untuk peringkat preferensi manusia pada distribusi prompt tertentu. Karena tujuan memaksimalkan preferensi ini berbeda dari tujuan pelatihan awal (*pretraining*)—yang memaksimalkan *log likelihood* dari teks web—hal ini dapat menyebabkan model berkinerja lebih buruk pada tugas-tugas NLP standar yang bersifat non-interaktif.

Dalam Ouyang dkk. (2022), model PPO dasar yang dilatih hanya pada distribusi prompt manusia mengalami penurunan performa yang signifikan pada beberapa tolok ukur NLP publik, termasuk:
- **SQuAD** (Tanya Jawab)
- **DROP** (Pemahaman Bacaan)
- **HellaSwag** (Penalaran Logika Dasar)
- **WMT 2015** (Terjemahan Bahasa Prancis ke Inggris)

## Mitigasi: Fungsi Objektif PPO-ptx

Untuk meminimalkan efek *alignment tax* ini, para peneliti mengusulkan modifikasi fungsi objektif PPO yang disebut **PPO-ptx**. Pendekatan ini mencampurkan kembali gradien dari distribusi data *pretraining* ke dalam pembaruan PPO.

Fungsi objektif gabungannya adalah:

$$\text{objective}(\phi) = \mathbb{E}_{(x, y) \sim D_{\pi_{\text{RL}}}} \left[ r_\theta(x, y) - \beta \log \left( \frac{\pi_{\text{RL}}^\phi(y \mid x)}{\pi_{\text{SFT}}(y \mid x)} \right) \right] + \gamma \mathbb{E}_{x \sim D_{\text{pretrain}}} \left[ \log\left(\pi_{\text{RL}}^\phi(x)\right) \right]$$

Di mana:
- $\pi_{\text{RL}}^\phi$ adalah kebijakan RL yang sedang dipelajari.
- $\pi_{\text{SFT}}$ adalah model hasil *supervised fine-tuning*.
- $D_{\text{pretrain}}$ adalah distribusi data *pretraining*.
- $\beta$ mengontrol kekuatan penalti *KL divergence*.
- $\gamma$ mengontrol bobot gradien *pretraining*.

Dengan menetapkan nilai non-nol pada $\gamma$, model dipaksa untuk mempertahankan nilai *log likelihood* yang tinggi pada teks *pretraining*, yang secara efektif memitigasi penurunan performa pada tugas NLP downstream sembari mempertahankan peningkatan dalam kemampuan mengikuti instruksi.

## Lihat Juga

- [[reinforcement-learning-dari-umpan-balik-manusia]]
- [[supervised-fine-tuning-id]]
- [[pemodelan-reward]]
