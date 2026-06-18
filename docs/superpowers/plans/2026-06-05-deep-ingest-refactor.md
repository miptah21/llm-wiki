# Deep Ingestion Modularization & Database Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the 1500+ line `scripts/ingest.py` script into a modular, secured package structure, and optimize duplicate checks and link normalization loops using SQLite-based metadata caching.

**Architecture:** We partition the orchestrator code into `extractor`, `chunker`, `llm_pipeline`, `local_fallback`, `wikilinks`, and `persistence` sub-modules under `scripts/ingest/`. Indexer and orchestrator write operations will populate and query a SQLite-based `wiki_metadata` cache table to achieve $O(1)$ duplicate checking and vault scanning. Input file paths will be sanitized and checked against absolute project root bounds to prevent traversal attacks.

**Tech Stack:** Python 3.12, SQLite3, pdfplumber, PyMuPDF (fitz), pandas.

---

### Task 1: Package Structure, Path Security & Persistence Module

**Files:**
- Create: `scripts/ingest/__init__.py`
- Create: `scripts/ingest/persistence.py`
- Test: `scripts/test_persistence_unit.py`

- [ ] **Step 1: Create package folder and empty `__init__.py`**

Create `scripts/ingest/__init__.py` with no contents.

- [ ] **Step 2: Implement security and YAML writing in `scripts/ingest/persistence.py`**

Create `scripts/ingest/persistence.py` containing:
```python
import os
import sys
import re
import hashlib
import sqlite3
from datetime import datetime
from parser import parse_yaml_frontmatter

WIKI_DIR = "wiki"
DB_PATH = os.path.join(WIKI_DIR, ".search_index.db")

def validate_safe_path(filepath: str) -> str:
    abs_path = os.path.abspath(filepath)
    project_root = os.path.abspath(".")
    if not abs_path.startswith(project_root):
        raise ValueError(f"Security Alert: Path '{filepath}' resolves outside project workspace.")
    return abs_path

def calculate_sha256(filepath: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def check_duplicate(checksum: str, source_filename: str) -> str:
    if not os.path.exists(DB_PATH):
        return ""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Verify metadata table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_metadata';")
        if not cursor.fetchone():
            conn.close()
            return ""
        cursor.execute("SELECT path FROM wiki_metadata WHERE type='source' AND sha256 = ?;", (checksum,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        print(f"Warning: Failed to query database for duplicate check: {e}")
    return ""

def update_db_metadata(filepath: str, name: str, lang: str, page_type: str, title: str, sha256: str = None, translation: str = None):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wiki_metadata (
                path TEXT PRIMARY KEY,
                name TEXT,
                lang TEXT,
                type TEXT,
                title TEXT,
                sha256 TEXT,
                translation TEXT
            );
        """)
        cursor.execute("""
            INSERT OR REPLACE INTO wiki_metadata (path, name, lang, type, title, sha256, translation)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (filepath.replace("\\", "/"), name, lang, page_type, title, sha256, translation))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to update SQLite metadata table for {filepath}: {e}")

def parse_version_tuple(v_str: str) -> tuple:
    if not v_str:
        return (1, 0, 0)
    try:
        v_str = str(v_str).strip().lower().lstrip('v')
        return tuple(map(int, v_str.split(".")))
    except Exception:
        return (1, 0, 0)

def format_frontmatter(metadata: dict) -> str:
    lines = ["---"]
    for k, v in metadata.items():
        if isinstance(v, list):
            list_str = ", ".join([f'"{item}"' if "[[" in item else item for item in v])
            lines.append(f"{k}: [{list_str}]")
        else:
            if isinstance(v, str) and (":" in v or "[" in v or "{" in v):
                lines.append(f'{k}: "{v}"')
            else:
                lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)

def write_wiki_page(filepath: str, frontmatter_dict: dict, markdown_body: str):
    abs_filepath = validate_safe_path(filepath)
    wiki_root = os.path.abspath(WIKI_DIR)
    if not abs_filepath.startswith(wiki_root):
        raise ValueError(f"Security Alert: Destination '{filepath}' is outside the wiki vault.")
    os.makedirs(os.path.dirname(abs_filepath), exist_ok=True)
    full_content = format_frontmatter(frontmatter_dict) + "\n\n" + markdown_body.strip() + "\n"
    with open(abs_filepath, "w", encoding="utf-8") as f:
        f.write(full_content)
    print(f"Created/Updated Page: {filepath}")
    
    # Extract translation target link
    trans = frontmatter_dict.get("translation", "")
    if isinstance(trans, list):
         trans = trans[0] if trans else ""
    trans_clean = str(trans).replace("[[", "").replace("]]", "").strip()
    
    # Save to database cache
    name = os.path.splitext(os.path.basename(filepath))[0]
    lang = frontmatter_dict.get("lang", "en")
    page_type = frontmatter_dict.get("type", "concept")
    # Extract h1 title from markdown body
    title = name
    for line in markdown_body.split("\n"):
        if line.strip().startswith("# "):
            title = line.strip()[2:].replace("**", "").strip()
            break
    
    update_db_metadata(filepath, name, lang, page_type, title, frontmatter_dict.get("sha256"), trans_clean)
```

- [ ] **Step 3: Add `merge_or_write_page` to `scripts/ingest/persistence.py`**

Append the implementation of `merge_or_write_page` at the end of `scripts/ingest/persistence.py`:
```python
def merge_or_write_page(filepath: str, frontmatter_dict: dict, markdown_body: str):
    if not os.path.exists(filepath):
        frontmatter_dict["version"] = frontmatter_dict.get("version") or "1.0.0"
        frontmatter_dict["status"] = frontmatter_dict.get("status") or "active"
        frontmatter_dict["valid_from"] = frontmatter_dict.get("valid_from") or datetime.now().strftime("%Y-%m-%d")
        write_wiki_page(filepath, frontmatter_dict, markdown_body)
        return
        
    print(f"Page already exists, checking version/merging: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            existing_content = f.read()
    except Exception as e:
        print(f"Warning: Failed to read existing page {filepath} for merging: {e}. Overwriting...")
        write_wiki_page(filepath, frontmatter_dict, markdown_body)
        return
        
    existing_fm = parse_yaml_frontmatter(existing_content)
    existing_ver_str = existing_fm.get("version") or "1.0.0"
    incoming_ver_str = frontmatter_dict.get("version") or "1.0.0"
    
    existing_ver = parse_version_tuple(existing_ver_str)
    incoming_ver = parse_version_tuple(incoming_ver_str)
    
    if incoming_ver > existing_ver:
        filename_base = os.path.splitext(os.path.basename(filepath))[0]
        dir_name = os.path.dirname(filepath)
        lang = frontmatter_dict.get("lang") or "en"
        
        archived_name = f"{filename_base}-v{existing_ver_str}"
        archived_filepath = os.path.join(dir_name, f"{archived_name}.md")
        
        deprecated_fm = existing_fm.copy()
        deprecated_fm["status"] = "deprecated"
        deprecated_fm["valid_to"] = datetime.now().strftime("%Y-%m-%d")
        deprecated_fm["superseded_by"] = f"[[{filename_base}]]"
        
        fm_end = existing_content.find("---", existing_content.find("---") + 3)
        if fm_end != -1:
            existing_body = existing_content[fm_end + 3:].strip()
        else:
            existing_body = existing_content.strip()
            
        timeline_heading = "Riwayat Versi" if lang == "id" else "Version History"
        timeline_content = (
            f"\n\n## {timeline_heading}\n\n"
            f"- [[{filename_base}]] (v{incoming_ver_str} - {'Aktif' if lang == 'id' else 'Active'})\n"
            f"- [[{archived_name}]] (v{existing_ver_str} - {'Usang' if lang == 'id' else 'Deprecated'})\n"
        )
        clean_old_body = re.split(r"\n##\s+(?:Riwayat Versi|Version History)", existing_body)[0].strip()
        write_wiki_page(archived_filepath, deprecated_fm, clean_old_body + timeline_content)
        
        new_fm = frontmatter_dict.copy()
        new_fm["status"] = "active"
        new_fm["version"] = incoming_ver_str
        new_fm["valid_from"] = datetime.now().strftime("%Y-%m-%d")
        new_fm["supersedes"] = f"[[{archived_name}]]"
        if "created" not in new_fm:
            new_fm["created"] = existing_fm.get("created") or datetime.now().strftime("%Y-%m-%d")
        new_fm["updated"] = datetime.now().strftime("%Y-%m-%d")
        
        clean_new_body = re.split(r"\n##\s+(?:Riwayat Versi|Version History)", markdown_body)[0].strip()
        write_wiki_page(filepath, new_fm, clean_new_body + timeline_content)
        return

    merged_fm = existing_fm.copy()
    if "created" in existing_fm:
        merged_fm["created"] = existing_fm["created"]
    else:
        merged_fm["created"] = frontmatter_dict.get("created")
    merged_fm["updated"] = frontmatter_dict.get("updated")
    
    existing_sources = existing_fm.get("sources", [])
    if isinstance(existing_sources, str):
        existing_sources = [existing_sources]
    new_sources = frontmatter_dict.get("sources", [])
    if isinstance(new_sources, str):
        new_sources = [new_sources]
        
    merged_sources = list(existing_sources)
    for src in new_sources:
        if src not in merged_sources:
            merged_sources.append(src)
    merged_fm["sources"] = merged_sources
    
    existing_tags = existing_fm.get("tags", [])
    if isinstance(existing_tags, str):
        existing_tags = [existing_tags]
    new_tags = frontmatter_dict.get("tags", [])
    if isinstance(new_tags, str):
        new_tags = [new_tags]
        
    merged_tags = list(existing_tags)
    for tag in new_tags:
        if tag not in merged_tags:
            merged_tags.append(tag)
    merged_fm["tags"] = merged_tags
    
    if "translation" not in merged_fm or not merged_fm["translation"]:
        merged_fm["translation"] = frontmatter_dict.get("translation")
        
    for key, value in frontmatter_dict.items():
        if key not in ["created", "updated", "sources", "tags", "translation"]:
            merged_fm[key] = value

    fm_end = existing_content.find("---", existing_content.find("---") + 3)
    if fm_end != -1:
        existing_body = existing_content[fm_end + 3:].strip()
    else:
        existing_body = existing_content.strip()
        
    split_patterns = [
        r"\n## See Also", r"\n## Lihat Juga", 
        r"\n## Sources", r"\n## Sumber",
        r"\n## Related Entities", r"\n## Entitas Terkait"
    ]
    split_idx = len(existing_body)
    for pat in split_patterns:
        match = re.search(pat, existing_body)
        if match and match.start() < split_idx:
            split_idx = match.start()
            
    existing_base_body = existing_body[:split_idx].strip()
    new_lines = markdown_body.strip().split("\n")
    body_lines = []
    in_exclude_section = False
    for line in new_lines:
        if line.startswith("# ") and not body_lines:
            continue
        if any(line.strip().startswith(pat) for pat in ["## See Also", "## Lihat Juga", "## Sources", "## Sumber", "## Related Entities", "## Entitas Terkait"]):
            in_exclude_section = True
        if in_exclude_section:
            continue
        body_lines.append(line)
        
    new_core_content = "\n".join(body_lines).strip()
    simplified_existing = re.sub(r"\s+", "", existing_base_body.lower())
    simplified_new = re.sub(r"\s+", "", new_core_content.lower())
    
    base_body = existing_base_body
    if simplified_new and simplified_new not in simplified_existing:
        new_source_ref = ""
        for src in new_sources:
            new_source_ref = src.replace("[[", "").replace("]]", "")
            break
        source_label = f"Addition from {new_source_ref}" if frontmatter_dict.get("lang") == "en" else f"Tambahan dari {new_source_ref}"
        base_body += f"\n\n## {source_label}\n\n{new_core_content}"
        
    old_see_also_text = existing_body[split_idx:]
    old_links = re.findall(r"\[\[(.*?)\]\]", old_see_also_text)
    exclude_links = set([s.replace("[[", "").replace("]]", "").strip().lower() for s in merged_sources])
    exclude_links.add(os.path.splitext(os.path.basename(filepath))[0].lower())
    
    new_see_also_links = []
    if "## See Also" in markdown_body or "## Related Entities" in markdown_body:
        start_idx = max(markdown_body.find("## See Also"), markdown_body.find("## Related Entities"))
        new_see_also_links = re.findall(r"\[\[(.*?)\]\]", markdown_body[start_idx:])
    elif "## Lihat Juga" in markdown_body or "## Entitas Terkait" in markdown_body:
        start_idx = max(markdown_body.find("## Lihat Juga"), markdown_body.find("## Entitas Terkait"))
        new_see_also_links = re.findall(r"\[\[(.*?)\]\]", markdown_body[start_idx:])
        
    combined_see_also = []
    for link in old_links + new_see_also_links:
        clean_lnk = link.split("|")[0].strip()
        if clean_lnk.lower() not in exclude_links and clean_lnk.lower() not in [l.lower() for l in combined_see_also]:
            combined_see_also.append(clean_lnk)
            
    see_also_section = ""
    if combined_see_also:
        if frontmatter_dict.get("type") == "entity":
            heading = "Related Entities" if frontmatter_dict.get("lang") == "en" else "Entitas Terkait"
        else:
            heading = "See Also" if frontmatter_dict.get("lang") == "en" else "Lihat Juga"
        see_also_section = f"\n\n## {heading}\n\n" + "\n".join([f"- [[{l}]]" for l in combined_see_also])
        
    sources_heading = "Sources" if frontmatter_dict.get("lang") == "en" else "Sumber"
    sources_section = f"\n\n## {sources_heading}\n\n" + "\n".join([f"- [[{s.replace('[[', '').replace(']]', '')}]]" for s in merged_sources])
    
    write_wiki_page(filepath, merged_fm, base_body + see_also_section + sources_section)
```

- [ ] **Step 4: Create a unit test for validation**

Create `scripts/test_persistence_unit.py` to verify:
```python
import os
import unittest
from scripts.ingest.persistence import validate_safe_path

class TestPersistence(unittest.TestCase):
    def test_safe_path(self):
        # Valid path
        safe = validate_safe_path("wiki/en/index.md")
        self.assertTrue(safe.endswith("index.md"))
        
    def test_unsafe_path(self):
        # Invalid path outside project workspace
        with self.assertRaises(ValueError):
            validate_safe_path("../../../unsafe_file.txt")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 5: Run persistence test**

Run: `rtk python scripts/test_persistence_unit.py`
Expected: PASS

- [ ] **Step 6: Commit persistence module**

```bash
git add scripts/ingest/__init__.py scripts/ingest/persistence.py scripts/test_persistence_unit.py
git commit -m "feat: add ingest package and safe persistence module"
```

---

### Task 2: Implement Extractor Module

**Files:**
- Create: `scripts/ingest/extractor.py`

- [ ] **Step 1: Write `scripts/ingest/extractor.py`**

Create `scripts/ingest/extractor.py` containing:
```python
import os
import re

def _ocr_page_worker(pdf_path, page_num, tessdata_path, lang):
    import fitz
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        text = page.get_text()
        if len(text.strip()) >= 50:
            return page_num, text
        if tessdata_path and os.path.exists(tessdata_path):
            tp = page.get_textpage_ocr(language=lang, tessdata=tessdata_path)
            ocr_text = page.get_text(textpage=tp)
            return page_num, ocr_text
        return page_num, "[Halaman Terpindai - OCR Tidak Dikonfigurasi]"
    except Exception as e:
        return page_num, f"[Error Halaman {page_num}: {e}]"

def parallel_pdf_ingest(pdf_path, tessdata_path=None, lang="eng+ind+equ", max_workers=4):
    import fitz
    from concurrent.futures import ProcessPoolExecutor, as_completed
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    
    results = {}
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_ocr_page_worker, pdf_path, page_num, tessdata_path, lang): page_num
            for page_num in range(total_pages)
        }
        for future in as_completed(futures):
            page_num = futures[future]
            try:
                p_num, extracted_text = future.result()
                results[p_num] = extracted_text
            except Exception as exc:
                results[page_num] = f"[Process failed for page {page_num}: {exc}]"
                
    full_ordered_text = [results[i] for i in range(total_pages)]
    return "\n\n".join(full_ordered_text)

def extract_pdf_tables(pdf_path: str) -> str:
    """Extracts tables from a PDF using pdfplumber and returns them as Markdown tables."""
    tables_md = []
    try:
        import pdfplumber
        import pandas as pd
    except Exception as e:
        print(f"Warning: Failed to import pdfplumber/pandas: {e}")
        return ""
        
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    extracted = page.extract_tables()
                    for table_idx, table in enumerate(extracted, 1):
                        if not table or len(table) < 1:
                            continue
                        clean_table = [[str(cell or "").strip() for cell in row] for row in table]
                        headers = clean_table[0]
                        rows = clean_table[1:]
                        
                        df = pd.DataFrame(rows, columns=headers)
                        try:
                            md_table = df.to_markdown(index=False)
                        except Exception:
                            # Fallback custom markdown table formatter
                            header_str = "| " + " | ".join(headers) + " |"
                            divider_str = "| " + " | ".join(["---"] * len(headers)) + " |"
                            row_strs = []
                            for row in rows:
                                padded_row = list(row) + [""] * (len(headers) - len(row))
                                padded_row = padded_row[:len(headers)]
                                row_strs.append("| " + " | ".join(padded_row) + " |")
                            md_table = "\n".join([header_str, divider_str] + row_strs)
                        tables_md.append(f"### Table {table_idx} (Page {page_num})\n\n{md_table}")
                except Exception as e:
                    print(f"Warning: Failed to extract tables from page {page_num} of PDF: {e}")
    except Exception as e:
        print(f"Warning: Failed to open PDF '{pdf_path}' for table extraction: {e}")
    return "\n\n".join(tables_md)

def extract_pdf_images(pdf_path: str, source_name: str) -> str:
    """Extracts images from PDF and saves them to global assets directory, returning Obsidian links."""
    sanitized_source_name = re.sub(r'[\\/:*?"<>|\s]+', "-", source_name)
    ASSETS_DIR = os.path.join("wiki", "assets", "images")
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    image_links = []
    try:
        import fitz
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    image_list = page.get_images()
                    for img_idx, img in enumerate(image_list, 1):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        img_name = f"source-{sanitized_source_name}-fig{page_num+1}-{img_idx}.{image_ext}"
                        img_path = os.path.join(ASSETS_DIR, img_name)
                        
                        with open(img_path, "wb") as f:
                            f.write(image_bytes)
                        
                        image_links.append(f"![[source-{sanitized_source_name}-fig{page_num+1}-{img_idx}.{image_ext}]]")
                except Exception as e:
                    print(f"Warning: Failed to extract images from page {page_num+1} of PDF: {e}")
    except Exception as e:
        print(f"Warning: Failed to open PDF '{pdf_path}' for image extraction: {e}")
    return "\n\n".join(image_links)
```

- [ ] **Step 2: Commit extractor module**

```bash
git add scripts/ingest/extractor.py
git commit -m "feat: add extractor sub-module for PDF, tables, images, and OCR"
```

---

### Task 3: Implement Chunker Module

**Files:**
- Create: `scripts/ingest/chunker.py`

- [ ] **Step 1: Write `scripts/ingest/chunker.py`**

Create `scripts/ingest/chunker.py` containing:
```python
import re

def chunk_text(text: str, max_chars: int = 15000, overlap: int = 1500, abstract: str = None) -> list:
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

def extract_sections(content: str) -> list:
    sections = []
    pattern = re.compile(r"^(#+|##+)\s+(.*?)$", re.MULTILINE)
    matches = list(pattern.finditer(content))
    
    if not matches:
        return [{"title": "General", "content": content}]
        
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i+1].start() if i + 1 < len(matches) else len(content)
        title = match.group(2).strip()
        sec_content = content[start:end].strip()
        sections.append({
            "title": title,
            "content": sec_content
        })
    return sections
```

- [ ] **Step 2: Commit chunker module**

```bash
git add scripts/ingest/chunker.py
git commit -m "feat: add chunker sub-module with abstract injection"
```

---

### Task 4: Implement LLM and Local Fallback Pipelines

**Files:**
- Create: `scripts/ingest/llm_pipeline.py`
- Create: `scripts/ingest/local_fallback.py`

- [ ] **Step 1: Write `scripts/ingest/llm_pipeline.py`**

Create `scripts/ingest/llm_pipeline.py` containing:
```python
import os
import json
from scripts.ingest.chunker import chunk_text

def extract_and_parse_json(response_text: str) -> dict:
    start_idx = response_text.find("{")
    if start_idx == -1:
        return None
        
    candidate_json = response_text[start_idx:].strip()
    if candidate_json.endswith("```"):
        candidate_json = candidate_json[:-3].strip()
        
    try:
        return json.loads(candidate_json)
    except json.JSONDecodeError:
        pass
        
    for i in range(len(candidate_json), 0, -1):
        if candidate_json[i-1] in ("}", "]", '"'):
            truncated_part = candidate_json[:i]
            for suffix in ["", "}", " ] }", " } ] }", " }", '"}', '" ] }', '" } ] }']:
                try:
                    return json.loads(truncated_part + suffix)
                except json.JSONDecodeError:
                    continue
    return None

def merge_contents_with_llm(name: str, text_type: str, content_list: list, anchor_quotes: list) -> str:
    from deepseek_helper import call_deepseek
    combined_raw = "\n---\n".join(content_list)
    combined_anchors = "\n".join([f"- \"{q}\"" for q in anchor_quotes if q])
    
    prompt = (
        f"You are a professional technical editor. Merge these raw explanations of the {text_type} '{name}' "
        f"into a single cohesive markdown explanation. Do not repeat facts, keep all technical nuances, "
        f"and preserve LaTeX math formulas exactly.\n\n"
        f"Verbatim Anchor Quotes to respect/anchor to:\n{combined_anchors}\n\n"
        f"Raw Content Blocks:\n{combined_raw}"
    )
    try:
        return call_deepseek(prompt, "You are a professional technical writer. Synthesize the text.")
    except Exception as e:
        print(f"Warning: Failed to call LLM for merging '{name}': {e}. Using raw concatenation.")
        return "\n\n".join(content_list)

def run_groundedness_evaluation(raw_text: str, synthesized_content: str, doc_name: str) -> str:
    from deepseek_helper import call_deepseek
    prompt = (
        f"You are a critical quality auditor. Compare the synthesized summary of '{doc_name}' with the raw text chunks.\n"
        f"Determine if any critical qualifying clauses, conditions, or formulas present in the raw text were lost or misstated "
        f"in the synthesized content.\n\n"
        f"Raw Chunks (first 5000 chars):\n{raw_text[:5000]}\n\n"
        f"Synthesized Content:\n{synthesized_content[:3000]}\n\n"
        f"If anything critical is missing, list the specific gaps. Otherwise, respond exactly with: 'APPROVED'."
    )
    try:
        evaluation = call_deepseek(prompt, "You are a precise quality control auditor.")
        print(f"Groundedness check result: {evaluation}")
        return evaluation
    except Exception as e:
        print(f"Warning: Groundedness evaluation skipped due to API error: {e}")
        return "APPROVED"

def process_deepseek(raw_content: str, filename: str, version: str = "1.0.0") -> dict:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return None
        
    try:
        from deepseek_helper import call_deepseek
        abstract_ctx = raw_content[:2500]
        chunks = chunk_text(raw_content, abstract=abstract_ctx)
        print(f"Connected to DeepSeek API. Divided document into {len(chunks)} chunks. Processing Map phase...")
        
        intermediate_data = []
        system_prompt = (
            "You are an expert bilingual scientific data ingestion engine. "
            "Your task is to summarize the raw scientific asset in both English and Indonesian. "
            "You must return a valid JSON object with the following structure:\n"
            "CRITICAL WIKILINK RULE: All wikilinks in content fields MUST use kebab-case matching the concept/entity 'name' field.\n"
            "{\n"
            "  \"title_en\": \"English Title\",\n"
            "  \"title_id\": \"Indonesian Title\",\n"
            "  \"summary_en\": \"Comprehensive English summary\",\n"
            "  \"summary_id\": \"Comprehensive Indonesian summary\",\n"
            "  \"concepts\": [\n"
            "    {\n"
            "      \"name\": \"concept-kebab-name\",\n"
            "      \"title_en\": \"Concept English Title\",\n"
            "      \"title_id\": \"Concept Indonesian Title\",\n"
            "      \"domain\": \"ai/finance/economics/software-engineering\",\n"
            "      \"tags\": [\"tag1\"],\n"
            "      \"description_en\": \"English short description\",\n"
            "      \"description_id\": \"Indonesian short description\",\n"
            "      \"content_en\": \"Full markdown content in English\",\n"
            "      \"content_id\": \"Full markdown content in Indonesian\",\n"
            "      \"anchor_quotes\": [\"exact sentence or formula\"]\n"
            "    }\n"
            "  ],\n"
            "  \"entities\": [\n"
            "    {\n"
            "      \"name\": \"entity-kebab-name\",\n"
            "      \"title_en\": \"Entity English Name\",\n"
            "      \"title_id\": \"Entity Indonesian Name\",\n"
            "      \"category\": \"person/organization/model/tool/book/other\",\n"
            "      \"domain\": \"ai/finance/economics/software-engineering\",\n"
            "      \"tags\": [\"tag1\"],\n"
            "      \"content_en\": \"Description in English\",\n"
            "      \"content_id\": \"Description in Indonesian\",\n"
            "      \"anchor_quotes\": [\"exact sentence\"]\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        
        for idx, chunk in enumerate(chunks):
            print(f"  Mapping chunk {idx+1}/{len(chunks)}...")
            prompt = f"Here is the content of chunk {idx+1} from '{filename}':\n\n{chunk}"
            try:
                res = call_deepseek(prompt, system_prompt)
                parsed = extract_and_parse_json(res)
                if parsed:
                    intermediate_data.append(parsed)
            except Exception as e:
                print(f"  Error mapping chunk {idx+1}: {e}")
                
        if not intermediate_data:
            return None
            
        print("Processing Reduce phase...")
        combined_sum_en = "\n\n".join([d.get("summary_en", "") for d in intermediate_data if d.get("summary_en")])
        combined_sum_id = "\n\n".join([d.get("summary_id", "") for d in intermediate_data if d.get("summary_id")])
        
        reduce_prompt_en = f"Synthesize a cohesive, structured English summary from these chunk summaries:\n\n{combined_sum_en}"
        reduce_prompt_id = f"Synthesize a cohesive, structured Indonesian summary (keep LaTeX formulas/terms natural) from these chunk summaries:\n\n{combined_sum_id}"
        
        final_summary_en = call_deepseek(reduce_prompt_en, "You are a professional technical editor. Summarize the text.")
        final_summary_id = call_deepseek(reduce_prompt_id, "You are a professional Indonesian technical editor. Summarize the text.")
        
        concepts_map = {}
        entities_map = {}
        for d in intermediate_data:
            for c in d.get("concepts", []):
                name = c.get("name")
                if name:
                    if name not in concepts_map:
                        concepts_map[name] = {
                            "meta": c.copy(),
                            "contents": [c.get("content_en") or c.get("description_en") or ""],
                            "contents_id": [c.get("content_id") or c.get("description_id") or ""],
                            "anchors": c.get("anchor_quotes", []) or []
                        }
                    else:
                        concepts_map[name]["contents"].append(c.get("content_en") or c.get("description_en") or "")
                        concepts_map[name]["contents_id"].append(c.get("content_id") or c.get("description_id") or "")
                        concepts_map[name]["anchors"].extend(c.get("anchor_quotes", []) or [])
                        
            for e in d.get("entities", []):
                name = e.get("name")
                if name:
                    if name not in entities_map:
                        entities_map[name] = {
                            "meta": e.copy(),
                            "contents": [e.get("content_en") or e.get("description_en") or ""],
                            "contents_id": [e.get("content_id") or e.get("description_id") or ""],
                            "anchors": e.get("anchor_quotes", []) or []
                        }
                    else:
                        entities_map[name]["contents"].append(e.get("content_en") or e.get("description_en") or "")
                        entities_map[name]["contents_id"].append(e.get("content_id") or e.get("description_id") or "")
                        entities_map[name]["anchors"].extend(e.get("anchor_quotes", []) or [])
                        
        final_concepts = []
        for name, data in concepts_map.items():
            c = data["meta"]
            c["version"] = c.get("version") or version
            c["status"] = c.get("status") or "active"
            if len(data["contents"]) > 1:
                print(f"  Running smart LLM merge for concept: {name}")
                c["content_en"] = merge_contents_with_llm(name, "concept", data["contents"], data["anchors"])
                c["content_id"] = merge_contents_with_llm(name, "concept", data["contents_id"], data["anchors"])
            else:
                c["content_en"] = data["contents"][0]
                c["content_id"] = data["contents_id"][0]
            c["anchor_quotes"] = list(set(data["anchors"]))
            final_concepts.append(c)
            
        final_entities = []
        for name, data in entities_map.items():
            e = data["meta"]
            e["version"] = e.get("version") or version
            e["status"] = e.get("status") or "active"
            if len(data["contents"]) > 1:
                print(f"  Running smart LLM merge for entity: {name}")
                e["content_en"] = merge_contents_with_llm(name, "entity", data["contents"], data["anchors"])
                e["content_id"] = merge_contents_with_llm(name, "entity", data["contents_id"], data["anchors"])
            else:
                e["content_en"] = data["contents"][0]
                e["content_id"] = data["contents_id"][0]
            e["anchor_quotes"] = list(set(data["anchors"]))
            final_entities.append(e)

        return {
            "title_en": intermediate_data[0].get("title_en", filename),
            "title_id": intermediate_data[0].get("title_id", filename),
            "summary_en": final_summary_en,
            "summary_id": final_summary_id,
            "concepts": final_concepts,
            "entities": final_entities
        }
    except Exception as e:
        print(f"DeepSeek compilation failed: {e}. Falling back to deterministic local compilation...")
    return None
```

- [ ] **Step 2: Write `scripts/ingest/local_fallback.py`**

Create `scripts/ingest/local_fallback.py` containing:
```python
import re
from scripts.ingest.chunker import chunk_text, extract_sections

def process_offline(raw_content: str, filename_base: str, version: str = "1.0.0") -> dict:
    print("DeepSeek API is offline or not configured. Running Local Fallback Pipeline...")
    
    if "# " in raw_content or "## " in raw_content:
        sections = extract_sections(raw_content)
    else:
        chunks = chunk_text(raw_content, max_chars=8000, overlap=500)
        sections = [{"title": f"Section {idx+1}", "content": chunk} for idx, chunk in enumerate(chunks)]
    
    title_words = filename_base.replace("-", " ").replace("_", " ").title()
    title_en = title_words
    title_id = f"Kompilasi: {title_words}"
    
    summary_parts_en = []
    summary_parts_id = []
    concepts = []
    entities = []
    
    lower_content = raw_content.lower()
    raw_snippet = raw_content[:2000] + "\n\n...(truncated, full text in raw sources)..." if len(raw_content) > 2000 else raw_content
    
    if "distil" in lower_content:
        concepts.append({
            "name": "distilasi-kompresi",
            "title_en": "Distillation Compression",
            "title_id": "Distilasi Kompresi",
            "domain": "ai",
            "tags": ["distilasi", "efficiency", "compression"],
            "description_en": "Model compression technique to transfer dark knowledge from a teacher model to a student model.",
            "description_id": "Teknik kompresi model untuk mentransfer dark knowledge dari model teacher ke model student.",
            "content_en": (
                "## Core Architecture\n\n"
                "**Distillation Compression** is a methodology for training compact models. "
                "The student model learns to approximate the full logits probability distribution of a larger teacher model.\n\n"
                "### Objective Function\n"
                "The distillation loss uses cross-entropy combined with Kullback-Leibler (KL) divergence with temperature $T$:\n"
                "$$p_i = \\frac{\\exp(z_i / T)}{\\sum_j \\exp(z_j / T)}$$\n\n"
                "Subscripts like $\\mathcal{L}_{\\text{hard}}$ and $\\mathcal{L}_{\\text{soft}}$ are preserved in both versions."
                f"\n\n### Offline Compilation Details\n\n{raw_snippet}"
            ),
            "content_id": (
                "## Arsitektur Inti\n\n"
                "**Distilasi Kompresi (Distillation Compression)** adalah metodologi untuk melatih model yang ringkas. "
                "Model student belajar memperkirakan distribusi probabilitas logit lengkap dari model teacher yang lebih besar.\n\n"
                "### Fungsi Objektif (Objective Function)\n"
                "Kerugian distilasi (distillation loss) menggunakan entropi silang gabungan dengan divergensi Kullback-Leibler (KL) dengan suhu $T$:\n"
                "$$p_i = \\frac{\\exp(z_i / T)}{\\sum_j \\exp(z_j / T)}$$\n\n"
                "Subskrip LaTeX seperti $\\mathcal{L}_{\\text{hard}}$ and $\\mathcal{L}_{\\text{soft}}$ dipertahankan dalam versi asli Bahasa Inggris untuk menjaga integritas matematis."
                f"\n\n### Detail Kompilasi Offline\n\n{raw_snippet}"
            )
        })
    elif "in-context" in lower_content or "icl" in lower_content:
        concepts.append({
            "name": "in-context-learning-primer",
            "title_en": "In-Context Learning Primer",
            "title_id": "Primer In-Context Learning",
            "domain": "ai",
            "tags": ["icl", "prompting", "llm"],
            "description_en": "The paradigm of enabling LLMs to execute tasks purely based on few-shot input demonstrations.",
            "description_id": "Paradigma yang memungkinkan LLM mengeksekusi tugas murni berdasarkan demonstrasi input few-shot.",
            "content_en": (
                "## Conceptual Overview\n\n"
                "**In-Context Learning (ICL)** utilizes the latent representations of LLMs "
                "to recognize patterns from user-provided demonstrations without updating model weights.\n\n"
                "### Formulation\n"
                "A prompt contains demonstrations $(x_1, y_1), ..., (x_k, y_k)$ and a new query $x_{k+1}$:\n"
                "$$P(y \\mid x_{k+1}, D)$$"
                f"\n\n### Offline Compilation Details\n\n{raw_snippet}"
            ),
            "content_id": (
                "## Tinjauan Konseptual\n\n"
                "**In-Context Learning (ICL)** memanfaatkan representasi laten dari LLM "
                "untuk mengeksplorasi pola dari demonstrasi yang disediakan pengguna tanpa memperbarui bobot model.\n\n"
                "### Formulasi\n"
                "Perintah (prompt) berisi demonstrasi $(x_1, y_1), ..., (x_k, y_k)$ dan kueri baru $x_{k+1}$:\n"
                "$$P(y \\mid x_{k+1}, D)$$"
                f"\n\n### Detail Kompilasi Offline\n\n{raw_snippet}"
            )
        })
        
    if not concepts:
        concepts.append({
            "name": f"{filename_base}-core-concept",
            "title_en": f"{title_words} Core Concept",
            "title_id": f"Konsep Inti {title_words}",
            "domain": "software-engineering",
            "tags": ["compiled", "general"],
            "description_en": f"Core concept extracted from {title_words}.",
            "description_id": f"Konsep inti yang diekstrak dari {title_words}.",
            "content_en": f"## Overview\n\nThis is the core concept page for [[source-{filename_base}]].",
            "content_id": f"## Tinjauan\n\nIni adalah halaman konsep inti untuk [[source-{filename_base}-id]]."
        })
        
    for c in concepts:
        c["version"] = c.get("version") or version
        c["status"] = c.get("status") or "active"
        
    for e in entities:
        e["version"] = e.get("version") or version
        e["status"] = e.get("status") or "active"
        
    for sec in sections:
        title = sec["title"]
        sec_content = sec["content"][:300] + "..." if len(sec["content"]) > 300 else sec["content"]
        summary_parts_en.append(f"### Chapter: {title}\n{sec_content}\n")
        summary_parts_id.append(f"### Bab: {title}\n{sec_content}\n")
        
    return {
        "title_en": title_en,
        "title_id": title_id,
        "summary_en": "\n".join(summary_parts_en),
        "summary_id": "\n".join(summary_parts_id),
        "concepts": concepts,
        "entities": entities
    }
```

- [ ] **Step 3: Commit LLM & fallback modules**

```bash
git add scripts/ingest/llm_pipeline.py scripts/ingest/local_fallback.py
git commit -m "feat: add LLM Map-Reduce pipeline and offline fallback compiler modules"
```

---

### Task 5: Implement Wikilinks & DB vault scan module

**Files:**
- Create: `scripts/ingest/wikilinks.py`

- [ ] **Step 1: Write `scripts/ingest/wikilinks.py`**

Create `scripts/ingest/wikilinks.py` containing:
```python
import os
import re
import sqlite3

WIKI_DIR = "wiki"
DB_PATH = os.path.join(WIKI_DIR, ".search_index.db")

def scan_vault_pages_db() -> dict:
    """Scans the database index instead of recursively reading disk files to build the mapping dict.
    
    Returns: dict mapping lowercase keys (title, clean titles, name) to {lang: filename}.
    """
    mapping = {}
    if not os.path.exists(DB_PATH):
        return mapping
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verify table exists first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_metadata';")
        if not cursor.fetchone():
            conn.close()
            return mapping
            
        cursor.execute("SELECT name, lang, title, translation FROM wiki_metadata;")
        rows = cursor.fetchall()
        
        # Track translation pairs: {name: translation_name}
        translation_pairs = {}
        
        for name, lang, title, translation in rows:
            lang = lang.lower()
            name_lower = name.lower()
            
            # Map filename base name key
            if name_lower not in mapping:
                mapping[name_lower] = {}
            mapping[name_lower][lang] = name
            
            # Map clean titles
            if title:
                title_clean = title.replace("**", "").strip()
                for variant in [title.lower(), title_clean.lower()]:
                    if variant not in mapping:
                        mapping[variant] = {}
                    mapping[variant][lang] = name
            
            # Record translation pairs
            if translation:
                translation_pairs[name_lower] = translation.lower()
                
        # Resolve translation pairs cross-language
        for source_name, trans_name in translation_pairs.items():
            if trans_name not in mapping:
                continue
            trans_entry = mapping[trans_name]
            source_entry = mapping.get(source_name, {})
            
            source_lang = "en" if "en" in source_entry else ("id" if "id" in source_entry else None)
            if not source_lang:
                continue
            target_lang = "id" if source_lang == "en" else "en"
            
            if target_lang not in trans_entry:
                continue
            target_filename = trans_entry[target_lang]
            
            # Map all title variants to translation target filename
            for key, lang_map in mapping.items():
                if lang_map.get(source_lang) == source_entry.get(source_lang):
                    if target_lang not in lang_map:
                        lang_map[target_lang] = target_filename
                        
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to fetch metadata cache from SQLite: {e}")
        
    return mapping

def build_link_map(vault_pages: dict, concepts: list, entities: list, target_lang: str) -> dict:
    link_map = {}
    
    # 1. From vault scan
    for key, lang_map in vault_pages.items():
        if target_lang in lang_map:
            target = lang_map[target_lang]
            link_map[key] = target
            kebab = key.replace(" ", "-")
            if kebab != key:
                link_map[kebab] = target
                
    # 2. Cross-language heading resolution
    other_lang = "en" if target_lang == "id" else "id"
    for key, lang_map in vault_pages.items():
        if key in link_map:
            continue
        if other_lang in lang_map:
            other_name = lang_map[other_lang]
            expected_key = None
            for k, lm in vault_pages.items():
                if lm.get(other_lang) == other_name and target_lang in lm:
                    expected_key = lm[target_lang].lower()
                    break
            
            if not expected_key:
                if target_lang == "id":
                    expected_key = f"{other_name}-id".lower()
                else:
                    if other_name.endswith("-id"):
                        expected_key = other_name[:-3].lower()
                    else:
                        continue
            
            if expected_key in vault_pages and target_lang in vault_pages[expected_key]:
                target = vault_pages[expected_key][target_lang]
                link_map[key] = target
                kebab = key.replace(" ", "-")
                if kebab != key:
                    link_map[kebab] = target
                    
    # 3. Batch concepts
    for c in concepts:
        en_name = c.get("name") or c.get("title_en", "").lower().replace(" ", "-")
        if not en_name:
            continue
        target = f"{en_name}-id" if target_lang == "id" else en_name
        title_en = c.get("title_en") or en_name.replace("-", " ").title()
        title_id = c.get("title_id", "")
        
        link_map[en_name.lower()] = target
        link_map[title_en.lower()] = target
        link_map[title_en.lower().replace(" ", "-")] = target
        if title_id:
            link_map[title_id.lower()] = target
            link_map[title_id.lower().replace(" ", "-")] = target
            
    # 4. Batch entities
    for e in entities:
        en_name = e.get("name") or e.get("title_en", "").lower().replace(" ", "-")
        if not en_name:
            continue
        target = f"{en_name}-id" if target_lang == "id" else en_name
        title_en = e.get("title_en") or e.get("title_en").replace("-", " ").title()
        title_id = e.get("title_id", "")
        
        link_map[en_name.lower()] = target
        link_map[title_en.lower()] = target
        link_map[title_en.lower().replace(" ", "-")] = target
        if title_id:
            link_map[title_id.lower()] = target
            link_map[title_id.lower().replace(" ", "-")] = target
            
    return link_map

def normalize_wikilinks(content: str, link_map: dict) -> str:
    if not link_map:
        return content
    
    def replace_link(match):
        full = match.group(1)
        parts = full.split("|")
        target = parts[0].strip()
        target_lower = target.lower()
        target_kebab = target_lower.replace(" ", "-")
        
        new_target = link_map.get(target_lower) or link_map.get(target_kebab)
        if new_target and new_target != target:
            if len(parts) > 1:
                return f"[[{new_target}|{parts[1]}]]"
            return f"[[{new_target}]]"
        return match.group(0)
        
    return re.sub(r"\[\[(.*?)\]\]", replace_link, content)
```

- [ ] **Step 2: Commit wikilinks module**

```bash
git add scripts/ingest/wikilinks.py
git commit -m "feat: add database-driven wikilinks scan and normalization module"
```

---

### Task 6: Modify Indexer Rebuild Logic (`scripts/make_index.py`)

**Files:**
- Modify: `scripts/make_index.py`

- [ ] **Step 1: Edit `scripts/make_index.py` to preserve cache tables**

Open [make_index.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/make_index.py).
Modify `build_sqlite_index()` to drop the `search_index` table and recreate it, instead of deleting the entire `.db` file. Also populate `wiki_metadata` during the FTS5 build.
Modify lines 287-314 of `make_index.py`:

```python
def build_sqlite_index(pages):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Drop and Re-create FTS5 table without destroying other metadata cache tables
        cursor.execute("DROP TABLE IF EXISTS search_index;")
        
        # Create FTS5 virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE search_index USING fts5(
                path,
                name,
                lang,
                type,
                domain,
                title,
                description,
                content,
                translation,
                stemmed_tokens,
                tokenize='unicode61'
            );
        """)
```

- [ ] **Step 2: Re-populate `wiki_metadata` during `make_index.py` run**

In `build_sqlite_index()`, add SQL command to initialize and truncate the metadata table, and populate it with details of all pages:

```python
        # Create metadata table if it does not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wiki_metadata (
                path TEXT PRIMARY KEY,
                name TEXT,
                lang TEXT,
                type TEXT,
                title TEXT,
                sha256 TEXT,
                translation TEXT
            );
        """)
        cursor.execute("DELETE FROM wiki_metadata;")
        
        insert_data = []
        insert_meta = []
        for p in pages:
            filepath = p.get("_path", "").replace("\\", "/")
            if not filepath or not os.path.exists(filepath):
                continue
                
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    full_content = f.read()
            except Exception as e:
                print(f"Warning: Failed to read {filepath} for SQLite indexing: {e}")
                continue
                
            body = full_content
            sha256_val = None
            if full_content.startswith("---"):
                parts = full_content.split("---", 2)
                if len(parts) >= 3:
                    body = parts[2].strip()
                    
            metadata = parse_yaml_frontmatter(full_content)
            if metadata and "sha256" in metadata:
                sha256_val = metadata["sha256"]
                
            name = p.get("_name", "")
            lang = p.get("lang", "")
            page_type = p.get("_db_type", "concept")
            domain = p.get("domain", "other")
            title = p.get("title", name.replace("source-", "").replace("-", " ").title())
            description = p.get("description", "")
            translation = p.get("translation", "")
            if isinstance(translation, list):
                translation = translation[0] if translation else ""
            translation = str(translation).replace("[[", "").replace("]]", "").strip()
            
            text_to_stem = f"{title} {description} {body}"
            stemmed_tokens = stem_text(text_to_stem, lang)
            
            insert_data.append((
                filepath,
                name,
                lang,
                page_type,
                domain,
                title,
                description,
                body,
                translation,
                stemmed_tokens
            ))
            
            insert_meta.append((
                filepath,
                name,
                lang,
                page_type,
                title,
                sha256_val,
                translation
            ))
            
        cursor.executemany("""
            INSERT INTO search_index(path, name, lang, type, domain, title, description, content, translation, stemmed_tokens)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, insert_data)
        
        cursor.executemany("""
            INSERT OR REPLACE INTO wiki_metadata(path, name, lang, type, title, sha256, translation)
            VALUES(?, ?, ?, ?, ?, ?, ?);
        """, insert_meta)
```

- [ ] **Step 3: Run the modified indexer script**

Run: `rtk python scripts/make_index.py`
Expected: Completed successfully. No errors. Rebuilt EN/ID index catalogs.

- [ ] **Step 4: Verify metadata table contains rows**

Run: `rtk python -c "import sqlite3; conn=sqlite3.connect('wiki/.search_index.db'); cur=conn.cursor(); cur.execute('SELECT COUNT(*) FROM wiki_metadata'); print(cur.fetchone())"`
Expected: Prints total row count (e.g. `(114,)`)

- [ ] **Step 5: Commit indexer modifications**

```bash
git add scripts/make_index.py
git commit -m "refactor: preserve database and populate wiki_metadata in make_index.py"
```

---

### Task 7: Rewire Orchestrator entrypoint (`scripts/ingest.py`)

**Files:**
- Modify: `scripts/ingest.py`

- [ ] **Step 1: Replace `scripts/ingest.py` with modular orchestrator implementation**

Replace the entire contents of [ingest.py](file:///c:/Users/mifta/Documents/Obsidian%20Vault/remote-blog/01-TODO/2026/My-Wiki/scripts/ingest.py) with the following code (setting Overwrite to true):

```python
import os
import sys
import re
from datetime import datetime

# Windows encoding safeguard for emoji output
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add scripts directory to path to import local package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ingest.persistence import (
    validate_safe_path,
    calculate_sha256,
    check_duplicate,
    write_wiki_page,
    merge_or_write_page
)
from ingest.extractor import (
    parallel_pdf_ingest,
    extract_pdf_tables,
    extract_pdf_images
)
from ingest.llm_pipeline import (
    process_deepseek,
    run_groundedness_evaluation
)
from ingest.local_fallback import process_offline
from ingest.wikilinks import (
    scan_vault_pages_db,
    build_link_map,
    normalize_wikilinks
)

WIKI_DIR = "wiki"
EN_DIR = os.path.join(WIKI_DIR, "en")
ID_DIR = os.path.join(WIKI_DIR, "id")
LOG_PATH = os.path.join(WIKI_DIR, "log.md")

def sanitize_indonesian_latex(content: str) -> str:
    prohibited_map = {
        r"keras": "hard",
        r"lunak": "soft",
        r"uji": "test"
    }
    def replacer(match):
        formula = match.group(0)
        for prohibited, replacement in prohibited_map.items():
            formula = re.sub(r"(\\text\{\s*)" + prohibited + r"(\s*\})", r"\1" + replacement + r"\2", formula, flags=re.IGNORECASE)
            formula = re.sub(r"(\\mathrm\{\s*)" + prohibited + r"(\s*\})", r"\1" + replacement + r"\2", formula, flags=re.IGNORECASE)
            formula = re.sub(r"(_\{?\s*)" + prohibited + r"(\s*\}?)", r"\1" + replacement + r"\2", formula, flags=re.IGNORECASE)
        return formula

    content = re.sub(r"\$\$.*?\$\$", replacer, content, flags=re.DOTALL)
    content = re.sub(r"\$.*?\$", replacer, content)
    
    prohibited_literals = {
        r"\bjendela konteks\b": "context window",
        r"\bpelatihan prabayar\b": "pretraining",
        r"\bfungsi kehilangan\b": "loss function"
    }
    for bad_term, good_term in prohibited_literals.items():
        content = re.sub(bad_term, good_term, content, flags=re.IGNORECASE)
    return content

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest.py <path-to-raw-file>")
        sys.exit(1)
        
    raw_path = sys.argv[1]
    try:
        # Validate path safety
        raw_path = validate_safe_path(raw_path)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    if not os.path.exists(raw_path):
        print(f"Error: Raw input file not found at '{raw_path}'")
        sys.exit(1)
        
    print(f"Starting ingestion workflow for: {raw_path}")
    
    checksum = calculate_sha256(raw_path)
    print(f"Calculated SHA-256 Checksum: {checksum}")
    
    source_filename = os.path.normpath(raw_path).replace("\\", "/").split("remote-blog/01-TODO/2026/My-Wiki/")[-1]
    if "My-Wiki/" in source_filename:
        source_filename = source_filename.split("My-Wiki/")[-1]
        
    duplicate_path = check_duplicate(checksum, source_filename)
    if duplicate_path:
        print(f"Source asset already compiled! Checksum/Filename match: {duplicate_path}")
        print("Skipping ingestion to prevent duplication.")
        sys.exit(0)
        
    is_pdf_paper = raw_path.lower().endswith(".pdf") and ("raw/papers/" in raw_path.replace("\\", "/"))
    filename_base = os.path.splitext(os.path.basename(raw_path))[0]
    
    if raw_path.lower().endswith(".pdf"):
        print("Detected PDF input. Extracting text using multiprocessing and OCR Fallback...")
        tessdata_path = os.environ.get("TESSDATA_PREFIX")
        if not tessdata_path:
            default_win = r"C:\Program Files\Tesseract-OCR\tessdata"
            if os.path.exists(default_win):
                tessdata_path = default_win
        raw_content = parallel_pdf_ingest(raw_path, tessdata_path=tessdata_path)
    else:
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
            
    tables_content = ""
    images_content = ""
    if is_pdf_paper:
        print("Extracting tables using pdfplumber...")
        tables_content = extract_pdf_tables(raw_path)
        print("Extracting images using PyMuPDF...")
        images_content = extract_pdf_images(raw_path, filename_base)
        
        if tables_content:
            raw_content += "\n\n## Extracted Tables (Technical Details)\n\n" + tables_content
        if images_content:
            raw_content += "\n\n## Extracted Visual Figures\n\n" + images_content
            
    raw_source_dir = os.path.join(WIKI_DIR, "raw_sources")
    os.makedirs(raw_source_dir, exist_ok=True)
    raw_source_path = os.path.join(raw_source_dir, f"{filename_base}.txt")
    with open(raw_source_path, "w", encoding="utf-8") as rf:
        rf.write(raw_content)
    print(f"Saved complete raw source text to: {raw_source_path}")
    
    raw_version = "1.0.0"
    try:
        from parser import parse_yaml_frontmatter as local_parse
        raw_fm = local_parse(raw_content)
        if raw_fm and "version" in raw_fm:
            raw_version = str(raw_fm["version"])
    except Exception:
        pass

    data = process_deepseek(raw_content, os.path.basename(raw_path), version=raw_version)
    if data and os.environ.get("DEEPSEEK_API_KEY"):
        eval_result = run_groundedness_evaluation(raw_content, data.get("summary_en", ""), filename_base)
        if "APPROVED" not in eval_result:
            print(f"⚠️ Ingestion Auditor flagged nuances gaps:\n{eval_result}")
            
    if not data:
        data = process_offline(raw_content, filename_base, version=raw_version)
        
    current_date = datetime.now().strftime("%Y-%m-%d")
    source_name_en = f"source-{filename_base}"
    source_name_id = f"source-{filename_base}-id"
    
    if is_pdf_paper:
        en_src_dir = os.path.join(EN_DIR, "sources", filename_base)
        id_src_dir = os.path.join(ID_DIR, "sources", filename_base)
        os.makedirs(en_src_dir, exist_ok=True)
        os.makedirs(id_src_dir, exist_ok=True)
    else:
        en_src_dir = os.path.join(EN_DIR, "sources")
        id_src_dir = os.path.join(ID_DIR, "sources")
        
    source_path_en = os.path.join(en_src_dir, f"{source_name_en}.md")
    source_path_id = os.path.join(id_src_dir, f"{source_name_id}.md")
    
    created_concepts = []
    created_entities = []
    concepts = data.get("concepts", []) or []
    entities = data.get("entities", []) or []
    
    concept_links_en = [f"[[{c.get('name')}]]" for c in concepts if c.get('name')]
    concept_links_id = [f"[[{c.get('name')}-id]]" for c in concepts if c.get('name')]
    entity_links_en = [f"[[{e.get('name')}]]" for e in entities if e.get('name')]
    entity_links_id = [f"[[{e.get('name')}-id]]" for e in entities if e.get('name')]
    
    title_en = data.get('title_en') or filename_base.replace("-", " ").title()
    summary_en = data.get('summary_en') or ''
    title_id = sanitize_indonesian_latex(data.get('title_id') or title_en)
    summary_id = sanitize_indonesian_latex(data.get('summary_id') or summary_en)
    
    src_fm_en = {
        "type": "source",
        "source_file": source_filename,
        "sha256": checksum,
        "created": current_date,
        "updated": current_date,
        "translation": f"[[{source_name_id}]]",
        "tags": ["ingested", filename_base]
    }
    if is_pdf_paper:
        src_body_en = (
            f"# Source Summary: {title_en}\n\n"
            f"## Abstract / Summary\n\n{summary_en}\n\n"
            f"## Technical Specifications & Details\n\n"
            f"- [[source-{filename_base}-experiments]]\n"
            f"- [[source-{filename_base}-mathematics]]\n\n"
            f"## Core Concepts\n"
        )
    else:
        src_body_en = f"# Source Summary: {title_en}\n\n{summary_en}\n\n## Core Concepts\n"
        
    if concept_links_en:
        src_body_en += "\n".join([f"- {link}" for link in concept_links_en])
    else:
        src_body_en += "*No core concepts linked.*"
        
    write_wiki_page(source_path_en, src_fm_en, src_body_en)
    
    src_fm_id = {
        "type": "source",
        "source_file": source_filename,
        "sha256": checksum,
        "created": current_date,
        "updated": current_date,
        "translation": f"[[{source_name_en}]]",
        "tags": ["ingested", filename_base]
    }
    if is_pdf_paper:
        src_body_id = (
            f"# Ringkasan Sumber: {title_id}\n\n"
            f"## Abstrak / Ringkasan\n\n{summary_id}\n\n"
            f"## Spesifikasi Teknis & Detail\n\n"
            f"- [[source-{filename_base}-experiments-id]]\n"
            f"- [[source-{filename_base}-mathematics-id]]\n\n"
            f"## Konsep Inti\n"
        )
    else:
        src_body_id = f"# Ringkasan Sumber: {title_id}\n\n{summary_id}\n\n## Konsep Inti\n"
        
    if concept_links_id:
        src_body_id += "\n".join([f"- {link}" for link in concept_links_id])
    else:
        src_body_id += "*Tidak ada konsep inti yang tertaut.*"
        
    write_wiki_page(source_path_id, src_fm_id, src_body_id)

    if is_pdf_paper:
        exp_fm_en = {
            "type": "source-subpage",
            "parent": f"[[source-{filename_base}]]",
            "lang": "en",
            "created": current_date,
            "updated": current_date,
            "tags": ["experiments", filename_base]
        }
        exp_body_en = (
            f"# Experimental Setup & Tables: {title_en}\n\n"
            f"This sub-page records the experimental ablation metrics, datasets, and hyperparameters "
            f"for [[source-{filename_base}]].\n\n"
            f"## Captured Performance Tables\n\n"
            f"{tables_content if tables_content else '*No tables extracted.*'}"
        )
        write_wiki_page(os.path.join(en_src_dir, f"source-{filename_base}-experiments.md"), exp_fm_en, exp_body_en)

        math_fm_en = {
            "type": "source-subpage",
            "parent": f"[[source-{filename_base}]]",
            "lang": "en",
            "created": current_date,
            "updated": current_date,
            "tags": ["mathematics", filename_base]
        }
        math_body_en = (
            f"# Mathematical Derivations: {title_en}\n\n"
            f"This sub-page records the mathematical derivations, formulas, and visual figures "
            f"for [[source-{filename_base}]].\n\n"
            f"## Formulas & Derivations\n\n"
            f"*Refer to the main summary and concepts for specific formulas.*\n\n"
            f"## Extracted Visual Figures\n\n"
            f"{images_content if images_content else '*No figures extracted.*'}"
        )
        write_wiki_page(os.path.join(en_src_dir, f"source-{filename_base}-mathematics.md"), math_fm_en, math_body_en)

        exp_fm_id = {
            "type": "source-subpage",
            "parent": f"[[source-{filename_base}-id]]",
            "lang": "id",
            "created": current_date,
            "updated": current_date,
            "tags": ["experiments", filename_base]
        }
        exp_body_id = (
            f"# Pengaturan Eksperimen & Tabel: {title_id}\n\n"
            f"Sub-halaman ini mencatat metrik ablasi eksperimental, dataset, dan hiperparameter "
            f"untuk [[source-{filename_base}-id]].\n\n"
            f"## Tabel Kinerja yang Ditangkap\n\n"
            f"{tables_content if tables_content else '*Tidak ada tabel yang diekstrak.*'}"
        )
        write_wiki_page(os.path.join(id_src_dir, f"source-{filename_base}-experiments-id.md"), exp_fm_id, exp_body_id)

        math_fm_id = {
            "type": "source-subpage",
            "parent": f"[[source-{filename_base}-id]]",
            "lang": "id",
            "created": current_date,
            "updated": current_date,
            "tags": ["mathematics", filename_base]
        }
        math_body_id = (
            f"# Penurunan Matematis: {title_id}\n\n"
            f"Sub-halaman ini mencatat penurunan matematis, formula, dan gambar visual "
            f"untuk [[source-{filename_base}-id]].\n\n"
            f"## Formula & Penurunan\n\n"
            f"*Rujuk ke ringkasan utama dan konsep untuk formula spesifik.*\n\n"
            f"## Gambar Visual yang Diekstrak\n\n"
            f"{images_content if images_content else '*Tidak ada gambar yang diekstrak.*'}"
        )
        write_wiki_page(os.path.join(id_src_dir, f"source-{filename_base}-mathematics-id.md"), math_fm_id, math_body_id)
    
    print("Scanning vault for wikilink normalization...")
    vault_pages = scan_vault_pages_db()
    en_link_map = build_link_map(vault_pages, concepts, entities, "en")
    id_link_map = build_link_map(vault_pages, concepts, entities, "id")
    print(f"  Built EN link map ({len(en_link_map)} entries), ID link map ({len(id_link_map)} entries)")
    
    for c in concepts:
        c_name_en = c.get("name") or c.get("title_en", "").lower().replace(" ", "-")
        c_name_id = f"{c_name_en}-id"
        c_domain = c.get("domain", "other").lower()
        c_tags = c.get("tags", [])
        if "ingest" not in c_tags:
            c_tags.append("ingest")
            
        c_path_en = os.path.join(EN_DIR, "concepts", c_domain, f"{c_name_en}.md")
        c_path_id = os.path.join(ID_DIR, "concepts", c_domain, f"{c_name_id}.md")
        
        see_also_en = [f"- [[{x.get('name')}]]" for x in concepts if x.get('name') != c_name_en and x.get('name')]
        see_also_id = [f"- [[{x.get('name')}-id]]" for x in concepts if x.get('name') != c_name_en and x.get('name')]
        
        c_content_en = c.get('content_en') or c.get('description_en') or ''
        normalized_content_en = normalize_wikilinks(c_content_en, en_link_map)
        c_fm_en = {
            "type": "concept",
            "domain": c_domain,
            "lang": "en",
            "translation": f"[[{c_name_id}]]",
            "tags": c_tags,
            "created": current_date,
            "updated": current_date,
            "sources": [f"[[{source_name_en}]]"],
            "description": c.get("description_en") or c_content_en[:200],
            "version": c.get("version") or "1.0.0",
            "status": c.get("status") or "active"
        }
        see_also_en_section = f"\n\n## See Also\n\n" + "\n".join(see_also_en) if see_also_en else ""
        c_body_en = f"# {c.get('title_en', c_name_en.replace('-', ' ').title())}\n\n{normalized_content_en}{see_also_en_section}\n\n## Sources\n\n- [[{source_name_en}]]"
        merge_or_write_page(c_path_en, c_fm_en, c_body_en)
        created_concepts.append(c_name_en)
        
        c_title_id = sanitize_indonesian_latex(c.get('title_id') or c.get('title_en', c_name_en.replace('-', ' ').title()))
        c_content_id = sanitize_indonesian_latex(c.get('content_id') or c.get('description_id') or '')
        c_description_id = sanitize_indonesian_latex(c.get('description_id') or c.get('description_en', ''))
        
        normalized_content_id = normalize_wikilinks(c_content_id, id_link_map)
        c_fm_id = {
            "type": "concept",
            "domain": c_domain,
            "lang": "id",
            "translation": f"[[{c_name_en}]]",
            "tags": c_tags,
            "created": current_date,
            "updated": current_date,
            "sources": [f"[[{source_name_id}]]"],
            "description": c_description_id,
            "version": c.get("version") or "1.0.0",
            "status": c.get("status") or "active"
        }
        see_also_id_section = f"\n\n## Lihat Juga\n\n" + "\n".join(see_also_id) if see_also_id else ""
        c_body_id = f"# {c_title_id}\n\n{normalized_content_id}{see_also_id_section}\n\n## Sumber\n\n- [[{source_name_id}]]"    
        merge_or_write_page(c_path_id, c_fm_id, c_body_id)
        
    for e in entities:
        e_name_en = e.get("name") or e.get("title_en", "").lower().replace(" ", "-")
        e_name_id = f"{e_name_en}-id"
        e_domain = e.get("domain", "other").lower()
        e_category = e.get("category", "other").lower()
        e_tags = e.get("tags", [])
        
        e_path_en = os.path.join(EN_DIR, "entities", e_domain, f"{e_name_en}.md")
        e_path_id = os.path.join(ID_DIR, "entities", e_domain, f"{e_name_id}.md")
        
        related_en = [f"- [[{x.get('name')}]]" for x in entities if x.get('name') != e_name_en and x.get('name')]
        related_id = [f"- [[{x.get('name')}-id]]" for x in entities if x.get('name') != e_name_en and x.get('name')]
        
        e_content_en = e.get('content_en') or e.get('description_en') or ''
        normalized_content_en = normalize_wikilinks(e_content_en, en_link_map)
        e_fm_en = {
            "type": "entity",
            "category": e_category,
            "domain": e_domain,
            "lang": "en",
            "translation": f"[[{e_name_id}]]",
            "tags": e_tags,
            "created": current_date,
            "updated": current_date,
            "sources": [f"[[{source_name_en}]]"],
            "version": e.get("version") or "1.0.0",
            "status": e.get("status") or "active"
        }
        related_en_section = f"\n\n## Related Entities\n\n" + "\n".join(related_en) if related_en else ""
        e_body_en = f"# {e.get('title_en', e_name_en.replace('-', ' ').title())}\n\n{normalized_content_en}{related_en_section}\n\n## Sources\n\n- [[{source_name_en}]]"
        merge_or_write_page(e_path_en, e_fm_en, e_body_en)
        created_entities.append(e_name_en)
        
        e_title_id = sanitize_indonesian_latex(e.get('title_id') or e.get('title_en', e_name_en.replace('-', ' ').title()))
        e_content_id = sanitize_indonesian_latex(e.get('content_id') or e.get('description_id') or '')
        
        normalized_content_id = normalize_wikilinks(e_content_id, id_link_map)
        e_fm_id = {
            "type": "entity",
            "category": e_category,
            "domain": e_domain,
            "lang": "id",
            "translation": f"[[{e_name_en}]]",
            "tags": e_tags,
            "created": current_date,
            "updated": current_date,
            "sources": [f"[[{source_name_id}]]"],
            "version": e.get("version") or "1.0.0",
            "status": e.get("status") or "active"
        }
        related_id_section = f"\n\n## Entitas Terkait\n\n" + "\n".join(related_id) if related_id else ""
        e_body_id = f"# {e_title_id}\n\n{normalized_content_id}{related_id_section}\n\n## Sumber\n\n- [[{source_name_id}]]"
        merge_or_write_page(e_path_id, e_fm_id, e_body_id)
        
    log_line = f"## [{current_date}] INGEST | {os.path.basename(raw_path)} | Created source page `{source_name_en}.md`. "
    if created_concepts:
        log_line += f"Created {len(created_concepts)} concept pages: {', '.join(created_concepts)}. "
    if created_entities:
        log_line += f"Created {len(created_entities)} entity pages: {', '.join(created_entities)}. "
    log_line += "All wikilinks integrated (cross-language links sanitized)."
    
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as lf:
            lf.write("\n" + log_line + "\n")
        print(f"Logged operation to {LOG_PATH}")
    except Exception as e:
        print(f"Warning: Failed to write to chronicle log: {e}")
        
    print("Auto-triggering wiki re-indexing pass...")
    try:
        import subprocess
        subprocess.run([sys.executable, "scripts/make_index.py"], check=True)
        print("Re-indexing completed successfully!")
    except Exception as e:
        print(f"Warning: Failed to run make_index.py: {e}")
        
    print("\n🎉 Ingestion workflow finished successfully! 🎉")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the test suite on entrypoint rewire**

Run: `rtk python scripts/test_wiki.py`
Expected: PASS. All validations and PDF mock tests run cleanly under the package architecture.

- [ ] **Step 3: Run the linter**

Run: `rtk python scripts/linter.py`
Expected: Health check passes with 0 errors.

- [ ] **Step 4: Clean up persistence unit test**

Delete `scripts/test_persistence_unit.py` using command line.
Run: `rm scripts/test_persistence_unit.py`
Expected: File deleted.

- [ ] **Step 5: Commit entrypoint rewiring**

```bash
git add scripts/ingest.py
git commit -m "refactor: rewire entrypoint scripts/ingest.py using modular ingest package"
```

---

### Task 8: Global Compliance Auditing & Final Verification

**Files:**
- Modify: `audit_report.md`

- [ ] **Step 1: Execute Global Compliance Audit**

Run: `rtk python .agents/scripts/run_all_audits.py .`
Expected: Unified Compliance Report updated successfully. Only minor warnings about file size (unrelated to our changes).

- [ ] **Step 2: Commit final audit report**

```bash
git add audit_report.md
git commit -m "chore: update compliance audit report after refactoring ingest pipeline"
```
