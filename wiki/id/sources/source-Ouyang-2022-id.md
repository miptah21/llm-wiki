---
type: source
source_file: "raw/papers/Ouyang-2022.pdf"
sha256: "c1984bb50a5b90fddb895fdc3a0f72e5bc977148c9f63ef6040cbe7a3e1f0d98"
created: 2026-06-03
updated: 2026-06-03
translation: "[[source-Ouyang-2022]]"
tags: [ingested, RLHF, alignment, instructgpt]
---

# Ringkasan Sumber: Training Language Models to Follow Instructions with Human Feedback

**Training Language Models to Follow Instructions with Human Feedback** (Ouyang et al., 2022) adalah makalah ilmiah penting dari [[openai-id]] yang memperkenalkan **InstructGPT**, jajaran model bahasa besar (large language models) yang diselaraskan dengan menggunakan **Reinforcement Learning from Human Feedback (RLHF)**. Makalah ini menunjukkan bahwa mengoptimalkan model bahasa untuk mengikuti user intent (alih-alih sekadar memprediksi *next token*) menghasilkan model yang lebih aman, lebih membantu (*helpful*), dan lebih jujur (*honest*), bahkan pada skala parameter yang jauh lebih kecil.

## Tinjauan Umum (Overview)

Model bahasa besar (LMs) tradisional, seperti GPT-3, dilatih dengan tujuan memprediksi *next token* pada korpus teks web yang sangat besar. Meskipun mampu melakukan berbagai tugas, model-model ini sering kali mengalami masalah *misalignment* dengan *user intent*: mereka dapat melakukan halusinasi fakta, menghasilkan luaran yang beracun (*toxic*) atau bias, atau sekadar gagal mengikuti instruksi yang diberikan.

Ouyang dkk. mengatasi masalah *misalignment* ini dengan menggunakan kerangka kerja RLHF tiga langkah untuk menyelaraskan model dasar GPT-3 dengan preferensi manusia, yang berpuncak pada penciptaan InstructGPT. Dalam evaluasi manusia, luaran dari InstructGPT versi 1.3B parameter lebih disukai dibandingkan dengan luaran model dasar GPT-3 versi 175B, meskipun memiliki parameter 100x lebih sedikit.

## Metodologi Inti

Makalah ini menguraikan pipa pemrosesan (*pipeline*) *reinforcement learning* tiga langkah:

1. **Supervised Fine-Tuning (SFT)**: 
   Mengumpulkan data demonstrasi dari kontraktor manusia yang menjawab prompt instruksi berkualitas tinggi dan beragam. Lakukan *fine-tuning* pada model dasar GPT-3 menggunakan pembelajaran terawasi (*supervised learning*).
   - *Detail*: Model SFT cenderung mengalami *overfitting* pada *validation loss* setelah 1 *epoch*, namun melatih model untuk *epoch* yang lebih banyak (hingga 16 *epoch*) terbukti meningkatkan skor RM dan peringkat preferensi manusia.

2. **Reward Modeling (RM)**:
   Menghasilkan beberapa luaran ($K = 4$ hingga $K = 9$) dari model SFT untuk satu prompt tunggal. Kontraktor manusia kemudian mengurutkan (*rank*) peringkat dari luaran tersebut. Latih model *Reward Model* (menggunakan arsitektur 6B parameter untuk efisiensi komputasi dan stabilitas) untuk memprediksi preferensi manusia.
   - *Fungsi Kerugian (Loss Function)*:
     $$\text{loss}(\theta) = -\frac{1}{\binom{K}{2}} \mathbb{E}_{(x, y_w, y_l) \sim D} \left[ \log\left(\sigma\left(r_\theta(x, y_w) - r_\theta(x, y_l)\right)\right) \right]$$
     di mana $r_\theta(x, y)$ adalah nilai luaran skalar dari RM, $y_w$ adalah luaran yang lebih disukai (*preferred*), dan $y_l$ adalah luaran yang kurang disukai (*less preferred*).

3. **Reinforcement Learning via Proximal Policy Optimization (PPO)**:
   Melakukan *fine-tuning* pada model SFT dalam lingkungan *bandit* menggunakan PPO untuk memaksimalkan *reward* yang diprediksi oleh RM. Penalti divergensi KL per-token dari model SFT ditambahkan ke fungsi *reward* untuk mencegah optimasi berlebih (*over-optimization*) pada *reward model*.
   - *Fungsi Objektif (PPO-ptx)*:
     $$\text{objective}(\phi) = \mathbb{E}_{(x, y) \sim D_{\pi_{\text{RL}}}} \left[ r_\theta(x, y) - \beta \log \left( \frac{\pi_{\text{RL}}^\phi(y \mid x)}{\pi_{\text{SFT}}(y \mid x)} \right) \right] + \gamma \mathbb{E}_{x \sim D_{\text{pretrain}}} \left[ \log\left(\pi_{\text{RL}}^\phi(x)\right) \right]$$
     Di sini, koefisien penalti KL $\beta$ membatasi divergensi kebijakan dari SFT, sementara koefisien kerugian *pretraining* $\gamma$ digunakan untuk memitigasi efek [[pajak-penyelarasan]] (*alignment tax*) pada tolok ukur NLP publik.

## Temuan Utama & Kontribusi

- **Validasi Preferensi Manusia**: Luaran InstructGPT sangat disukai dibandingkan dengan *baseline* GPT-3. Luaran InstructGPT 175B disukai daripada GPT-3 175B sebesar $85 \pm 3\%$ dari keseluruhan evaluasi.
- **Kejujuran dan Toksisitas**: Pada tolok ukur TruthfulQA, InstructGPT menghasilkan jawaban yang jujur dan informatif dua kali lebih sering dibanding GPT-3. Toksisitas berkurang sekitar 25% ketika model diinstruksikan untuk bersikap sopan (*respectful*).
- **Generalisasi**: Model InstructGPT menunjukkan kemampuan generalisasi yang sangat baik untuk instruksi di luar distribusi pelatihan (seperti penulisan kode, prompt non-Inggris), menunjukkan bahwa model berhasil mempelajari konsep umum dari "mengikuti instruksi."
- **Mitigasi Alignment Tax**: *Reinforcement learning* murni pada umpan balik RM menyebabkan penurunan performa (*performance regression*) pada tolok ukur NLP standar (seperti SQuAD, HellaSwag). Dengan menggabungkan *pretraining gradients* (PPO-ptx), degradasi kemampuan ini dapat ditekan secara signifikan sembari tetap mempertahankan keselarasan preferensi manusia.

## Konsep Inti

- [[reinforcement-learning-dari-umpan-balik-manusia]]
- [[supervised-fine-tuning-id]]
- [[pemodelan-reward]]
- [[pajak-penyelarasan]]

## Entitas Inti

- [[openai-id]]
- [[instructgpt-id]]
