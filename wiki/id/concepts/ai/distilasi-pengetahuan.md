---
type: concept
domain: ai
lang: id
tags: [knowledge-distillation, model-compression, efficiency, LLM]
created: 2026-06-02
updated: 2026-06-02
translation: "[[knowledge-distillation]]"
description: Teknik kompresi model di mana model 'student' yang lebih kecil dilatih untuk meniru perilaku dan distribusi keluaran dari model 'teacher' yang lebih besar dan berkinerja tinggi.
---

# Distilasi Pengetahuan (Knowledge Distillation)

**Distilasi Pengetahuan (Knowledge Distillation)** adalah teknik pembelajaran mesin yang diperkenalkan oleh Geoffrey Hinton dkk. pada tahun 2015. Teknik ini berfokus pada kompresi model "teacher" yang besar dan berat secara komputasi menjadi model "student" yang lebih kecil dan lebih cepat dengan tetap mempertahankan kinerja sebanyak mungkin.

## Detail Teknis

Ide intinya adalah melatih model student tidak hanya pada label keras (misalnya, indeks kelas 1), tetapi pada "label lunak" (soft labels) yang dihasilkan oleh model teacher. Label lunak ini adalah distribusi probabilitas atas kelas-kelas, yang mengandung "pengetahuan gelap" (dark knowledge) yang berharga tentang bagaimana model teacher mengkategorikan data.

Distribusi target lunak dihitung menggunakan fungsi Softmax dengan suhu (temperature) $T$:
$$p_i = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}$$

Di mana $z_i$ mewakili logit. Suhu yang lebih tinggi $T > 1$ melunakkan distribusi, memperjelas hubungan halus antar kelas.

## Fungsi Kerugian (Loss Function)

Model student dioptimalkan menggunakan fungsi kerugian gabungan:
$$\mathcal{L} = (1 - \alpha) \mathcal{L}_{\text{hard}}(y, \hat{y}) + \alpha \mathcal{L}_{\text{soft}}(p_{\text{teacher}}, p_{\text{student}})$$

Di mana:
- $\mathcal{L}_{\text{hard}}$ adalah entropi silang standar dengan label asli (hard labels).
- $\mathcal{L}_{\text{soft}}$ adalah divergensi Kullback-Leibler (KL) dengan target lunak (soft targets) dari model teacher.
- $\alpha$ adalah hiperparameter penskalaan.

## Penerapan pada LLM

Dalam LLM modern, distilasi pengetahuan digunakan secara luas untuk:
- Mengompresi model garis depan (seperti GPT-4) menjadi model yang dapat dijalankan secara lokal/edge.
- Mendukung distilasi khusus tugas (misalnya, menghasilkan kumpulan data penyetelan halus dari model teacher).
- Mendistilasi petunjuk dan perilaku, seperti dalam [[cheat-sheet-icl-id]], yang mendistilasi demonstrasi multi-contoh menjadi lembar petunjuk aturan yang ringkas.
- Menyuling kemampuan penalaran (*reasoning*) dan lintasan *Chain-of-Thought* (CoT), seperti yang ditunjukkan oleh [[deepseek-r1-id]] (DeepSeek-AI, 2025), di mana model terbuka yang lebih kecil (seperti Qwen dan Llama dari 1.5B hingga 70B parameter) yang melalui *fine-tuning* SFT pada data penalaran R1 terbukti mengungguli model kecil yang dilatih langsung menggunakan RL.

## Padanan Bahasa Inggris

- [[knowledge-distillation]]
