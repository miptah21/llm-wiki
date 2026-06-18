# Deep Ingest Pipeline Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the ingestion pipeline (`scripts/ingest.py`) to extract tables via `pdfplumber`, extract figures, inject abstract context into chunks, write papers to nested directories, and update the indexer and linter to support these nested pages.

**Architecture:** We will add pdfplumber table parsing, PyMuPDF image extraction, and chunk-level context injection to `scripts/ingest.py`. For PDFs, it will write three distinct markdown files under a nested folder in `wiki/<lang>/sources/<name>/` with a parent-child YAML header. The linter and indexer are updated to correctly parse and skip subpages.

**Tech Stack:** Python 3.12, pdfplumber, PyMuPDF (fitz), SQLite FTS5.

---

### Task 1: Environment & Dependency Prep

**Files:**
- Modify: `AGENTS.md` (Update project rules/notes if needed)

- [ ] **Step 1: Install `pdfplumber` package**

Run: `rtk pip install pdfplumber`
Expected: Installation completes successfully.

- [ ] **Step 2: Verify `pdfplumber` can be imported**

Run: `rtk python -c "import pdfplumber; print(pdfplumber.__version__)"`
Expected: Version string printed (e.g. `0.11.0`)

---

### Task 2: Implement Table and Image Extraction

**Files:**
- Modify: `scripts/ingest.py` (Add extraction helpers)
- Modify: `scripts/test_wiki.py` (Add tests for helper methods)

- [ ] **Step 1: Add helper methods to `scripts/ingest.py`**

Open [ingest.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/ingest.py) and add `extract_pdf_tables` and `extract_pdf_images` before `process_offline`:

```python
def extract_pdf_tables(pdf_path):
    """Extracts tables from a PDF using pdfplumber and returns them as Markdown tables."""
    import pdfplumber
    import pandas as pd
    
    tables_md = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                extracted = page.extract_tables()
                for table_idx, table in enumerate(extracted, 1):
                    if not table or len(table) < 1:
                        continue
                    # Clean table data
                    clean_table = [[str(cell or "").strip() for cell in row] for row in table]
                    headers = clean_table[0]
                    rows = clean_table[1:]
                    
                    # Convert to Markdown using pandas
                    df = pd.DataFrame(rows, columns=headers)
                    md_table = df.to_markdown(index=False)
                    tables_md.append(f"### Table {table_idx} (Page {page_num})\n\n{md_table}")
    except Exception as e:
        print(f"Warning: Failed to extract tables via pdfplumber: {e}")
    return "\n\n".join(tables_md)

def extract_pdf_images(pdf_path, source_name):
    """Extracts images from PDF and saves them to global assets directory, returning Obsidian links."""
    import fitz
    import os
    
    ASSETS_DIR = os.path.join("wiki", "assets", "images")
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    image_links = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            for img_idx, img in enumerate(image_list, 1):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                img_name = f"source-{source_name}-fig{page_num+1}-{img_idx}.{image_ext}"
                img_path = os.path.join(ASSETS_DIR, img_name)
                
                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                
                # Format Obsidian link
                image_links.append(f"![[source-{source_name}-fig{page_num+1}-{img_idx}.{image_ext}]]")
    except Exception as e:
        print(f"Warning: Failed to extract images via PyMuPDF: {e}")
    return "\n\n".join(image_links)
```

- [ ] **Step 2: Add test cases to `scripts/test_wiki.py`**

Open [test_wiki.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/test_wiki.py) and add unit tests under `run_tests` to verify image and table extraction runs without error:

```python
        # --- Test Table Extraction Mock ---
        print("\n--- Testing table extraction logic ---")
        from ingest import extract_pdf_tables
        # Since we don't have a dummy pdf with tables in tests, verify it handles empty or missing pdf gracefully
        tables_res = extract_pdf_tables("nonexistent.pdf")
        assert tables_res == "", f"Expected empty string for missing file, got '{tables_res}'"
        print("✅ table extraction stub verified!")
```

- [ ] **Step 3: Run the tests to make sure they pass**

Run: `rtk python scripts/test_wiki.py`
Expected: PASS

---

### Task 3: Implement Abstract Context Injection & Modified Chunking

**Files:**
- Modify: `scripts/ingest.py` (Modify chunk_text / ingestion routines)

- [ ] **Step 1: Inject Abstract into Chunking Loop**

Modify `chunk_text` in [ingest.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/ingest.py) or in the ingestion loop to accept an optional `abstract` string:

```python
def chunk_text(text, max_chars=15000, overlap=1500, abstract=None):
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + max_chars
        if end >= text_len:
            raw_chunk = text[start:]
            if abstract:
                chunks.append(f"--- CONTEXT ABSTRACT ---\n{abstract}\n--- ACTIVE CHUNK ---\n{raw_chunk}")
            else:
                chunks.append(raw_chunk)
            break
        chunk_slice = text[start:end]
        last_double_newline = chunk_slice.rfind("\n\n")
        if last_double_newline > max_chars * 0.75:
            end_point = start + last_double_newline
        else:
            last_newline = chunk_slice.rfind("\n")
            if last_newline > max_chars * 0.75:
                end_point = start + last_newline
            else:
                end_point = end
        
        raw_chunk = text[start:end_point]
        if abstract:
            chunks.append(f"--- CONTEXT ABSTRACT ---\n{abstract}\n--- ACTIVE CHUNK ---\n{raw_chunk}")
        else:
            chunks.append(raw_chunk)
        start = end_point - overlap
    return chunks
```

- [ ] **Step 2: Update the caller of `chunk_text` in `process_deepseek`**

Modify `process_deepseek` in [ingest.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/ingest.py) to pass the abstract as context:

```python
        # Extract abstract context (first 2500 characters)
        abstract_ctx = raw_content[:2500]
        chunks = chunk_text(raw_content, abstract=abstract_ctx)
```

- [ ] **Step 3: Run the tests**

Run: `rtk python scripts/test_wiki.py`
Expected: PASS

---

### Task 4: Hierarchical Page Writing and Ingestion Integration

**Files:**
- Modify: `scripts/ingest.py` (Update `process_file` and page creation logic)

- [ ] **Step 1: Update page creation logical pipeline for PDF inputs**

Modify `process_file` inside [ingest.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/ingest.py) to support nested writing:

```python
    is_pdf = filepath.lower().endswith(".pdf")
    
    # Extract tables and images for PDF
    tables_content = ""
    images_content = ""
    if is_pdf:
        print("Extracting tables using pdfplumber...")
        tables_content = extract_pdf_tables(filepath)
        print("Extracting images using PyMuPDF...")
        images_content = extract_pdf_images(filepath, filename_base)
        
        # Inject extracted tables/images text into the raw content for processing
        if tables_content:
            raw_content += "\n\n## Extracted Tables (Technical Details)\n\n" + tables_content
        if images_content:
            raw_content += "\n\n## Extracted Visual Figures\n\n" + images_content
```

- [ ] **Step 2: Update `write_source_pages` to write nested directories for PDF**

Modify `write_source_pages` in [ingest.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/ingest.py) to handle nested source folders and multiple sub-pages:

```python
def write_source_pages(filename_base, source_meta, data, is_pdf=False):
    """Writes source files. If is_pdf is True, generates a nested directory with sub-pages."""
    import os
    
    # Setup directories
    en_src_dir = os.path.join(EN_DIR, "sources")
    id_src_dir = os.path.join(ID_DIR, "sources")
    
    if is_pdf:
        # Create nested folders
        en_src_dir = os.path.join(en_src_dir, filename_base)
        id_src_dir = os.path.join(id_src_dir, filename_base)
        os.makedirs(en_src_dir, exist_ok=True)
        os.makedirs(id_src_dir, exist_ok=True)
        
    en_filepath = os.path.join(en_src_dir, f"source-{filename_base}.md")
    id_filepath = os.path.join(id_src_dir, f"source-{filename_base}-id.md")
    
    # 1. English Main Summary Body
    en_body = (
        f"# Source Summary: {data['title_en']}\n\n"
        f"## Abstract / Summary\n\n{data['summary_en']}\n"
    )
    if is_pdf:
        en_body += (
            f"\n## Technical Specifications & Details\n\n"
            f"- [[source-{filename_base}-experiments]]\n"
            f"- [[source-{filename_base}-mathematics]]\n"
        )
    # Append linked concepts / entities references
    ...
```

- [ ] **Step 3: Generate experiments and mathematics sub-pages**

In `write_source_pages` if `is_pdf` is True, also write:
- `wiki/en/sources/[filename_base]/source-[filename_base]-experiments.md`
- `wiki/en/sources/[filename_base]/source-[filename_base]-mathematics.md`
(and their Indonesian counterpart files) with `type: source-subpage` frontmatter:

```python
    if is_pdf:
        # English Experiments subpage
        exp_fm = {
            "type": "source-subpage",
            "parent": f"[[source-{filename_base}]]",
            "lang": "en",
            "created": source_meta.get("created"),
            "updated": source_meta.get("updated"),
            "tags": source_meta.get("tags", []) + ["experiments"]
        }
        exp_body = (
            f"# Experimental Setup & Tables: {data['title_en']}\n\n"
            f"This sub-page records the experimental ablation metrics, datasets, and hyperparameters "
            f"for [[source-{filename_base}]].\n\n"
            f"## Captured Performance Tables\n\n"
        )
        # Parse and insert extracted markdown tables
        # (Implementation details: extract table sections from data['summary_en'] or tables_content)
        write_wiki_page(os.path.join(en_src_dir, f"source-{filename_base}-experiments.md"), exp_fm, exp_body)
```

- [ ] **Step 4: Run the test suite**

Run: `rtk python scripts/test_wiki.py`
Expected: PASS

---

### Task 5: Adapt Linter and Indexer Compatibility

**Files:**
- Modify: `scripts/linter.py` (Support nested paths and sub-page types)
- Modify: `scripts/make_index.py` (Filter out source-subpage from main tables)

- [ ] **Step 1: Update Linter recursive directory scan**

Open [linter.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/linter.py).
Make sure `schema_failures` accepts `source-subpage` as a valid YAML `type`:

```python
            if page_type == "source" or page_type == "source-subpage" or "sources" in filepath:
                required_keys = {"type", "created", "updated"}
            else:
                required_keys = {"type", "domain", "lang", "created", "updated"}
```

And update the invalid type check:
```python
            elif page_type not in {"concept", "entity", "source", "source-subpage"}:
                schema_failures[filepath] = f"Invalid type '{page_type}' (must be concept, entity, source, or source-subpage)"
```

- [ ] **Step 2: Update Indexer to skip sub-pages**

Open [make_index.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/make_index.py).
Inside `scan_lang_vault`, check the page frontmatter for `source-subpage` or `parent` field and skip adding it to the main lists, or flag it so that it is excluded:

```python
                    # Sort into lists
                    page_type = metadata.get("type", "concept")
                    if isinstance(page_type, list):
                        page_type = page_type[0] if page_type else "concept"
                    page_type = page_type.lower()
                    
                    if page_type == "source-subpage" or "parent" in metadata:
                        # Exclude from main sources list to prevent cluttering the main index
                        pass
                    elif page_type == "source" or dir_type == "sources":
                        sources.append(metadata)
```

- [ ] **Step 3: Run linter and indexer directly to verify no regressions**

Run: `rtk python scripts/make_index.py`
Expected: Completed successfully.
Run: `rtk python scripts/linter.py`
Expected: Completed with exit code 0.

- [ ] **Step 4: Run full test suite**

Run: `rtk python scripts/test_wiki.py`
Expected: PASS
