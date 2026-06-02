---
type: source
source_file: "raw/articles/llm-wiki.md"
sha256: "dc3efe98ae62f23dd08acad13aba2e95287beb20b6bec2f4af0423557fe37401"
translation: "[[source-llm-wiki]]"
created: 2026-06-03
updated: 2026-06-03
tags: [llm-wiki, knowledge-base, system-design, obsidian]
---

# Ringkasan Sumber: Pola LLM Wiki (LLM Wiki Pattern)

**Penulis:** Tidak Diketahui / Draf Ide
**Format:** Proposal Konsep
**Reading Time:** 4 menit

---

## Abstrak / Ringkasan

Dokumen ini menjelaskan tentang **LLM Wiki Pattern** (Pola LLM Wiki), sebuah arsitektur perangkat lunak (*software architecture*) dan alur kerja (*workflow*) untuk membangun basis pengetahuan pribadi (*personal knowledge base*) yang *compounding* dan *persisten* menggunakan LLM. Berbeda dengan sistem RAG standar di mana LLM menemukan kembali pengetahuan dari dokumen mentah (*raw documents*) pada setiap kueri (*query*) tanpa akumulasi, LLM Wiki Pattern memperkenalkan sebuah lapisan perantara (*intermediate layer*) yang persisten berupa file-file Markdown yang dikelola oleh LLM (*wiki*). Ketika sumber baru di-*ingest*, LLM memperbarui ringkasan konsep dan entitas yang relevan secara inkremental, menyusun referensi silang (*cross-reference*), dan mencatat konflik, sehingga menciptakan *knowledge base* yang berkembang dan semakin kaya seiring waktu.

---

## Lapisan Arsitektur Utama (Key Architectural Layers)

1. **Raw Sources**: Lapisan kurasi yang berisi dokumen sumber yang bersifat *immutable* (makalah, artikel, transkrip). LLM membaca dari sini tetapi tidak pernah memodifikasinya.
2. **The Wiki**: Direktori terstruktur dan persisten berisi file Markdown yang dihasilkan oleh LLM (ringkasan, konsep, entitas, indeks).
3. **The Schema**: Lapisan konfigurasi dan protokol (misalnya `AGENTS.md` atau `WIKI_SCHEMA.md`) yang memandu agen LLM dalam mengelola, melakukan *linting*, dan memperbarui wiki.

---

## Operasi Utama (Core Operations)

1. **Ingest**: Dipicu saat menambahkan sumber baru. LLM meringkas file, mengekstrak konsep dan entitas penting, memperbarui halaman wiki yang ada untuk mengintegrasikan pengetahuan baru, dan menambahkan entri ke *chronological audit log*.
2. **Query**: Menjawab pertanyaan pengguna dengan mencari dan membaca halaman wiki yang telah dikompilasi, menyintesis jawaban dengan kutipan (*citation*), dan secara opsional menyimpan kueri bernilai tinggi kembali ke wiki sebagai halaman baru.
3. **Lint**: Audit otomatis berkala untuk mendeteksi kontradiksi fakta (*factual contradictions*), referensi silang yang rusak (*broken cross-references*), halaman yatim piatu (*orphaned pages*), atau celah informasi (*information gaps*) yang memerlukan pencarian web atau riset lebih lanjut.

---

## Komponen Sistem Utama (Key System Components)

* **index.md**: Katalog visual berorientasi konten yang mencantumkan semua halaman pengetahuan yang telah dikompilasi, kategori, dan sumber.
* **log.md**: Catatan kronologis *append-only* dari operasi sistem.
* **CLI/MCP Tools**: Alat bantu *scripting* opsional (seperti [qmd](https://github.com/tobi/qmd) untuk pencarian hibrida BM25/vektor) untuk mengotomatiskan tugas-tugas *indexing* atau *query-routing*.

---

## Konsep Terkait

- [[llm-wiki-pattern-id]]
- [[pembelajaran-dalam-konteks]]

## Entitas Terkait

- [[obsidian-id]]
- [[vannevar-bush-id]]
- [[memex-id]]
