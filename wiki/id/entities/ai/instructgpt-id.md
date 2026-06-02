---
type: entity
category: model
domain: ai
lang: id
translation: "[[instructgpt]]"
created: 2026-06-03
updated: 2026-06-03
sources: ["[[source-Ouyang-2022-id]]"]
tags: [instructgpt, gpt-3, openai, llm]
---

# InstructGPT

**InstructGPT** adalah jajaran model bahasa besar yang dikembangkan oleh [[openai-id]] yang telah melalui proses *fine-tuning* menggunakan *Reinforcement Learning from Human Feedback* (RLHF) agar dapat mengikuti instruksi dengan lebih baik. Pertama kali diperkenalkan dalam makalah *Training language models to follow instructions with human feedback* (Ouyang dkk., 2022), InstructGPT merupakan pendahulu langsung dari ChatGPT.

## Pengembangan dan Arsitektur

Model InstructGPT menggunakan arsitektur transformer GPT-3 dan dilatih dalam tiga ukuran skala parameter: 1.3B, 6B, dan 175B. Berbeda dengan model GPT-3 standar yang hanya dioptimalkan untuk melakukan prediksi *next token*, InstructGPT dioptimalkan dengan menggunakan:
1. **Supervised Fine-Tuning (SFT)** pada pasangan prompt-respon yang ditulis oleh anotator manusia.
2. **Reward Modeling** pada peringkat preferensi manusia.
3. **Proximal Policy Optimization (PPO)** dengan memanfaatkan *reward model*.

## Validasi dan Dampak

InstructGPT membuktikan bahwa optimasi menggunakan peringkat preferensi manusia dapat meningkatkan kegunaan model secara drastis. Meskipun memiliki parameter 100x lebih kecil, luaran dari model InstructGPT 1.3B lebih disukai oleh evaluator manusia dibandingkan dengan luaran model GPT-3 175B dasar. InstructGPT juga menunjukkan penurunan signifikan pada tingkat halusinasi serta luaran yang beracun (*toxic*).

## Lihat Juga

- [[openai-id]]
- [[reinforcement-learning-dari-umpan-balik-manusia]]
- [[supervised-fine-tuning-id]]
- [[pemodelan-reward]]
