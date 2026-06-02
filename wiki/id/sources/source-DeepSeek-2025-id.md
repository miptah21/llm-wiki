---
type: source
source_file: "raw/papers/DeepSeek-2025.pdf"
sha256: "52d8ca3ac93e88cef9944e1fd03b0e04aec5954495a8250fb2fadf8fa20a4dad"
created: 2026-06-03
updated: 2026-06-03
translation: "[[source-DeepSeek-2025]]"
tags: [ingested, RL, reasoning, deepseek, grpo]
---

# Ringkasan Sumber: DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning

**DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning** (DeepSeek-AI, 2025) adalah makalah ilmiah terobosan yang mengeksplorasi pengembangan kemampuan penalaran (*reasoning*) tingkat lanjut pada model bahasa besar dengan menggunakan *reinforcement learning* (RL) skala besar. Makalah ini memperkenalkan **DeepSeek-R1-Zero**, model yang dilatih murni melalui RL tanpa *supervised fine-tuning* (SFT) sebagai *cold start*, dan **DeepSeek-R1**, yang menggabungkan pipa pemrosesan multi-tahap (SFT + RL) untuk meningkatkan keterbacaan (*readability*), menghilangkan pencampuran bahasa (*language mixing*), dan menyelaraskan dengan preferensi manusia.

## Tinjauan Umum (Overview)

Secara historis, model penalaran sangat bergantung pada data terawasi (*supervised data*). DeepSeek-AI menunjukkan bahwa kemampuan penalaran tingkat lanjut (seperti verifikasi mandiri, refleksi, dan pembuatan *Chain-of-Thought* yang panjang) dapat muncul secara alami murni melalui *reinforcement learning* pada model dasar (*base models*).

Untuk mencapai hal ini secara efisien, mereka menggunakan algoritme **Group Relative Policy Optimization (GRPO)**, yang memperkirakan *baseline* untuk *reinforcement learning* dari skor kelompok alih-alih mempertahankan model kritikus (*critic model*) berukuran besar. Makalah ini juga memvalidasi efektivitas teknik **knowledge distillation**, menunjukkan bahwa pola penalaran yang ditemukan oleh model frontier dapat langsung disuling ke model padat yang lebih kecil (model 1.5B hingga 70B parameter berbasis Qwen dan Llama), menjadikannya sangat kompetitif dengan model-model komersial tertutup.

## Metodologi Inti

Makalah ini menyajikan dua model utama dan satu pipa penyulingan (*distillation pipeline*):

### 1. DeepSeek-R1-Zero (Pure RL)
Menerapkan RL secara langsung pada `DeepSeek-V3-Base` tanpa fase *cold-start* SFT pendahuluan.
- **Reward Signal**: Dievaluasi menggunakan metrik berbasis aturan (*rule-based*):
  - *Accuracy rewards*: Kompiler program untuk tugas pengodean (seperti LeetCode) dan pemeriksa format untuk jawaban matematika deterministik.
  - *Format rewards*: Memaksa model untuk menempatkan proses berpikirnya di antara tag `<think>` dan `</think>`.
- **Perilaku Emergent**: Memunculkan kemampuan refleksi secara alami, penelusuran kembali (*backtracking*), koreksi mandiri (*self-correction*), dan "momen aha" (*aha moment*) di mana model mengevaluasi kembali langkah penalaran di tengah proses pembuatan jawaban.
- **Kelemahan**: Menghadapi masalah keterbacaan yang buruk, kekacauan struktur, dan pencampuran bahasa (*language mixing*).

### 2. DeepSeek-R1 (Multi-Stage Pipeline)
Untuk mengatasi keterbatasan DeepSeek-R1-Zero, DeepSeek-R1 dilatih menggunakan pipa pemrosesan empat tahap:
1. **Cold Start**: Melakukan *fine-tuning* pada `DeepSeek-V3-Base` dengan ribuan data demonstrasi penalaran *CoT* yang panjang (baik hasil kurasi manusia maupun model) untuk memulai proses RL.
2. **Reasoning-oriented RL**: Menerapkan RL menggunakan GRPO. Skor akurasi digabungkan dengan *language consistency reward* untuk mencegah pencampuran bahasa di dalam CoT.
3. **Rejection Sampling & SFT**: Melakukan *rejection sampling* pada checkpoint Tahap 2 untuk mengumpulkan 600k sampel penalaran berkualitas tinggi. Gabungkan ini dengan 200k sampel non-penalaran (seperti penulisan kreatif, QA fakta, penerjemahan) dari dataset `DeepSeek-V3`. Lakukan *fine-tuning* pada model dasar dengan total 800k sampel selama dua *epoch*.
4. **RL for all Scenarios**: Tahap RL kedua menggunakan GRPO untuk menyelaraskan model dengan preferensi manusia pada aspek kegunaan (*helpfulness*, dievaluasi pada ringkasan akhir) dan keselamatan (*harmlessness*, dievaluasi pada CoT dan ringkasan).

### 3. Distilasi (Distillation)
Menyuling dataset penalaran SFT hasil kurasi sebanyak 800k dari DeepSeek-R1 ke model dasar sumber terbuka yang lebih kecil (Qwen2.5 dan Llama3). Metode distilasi SFT langsung ini memberikan hasil yang jauh lebih baik dibandingkan dengan melatih RL secara langsung pada model kecil tersebut.

## Temuan Utama & Performa Benchmark

- **Kemampuan Penalaran**: DeepSeek-R1 mencapai nilai **79.8% Pass@1 pada AIME 2024** dan **97.3% pada MATH-500**, setara atau sedikit melampaui OpenAI-o1-1217.
- **Coding Elo**: Meraih peringkat **2,029 Elo pada Codeforces**, mengungguli 96.3% peserta manusia.
- **Efisiensi Model Hasil Distilasi**: DeepSeek-R1-Distill-Qwen-32B mencapai 72.6% pada AIME 2024, secara signifikan mengungguli model sumber terbuka lainnya dan menyamai performa o1-mini.

## Konsep Inti

- [[group-relative-policy-optimization-id]]
- [[reinforcement-learning-dari-umpan-balik-manusia]]
- [[distilasi-pengetahuan]]

## Entitas Inti

- [[deepseek-r1-zero-id]]
- [[deepseek-r1-id]]
