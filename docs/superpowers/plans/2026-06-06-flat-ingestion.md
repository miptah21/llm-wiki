# Flat Ingestion and Paper-Specific Structure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transition the PDF ingestion pipeline to a flat single-file format containing structured paper-specific details, disabling table/image extraction.

**Architecture:** Update `llm_pipeline.py` to extract metadata and structure the summary, update `local_fallback.py` to match the schema offline, update `ingest.py` to remove table/image extraction and nesting, and update `test_wiki.py` to verify the flat single-file output.

**Tech Stack:** Python, PyMuPDF (fitz), pdfplumber

---

### Task 1: Update LLM Ingestion Pipeline (`llm_pipeline.py`)

**Files:**
- Modify: `scripts/ingest/llm_pipeline.py`
- Test: Run validation suite after all changes.

- [ ] **Step 1: Update the map phase system prompt and JSON schema in `process_deepseek`**
  Modify lines 128-166 in `scripts/ingest/llm_pipeline.py` to request `authors`, `affiliation`, `published`, and `code` in the JSON structure.
  ```python
        system_prompt = (
            "You are an expert bilingual scientific data ingestion engine. "
            "Your task is to summarize the raw scientific asset in both English and Indonesian. "
            "You must return a valid JSON object with the following structure:\n"
            "CRITICAL WIKILINK RULE: All wikilinks in content fields MUST use kebab-case matching the concept/entity 'name' field.\n"
            "{\n"
            "  \"title_en\": \"English Title\",\n"
            "  \"title_id\": \"Indonesian Title\",\n"
            "  \"authors\": \"Author names (only if present in this chunk, otherwise null)\",\n"
            "  \"affiliation\": \"Affiliation details (only if present in this chunk, otherwise null)\",\n"
            "  \"published\": \"Publication date/venue/arXiv details (only if present in this chunk, otherwise null)\",\n"
            "  \"code\": \"Code repository URL (only if present in this chunk, otherwise null)\",\n"
            "  \"summary_en\": \"Comprehensive English summary of this chunk\",\n"
            "  \"summary_id\": \"Comprehensive Indonesian summary of this chunk\",\n"
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
  ```

- [ ] **Step 2: Update the reduce phase prompts to request paper-specific structure**
  Modify lines 186-190 in `scripts/ingest/llm_pipeline.py` to direct the LLM to write a structured markdown report using paper sections separated by `---`:
  ```python
        reduce_prompt_en = (
            f"Synthesize a cohesive, structured English summary from these chunk summaries. "
            f"The summary MUST be structured to match the sections of the paper, using horizontal rules '---' to separate sections. "
            f"Include the following sections if discussed in the paper:\n"
            f"- ## Abstract (high-level summary)\n"
            f"- ## Problem Statement (motivation, core problem, limitations of existing work)\n"
            f"- ## Core Method (proposed approach, algorithm, steps, mathematical formulations with LaTeX formulas)\n"
            f"- ## Key Experimental Results (benchmarks, datasets, findings, transferability, robustness)\n"
            f"- ## Limitations\n"
            f"- ## Error Analysis & Interpretability (or other analytical sections if applicable)\n\n"
            f"Chunk summaries:\n{combined_sum_en}"
        )
        reduce_prompt_id = (
            f"Synthesize a cohesive, structured Indonesian summary (keep LaTeX formulas/terms natural) from these chunk summaries. "
            f"The summary MUST be structured to match the sections of the paper, using horizontal rules '---' to separate sections. "
            f"Include the following sections if discussed in the paper:\n"
            f"- ## Abstrak (Abstract) (ringkasan tingkat tinggi)\n"
            f"- ## Pernyataan Masalah (Problem Statement) (motivasi, masalah inti, batasan dari pekerjaan yang ada)\n"
            f"- ## Metode Inti (Core Method) (pendekatan yang diusulkan, algoritma, tahapan, formula matematika dalam LaTeX)\n"
            f"- ## Hasil Eksperimen Utama (Key Experimental Results) (benchmarks, dataset, temuan utama, kemampuan transfer, ketangguhan)\n"
            f"- ## Batasan (Limitations)\n"
            f"- ## Analisis Kesalahan & Interpretabilitas (atau bagian analitis lainnya jika ada)\n\n"
            f"Chunk summaries:\n{combined_sum_id}"
        )
  ```

- [ ] **Step 3: Extract and return metadata from map-reduce outputs**
  Modify lines 255-262 in `scripts/ingest/llm_pipeline.py` to aggregate the metadata fields and return them:
  ```python
        authors = ""
        affiliation = ""
        published = ""
        code = ""
        for d in intermediate_data:
            if d.get("authors") and not authors:
                authors = d.get("authors")
            if d.get("affiliation") and not affiliation:
                affiliation = d.get("affiliation")
            if d.get("published") and not published:
                published = d.get("published")
            if d.get("code") and not code:
                code = d.get("code")

        return {
            "title_en": intermediate_data[0].get("title_en", filename),
            "title_id": intermediate_data[0].get("title_id", filename),
            "authors": authors,
            "affiliation": affiliation,
            "published": published,
            "code": code,
            "summary_en": final_summary_en,
            "summary_id": final_summary_id,
            "concepts": final_concepts,
            "entities": final_entities
        }
  ```

---

### Task 2: Update Local Fallback Pipeline (`local_fallback.py`)

**Files:**
- Modify: `scripts/ingest/local_fallback.py`

- [ ] **Step 1: Update `process_offline` to extract/return metadata**
  Modify `process_offline` in `scripts/ingest/local_fallback.py` to extract metadata (`authors`, `affiliation`, `published`, `code`) from `pre_translated` dictionary or fall back to defaults, returning them in the output dictionary.
  Replace lines 516-530 with:
  ```python
    custom_body_en = pre_translated.get("custom_body_en") if pre_translated else None
    custom_body_id = pre_translated.get("custom_body_id") if pre_translated else None
    tags = pre_translated.get("tags") if pre_translated else None
    
    # Extract metadata fields for the main return
    authors = pre_translated.get("authors", "") if pre_translated else ""
    affiliation = pre_translated.get("affiliation", "") if pre_translated else ""
    published = pre_translated.get("published", "") if pre_translated else ""
    code = pre_translated.get("code", "") if pre_translated else ""

    return {
        "title_en": title_en,
        "title_id": title_id,
        "authors": authors,
        "affiliation": affiliation,
        "published": published,
        "code": code,
        "summary_en": summary_en,
        "summary_id": summary_id,
        "concepts": concepts,
        "entities": entities,
        "custom_body_en": custom_body_en,
        "custom_body_id": custom_body_id,
        "tags": tags
    }
  ```

- [ ] **Step 2: Update the pre-translated dictionary entries**
  Ensure the pre-translated metadata keys are separated so they can be formatted dynamically:
  Modify `PRE_TRANSLATED_SUMMARIES["DeepSeek-2025"]` to add keys:
  ```python
        "authors": "DeepSeek-AI",
        "affiliation": "DeepSeek-AI, Hangzhou, China",
        "published": "2025-01-22 (arXiv:2501.12948v1 [cs.CL])",
        "code": "https://github.com/deepseek-ai/DeepSeek-R1",
  ```

---

### Task 3: Update Main Ingestion Flow (`ingest.py`)

**Files:**
- Modify: `scripts/ingest.py`

- [ ] **Step 1: Disable table/image extraction**
  Remove table and image extraction invocation around lines 177-187 in `scripts/ingest.py`. Replace with:
  ```python
    tables_content = ""
    images_content = ""
    # Image and table extraction is disabled.
  ```

- [ ] **Step 2: Keep the directories flat (do not nesting under `filename_base` for papers)**
  Modify directory setup around lines 223-233 in `scripts/ingest.py` so that all source pages are written directly under `sources/`.
  Replace:
  ```python
    en_src_dir = os.path.join(EN_DIR, "sources")
    id_src_dir = os.path.join(ID_DIR, "sources")
    
    source_path_en = os.path.join(en_src_dir, f"{source_name_en}.md")
    source_path_id = os.path.join(id_src_dir, f"{source_name_id}.md")
  ```

- [ ] **Step 3: Format the English and Indonesian Source summaries**
  Update the formatting of `src_body_en` and `src_body_id` to build a single structured markdown document.
  Replace the format block in `scripts/ingest.py` lines 262-316 with:
  ```python
    authors = data.get("authors") or ""
    affiliation = data.get("affiliation") or ""
    published = data.get("published") or ""
    code = data.get("code") or ""

    if data.get("custom_body_en"):
        src_body_en = data["custom_body_en"]
    else:
        metadata_header = f"# {title_en}\n\n"
        if authors:
            metadata_header += f"**Authors:** {authors}\n"
        if affiliation:
            metadata_header += f"**Affiliation:** {affiliation}\n"
        if published:
            metadata_header += f"**Published:** {published}\n"
        if code:
            metadata_header += f"**Code:** {code}\n"

        related_work_section = "## Related Work Connections\n\n"
        if concept_links_en:
            concept_bullets = []
            for c in concepts:
                c_name = c.get("name")
                c_title = c.get("title_en") or c_name.replace("-", " ").title()
                if c_name:
                    concept_bullets.append(f"- **{c_title}:** [[{c_name}]]")
            related_work_section += "\n".join(concept_bullets)
        else:
            related_work_section += "*No related work connections.*"

        linked_entities_section = "## Linked Entities\n\n"
        if entity_links_en:
            entity_bullets = []
            for e in entities:
                e_name = e.get("name")
                if e_name:
                    entity_bullets.append(f"- [[{e_name}]]")
            linked_entities_section += "\n".join(entity_bullets)
        else:
            linked_entities_section += "*No linked entities.*"

        src_body_en = (
            f"{metadata_header}\n"
            f"---\n\n"
            f"{summary_en.strip()}\n\n"
            f"---\n\n"
            f"{related_work_section}\n\n"
            f"{linked_entities_section}"
        )

    write_wiki_page(source_path_en, src_fm_en, src_body_en)

    if data.get("custom_body_id"):
        src_body_id = data["custom_body_id"]
    else:
        metadata_header_id = f"# {title_id}\n\n"
        if authors:
            metadata_header_id += f"**Penulis:** {authors}\n"
        if affiliation:
            metadata_header_id += f"**Afiliasi:** {affiliation}\n"
        if published:
            metadata_header_id += f"**Publikasi:** {published}\n"
        if code:
            metadata_header_id += f"**Kode Sumber:** {code}\n"

        related_work_section_id = "## Koneksi Penelitian Terkait (Related Work)\n\n"
        if concept_links_id:
            concept_bullets_id = []
            for c in concepts:
                c_name = c.get("name")
                c_title = c.get("title_id") or c.get("title_en") or c_name.replace("-", " ").title()
                if c_name:
                    concept_bullets_id.append(f"- **{c_title}:** [[{c_name}-id]]")
            related_work_section_id += "\n".join(concept_bullets_id)
        else:
            related_work_section_id += "*Tidak ada koneksi penelitian terkait.*"

        linked_entities_section_id = "## Entitas Terkait\n\n"
        if entity_links_id:
            entity_bullets_id = []
            for e in entities:
                e_name = e.get("name")
                if e_name:
                    entity_bullets_id.append(f"- [[{e_name}-id]]")
            linked_entities_section_id += "\n".join(entity_bullets_id)
        else:
            linked_entities_section_id += "*Tidak ada entitas terkait.*"

        src_body_id = (
            f"{metadata_header_id}\n"
            f"---\n\n"
            f"{summary_id.strip()}\n\n"
            f"---\n\n"
            f"{related_work_section_id}\n\n"
            f"{linked_entities_section_id}\n\n"
            f"---\n\n"
            f"## Padanan Bahasa Inggris\n\n"
            f"- [[{source_name_en}]] (Catatan Bahasa Inggris)"
        )

    write_wiki_page(source_path_id, src_fm_id, src_body_id)
  ```

- [ ] **Step 4: Remove the subpage generation logic**
  Remove lines 318-390 in `scripts/ingest.py` which creates the experiments and mathematics subpages for both English and Indonesian.

---

### Task 4: Update Tests Suite (`test_wiki.py`)

**Files:**
- Modify: `scripts/test_wiki.py`

- [ ] **Step 1: Update paper ingestion test assertions**
  Update the tests in `scripts/test_wiki.py` (lines 521-562) to expect flat single files instead of subpages and nested directories.
  Replace with:
  ```python
        # Verify that flat files exist
        main_summary_en = os.path.join(EN_DIR, "sources", "source-mock_paper_test.md")
        main_summary_id = os.path.join(ID_DIR, "sources", "source-mock_paper_test-id.md")
        
        assert os.path.exists(main_summary_en), "English main summary file missing!"
        assert os.path.exists(main_summary_id), "Indonesian main summary file missing!"
        
        # Verify that main summary contains the expected sections/concepts
        with open(main_summary_en, "r", encoding="utf-8") as f:
            main_sum_en_content = f.read()
        assert "Related Work Connections" in main_sum_en_content, "Missing Related Work Connections section!"
        assert "[[mock-distilasi-kompresi]]" in main_sum_en_content, "Missing link to concept!"

        with open(main_summary_id, "r", encoding="utf-8") as f:
            main_sum_id_content = f.read()
        assert "Koneksi Penelitian Terkait" in main_sum_id_content, "Missing Indonesian Related Work Connections section!"
        assert "[[mock-distilasi-kompresi-id]]" in main_sum_id_content, "Missing link to Indonesian concept!"
  ```

- [ ] **Step 2: Update mock paths and cleanup**
  Verify the cleanups array in `cleanup()` contains the flat file paths:
  ```python
        os.path.join(EN_DIR, "sources", "source-mock_paper_test.md"),
        os.path.join(ID_DIR, "sources", "source-mock_paper_test-id.md"),
  ```
  Instead of `INGESTED_PAPER_DIR_EN` and `INGESTED_PAPER_DIR_ID` directories if applicable.

---

### Task 5: Run Verification

- [ ] **Step 1: Execute `test_wiki.py`**
  Run `rtk python scripts/test_wiki.py` to ensure all tests pass cleanly.

- [ ] **Step 2: Execute `linter.py`**
  Run `rtk python scripts/linter.py` to check for format or reciprocal link violations.
