---
type: concept
domain: ai
lang: id
translation: "[[supervised-fine-tuning]]"
tags: [sft, fine-tuning, training, deep-learning]
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Ouyang-2022-id]]"]
description: Proses melakukan fine-tuning pada model bahasa yang telah dilatih sebelumnya menggunakan kumpulan data prompt-demonstrasi berkualitas tinggi lewat pembelajaran terawasi.
---

# Supervised Fine-Tuning (SFT)

**Supervised Fine-Tuning (SFT)** adalah langkah pertama dalam proses penyelarasan (*alignment*) model bahasa besar (LLMs). SFT mentransformasikan model *pretraining* mentah (yang dilatih untuk melakukan prediksi *next token*) menjadi sebuah kebijakan (*policy*) yang dapat mengikuti instruksi pengguna, menjawab pertanyaan, dan menyelesaikan tugas-tugas tertentu dengan melatihnya pada dataset pasangan prompt-respon yang telah dikurasi.

## Metodologi

Selama proses SFT, parameter model diperbarui menggunakan pembelajaran terawasi (*supervised learning*) standar. Dataset pelatihan terdiri dari prompt masukan $x$ yang dipasangkan dengan respon demonstrasi standar emas (*gold-standard*) $y$ yang ditulis oleh anotator manusia:

$$D_{\text{SFT}} = \{(x_1, y_1), (x_2, y_2), \dots, (x_n, y_n)\}$$

Model dioptimalkan menggunakan fungsi kerugian *cross-entropy* autoregresif standar, yang dihitung hanya pada token dari urutan target $y$:

$$\mathcal{L}_{\text{SFT}}(\theta) = -\sum_{i=1}^{|y|} \log P_\theta(y_i \mid y_{<i}, x)$$

## Karakteristik Utama & Tantangan

- **Overfitting**: Selama proses SFT, LLM cenderung mengalami *overfitting* pada *validation loss* dengan cepat (sering kali setelah hanya 1 *epoch*). Meskipun demikian, melatih model untuk *epoch* yang lebih banyak (misalnya, hingga 16 *epoch* dalam Ouyang dkk., 2022) terbukti bermanfaat bagi penilaian evaluasi manusia dan skor *reward model*, terlepas dari regresi *validation loss* nominal.
- **Kualitas vs Kuantitas Data**: Demonstrasi berkualitas tinggi dan beragam (ditulis oleh anotator ahli) jauh lebih efektif untuk penyelarasan instruksi dibandingkan dengan data sintetis atau data hasil ekstraksi (*scraped data*) dalam jumlah besar.
- **Keterbatasan**: Meskipun SFT menghasilkan luaran berkualitas tinggi, ia tetap terbatas pada mereplikasi gaya demonstrasi yang tepat dan tidak berskala secara efisien untuk menangkap preferensi manusia yang kompleks atau kompromi (*tradeoffs*) multi-tujuan. Oleh karena itu, SFT biasanya dilanjutkan dengan [[pemodelan-reward]] dan *reinforcement learning*.

## Lihat Juga

- [[reinforcement-learning-dari-umpan-balik-manusia]]
- [[pemodelan-reward]]
- [[pajak-penyelarasan]]
