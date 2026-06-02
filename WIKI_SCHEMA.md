# LLM Wiki Schema & Guidelines (`WIKI_SCHEMA.md`)

This configuration file defines the bilingual parallel directory structure, metadata schemas, operation protocols, and local fallback heuristics for the compounding knowledge base. Any AI agent operating within this vault MUST strictly adhere to these rules.

---

## 1. Directory Structure

- `raw/`: Immutable raw source materials. Do NOT modify files in this directory.
  - `raw/papers/`: PDF research papers, textbooks, and technical journals.
  - `raw/articles/`: Web clips, blog posts, news, and markdown clippings.
  - `raw/notes/`: Personal raw thoughts, logs, and transcriptions.
- `wiki/`: Persistent compiled AI-managed Markdown Wiki.
  - `wiki/log.md`: Unified chronological log of all actions. Do NOT edit manually.
  - `wiki/en/`: === English Sub-Wiki ===
    - `wiki/en/index.md`: Auto-generated English visual index catalog.
    - `wiki/en/sources/`: Detailed summaries of sources written in English.
    - `wiki/en/concepts/`: concepts/finance/, concepts/software-engineering/, concepts/ai/, concepts/economics/
    - `wiki/en/entities/`: entities/finance/, entities/software-engineering/, entities/ai/, entities/economics/
  - `wiki/id/`: === Indonesian Sub-Wiki ===
    - `wiki/id/index.md`: Auto-generated Indonesian visual index catalog.
    - `wiki/id/sources/`: Detailed summaries of sources written in Indonesian.
    - `wiki/id/concepts/`: concepts/finance/, concepts/software-engineering/, concepts/ai/, concepts/economics/
    - `wiki/id/entities/`: entities/finance/, entities/software-engineering/, entities/ai/, entities/economics/
- `scripts/`: Pure local Python scripts for indexing, linting, search, and fallbacks.

---

## 2. Strict Page Schemas (YAML Frontmatter)

Every `.md` file created or updated in the `wiki/en/` or `wiki/id/` directories MUST start with clean YAML frontmatter.

### 2.1. Concept Page (`wiki/<lang>/concepts/<domain>/`)
```yaml
---
type: concept
domain: ai        # Options: finance, software-engineering, ai, economics
lang: en          # Options: en, id
translation: "[[translated_page_name]]" # Link to parallel version in other language
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["[[source-page-name]]"]
description: A short 1-2 sentence definition of the concept.
---
```

### 2.2. Entity Page (`wiki/<lang>/entities/<domain>/`)
```yaml
---
type: entity
category: person  # Options: person, organization, book, software, model, tool
domain: ai        # Options: finance, software-engineering, ai, economics
lang: en          # Options: en, id
translation: "[[translated_page_name]]" # Link to parallel version in other language
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["[[source-page-name]]"]
tags: [tag1, tag2]
---
```

### 2.3. Source Metadata Page (`wiki/<lang>/sources/`)
```yaml
---
type: source
source_file: "raw/category/filename.ext"
sha256: "hex-hash-value"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
---
```

---

## 3. Operations & Agent Protocols

### 3.1. Bilingual Ingest Protocol (`/ingest <source-file>`)
Triggered when a new source is added to `raw/`.
1.  **Checksum Check**: Verify if the SHA-256 of `<source-file>` has already been processed by searching `wiki/en/sources/` or `wiki/id/sources/`.
2.  **Generate Parallel Source Metadata Pages**:
    - Create an English summary in `wiki/en/sources/source-<filename>.md`.
    - Create an Indonesian summary in `wiki/id/sources/source-<filename>-id.md`.
3.  **Compile & Integrate Bilingual Knowledge**:
    - Identify core **Concepts** in the source. Write or update parallel concepts in **both English and Indonesian** under their respective folders (e.g. `wiki/en/concepts/ai/` and `wiki/id/concepts/ai/`).
    - Cross-link them using the `translation: "[[translated_page_name]]"` frontmatter property.
    - **Indonesian Content Integrity**: In the Indonesian (`id`) version of concepts, entities, and summaries, **always preserve original mathematical formulas in LaTeX notation** (do not translate mathematical variables, subscripts, or symbols) and **maintain original English scientific/technical terms** to ensure absolute technical precision and prevent awkward literal translations.
      - *Examples of strictly preserved English terms*: *In-Context Learning*, *Few-Shot Learning*, *Prompt Engineering*, *Knowledge Distillation*, *Attention Mechanism*, *Softmax*, *Logits*, *Transformer*, *Reasoning*, *Prompt Compression*, *Embeddings*, *Context Window*, *Token*, *Inference*, *Caching*, *Fine-tuning*, *Pretraining*, *Evaluation*, *Dataset*, *Underfitting*, *Overfitting*, *Cross-entropy*, *Divergence*, *Loss Function*, *Gradient Descent*, *Neural Network*, *Gradient*, *Optimizer*, *Retrieval*, *SVG Path*, *Pattern Recognition*.
      - *Prohibited awkward literal translations*: Do NOT use awkward literal translations like "jendela konteks" (use *context window*), "pelatihan prabayar" (use *pretraining*), "penyetelan halus" (use *fine-tuning*), "pengambilan kembali" for retrieval (use *retrieval*), or "fungsi kehilangan" (use *loss function*).
    - Identify core **Entities**. Write or update parallel entities in both languages under `wiki/en/entities/` and `wiki/id/entities/`, linking them together.
4.  **Audit Logging**: Append a log entry to `wiki/log.md`:
    `## [YYYY-MM-DD] INGEST | <filename> | Compiled parallel English and Indonesian notes.`
5.  **Re-Index**: Execute `python scripts/make_index.py` locally to automatically compile both localized index files: `wiki/en/index.md` and `wiki/id/index.md`.

### 3.2. Localized Query Protocol (`/query <question>`)
1.  **Detect query language**: Determine if the query is in English or Indonesian.
2.  **Retrieve Content**: Execute `python scripts/search.py "<query>"` to locate matching pages in the target language vault.
3.  **Formulate cited answer**: Synthesize the final answer in the query language, placing explicit wikilinks (e.g. `[[Arsitektur Transformer]]` or `[[Transformer Architecture]]`) at points of assertion.

### 3.3. Bilingual Lint Protocol (`/lint`)
Verify the structural integrity of both vaults.
1.  **Execute Local Linter**: Run `python scripts/linter.py`.
2.  **Verify Translation Links**: The linter will ensure that translation target links are reciprocal (e.g. if Page A links to Page B as its translation, Page B must exist and link back to Page A).

---

## 4. Factual Contradiction Resolution Heuristics

When a new source directly contradicts facts or data recorded on an existing wiki page:
1.  **No Silent Overwrites**: Do NOT replace the old fact or statistics silently.
2.  **No Averaging**: Do NOT merge mathematical figures.
3.  **Bilingual Attribution Blocks**: Introduce matching visible `## Factual Conflicts & Debate` / `## Konflik Fakta & Debat` sections on the target pages in both languages, showing the claims side-by-side with source attribution and date.
4.  **Conflict Escalation**: Stop and prompt the user during the active session for human-in-the-loop review.

---

## 5. Pure Local Offline Fallback Protocol

If the `DEEPSEEK_API_KEY` is not present, or if external API requests fail/timeout:
1.  The system transitions to **Local Fallback Mode**.
2.  The **Antigravity CLI** agent handles all cognitive operations (summarization, extraction, integration in both languages) locally using standard vault tools.
3.  All file indexing (`en/index.md`, `id/index.md`) and validation are still automated via local Python CLI commands (`make_index.py`, `linter.py`).
