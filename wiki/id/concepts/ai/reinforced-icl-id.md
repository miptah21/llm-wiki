---
type: concept
domain: ai
lang: id
tags: [in-context-learning, rationale-augmentation, chain-of-thought]
created: 2026-06-02
updated: 2026-06-02
translation: "[[reinforced-icl]]"
sources: ["[[source-2509.20820v1-id]]"]
description: Baseline ICL yang ditingkatkan dengan melengkapi demonstrasi dengan penjelasan penalaran (rationale) model-generated CoT, menyaring penalaran yang benar untuk mendongkrak performa.
---

# Reinforced ICL (ICL yang Diperkuat)

**Reinforced ICL** (Agarwal et al., 2024) adalah baseline Pembelajaran dalam Konteks (**In-Context Learning**) yang ditingkatkan dengan melengkapi setiap contoh demonstrasi dengan penjelasan penalaran (*rationale*) yang dihasilkan model — jalur penalaran **Chain-of-Thought (CoT)** yang mengarah pada jawaban yang benar.

## Mekanisme Kerja

1. Untuk setiap contoh demonstrasi $(x_i, y_i)$, ambil sampel beberapa jalur penalaran CoT dari LLM.
2. Saring dan pilih hanya jalur penalaran yang menghasilkan jawaban akhir yang benar $y_i$.
3. Kumpulan demonstrasi yang diperkaya menjadi:
$$\hat{D}_n = \{(x_i, \hat{r}_i, y_i)\}_{i=1}^{n}$$

## Optimasi Efisiensi X-ICL

He et al. (2024) mengusulkan metode pengayaan penjelasan (*rationale-augmentation*) yang lebih efisien yang digunakan dalam penelitian Cheat-Sheet ICL:
- Alih-alih melakukan *sampling* beberapa jalur dan menyaringnya, kondisikan LLM pada masukan $x_i$ **dan** label jawaban yang benar $y_i$ ketika menghasilkan penjelasan $\hat{r}$.
- Pendekatan ini menghasilkan penjelasan yang valid dengan satu kali proses *sampling*, sehingga menghemat token pemrosesan.

## Dampak Performa

Reinforced ICL terbukti mengungguli *vanilla ICL* konvensional pada berbagai variasi jumlah contoh (*shot counts*). Metode ini berfungsi sebagai baseline untuk seluruh variasi ICL dalam penelitian Honda et al. (2025), termasuk [[cheat-sheet-icl-id]], [[many-shot-in-context-learning-id]], dan [[demonstration-retrieval-for-icl-id]].

## Padanan Bahasa Inggris

- [[reinforced-icl]] (Catatan Bahasa Inggris)
