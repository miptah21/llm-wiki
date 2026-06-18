# LLM Wiki Schema & Guidelines (`WIKI_SCHEMA.md`)

This configuration file defines the bilingual parallel directory structure, metadata schemas, operation protocols, and local fallback heuristics for the compounding knowledge base. Any AI agent operating within this vault MUST strictly adhere to these rules.

---

## 1. Directory Structure

- `raw/`: Immutable raw source materials. Do NOT modify files in this directory.
  - `raw/papers/`: PDF research papers, textbooks, and technical journals. Separated into domain subfolders (e.g., `raw/papers/ai-ml/`, `raw/papers/finance/`, `raw/papers/personal-development/`).
  - `raw/articles/`: Web clips, blog posts, news, and markdown clippings.
  - `raw/notes/`: Personal raw thoughts, logs, and transcriptions.
- `wiki/`: Persistent compiled AI-managed Markdown Wiki.
  - `wiki/log.md`: Unified chronological log of all actions. Do NOT edit manually.
  - `wiki/en/`: === English Sub-Wiki ===
    - `wiki/en/index.md`: Auto-generated English visual index catalog.
    - `wiki/en/sources/`: Detailed summaries of sources written in English.
    - `wiki/en/concepts/`: concepts/finance/, concepts/software-engineering/, concepts/ai/, concepts/economics/, concepts/education/, concepts/personal-development/, concepts/mathematics/, concepts/language-learning/
    - `wiki/en/entities/`: entities/finance/, entities/software-engineering/, entities/ai/, entities/economics/, entities/education/, entities/personal-development/, entities/mathematics/, entities/language-learning/
  - `wiki/id/`: === Indonesian Sub-Wiki ===
    - `wiki/id/index.md`: Auto-generated Indonesian visual index catalog.
    - `wiki/id/sources/`: Detailed summaries of sources written in Indonesian.
    - `wiki/id/concepts/`: concepts/finance/, concepts/software-engineering/, concepts/ai/, concepts/economics/, concepts/education/, concepts/personal-development/, concepts/mathematics/, concepts/language-learning/
    - `wiki/id/entities/`: entities/finance/, entities/software-engineering/, entities/ai/, entities/economics/, entities/education/, entities/personal-development/, entities/mathematics/, entities/language-learning/
- `scripts/`: Pure local Python scripts for indexing, linting, search, and fallbacks.

---

## 2. Strict Page Schemas (YAML Frontmatter)

Every `.md` file created or updated in the `wiki/en/` or `wiki/id/` directories MUST start with clean YAML frontmatter.

### 2.1. Concept Page (`wiki/<lang>/concepts/<domain>/`)
```yaml
---
type: concept
domain: ai        # Options: finance, software-engineering, ai, economics, education, personal-development, mathematics, language-learning
lang: en          # Options: en, id
translation: "[[translated_page_name]]" # Link to parallel version in other language
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["[[source-page-name]]"]
description: A short 1-2 sentence definition of the concept.
relations:        # Optional. Auto-detected cross-references to other concepts.
  - target: "[[other-concept-name]]"
    type: supports | contradicts | contrasting | extends
    source: "[[source-page-name]]"
    claim: "Brief description of the specific claim"
---
```

### 2.2. Entity Page (`wiki/<lang>/entities/<domain>/`)
```yaml
---
type: entity
category: person  # Options: person, organization, book, software, model, tool
domain: ai        # Options: finance, software-engineering, ai, economics, education, personal-development, mathematics, language-learning
lang: en          # Options: en, id
translation: "[[translated_page_name]]" # Link to parallel version in other language
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["[[source-page-name]]"]
tags: [tag1, tag2]
relations:        # Optional. Auto-detected cross-references.
  - target: "[[other-entity-name]]"
    type: supports | contradicts | contrasting | extends
    source: "[[source-page-name]]"
    claim: "Brief description of the specific claim"
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
5.  **Re-Index**: Execute `rtk python scripts/make_index.py` locally to automatically compile both localized index files: `wiki/en/index.md` and `wiki/id/index.md`.

### 3.2. Localized Query & Conversational Chat Protocol (`/query <question>` or `--chat "<question>"`)
1.  **Standard Query Mode**:
    - Execute `rtk python scripts/search.py "<query>"` to locate matching pages in the target language vault.
    - Synthesize or retrieve matching pages with relevance scores and snippets.
2.  **Conversational RAG Chat Mode**:
    - Execute `rtk python scripts/search.py --chat "<question>"` to launch the RAG chat protocol. If no question is supplied, enters an interactive chat loop.
    - **Keyword Extraction**: Automatically filters out common English/Indonesian question stopwords (e.g., *what*, *how*, *apa*, *itu*, *bagaimana*) using a local heuristic stopword list to construct optimal keyword search queries.
    - **Context Retrieval**: Performs a search on the extracted keywords to find the most relevant source documents in the SQLite FTS5 database (or falls back to a linear scan).
    - **DeepSeek Integration**: Feeds the top 5 document contents as context to the DeepSeek API (`deepseek-chat`). If the API key is missing or in mock mode (`MOCK_DEEPSEEK=1`), simulates the response.
    - **Preservation of Terms**: Ensures the generated answer grounds itself in the provided context, matches the user's queried language, and strictly preserves scientific terms (e.g., *In-Context Learning*, *Softmax*) and LaTeX mathematical notations natively.

### 3.3. Bilingual Lint Protocol (`/lint`)
Verify the structural integrity of both vaults.
1.  **Execute Local Linter**: Run `rtk python scripts/linter.py`.
2.  **Verify Translation Links**: The linter will ensure that translation target links are reciprocal (e.g. if Page A links to Page B as its translation, Page B must exist and link back to Page A).

---

## 4. Cross-Reference & Contradiction Resolution

The ingestion pipeline automatically detects and surfaces relationships between concepts from different sources.

### 4.1. Relation Types
- **`supports`**: New source provides evidence that reinforces an existing concept's claims.
- **`contradicts`**: New source presents findings that conflict with an existing concept.
- **`contrasting`**: New source presents findings that contrast, differ from, or offer an alternative perspective to an existing concept (mapped to `contradicts` / `bertentangan` groups).
- **`extends`**: New source builds upon, refines, or generalizes an existing concept.

### 4.2. Rendering Rules
1.  **No Silent Overwrites**: Do NOT replace old facts or statistics silently.
2.  **No Averaging**: Do NOT merge mathematical figures.
3.  **Bilingual Cross-Reference Sections**: Every concept/entity page with detected relations MUST have a `## Cross-References` (EN) / `## Referensi Silang` (ID) section, grouped by relation type:
    - `### Supports` / `### Mendukung`
    - `### Contradicts` / `### Bertentangan` (includes both `contradicts` and `contrasting` relations)
    - `### Extends` / `### Memperluas`
4.  **Source Attribution**: Each relation entry must cite the source paper via wikilink.
5.  **Conflict Escalation**: When `contradicts` relations are detected, log a warning and prompt the user during the active session for human-in-the-loop review.
6.  **Source Page Summary**: Each source page includes a `## Cross-References` table summarizing all relations detected from that paper.
7.  **Frontmatter Storage**: Relations are stored in the `relations:` frontmatter field for programmatic access.

---

## 5. Pure Local Offline Fallback Protocol

If the `DEEPSEEK_API_KEY` is not present, or if external API requests fail/timeout:
1.  The system transitions to **Local Fallback Mode**.
2.  The **Antigravity CLI** agent handles all cognitive operations (summarization, extraction, integration in both languages) locally using standard vault tools.
3.  All file indexing (`en/index.md`, `id/index.md`) and validation are still automated via local Python CLI commands (`make_index.py`, `linter.py`).
