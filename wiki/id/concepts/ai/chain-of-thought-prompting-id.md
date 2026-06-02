---
type: concept
domain: ai
lang: id
tags: [prompting, reasoning, LLM]
created: 2026-06-02
updated: 2026-06-02
translation: "[[chain-of-thought-prompting]]"
sources: ["[[source-2509.20820v1-id]]"]
description: Teknik pembuatan prompt yang memicu penalaran langkah-demi-langkah dari LLM dengan menyertakan langkah penalaran perantara dalam demonstrasi, yang secara signifikan meningkatkan kinerja pada tugas-tugas kompleks.
---

# Chain-of-Thought (CoT) Prompting

**Chain-of-Thought (CoT) prompting** (Wei et al., 2022) adalah teknik yang meningkatkan kemampuan penalaran LLM dengan menyediakan contoh demonstrasi yang mencakup langkah-langkah penalaran perantara eksplisit — sebuah "rantai pemikiran" — daripada hanya pasangan masukan-keluaran (*input-output pairs*).

## Ide Inti

Alih-alih menggunakan format standar:
```
Q: Roger has 5 tennis balls...
A: 11
```

CoT prompting menggunakan:
```
Q: Roger has 5 tennis balls...
A: Roger started with 5. He bought 2 cans of 3 = 6. 5 + 6 = 11. The answer is 11.
```

Hal ini mendorong model untuk menguraikan masalah kompleks menjadi penalaran langkah-demi-langkah sebelum memberikan jawaban akhir.

## Peran dalam Penelitian Cheat-Sheet ICL

Dalam penelitian Honda et al. (2025), semua metode ICL menggunakan **rationale-augmented demonstrations** yang mengikuti kerangka kerja [[reinforced-icl-id]]:
- Setiap contoh demonstrasi menyertakan penjelasan penalaran CoT yang dihasilkan oleh model.
- Prompt pembuatan cheat sheet menerima demonstrasi yang diperkaya dengan penalaran ini.
- Bahkan Cheat-Sheet ICL tanpa dukungan penalaran (*rationale-augmented*) tetap efektif, yang menunjukkan ketangguhan metode ini.

## Ekstensi Lanjutan

- **Self-consistency** (Wang et al., 2023): Mengambil sampel beberapa jalur CoT dan melakukan pemilihan suara mayoritas (*majority vote*).
- **[[reinforced-icl-id]]**: Menyaring jalur CoT untuk hanya mempertahankan jalur yang menghasilkan jawaban yang benar.

## Padanan Bahasa Inggris

- [[chain-of-thought-prompting]] (Catatan Bahasa Inggris)
