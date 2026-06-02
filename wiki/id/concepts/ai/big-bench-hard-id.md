---
type: concept
domain: ai
lang: id
tags: [benchmark, reasoning, LLM-evaluation]
created: 2026-06-02
updated: 2026-06-02
translation: "[[big-bench-hard]]"
sources: ["[[source-2509.20820v1-id]]"]
description: Kumpulan tugas penalaran menantang yang diturunkan dari BIG-Bench, dikurasi secara khusus agar cukup sulit sehingga memerlukan chain-of-thought prompting untuk meningkatkan kinerja.
---

# BIG-Bench Hard (BBH)

**BIG-Bench Hard (BBH)** (Suzgun et al., 2023) adalah subset dari benchmark BIG-Bench (Srivastava et al., 2023) yang terdiri dari tugas-tugas yang sangat menantang bagi LLM — khususnya, tugas-tugas di mana model-model sebelumnya berkinerja di bawah rata-rata penilai manusia.

## Peran dalam Penelitian Cheat-Sheet ICL

Honda et al. (2025) memilih 8 tugas BBH di mana **Many-Shot ICL** mengungguli **Few-Shot ICL** sebesar >1 persentase poin, menjadikannya basis pengujian yang cocok untuk mengevaluasi apakah **Cheat-Sheet ICL** dapat mempertahankan kinerja many-shot dengan token yang jauh lebih sedikit.

### Tugas-Tugas yang Dipilih:
1. **Boolean Expressions** — Mengevaluasi ekspresi boolean dengan True/False, and/or/not.
2. **Causal Judgement** — Menentukan apakah orang pada umumnya akan setuju dengan klaim kausalitas.
3. **Disambiguation QA** — Mengidentifikasi anteseden kata ganti (*pronoun antecedents*) atau menjawab "ambiguous."
4. **Geometric Shapes** — Mengidentifikasi bentuk geometris dari elemen SVG path.
5. **Movie Recommendation** — Memilih rekomendasi film serupa dari sebuah daftar.
6. **Salient Translation Error Detection** — Mengklasifikasikan kesalahan penerjemahan (Bahasa Jerman $\to$ Bahasa Inggris).
7. **Sports Understanding** — Menilai kelayakan (*plausibility*) kalimat terkait olahraga.
8. **Word Sorting** — Mengurutkan daftar kata secara alfabetis.

## Karakteristik Utama

Tugas-tugas BBH lebih berorientasi pada **pattern recognition** (pengenalan pola) dalam kumpulan data dibandingkan menguji pengetahuan akademik umum. Hal ini menjadikannya sangat cocok untuk evaluasi Many-Shot ICL menggunakan LLM modern yang kuat, karena tugas yang hanya memerlukan pengetahuan umum (seperti MATH500, GSM8K) tidak menunjukkan peningkatan kinerja pada skenario many-shot.

## Padanan Bahasa Inggris

- [[big-bench-hard]] (Catatan Bahasa Inggris)
