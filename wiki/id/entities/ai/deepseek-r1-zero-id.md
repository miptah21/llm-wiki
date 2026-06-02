---
type: entity
category: model
domain: ai
lang: id
translation: "[[deepseek-r1-zero]]"
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-DeepSeek-2025-id]]"]
tags: [deepseek, deepseek-r1-zero, llm, reasoning, RL]
---

# DeepSeek-R1-Zero

**DeepSeek-R1-Zero** adalah model bahasa besar eksperimental yang dikembangkan oleh DeepSeek-AI (2025). Model ini menunjukkan kemampuan penalaran (*reasoning*) tingkat lanjut yang dilatih murni melalui pembelajaran penguatan (*reinforcement learning* - RL) tanpa adanya tahap *Supervised Fine-Tuning* (SFT) pendahuluan atau data *cold start*.

## Pelatihan dan Mekanisme

DeepSeek-R1-Zero diinisialisasi langsung dari model dasar `DeepSeek-V3-Base` dan dioptimalkan menggunakan algoritme **Group Relative Policy Optimization (GRPO)**.
- **Sinyal Reward**: Alih-alih menggunakan model *reward* berbasis saraf (*neural reward models*) yang rentan terhadap *reward hacking*, pelatihannya mengandalkan metrik berbasis aturan (*rule-based rewards*):
  - *Accuracy reward*: Memvalidasi kebenaran jawaban melalui umpan balik kompiler (untuk tugas pemrograman) atau format jawaban akhir (untuk matematika deterministik).
  - *Formatting reward*: Memaksa model untuk menempatkan proses berpikirnya di antara tag `<think>` dan `</think>`.
- **Emergent Chain-of-Thought (CoT)**: Selama ribuan langkah pelatihan RL, model secara alami belajar menggunakan waktu berpikir yang lebih lama, mengembangkan perilaku refleksi, penelusuran kembali (*backtracking*), dan koreksi mandiri (*self-correction*).
- **Momen Aha (Aha Moment)**: Para peneliti mengamati tahap transisi yang menarik di mana model belajar untuk berhenti sejenak, mengidentifikasi kesalahan dalam perhitungan matematikanya sendiri, dan memulai kembali penurunannya menggunakan monolog internal antropomorfik (misalnya, menulis "Tunggu, tunggu. Ini salah...").

## Kelemahan

Meskipun menunjukkan skor penalaran yang tinggi (seperti 71.0% pada AIME 2024), DeepSeek-R1-Zero memiliki beberapa masalah:
- **Keterbacaan Buruk (Poor Readability)**: Proses berpikir yang dihasilkan sering kali tidak terstruktur atau sulit dipahami manusia.
- **Pencampuran Bahasa (Language Mixing)**: Model sering mencampuradukkan Bahasa Inggris, Bahasa Mandarin, dan bahasa lainnya di dalam *Chain-of-Thought*, terutama ketika dihadapkan pada prompt multibahasa.

Keterbatasan ini mendorong pengembangan model penerusnya, [[deepseek-r1-id]].

## Lihat Juga

- [[deepseek-r1-id]]
- [[group-relative-policy-optimization-id]]
- [[reinforcement-learning-dari-umpan-balik-manusia]]
