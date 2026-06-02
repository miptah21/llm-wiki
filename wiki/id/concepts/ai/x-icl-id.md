---
type: concept
domain: ai
lang: id
tags: [x-icl, ICL, reinforced-icl, rationales, few-shot-learning]
created: 2026-06-02
updated: 2026-06-02
translation: "[[x-icl]]"
description: Kerangka kerja pembelajaran dalam konteks yang melengkapi demonstrasi few-shot atau many-shot dengan penalaran langkah-demi-langkah (rationales), menggunakan sinyal penguatan untuk memilih atau menyempurnakan demonstrasi tersebut.
---

# X-ICL (Pembelajaran dalam Konteks dengan Penalaran yang Diperluas)

**X-ICL** merujuk pada variasi lanjutan dari Pembelajaran dalam Konteks (In-Context Learning - ICL) di mana contoh demonstrasi dilengkapi dengan penalaran penjelasan terperinci (mirip dengan Chain-of-Thought tetapi dipilih atau disempurnakan secara sistematis menggunakan sinyal penguatan).

## Prinsip Inti

ICL standar memetakan masukan langsung ke target:
$$x_i \to y_i$$

X-ICL memperkenalkan penalaran penjelasan perantara $r_i$ yang mewakili proses berpikir:
$$x_i \to r_i \to y_i$$

Dengan menyusun contoh demonstrasi menggunakan penalaran berkualitas tinggi yang terverifikasi, LLM dipandu untuk menghasilkan penalaran serupa untuk masukan uji, yang secara dramatis meningkatkan kinerja penalaran pada tugas-tugas multi-langkah.

## Hubungan dengan ICL yang Diperkuat (Reinforced ICL)

X-ICL sering dipasangkan dengan kerangka kerja **Reinforced ICL**, di mana:
1. Penjelasan dirancang oleh model generator.
2. Sinyal penghargaan (misalnya, akurasi pada set pengembangan) mengevaluasi kualitas penjelasan.
3. Contoh demonstrasi dalam prompt diperbarui atau dipangkas secara iteratif untuk memaksimalkan kinerja tugas.

Versi ringkas dari konfigurasi ini digunakan dalam metode seperti [[cheat-sheet-icl-id]], di mana penalaran disimpurnakan menjadi lembar aturan tunggal yang dapat dibaca dan didebug oleh manusia.

## Padanan Bahasa Inggris

- [[x-icl]] (Catatan terjemahan Bahasa Inggris)
