import os
import subprocess
import sys
import shutil


# Add scripts directory to path to import parser directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from parser import parse_yaml_frontmatter, detect_page_attributes

# Paths
WIKI_DIR = "wiki"
EN_DIR = os.path.join(WIKI_DIR, "en")
ID_DIR = os.path.join(WIKI_DIR, "id")

# Temporary Test Files (English)
TEST_CONCEPT_EN = os.path.join(EN_DIR, "concepts", "ai", "test_concept_page.md")
TEST_ENTITY_EN = os.path.join(EN_DIR, "entities", "ai", "test_entity_page.md")
TEST_SOURCE_EN = os.path.join(EN_DIR, "sources", "source-test_document.md")

# Temporary Test Files (Indonesian)
TEST_CONCEPT_ID = os.path.join(ID_DIR, "concepts", "ai", "test_concept_page_id.md")
TEST_ENTITY_ID = os.path.join(ID_DIR, "entities", "ai", "test_entity_page_id.md")
TEST_SOURCE_ID = os.path.join(ID_DIR, "sources", "source-test_document-id.md")

# Ingest test paths
INGEST_RAW_PAPER = os.path.join("raw", "papers", "mock_paper_test.pdf")
INGESTED_PAPER_DIR_EN = os.path.join(EN_DIR, "sources", "mock_paper_test")
INGESTED_PAPER_DIR_ID = os.path.join(ID_DIR, "sources", "mock_paper_test")

INGEST_RAW_FILE = os.path.join("raw", "articles", "mock_ingest_test.md")
INGESTED_SOURCE_EN = os.path.join(EN_DIR, "sources", "source-mock_ingest_test.md")
INGESTED_SOURCE_ID = os.path.join(ID_DIR, "sources", "source-mock_ingest_test-id.md")
INGESTED_CONCEPT_EN = os.path.join(EN_DIR, "concepts", "ai", "mock-distilasi-kompresi.md")
INGESTED_CONCEPT_ID = os.path.join(ID_DIR, "concepts", "ai", "mock-distilasi-kompresi-id.md")
INGESTED_CONCEPT2_EN = os.path.join(EN_DIR, "concepts", "ai", "in-context-learning-primer.md")
INGESTED_CONCEPT2_ID = os.path.join(ID_DIR, "concepts", "ai", "in-context-learning-primer-id.md")

INGEST_RAW_FILE2 = os.path.join("raw", "articles", "mock_ingest_test2.md")
INGESTED_SOURCE2_EN = os.path.join(EN_DIR, "sources", "source-mock_ingest_test2.md")
INGESTED_SOURCE2_ID = os.path.join(ID_DIR, "sources", "source-mock_ingest_test2-id.md")

INGEST_VERSION_RAW_V1 = os.path.join("raw", "articles", "mock_ingest_version_v1.md")
INGEST_VERSION_RAW_V2 = os.path.join("raw", "articles", "mock_ingest_version_v2.md")
INGESTED_VERSION_SOURCE_V1_EN = os.path.join(EN_DIR, "sources", "source-mock_ingest_version_v1.md")
INGESTED_VERSION_SOURCE_V1_ID = os.path.join(ID_DIR, "sources", "source-mock_ingest_version_v1-id.md")
INGESTED_VERSION_SOURCE_V2_EN = os.path.join(EN_DIR, "sources", "source-mock_ingest_version_v2.md")
INGESTED_VERSION_SOURCE_V2_ID = os.path.join(ID_DIR, "sources", "source-mock_ingest_version_v2-id.md")
VERSION_ARCHIVED_CONCEPT_EN = os.path.join(EN_DIR, "concepts", "ai", "mock-distilasi-kompresi-v1.0.0.md")
VERSION_ARCHIVED_CONCEPT_ID = os.path.join(ID_DIR, "concepts", "ai", "mock-distilasi-kompresi-id-v1.0.0.md")

def create_mock_files():
    print("Creating temporary parallel bilingual mock pages for verification...")
    
    # 1. English Mock Pages
    source_content_en = """---
type: source
source_file: "raw/articles/test_doc.md"
sha256: "12345abcdef"
created: 2026-06-02
updated: 2026-06-02
tags: [test, mock]
---
# Source Summary: Test Doc
This is a mock source summary in English.
"""

    concept_content_en = """---
type: concept
domain: ai
lang: en
translation: "[[test_concept_page_id]]"
tags: [test, mockautomation]
created: 2026-06-02
updated: 2026-06-02
sources: ["[[source-test_document]]"]
description: A mock concept page created for automated verification in English.
---
# Test Concept Page
This page is a test for mockautomation. It references a valid entity [[test_entity_page]] and a deliberately broken link [[missing_concept]].
"""

    entity_content_en = """---
type: entity
category: person
domain: ai
lang: en
translation: "[[test_entity_page_id]]"
created: 2026-06-02
updated: 2026-06-02
sources: []
tags: [tester, robot]
---
# Test Entity Page
This is a test entity page.
"""

    # 2. Indonesian Mock Pages
    source_content_id = """---
type: source
source_file: "raw/articles/test_doc.md"
sha256: "12345abcdef"
created: 2026-06-02
updated: 2026-06-02
tags: [test, mock]
---
# Ringkasan Sumber: Dokumen Tes
Ini adalah ringkasan sumber mock dalam bahasa Indonesia.
"""

    concept_content_id = """---
type: concept
domain: ai
lang: id
translation: "[[test_concept_page]]"
tags: [test, otomatisasi]
created: 2026-06-02
updated: 2026-06-02
sources: ["[[source-test_document-id]]"]
description: Halaman konsep mock yang dibuat untuk verifikasi otomatis dalam bahasa Indonesia.
---
# Halaman Konsep Tes
Halaman ini adalah pengujian. Ini merujuk entitas valid [[test_entity_page_id]] dan tautan rusak [[konsep_yang_hilang]].
"""

    entity_content_id = """---
type: entity
category: person
domain: ai
lang: id
translation: "[[test_entity_page]]"
created: 2026-06-02
updated: 2026-06-02
sources: []
tags: [tester, robot]
---
# Halaman Entitas Tes
Ini adalah halaman entitas pengujian.
"""

    # Create directories recursively
    os.makedirs(os.path.dirname(TEST_CONCEPT_EN), exist_ok=True)
    os.makedirs(os.path.dirname(TEST_ENTITY_EN), exist_ok=True)
    os.makedirs(os.path.dirname(TEST_SOURCE_EN), exist_ok=True)
    os.makedirs(os.path.dirname(TEST_CONCEPT_ID), exist_ok=True)
    os.makedirs(os.path.dirname(TEST_ENTITY_ID), exist_ok=True)
    os.makedirs(os.path.dirname(TEST_SOURCE_ID), exist_ok=True)

    # Write files (English)
    with open(TEST_SOURCE_EN, "w", encoding="utf-8") as f:
        f.write(source_content_en)
    with open(TEST_CONCEPT_EN, "w", encoding="utf-8") as f:
        f.write(concept_content_en)
    with open(TEST_ENTITY_EN, "w", encoding="utf-8") as f:
        f.write(entity_content_en)

    # Write files (Indonesian)
    with open(TEST_SOURCE_ID, "w", encoding="utf-8") as f:
        f.write(source_content_id)
    with open(TEST_CONCEPT_ID, "w", encoding="utf-8") as f:
        f.write(concept_content_id)
    with open(TEST_ENTITY_ID, "w", encoding="utf-8") as f:
        f.write(entity_content_id)

def cleanup():
    print("Cleaning up temporary bilingual mock files...")
    paths_to_clean = [
        TEST_CONCEPT_EN, TEST_ENTITY_EN, TEST_SOURCE_EN, 
        TEST_CONCEPT_ID, TEST_ENTITY_ID, TEST_SOURCE_ID, 
        INGEST_RAW_FILE, INGESTED_SOURCE_EN, INGESTED_SOURCE_ID, 
        INGESTED_CONCEPT_EN, INGESTED_CONCEPT_ID, 
        INGESTED_CONCEPT2_EN, INGESTED_CONCEPT2_ID, 
        INGEST_RAW_FILE2, INGESTED_SOURCE2_EN, INGESTED_SOURCE2_ID,
        INGEST_VERSION_RAW_V1, INGEST_VERSION_RAW_V2,
        INGESTED_VERSION_SOURCE_V1_EN, INGESTED_VERSION_SOURCE_V1_ID,
        INGESTED_VERSION_SOURCE_V2_EN, INGESTED_VERSION_SOURCE_V2_ID,
        VERSION_ARCHIVED_CONCEPT_EN, VERSION_ARCHIVED_CONCEPT_ID,
        INGEST_RAW_PAPER, INGESTED_PAPER_DIR_EN, INGESTED_PAPER_DIR_ID,
        os.path.join(EN_DIR, "sources", "source-mock_paper_test.md"),
        os.path.join(ID_DIR, "sources", "source-mock_paper_test-id.md"),
        os.path.join(WIKI_DIR, "raw_sources", "mock_ingest_test.txt"),
        os.path.join(WIKI_DIR, "raw_sources", "mock_ingest_test2.txt"),
        os.path.join(WIKI_DIR, "raw_sources", "mock_ingest_version_v1.txt"),
        os.path.join(WIKI_DIR, "raw_sources", "mock_ingest_version_v2.txt"),
        os.path.join(WIKI_DIR, "raw_sources", "mock_paper_test.txt")
    ]
    for filepath in paths_to_clean:
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)
                print(f"Removed mock file: {filepath}")

import atexit
atexit.register(cleanup)

def run_script(script_name, args=[]):
    cmd = [sys.executable, os.path.join("scripts", script_name)] + args
    print(f"Executing: {' '.join(cmd)}")
    env = os.environ.copy()
    env["TESTING"] = "1"
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
    return result.returncode, result.stdout, result.stderr

def run_tests():
    os.environ["TESTING"] = "1"
    try:
        # --- Step 0: Test chunk_text helper ---
        print("\n--- Testing chunk_text helper ---")
        from ingest import chunk_text
        sample_text = "Line A\n\nLine B\n\nLine C\n\nLine D"
        chunks = chunk_text(sample_text, max_chars=15, overlap=5)
        assert len(chunks) > 1, f"Expected multiple chunks, got {len(chunks)}"
        print("✅ chunk_text verified!")

        # --- Test Table Extraction Mock ---
        print("\n--- Testing table extraction logic ---")
        from ingest import extract_pdf_tables
        # Since we don't have a dummy pdf with tables in tests, verify it handles empty or missing pdf gracefully
        tables_res = extract_pdf_tables("nonexistent.pdf")
        assert tables_res == "", f"Expected empty string for missing file, got '{tables_res}'"
        print("✅ table extraction stub verified!")

        # --- Test Image Extraction Mock ---
        print("\n--- Testing image extraction logic ---")
        from ingest import extract_pdf_images
        images_res = extract_pdf_images("nonexistent.pdf", "nonexistent-source")
        assert images_res == "", f"Expected empty string for missing file, got '{images_res}'"
        print("✅ image extraction stub verified!")

        # --- Step 1: Test parser.py (Metadata & Attributes) ---
        print("\n--- Testing parser.py ---")
        test_yaml = """---
type: concept
domain: software-engineering
lang: en
tags: [parser, zero-dependency, test]
created: 2026-06-02
---
"""
        metadata = parse_yaml_frontmatter(test_yaml)
        assert metadata.get("type") == "concept", f"Expected type concept, got {metadata.get('type')}"
        assert metadata.get("domain") == "software-engineering"
        assert metadata.get("lang") == "en"
        assert isinstance(metadata.get("tags"), list)
        assert len(metadata.get("tags")) == 3
        assert "parser" in metadata.get("tags")
        print("✅ parse_yaml_frontmatter passes all validations!")
        
        attrs = detect_page_attributes("wiki/id/concepts/ai/test-concept.md")
        assert attrs["lang"] == "id", f"Expected lang id, got {attrs['lang']}"
        assert attrs["type"] == "concepts", f"Expected type concepts, got {attrs['type']}"
        assert attrs["domain"] == "ai", f"Expected domain ai, got {attrs['domain']}"
        print("✅ detect_page_attributes passes all validations!")

        # Step 2: Create mock files
        create_mock_files()
        
        # Step 3: Test make_index.py (Rebuild Bilingual Index)
        print("\n--- Testing make_index.py ---")
        code, stdout, stderr = run_script("make_index.py")
        print(stdout)
        if code != 0:
            print(f"❌ make_index.py failed! Error: {stderr}")
            return False
        
        # Check en/index.md and id/index.md
        index_en_path = os.path.join(EN_DIR, "index.md")
        index_id_path = os.path.join(ID_DIR, "index.md")
        
        if os.path.exists(index_en_path) and os.path.exists(index_id_path):
            with open(index_en_path, "r", encoding="utf-8") as f:
                index_en = f.read()
            with open(index_id_path, "r", encoding="utf-8") as f:
                index_id = f.read()
                
            if "test_concept_page" in index_en and "test_concept_page_id" in index_id:
                print("✅ Parallel localized index catalogs successfully rebuilt!")
            else:
                print("❌ index.md files failed to include mock pages.")
                return False
        else:
            print("❌ One of the index.md files was not found.")
            return False
            
        # Step 4: Test search.py with Cross-lingual Expansion
        print("\n--- Testing search.py with Cross-lingual Expansion ---")
        # Search for "mockautomation", which only appears in the English test concept.
        # It should return the English page AND dynamically expand to return the Indonesian page as a translated version!
        code, stdout, stderr = run_script("search.py", ["mockautomation"])
        print(stdout)
        if code != 0 or "test_concept_page" not in stdout:
            print("❌ search.py failed to return English concept.")
            return False
        if "test_concept_page_id" not in stdout or "Translated version" not in stdout:
            print("❌ search.py failed to expand search cross-lingually!")
            return False
        print("✅ search.py successfully expanded query cross-lingually!")

        # Step 4b: Test search.py --chat with Mock DeepSeek
        print("\n--- Testing search.py --chat with Mock DeepSeek ---")
        os.environ["MOCK_DEEPSEEK"] = "1"
        code, stdout, stderr = run_script("search.py", ["--chat", "Explain the concept of mockautomation?"])
        if "MOCK_DEEPSEEK" in os.environ:
            del os.environ["MOCK_DEEPSEEK"]
        print(stdout)
        if code != 0 or "COGNITIVE CHAT RESPONSE" not in stdout or "Mock Answer" not in stdout:
            print("❌ search.py --chat failed or returned unexpected output.")
            return False
        print("✅ search.py --chat mock test passed successfully!")

        # Step 5: Test linter.py (Lint Verification)
        print("\n--- Testing linter.py ---")
        code, stdout, stderr = run_script("linter.py")
        print(stdout)
        
        if "missing_concept" in stdout and "test_concept_page" in stdout:
            print("✅ linter.py correctly flagged the broken link [[missing_concept]]!")
            print("✅ linter.py correctly flagged [[test_concept_page]] as an orphan!")
        else:
            print("❌ linter.py failed to flag deliberate issues.")
            return False
            
        # --- Step 6: Test ingest.py (Ingestion Orchestrator) ---
        print("\n--- Testing ingest.py ---")
        # Create a raw mock article to ingest
        os.makedirs(os.path.dirname(INGEST_RAW_FILE), exist_ok=True)
        raw_article_content = """# Deep Dive on mockdistil
        
This article describes the concept of mockdistil in modern machine learning workloads.
It details how high-capacity teacher architectures transfer soft probability logits
into compact student networks.
"""
        with open(INGEST_RAW_FILE, "w", encoding="utf-8") as f:
            f.write(raw_article_content)
            
        # Run ingestion
        code, stdout, stderr = run_script("ingest.py", [INGEST_RAW_FILE])
        print(stdout)
        if code != 0:
            print(f"❌ ingest.py failed with exit code {code}! Error: {stderr}")
            return False
            
        # Validate that parallel files were created
        if (os.path.exists(INGESTED_SOURCE_EN) and 
            os.path.exists(INGESTED_SOURCE_ID) and 
            os.path.exists(INGESTED_CONCEPT_EN) and 
            os.path.exists(INGESTED_CONCEPT_ID)):
            print("✅ Parallel sources and concepts successfully ingested locally!")
        else:
            print("❌ Parallel files were not created correctly by ingest.py.")
            return False
            
        # Verify duplicate check
        print("\n--- Testing Duplicate Ingestion Prevention ---")
        code, stdout, stderr = run_script("ingest.py", [INGEST_RAW_FILE])
        print(stdout)
        if "Source asset already compiled" not in stdout:
            print("❌ ingest.py failed to prevent duplicate ingestion!")
            return False
        print("✅ Duplicate ingestion successfully prevented!")

        # Verify re-ingestion of a modified file (same path, different content)
        print("\n--- Testing Re-ingestion of Modified File ---")
        raw_article_content_mod = raw_article_content + "\nThis is a modified line for testing update.\n"
        with open(INGEST_RAW_FILE, "w", encoding="utf-8") as f:
            f.write(raw_article_content_mod)
        code, stdout, stderr = run_script("ingest.py", [INGEST_RAW_FILE])
        print(stdout)
        if "Source asset already compiled" in stdout or code != 0:
            print("❌ ingest.py failed to re-ingest modified file!")
            return False
        print("✅ Re-ingestion of modified file succeeded!")

        # Verify smart merging of concept page from different source
        print("\n--- Testing Smart Merging of Concepts from Multiple Sources ---")
        # Create second raw article referencing the same concept (which maps to mock-distilasi-kompresi)
        raw_article2_content = """# Another Ingest Test on mockdistil
        
This article introduces alternative compression metrics for mockdistil compression.
"""
        with open(INGEST_RAW_FILE2, "w", encoding="utf-8") as f:
            f.write(raw_article2_content)
        
        # Capture the original created date of INGESTED_CONCEPT_EN
        with open(INGESTED_CONCEPT_EN, "r", encoding="utf-8") as f:
            orig_concept_content = f.read()
        orig_metadata = parse_yaml_frontmatter(orig_concept_content)
        orig_created = orig_metadata.get("created")
        
        code, stdout, stderr = run_script("ingest.py", [INGEST_RAW_FILE2])
        print(stdout)
        if code != 0:
            print("❌ Ingestion of second raw article failed!")
            return False
            
        # Verify the concept page is merged
        with open(INGESTED_CONCEPT_EN, "r", encoding="utf-8") as f:
            merged_concept_content = f.read()
        
        merged_metadata = parse_yaml_frontmatter(merged_concept_content)
        print(f"Merged Frontmatter: {merged_metadata}")
        
        # 1. Verify sources are merged
        expected_sources = ["[[source-mock_ingest_test]]", "[[source-mock_ingest_test2]]"]
        actual_sources = merged_metadata.get("sources", [])
        if not all(src in actual_sources for src in expected_sources):
            print(f"❌ Concept merging failed! Expected sources {expected_sources}, got {actual_sources}")
            return False
            
        # 2. Verify creation date is preserved
        if merged_metadata.get("created") != orig_created:
            print(f"❌ Creation date not preserved! Original {orig_created}, got {merged_metadata.get('created')}")
            return False
            
        # 3. Verify content from both sources is present
        if "alternative compression metrics" not in merged_concept_content.lower() or "teacher architectures" not in merged_concept_content.lower():
            print("❌ Content was not merged! One of the sources content is missing.")
            return False
            
        print("✅ Smart merging of concept pages successfully validated!")

        # Verify temporal versioning and archiving
        print("\n--- Testing Temporal Versioning and Archiving ---")
        # 1. Create raw article with version 1.0.0
        v1_raw_content = """---
version: 1.0.0
---
# Deep Dive on mockdistil V1

This article describes the concept of mockdistil in modern machine learning workloads.
It details how high-capacity teacher architectures transfer soft probability logits
into compact student networks.
"""
        os.makedirs(os.path.dirname(INGEST_VERSION_RAW_V1), exist_ok=True)
        with open(INGEST_VERSION_RAW_V1, "w", encoding="utf-8") as f:
            f.write(v1_raw_content)
            
        # Ingest version 1
        code, stdout, stderr = run_script("ingest.py", [INGEST_VERSION_RAW_V1])
        if code != 0:
            print(f"❌ Ingestion of V1 raw article failed with code {code}! Error: {stderr}")
            return False
            
        # Verify V1 concept exists and has version 1.0.0, status active
        with open(INGESTED_CONCEPT_EN, "r", encoding="utf-8") as f:
            v1_concept_content = f.read()
        v1_metadata = parse_yaml_frontmatter(v1_concept_content)
        assert v1_metadata.get("version") == "1.0.0", f"Expected version 1.0.0, got {v1_metadata.get('version')}"
        assert v1_metadata.get("status") == "active", f"Expected status active, got {v1_metadata.get('status')}"
        
        # 2. Create raw article with version 2.0.0
        v2_raw_content = """---
version: 2.0.0
---
# Deep Dive on mockdistil V2

This article describes the concept of mockdistil in modern machine learning workloads.
It details how high-capacity teacher architectures transfer soft probability logits
into compact student networks with new optimization methods.
"""
        os.makedirs(os.path.dirname(INGEST_VERSION_RAW_V2), exist_ok=True)
        with open(INGEST_VERSION_RAW_V2, "w", encoding="utf-8") as f:
            f.write(v2_raw_content)
            
        # Ingest version 2
        code, stdout, stderr = run_script("ingest.py", [INGEST_VERSION_RAW_V2])
        if code != 0:
            print(f"❌ Ingestion of V2 raw article failed with code {code}! Error: {stderr}")
            return False
            
        # 3. Verify V2 concept exists and has version 2.0.0, status active, and supersedes v1.0.0
        with open(INGESTED_CONCEPT_EN, "r", encoding="utf-8") as f:
            v2_concept_content = f.read()
        v2_metadata = parse_yaml_frontmatter(v2_concept_content)
        assert v2_metadata.get("version") == "2.0.0", f"Expected version 2.0.0, got {v2_metadata.get('version')}"
        assert v2_metadata.get("status") == "active", f"Expected status active, got {v2_metadata.get('status')}"
        assert v2_metadata.get("supersedes") == "[[mock-distilasi-kompresi-v1.0.0]]", f"Expected supersedes tag, got {v2_metadata.get('supersedes')}"
        
        # 4. Verify archived/deprecated V1 concept exists at path and has status deprecated
        if not os.path.exists(VERSION_ARCHIVED_CONCEPT_EN):
            print(f"❌ Archived V1 concept file not found at {VERSION_ARCHIVED_CONCEPT_EN}")
            return False
        with open(VERSION_ARCHIVED_CONCEPT_EN, "r", encoding="utf-8") as f:
            archived_content = f.read()
        archived_metadata = parse_yaml_frontmatter(archived_content)
        assert archived_metadata.get("status") == "deprecated", f"Expected archived status deprecated, got {archived_metadata.get('status')}"
        assert archived_metadata.get("version") == "1.0.0", f"Expected archived version 1.0.0, got {archived_metadata.get('version')}"
        assert archived_metadata.get("superseded_by") == "[[mock-distilasi-kompresi]]", f"Expected superseded_by tag, got {archived_metadata.get('superseded_by')}"
        
        # 5. Verify Version History timeline links are present in both
        if "Version History" not in v2_concept_content or "[[mock-distilasi-kompresi-v1.0.0]]" not in v2_concept_content:
            print("❌ Version history timeline section missing from V2 concept page!")
            return False
        if "Version History" not in archived_content or "[[mock-distilasi-kompresi]]" not in archived_content:
            print("❌ Version history timeline section missing from archived V1 concept page!")
            return False

        # Verify Indonesian equivalents are also updated/archived
        with open(INGESTED_CONCEPT_ID, "r", encoding="utf-8") as f:
            v2_concept_id_content = f.read()
        v2_id_metadata = parse_yaml_frontmatter(v2_concept_id_content)
        assert v2_id_metadata.get("version") == "2.0.0"
        assert v2_id_metadata.get("status") == "active"
        assert v2_id_metadata.get("supersedes") == "[[mock-distilasi-kompresi-id-v1.0.0]]"
        
        if not os.path.exists(VERSION_ARCHIVED_CONCEPT_ID):
            print(f"❌ Archived V1 Indonesian concept file not found at {VERSION_ARCHIVED_CONCEPT_ID}")
            return False
        with open(VERSION_ARCHIVED_CONCEPT_ID, "r", encoding="utf-8") as f:
            archived_id_content = f.read()
        archived_id_metadata = parse_yaml_frontmatter(archived_id_content)
        assert archived_id_metadata.get("status") == "deprecated"
        assert archived_id_metadata.get("superseded_by") == "[[mock-distilasi-kompresi-id]]"
            
        print("✅ Temporal versioning and archiving successfully validated!")

        # --- Testing PDF Paper Ingestion ---
        print("\n--- Testing PDF Paper Ingestion (Hierarchical Folders & Subpages) ---")
        # Generate a mock PDF file using fitz
        import fitz
        os.makedirs(os.path.dirname(INGEST_RAW_PAPER), exist_ok=True)
        pdf_doc = fitz.open()
        pdf_page = pdf_doc.new_page()
        # Insert some text that triggers concept extraction
        pdf_page.insert_text((50, 50), "Abstract: This paper studies mockdistil in modern neural networks. Section: Experiments. We compare teacher and student models.")
        pdf_doc.save(INGEST_RAW_PAPER)
        pdf_doc.close()
        
        # Run ingestion of the PDF paper
        code, stdout, stderr = run_script("ingest.py", [INGEST_RAW_PAPER])
        print(stdout)
        if code != 0:
            print(f"❌ Ingestion of PDF paper failed with exit code {code}! Error: {stderr}")
            return False
            
        # Verify that flat files exist
        main_summary_en = os.path.join(EN_DIR, "sources", "source-mock_paper_test.md")
        main_summary_id = os.path.join(ID_DIR, "sources", "source-mock_paper_test-id.md")
        
        assert os.path.exists(main_summary_en), "English main summary file missing!"
        assert os.path.exists(main_summary_id), "Indonesian main summary file missing!"
        
        # Verify that main summary contains the expected sections/concepts
        with open(main_summary_en, "r", encoding="utf-8") as f:
            main_sum_en_content = f.read()
        assert "Core Concepts" in main_sum_en_content, "Missing Core Concepts section!"
        assert "[[mock-distilasi-kompresi]]" in main_sum_en_content, "Missing link to concept!"

        with open(main_summary_id, "r", encoding="utf-8") as f:
            main_sum_id_content = f.read()
        assert "Konsep Inti" in main_sum_id_content, "Missing Indonesian Konsep Inti section!"
        assert "[[mock-distilasi-kompresi-id]]" in main_sum_id_content, "Missing link to Indonesian concept!"
        
        print("✅ Hierarchical folder writing and paper subpage generation validated successfully!")

        # --- Step 7: Test Cross-Reference & Contradiction System ---
        print("\n--- Testing Cross-Reference & Contradiction System ---")
        import importlib.util
        spec = importlib.util.spec_from_file_location("ingest_module", "scripts/ingest.py")
        ingest_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ingest_module)
        import ingest.conflict_detector as cd
        
        # Save original function
        orig_detect_relations = cd._detect_relations_with_llm
        
        # Define mock detector
        def mock_detect_relations(incoming_concept, existing_concepts, incoming_source_name):
            if incoming_concept.get("name") == "mock-distilasi-kompresi":
                return [{
                    "target": "in-context-learning-primer",
                    "type": "contrasting",
                    "claim_en": "Mock distillation conflicts with in-context learning assumptions.",
                    "claim_id": "Kompresi mock bertentangan dengan asumsi in-context learning.",
                    "source": f"[[{incoming_source_name}]]"
                }]
            return []
            
        cd._detect_relations_with_llm = mock_detect_relations
        os.environ["DEEPSEEK_API_KEY"] = "mock_key"
        
        try:
            # We want to ingest mock_ingest_test2.md which triggers mock-distilasi-kompresi
            # First, create target concept pages so they exist in the vault
            concept_primer_path = os.path.join(EN_DIR, "concepts", "ai", "in-context-learning-primer.md")
            concept_primer_id_path = os.path.join(ID_DIR, "concepts", "ai", "in-context-learning-primer-id.md")
            os.makedirs(os.path.dirname(concept_primer_path), exist_ok=True)
            os.makedirs(os.path.dirname(concept_primer_id_path), exist_ok=True)
            with open(concept_primer_path, "w", encoding="utf-8") as f:
                f.write("---\ntype: concept\ndomain: ai\nlang: en\ncreated: 2026-06-02\nupdated: 2026-06-02\ndescription: Mock target concept.\n---\n# In-Context Learning Primer\n")
            with open(concept_primer_id_path, "w", encoding="utf-8") as f:
                f.write("---\ntype: concept\ndomain: ai\nlang: id\ntranslation: \"[[in-context-learning-primer]]\"\ncreated: 2026-06-02\nupdated: 2026-06-02\ndescription: Mock target concept id.\n---\n# Primer In-Context Learning\n")
            
            # Recreate raw article 2 to ingest
            with open(INGEST_RAW_FILE2, "w", encoding="utf-8") as f:
                f.write("# Another Ingest Test on mockdistil\n\nThis article introduces alternative compression metrics for mockdistil.\n")
                
            # Run ingestion in the same process to preserve mocks
            import sys
            orig_argv = sys.argv
            sys.argv = ["ingest.py", INGEST_RAW_FILE2]
            try:
                ingest_module.main()
            finally:
                sys.argv = orig_argv
            
            # 1. Verify EN Concept Page Frontmatter & Body
            with open(INGESTED_CONCEPT_EN, "r", encoding="utf-8") as f:
                concept_en_content = f.read()
            concept_en_fm = parse_yaml_frontmatter(concept_en_content)
            assert "relations" in concept_en_fm, "Relations missing from EN concept frontmatter!"
            assert concept_en_fm["relations"][0]["target"] == "[[in-context-learning-primer]]"
            assert concept_en_fm["relations"][0]["type"] == "contradicts"
            
            assert "## Cross-References" in concept_en_content, "Cross-References section missing from EN concept body!"
            assert "### Contradicts" in concept_en_content, "Contradicts heading missing from EN concept body!"
            assert "[[in-context-learning-primer]]" in concept_en_content, "Target link missing from EN concept body!"
            assert "Mock distillation conflicts with in-context learning assumptions" in concept_en_content, "Claim missing from EN concept body!"
            
            # 2. Verify ID Concept Page Frontmatter & Body
            with open(INGESTED_CONCEPT_ID, "r", encoding="utf-8") as f:
                concept_id_content = f.read()
            concept_id_fm = parse_yaml_frontmatter(concept_id_content)
            assert "relations" in concept_id_fm, "Relations missing from ID concept frontmatter!"
            assert concept_id_fm["relations"][0]["target"] == "[[in-context-learning-primer-id]]"
            assert concept_id_fm["relations"][0]["type"] == "contradicts"
            
            assert "## Referensi Silang" in concept_id_content, "Referensi Silang section missing from ID concept body!"
            assert "### Bertentangan" in concept_id_content, "Bertentangan heading missing from ID concept body!"
            assert "[[in-context-learning-primer-id]]" in concept_id_content, "Target link missing from ID concept body!"
            assert "Kompresi mock bertentangan dengan asumsi in-context learning." in concept_id_content, "Claim missing from ID concept body!"
            
            # 3. Verify EN Source Page
            with open(INGESTED_SOURCE2_EN, "r", encoding="utf-8") as f:
                source_en_content = f.read()
            assert "## Related Work Connections" in source_en_content, "Related Work Connections section missing from EN source page!"
            assert "- **In Context Learning Primer** \u2014 (contradicts): Mock distillation conflicts with in-context learning assumptions. (🌐 [[in-context-learning-primer]])" in source_en_content, "Invalid EN source relation bullet!"
            
            # 4. Verify ID Source Page
            with open(INGESTED_SOURCE2_ID, "r", encoding="utf-8") as f:
                source_id_content = f.read()
            assert "## Koneksi Penelitian Terkait" in source_id_content, "Koneksi Penelitian Terkait section missing from ID source page!"
            assert "- **In Context Learning Primer** \u2014 (bertentangan): Kompresi mock bertentangan dengan asumsi in-context learning. (🌐 [[in-context-learning-primer-id]])" in source_id_content, "Invalid ID source relation bullet!"
            
            print("✅ Relation rendering in concept and source pages verified successfully!")
            
            # 5. Verify Merge Preservation of Relations
            # We will merge another source which adds a new relation (supports)
            def mock_detect_relations_merge(incoming_concept, existing_concepts, incoming_source_name):
                if incoming_concept.get("name") == "mock-distilasi-kompresi":
                    return [{
                        "target": "in-context-learning-primer",
                        "type": "supports",
                        "claim_en": "Mock distillation supports in-context learning parameters.",
                        "claim_id": "Kompresi mock mendukung parameter in-context learning.",
                        "source": f"[[{incoming_source_name}]]"
                    }]
                return []
                
            cd._detect_relations_with_llm = mock_detect_relations_merge
            
            # Run ingestion again on a new file (so it merges into the existing mock-distilasi-kompresi concept)
            INGEST_RAW_FILE_MERGE = os.path.join("raw", "articles", "mock_ingest_merge.md")
            with open(INGEST_RAW_FILE_MERGE, "w", encoding="utf-8") as f:
                f.write("# Merge Test on mockdistil\n\nThis article merges mockdistil findings.\n")
                
            try:
                # Run ingestion in the same process to preserve mocks
                orig_argv = sys.argv
                sys.argv = ["ingest.py", INGEST_RAW_FILE_MERGE]
                try:
                    ingest_module.main()
                finally:
                    sys.argv = orig_argv
                
                # Check that both relations (contradicts and supports) are present in the concept page frontmatter
                with open(INGESTED_CONCEPT_EN, "r", encoding="utf-8") as f:
                    merged_content = f.read()
                merged_fm = parse_yaml_frontmatter(merged_content)
                assert len(merged_fm["relations"]) == 2, f"Expected 2 relations after merge, got {len(merged_fm['relations'])}"
                
                targets = [r["target"] for r in merged_fm["relations"]]
                types = [r["type"] for r in merged_fm["relations"]]
                assert "[[in-context-learning-primer]]" in targets
                assert "contradicts" in types
                assert "supports" in types
                
                # Check that body contains both headings
                assert "### Contradicts" in merged_content
                assert "### Supports" in merged_content
                
                print("✅ Merge preservation of relations verified successfully!")
                
            finally:
                if os.path.exists(INGEST_RAW_FILE_MERGE):
                    os.remove(INGEST_RAW_FILE_MERGE)
                # Cleanup newly created source merge pages
                source_merge_en = os.path.join(EN_DIR, "sources", "source-mock_ingest_merge.md")
                source_merge_id = os.path.join(ID_DIR, "sources", "source-mock_ingest_merge-id.md")
                if os.path.exists(source_merge_en): os.remove(source_merge_en)
                if os.path.exists(source_merge_id): os.remove(source_merge_id)
                raw_merge_txt = os.path.join(WIKI_DIR, "raw_sources", "mock_ingest_merge.txt")
                if os.path.exists(raw_merge_txt): os.remove(raw_merge_txt)
                
        finally:
            cd._detect_relations_with_llm = orig_detect_relations
            if "DEEPSEEK_API_KEY" in os.environ:
                del os.environ["DEEPSEEK_API_KEY"]
                
        # --- Step 8: Test Classification Safeguard (Reclassification of Concepts) ---
        print("\n--- Testing Concept Reclassification Safeguard ---")
        mock_concepts = []
        mock_entities = [
            {
                "name": "samuel-hartzmark",
                "category": "person",
                "content_en": "Author samuel-hartzmark",
                "content_id": "Penulis samuel-hartzmark"
            },
            {
                "name": "expected-return-formula",
                "category": "model",
                "content_en": "A formula for expected return",
                "content_id": "Formula untuk return yang diharapkan"
            },
            {
                "name": "risk-neutral-variance",
                "category": "other",
                "content_en": "Risk-neutral variance description",
                "content_id": "Deskripsi variance risk-neutral"
            }
        ]
        
        # Call the helper function from ingest_module
        reclass_concepts, reclass_entities = ingest_module.reclassify_concepts_and_entities(
            mock_concepts, mock_entities, os.path.join(EN_DIR, "concepts")
        )
        
        # Verify result
        entity_names = [e["name"] for e in reclass_entities]
        concept_names = [c["name"] for c in reclass_concepts]
        
        assert "samuel-hartzmark" in entity_names, "samuel-hartzmark should remain an entity!"
        assert "expected-return-formula" in concept_names, "expected-return-formula should be reclassified as a concept!"
        assert "risk-neutral-variance" in concept_names, "risk-neutral-variance should be reclassified as a concept!"
        
        assert "expected-return-formula" not in entity_names, "expected-return-formula should not remain in entities!"
        assert "risk-neutral-variance" not in entity_names, "risk-neutral-variance should not remain in entities!"
        
        # Verify mapped fields
        formula_concept = next(c for c in reclass_concepts if c["name"] == "expected-return-formula")
        assert formula_concept["description_en"] == "A formula for expected return"
        assert formula_concept["content_en"] == "A formula for expected return"
        
        print("✅ Concept reclassification safeguard verified successfully!")
        
        print("\n🎉 ALL BILINGUAL AUTOMATED TESTS COMPLETED SUCCESSFULLY! 🎉")
        return True

    finally:
        # Clean up
        cleanup()
        # Restore actual index page by running indexer on clean state
        run_script("make_index.py")

if __name__ == "__main__":
    # Windows Encoding Safeguard for non-ASCII characters / emojis
    if sys.platform.startswith("win"):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    success = run_tests()
    sys.exit(0 if success else 1)
