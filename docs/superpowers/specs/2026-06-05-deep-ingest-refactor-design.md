# Design Spec: Deep Ingestion Modularization & Database Optimization

**Date:** 2026-06-05  
**Topic:** Ingestion Pipeline Modularity, Database Caching, and Security Hardening

---

## 1. Goal & Context

The goal is to refactor [ingest.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/ingest.py) from a single 1500+ line script into a modular, testable package structure. In addition, we will optimize its performance to scale efficiently by using the existing SQLite search database as a metadata cache, and secure the path handling logic against traversal vulnerabilities.

---

## 2. Directory Structure & Modular Breakdown

We will move sub-components into a package structure under `scripts/ingest/`:

```
scripts/
├── ingest.py (CLI Orchestrator & Entrypoint)
└── ingest/
    ├── __init__.py
    ├── extractor.py    (PDF tables, images, parallel OCR extraction)
    ├── chunker.py      (text chunking, abstract context injection, section extraction)
    ├── llm_pipeline.py (DeepSeek APIs, Map-Reduce summarization, groundedness audit)
    ├── local_fallback.py (Offline local compiler and test mock summaries)
    ├── wikilinks.py    (Bilingual link mapping and normalization)
    └── persistence.py  (YAML formatting, file writers, version control merging)
```

### 2.1. Module Responsibilities
- **`extractor.py`**: Encapsulates all code related to file reading, `pdfplumber` tables parsing, PyMuPDF image extraction, and parallelized Tesseract OCR.
- **`chunker.py`**: Isolates text splitting algorithms and abstract header injection logic.
- **`llm_pipeline.py`**: Houses DeepSeek API client operations, groundedness reviews, and JSON response repair routines.
- **`local_fallback.py`**: Implements deterministic offline article and paper summaries.
- **`wikilinks.py`**: Resolves wikilinks between languages.
- **`persistence.py`**: Formats YAML frontmatter, compares versions, archives deprecated files, and merges content modifications.

---

## 3. SQLite Caching Schema & Integration

To remove the $O(N)$ filesystem scanning scaling bottleneck, we will store index metadata in `wiki/.search_index.db`.

### 3.1. Table Definition
```sql
CREATE TABLE IF NOT EXISTS wiki_metadata (
    path TEXT PRIMARY KEY,
    name TEXT,
    lang TEXT,
    type TEXT,
    title TEXT,
    sha256 TEXT,
    translation TEXT
);
```

### 3.2. Lifecycle Operations
- **Rebuilding Index (`scripts/make_index.py`)**:
  - The script will preserve the database file (removing the physical `os.remove` step).
  - It will run `DROP TABLE IF EXISTS search_index;` to rebuild FTS5 records.
  - It will truncate and rebuild `wiki_metadata` during indexing by scanning all markdown files.
- **Duplicate Check (`scripts/ingest/persistence.py`)**:
  - Perform query `SELECT path FROM wiki_metadata WHERE type='source' AND sha256 = ?` to resolve duplicate checks in $O(1)$ time.
- **Vault Scanning (`scripts/ingest/wikilinks.py`)**:
  - Perform query `SELECT name, lang, title, translation FROM wiki_metadata` to retrieve maps in memory instantly without reading any markdown files.

---

## 4. Security Hardening

To guard against malicious user input, we enforce absolute path checks:

### 4.1. Workspace Boundary Validation
All CLI file path arguments are checked:
1. Resolve to absolute path: `abs_path = os.path.abspath(filepath)`.
2. Retrieve project directory: `project_root = os.path.abspath(".")`.
3. Verify `abs_path.startswith(project_root)`. If false, raise `SecurityError`.

### 4.2. Target Directory Boundary Validation
All created directories (e.g. `wiki/en/sources/<name>`) must start with the absolute path of `wiki/` to prevent path injection from writing files to arbitrary system directories.

---

## 5. Verification Plan

We will verify this refactoring using the existing test suite and audits:

### 5.1. Automated Test Suites
- Run `rtk python scripts/test_wiki.py` to verify the ingestion, version control, duplicate checks, subpage generation, and index catalogs work.
- Run `rtk python scripts/linter.py` to check that the modularized outputs conform to schema rules and reciprocal translation links.
- Run `rtk python scripts/make_index.py` to ensure search indexes compile correctly.

### 5.2. Compliance Audit Suite
- Run `rtk python .agents/scripts/run_all_audits.py .` to ensure zero compilation or styling errors exist.
