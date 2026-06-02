---
type: entity
category: model
domain: ai
lang: id
translation: "[[deepseek-r1]]"
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-DeepSeek-2025-id]]"]
tags: [deepseek, deepseek-r1, llm, reasoning, RL]
---

# DeepSeek-R1

**DeepSeek-R1** adalah model bahasa besar penalaran (*reasoning*) mutakhir yang dikembangkan oleh DeepSeek-AI (2025). Dilatih menggunakan pipa pemrosesan multi-tahap yang menggabungkan *Supervised Fine-Tuning* (SFT) dan *Group Relative Policy Optimization* (GRPO), DeepSeek-R1 menunjukkan kinerja penalaran yang setara dengan model komersial tertutup seperti OpenAI-o1.

## Pipa Pemrosesan Pelatihan (Training Pipeline)

DeepSeek-R1 mengatasi masalah keterbacaan dan pencampuran bahasa dari [[deepseek-r1-zero-id]] dengan menggunakan metodologi pelatihan empat tahap:

1. **Cold Start SFT**: Melakukan *fine-tuning* pada model dasar (`DeepSeek-V3-Base`) dengan ribuan contoh demonstrasi penalaran *Chain-of-Thought* (CoT) panjang berkualitas tinggi untuk menetapkan keterbacaan dan struktur yang baik.
2. **Reasoning-Oriented RL**: Pelatihan RL skala besar menggunakan GRPO. Selain *accuracy rewards*, ditambahkan *language consistency reward* untuk memastikan model berpikir menggunakan bahasa target yang ditentukan oleh prompt.
3. **Rejection Sampling & SFT**: Ketika proses RL mencapai konvergensi, *rejection sampling* digunakan untuk menghasilkan 600k contoh penalaran berkualitas tinggi. Sampel ini digabungkan dengan 200k tugas SFT non-penalaran (seperti penulisan kreatif, penerjemahan, QA umum) dari korpus DeepSeek-V3. Model dasar kemudian dilatih kembali pada kumpulan 800k data ini selama 2 *epoch*.
4. **RL untuk Semua Skenario**: Tahap GRPO akhir yang dioptimalkan untuk kegunaan (*helpfulness*, mengevaluasi ringkasan akhir) dan keselamatan (*harmlessness*, mengevaluasi CoT dan ringkasan secara keseluruhan).

## Performa dan Distilasi Pengetahuan (Knowledge Distillation)

DeepSeek-R1 mencapai hasil yang luar biasa pada berbagai tolok ukur penalaran standar, meraih skor **79.8% Pass@1 pada AIME 2024** dan **97.3% pada MATH-500**.

Makalah ini juga membuktikan bahwa pola penalaran dari DeepSeek-R1 dapat disuling ke model yang lebih kecil. DeepSeek-AI merilis enam model hasil distilasi (1.5B, 7B, 8B, 14B, 32B, 70B parameter) berbasis arsitektur Qwen dan Llama. Menariknya, model **Qwen-32B hasil distilasi meraih skor 72.6% pada AIME 2024**, mengungguli model sumber terbuka lainnya dan menyamai performa OpenAI-o1-mini.

## Lihat Juga

- [[deepseek-r1-zero-id]]
- [[group-relative-policy-optimization-id]]
- [[distilasi-pengetahuan]]
