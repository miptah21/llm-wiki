import os
import subprocess
import sys
import shutil

# Windows Encoding Safeguard for non-ASCII characters / emojis
if sys.platform.startswith("win"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

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
INGEST_RAW_FILE = os.path.join("raw", "articles", "mock_ingest_test.md")
INGESTED_SOURCE_EN = os.path.join(EN_DIR, "sources", "source-mock_ingest_test.md")
INGESTED_SOURCE_ID = os.path.join(ID_DIR, "sources", "source-mock_ingest_test-id.md")
INGESTED_CONCEPT_EN = os.path.join(EN_DIR, "concepts", "ai", "distilasi-kompresi.md")
INGESTED_CONCEPT_ID = os.path.join(ID_DIR, "concepts", "ai", "distilasi-kompresi-id.md")
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
VERSION_ARCHIVED_CONCEPT_EN = os.path.join(EN_DIR, "concepts", "ai", "distilasi-kompresi-v1.0.0.md")
VERSION_ARCHIVED_CONCEPT_ID = os.path.join(ID_DIR, "concepts", "ai", "distilasi-kompresi-id-v1.0.0.md")

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
tags: [test, automation]
created: 2026-06-02
updated: 2026-06-02
sources: ["[[source-test_document]]"]
description: A mock concept page created for automated verification in English.
---
# Test Concept Page
This page is a test. It references a valid entity [[test_entity_page]] and a deliberately broken link [[missing_concept]].
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
        VERSION_ARCHIVED_CONCEPT_EN, VERSION_ARCHIVED_CONCEPT_ID
    ]
    for filepath in paths_to_clean:
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                shutil.rmtree(filepath)
            else:
                os.remove(filepath)
                print(f"Removed mock file: {filepath}")

def run_script(script_name, args=[]):
    cmd = [sys.executable, os.path.join("scripts", script_name)] + args
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return result.returncode, result.stdout, result.stderr

def run_tests():
    try:
        # --- Step 0: Test chunk_text helper ---
        print("\n--- Testing chunk_text helper ---")
        from ingest import chunk_text
        sample_text = "Line A\n\nLine B\n\nLine C\n\nLine D"
        chunks = chunk_text(sample_text, max_chars=15, overlap=5)
        assert len(chunks) > 1, f"Expected multiple chunks, got {len(chunks)}"
        print("✅ chunk_text verified!")

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
        # Search for "automation", which only appears in the English test concept.
        # It should return the English page AND dynamically expand to return the Indonesian page as a translated version!
        code, stdout, stderr = run_script("search.py", ["automation"])
        print(stdout)
        if code != 0 or "test_concept_page" not in stdout:
            print("❌ search.py failed to return English concept.")
            return False
        if "test_concept_page_id" not in stdout or "Translated version" not in stdout:
            print("❌ search.py failed to expand search cross-lingually!")
            return False
        print("✅ search.py successfully expanded query cross-lingually!")

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
        raw_article_content = """# Deep Dive on Distilasi
        
This article describes the concept of distilasi in modern machine learning workloads.
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
        # Create second raw article referencing the same concept (which maps to distilasi-kompresi)
        raw_article2_content = """# Another Ingest Test on Distilasi
        
This article introduces alternative compression metrics for distilasi compression.
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
# Deep Dive on Distilasi V1

This article describes the concept of distilasi in modern machine learning workloads.
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
# Deep Dive on Distilasi V2

This article describes the concept of distilasi in modern machine learning workloads.
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
        assert v2_metadata.get("supersedes") == "[[distilasi-kompresi-v1.0.0]]", f"Expected supersedes tag, got {v2_metadata.get('supersedes')}"
        
        # 4. Verify archived/deprecated V1 concept exists at path and has status deprecated
        if not os.path.exists(VERSION_ARCHIVED_CONCEPT_EN):
            print(f"❌ Archived V1 concept file not found at {VERSION_ARCHIVED_CONCEPT_EN}")
            return False
        with open(VERSION_ARCHIVED_CONCEPT_EN, "r", encoding="utf-8") as f:
            archived_content = f.read()
        archived_metadata = parse_yaml_frontmatter(archived_content)
        assert archived_metadata.get("status") == "deprecated", f"Expected archived status deprecated, got {archived_metadata.get('status')}"
        assert archived_metadata.get("version") == "1.0.0", f"Expected archived version 1.0.0, got {archived_metadata.get('version')}"
        assert archived_metadata.get("superseded_by") == "[[distilasi-kompresi]]", f"Expected superseded_by tag, got {archived_metadata.get('superseded_by')}"
        
        # 5. Verify Version History timeline links are present in both
        if "Version History" not in v2_concept_content or "[[distilasi-kompresi-v1.0.0]]" not in v2_concept_content:
            print("❌ Version history timeline section missing from V2 concept page!")
            return False
        if "Version History" not in archived_content or "[[distilasi-kompresi]]" not in archived_content:
            print("❌ Version history timeline section missing from archived V1 concept page!")
            return False

        # Verify Indonesian equivalents are also updated/archived
        with open(INGESTED_CONCEPT_ID, "r", encoding="utf-8") as f:
            v2_concept_id_content = f.read()
        v2_id_metadata = parse_yaml_frontmatter(v2_concept_id_content)
        assert v2_id_metadata.get("version") == "2.0.0"
        assert v2_id_metadata.get("status") == "active"
        assert v2_id_metadata.get("supersedes") == "[[distilasi-kompresi-id-v1.0.0]]"
        
        if not os.path.exists(VERSION_ARCHIVED_CONCEPT_ID):
            print(f"❌ Archived V1 Indonesian concept file not found at {VERSION_ARCHIVED_CONCEPT_ID}")
            return False
        with open(VERSION_ARCHIVED_CONCEPT_ID, "r", encoding="utf-8") as f:
            archived_id_content = f.read()
        archived_id_metadata = parse_yaml_frontmatter(archived_id_content)
        assert archived_id_metadata.get("status") == "deprecated"
        assert archived_id_metadata.get("superseded_by") == "[[distilasi-kompresi-id]]"
            
        print("✅ Temporal versioning and archiving successfully validated!")

        print("\n🎉 ALL BILINGUAL AUTOMATED TESTS COMPLETED SUCCESSFULLY! 🎉")
        return True

    finally:
        # Clean up
        cleanup()
        # Restore actual index page by running indexer on clean state
        run_script("make_index.py")

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
