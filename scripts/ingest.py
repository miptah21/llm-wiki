import os
import sys
import re
from datetime import datetime
from typing import Optional, List, Dict, Any

# Windows encoding safeguard for emoji output (at module load time)
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
    project_relative_path,
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
from ingest.conflict_detector import detect_cross_references, read_concept_pages
from ingest.wikilinks import (
    scan_vault_pages_db,
    build_link_map,
    normalize_wikilinks
)

WIKI_DIR = "wiki"
EN_DIR = os.path.join(WIKI_DIR, "en")
ID_DIR = os.path.join(WIKI_DIR, "id")
LOG_PATH = os.path.join(WIKI_DIR, "log.md")
def resolve_translation_target(target_name: str, target_lang: str) -> str:
    """Resolves the actual translation page name from the SQLite metadata database if it exists,
    otherwise falls back to f'{target_name}-id' (or stripping '-id' if target_lang is 'en').
    """
    import sqlite3
    db_path = os.path.join(WIKI_DIR, ".search_index.db")
    if not os.path.exists(db_path):
        return f"{target_name}-id" if target_lang == "id" else target_name.replace("-id", "")
        
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        lookup_lang = "en" if target_lang == "id" else "id"
        cursor.execute("SELECT translation FROM wiki_metadata WHERE name = ? AND lang = ?;", (target_name, lookup_lang))
        row = cursor.fetchone()
        if row and row[0] and row[0].strip().lower() != "none" and row[0].strip():
            return row[0].strip()
    except Exception:
        pass
    finally:
        if conn:
            conn.close()
            
    return f"{target_name}-id" if target_lang == "id" else target_name.replace("-id", "")


def resolve_canonical_en_name(name: str) -> str:
    """Resolves any concept name (English or Indonesian) to its canonical English name using SQLite metadata."""
    import sqlite3
    db_path = os.path.join(WIKI_DIR, ".search_index.db")
    if not os.path.exists(db_path):
        return name
        
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Check if the name exists and is already English
        cursor.execute("SELECT lang, translation FROM wiki_metadata WHERE name = ?;", (name,))
        row = cursor.fetchone()
        if row:
            lang, trans = row
            if lang == "en":
                return name
            elif lang == "id" and trans and trans.strip() and trans.strip().lower() != "none":
                clean_trans = trans.replace("[[", "").replace("]]", "").strip()
                return clean_trans
    except Exception:
        pass
    finally:
        if conn:
            conn.close()
            
    return name

def scan_existing_pages(vault_root: str):
    existing_en = set()
    existing_id = set()
    wiki_path = os.path.join(vault_root, "wiki")
    if not os.path.exists(wiki_path):
        return existing_en, existing_id
    for root, dirs, files in os.walk(wiki_path):
        relative_path = os.path.relpath(root, wiki_path).replace("\\", "/")
        parts = relative_path.split("/")
        if len(parts) >= 1:
            lang = parts[0].lower()
            for f in files:
                if f.endswith(".md"):
                    name_no_ext = os.path.splitext(f)[0].lower()
                    if lang == "en":
                        existing_en.add(name_no_ext)
                    elif lang == "id":
                        existing_id.add(name_no_ext)
    return existing_en, existing_id


def find_source_file_path(source_name: str) -> Optional[str]:
    en_sources_dir = os.path.join(EN_DIR, "sources")
    if os.path.exists(en_sources_dir):
        for root, _, files in os.walk(en_sources_dir):
            if f"{source_name}.md" in files:
                return os.path.join(root, f"{source_name}.md")
    return None

def extract_source_citation(source_name: str) -> str:
    source_name_en = resolve_canonical_en_name(source_name)
    if not source_name_en.startswith("source-"):
        source_name_en = f"source-{source_name_en}"
        
    fpath = find_source_file_path(source_name_en)
    if not fpath:
        match = re.search(r'source-([A-Za-z]+)-(\d{4})', source_name_en)
        if match:
            return f"{match.group(1)} et al. ({match.group(2)})"
        return source_name.replace("source-", "").replace("-id", "").replace("-", " ").title()

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            
        authors = ""
        year = ""
        
        auth_match = re.search(r'\*\*(?:Authors|Penulis):\*\*?\s*(.+)', content, re.IGNORECASE)
        if auth_match:
            authors_str = auth_match.group(1).strip()
            parts = re.split(r',\s*|\s+and\s+', authors_str)
            if len(parts) > 1:
                first_author = parts[0].strip()
                last_name = first_author.split()[-1] if first_author.split() else first_author
                authors = f"{last_name} et al."
            elif parts:
                first_author = parts[0].strip()
                last_name = first_author.split()[-1] if first_author.split() else first_author
                authors = last_name
                
        pub_match = re.search(r'\*\*(?:Published|Publikasi):\*\*?\s*(.+)', content, re.IGNORECASE)
        if pub_match:
            pub_str = pub_match.group(1).strip()
            year_match = re.search(r'\b(\d{4})\b', pub_str)
            if year_match:
                year = year_match.group(1)
                
        if not authors or not year:
            citation_match = re.search(r'\(([A-Za-z\s]+ et al\.),\s*(\d{4})\)', content)
            if citation_match:
                if not authors:
                    authors = citation_match.group(1)
                if not year:
                    year = citation_match.group(2)
                    
        if not year:
            year_match = re.search(r'\b(\d{4})\b', source_name_en)
            if year_match:
                year = year_match.group(1)
                
        if not authors:
            base_name = source_name_en.replace("source-", "")
            clean_name = re.sub(r'-\d{4}', '', base_name)
            authors = clean_name.replace("-", " ").title()
            
        if year:
            return f"{authors} ({year})"
        else:
            return authors
            
    except Exception:
        pass
        
    return source_name.replace("source-", "").replace("-id", "").replace("-", " ").title()

def get_concept_primary_source(concept_name: str, existing_concepts: dict) -> Optional[str]:
    if concept_name in existing_concepts:
        info = existing_concepts[concept_name]
        sources_val = info.get("sources", "")
        if isinstance(sources_val, list):
            sources_list = sources_val
        elif isinstance(sources_val, str):
            sources_list = [sources_val]
        else:
            sources_list = []
            
        for src in sources_list:
            src_str = str(src).strip()
            found = re.findall(r'\[\[(.*?)\]\]', src_str)
            if found:
                return found[0]
            if src_str.startswith("[[") and src_str.endswith("]]"):
                return src_str[2:-2].strip()
            if src_str:
                return src_str
    return None


def sanitize_indonesian_latex(content: str) -> str:
    """Sanitizes Indonesian LaTeX notations and terms to ensure standard terminology."""
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


def auto_link_media_and_tables(content: str, filename_base: str, lang: str) -> str:
    """Scan content for references to Tables and Figures, appending transclusions if found.

    Args:
        content: The raw markdown content.
        filename_base: The base name of the source PDF.
        lang: Language ('en' or 'id').

    Returns:
        The content with appended media/table transclusion links if they exist.
    """
    # 1. Look for figures: e.g. "Figure 1", "Fig. 2", "Gambar 3"
    fig_mentions = re.findall(r"\b(?:Figure|Fig\.|Gambar)\s+(\d+)", content, re.IGNORECASE)
    fig_links = []
    seen_figs = set()
    for num in fig_mentions:
        if num in seen_figs:
            continue
        seen_figs.add(num)
        
        # Check if the figure file exists in wiki/assets/images
        assets_dir = os.path.join("wiki", "assets", "images")
        if os.path.exists(assets_dir):
            for file in os.listdir(assets_dir):
                if file.startswith(f"source-{filename_base}-fig{num}."):
                    fig_links.append(f"![[{file}]]")
                    break
                    
    # 2. Look for tables: e.g. "Table 1", "Tabel 4"
    tab_mentions = re.findall(r"\b(?:Table|Tabel)\s+(\d+)", content, re.IGNORECASE)
    tab_links = []
    seen_tabs = set()
    for num in tab_mentions:
        if num in seen_tabs:
            continue
        seen_tabs.add(num)
        
        # Check if the experiments subpage exists and has the table header
        experiments_name = f"source-{filename_base}-experiments" + ("-id" if lang == "id" else "")
        experiments_dir = os.path.join("wiki", lang, "sources", filename_base)
        experiments_path = os.path.join(experiments_dir, f"{experiments_name}.md")
        
        if os.path.exists(experiments_path):
            with open(experiments_path, "r", encoding="utf-8") as f:
                exp_content = f.read()
            # Look for header matching "### Table {num} (Page" or similar
            match = re.search(fr"###\s+Table\s+{num}\s+\(Page\s+(\d+)\)", exp_content, re.IGNORECASE)
            if match:
                page_num = match.group(1)
                tab_links.append(f"![[{experiments_name}#Table {num} (Page {page_num})]]")
                
    # 3. Append to content
    append_str = ""
    if fig_links:
        header = "### Supporting Figures" if lang == "en" else "### Gambar Pendukung"
        append_str += f"\n\n{header}\n\n" + "\n\n".join(fig_links)
    if tab_links:
        header = "### Supporting Tables" if lang == "en" else "### Tabel Pendukung"
        append_str += f"\n\n{header}\n\n" + "\n\n".join(tab_links)
        
    return content + append_str


def sanitize_concept_name(name: str) -> str:
    """Sanitizes a concept/entity name to keep only alphanumeric characters and hyphens,
    ensuring safe file creation on all operating systems.
    """
    # Replace illegal/special chars with spaces, then strip and convert to kebab-case
    cleaned = re.sub(r"[\\/:*?\"<>|\[\]#]", " ", name)
    cleaned = re.sub(r"\s+", "-", cleaned.strip().lower())
    cleaned = re.sub(r"-+", "-", cleaned)
    return cleaned.strip("-")


def find_existing_concept_domain(c_name: str, base_dir: str) -> Optional[str]:
    """Scans all subfolders in the base directory to see if a page already exists.
    If found, returns the domain directory name (e.g. 'ai', 'finance').
    """
    if not os.path.exists(base_dir):
        return None
    for domain_dir in os.listdir(base_dir):
        domain_path = os.path.join(base_dir, domain_dir)
        if os.path.isdir(domain_path):
            if os.path.exists(os.path.join(domain_path, f"{c_name}.md")):
                return domain_dir
    return None


def get_known_concept_names(concepts_dir: str) -> set:
    """Scans all existing concept pages from a vault concepts directory to build a set of known concept names."""
    known = set()
    if not os.path.exists(concepts_dir):
        return known
    for root, dirs, files in os.walk(concepts_dir):
        for file in files:
            if file.endswith(".md"):
                name = os.path.splitext(file)[0]
                known.add(name)
                # Also index the base concept name if it's an ID page ending with -id
                if name.endswith("-id"):
                    known.add(name[:-3])
    return known


def reclassify_concepts_and_entities(concepts: list, entities: list, concepts_dir: str) -> tuple:
    """Classification safeguard to automatically move abstract concepts from entities to concepts."""
    known_concepts = get_known_concept_names(concepts_dir)
    
    # Keywords indicating a concept
    CONCEPT_KEYWORDS = {
        "formula", "drift", "disconnect", "variance", "index", "ratio", 
        "theorem", "accounting", "hypothesis", "bias", "fallacy", 
        "anomaly", "effect", "premium", "factor", "pricing", "multiplier",
        "correlation", "causality", "law", "illusion", "puzzle", "syndrome",
        "paradox", "model", "valuation", "pricing", "efficiency"
    }
    
    new_concepts = list(concepts)
    new_entities = []
    
    for entity in entities:
        name = entity.get("name", "")
        # Lowercase and split name by hyphen to check for keywords
        name_parts = set(name.lower().split("-"))
        
        category = entity.get("category", "").lower()
        
        # We classify as concept if:
        # 1. It is already known as a concept in the vault
        # 2. Or it contains any concept keyword AND is not explicitly a person
        is_concept = (
            name in known_concepts 
            or (not name_parts.isdisjoint(CONCEPT_KEYWORDS) and category != "person")
        )
        
        if is_concept:
            print(f"ℹ️ Reclassifying entity '{name}' to concept based on keyword or vault scan.")
            concept_obj = entity.copy()
            # Ensure it has the fields required by concepts
            if "description_en" not in concept_obj:
                concept_obj["description_en"] = entity.get("content_en") or entity.get("description_en") or ""
            if "description_id" not in concept_obj:
                concept_obj["description_id"] = entity.get("content_id") or entity.get("description_id") or ""
            if "content_en" not in concept_obj:
                concept_obj["content_en"] = entity.get("content_en") or ""
            if "content_id" not in concept_obj:
                concept_obj["content_id"] = entity.get("content_id") or ""
            if "relations" not in concept_obj:
                concept_obj["relations"] = []
            new_concepts.append(concept_obj)
        else:
            new_entities.append(entity)
            
    return new_concepts, new_entities

def cleanup_duplicate_empty_files():
    """Finds the vault root (containing .obsidian), scans for 0-byte markdown files,
    and deletes them if they conflict with any compiled wiki concepts or entities.
    """
    vault_root = None
    # Start searching up from current script folder
    curr = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    while True:
        if os.path.exists(os.path.join(curr, ".obsidian")):
            vault_root = curr
            break
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
        
    if not vault_root:
        return
        
    import sqlite3
    db_path = os.path.join("wiki", ".search_index.db")
    if not os.path.exists(db_path):
        return
        
    valid_names = set()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_metadata';")
        if cursor.fetchone():
            cursor.execute("SELECT name, title FROM wiki_metadata;")
            for name, title in cursor.fetchall():
                if name:
                    valid_names.add(name.lower())
                    valid_names.add(name.lower().replace("-", " "))
                    valid_names.add(name.lower().replace(" ", "-"))
                if title:
                    valid_names.add(title.lower())
                    valid_names.add(title.lower().replace("-", " "))
                    valid_names.add(title.lower().replace(" ", "-"))
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to query database for cleanup: {e}")
        return

    deleted = []
    # Scan the vault root recursively, ignoring system, raw, scratch, and config directories
    ignore_dirs = {".git", ".obsidian", ".pytest_cache", ".superpowers", ".agents", "raw", "scripts", "docs", "scratch"}
    for root, dirs, files in os.walk(vault_root):
        # Modify dirs in-place to avoid walking into ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for f in files:
            if f.endswith(".md"):
                filepath = os.path.join(root, f)
                try:
                    if os.path.isfile(filepath) and os.path.getsize(filepath) == 0:
                        name_no_ext = os.path.splitext(f)[0].lower()
                        name_clean = name_no_ext.replace("-id", "")
                        if (name_no_ext in valid_names or 
                            name_clean in valid_names or 
                            name_no_ext.replace(" ", "-") in valid_names or 
                            name_no_ext.replace("-", " ") in valid_names):
                            os.remove(filepath)
                            deleted.append(os.path.relpath(filepath, vault_root))
                except Exception:
                    pass
                        
    if deleted:
        print(f"🧹 Safeguard: Cleaned up {len(deleted)} duplicate 0-byte file(s) from vault: {', '.join(deleted)}")


def main():
    force = False
    metadata_file = None
    args = sys.argv[1:]
    
    # Check for --force / -f / force
    if "--force" in args:
        force = True
        args.remove("--force")
    if "-f" in args:
        force = True
        args.remove("-f")
    if "force" in args:
        force = True
        args.remove("force")
        
    # Check for --metadata / -m
    if "--metadata" in args:
        try:
            idx = args.index("--metadata")
            metadata_file = args[idx + 1]
            args.pop(idx + 1)
            args.pop(idx)
        except IndexError:
            print("Error: --metadata option requires a file path argument.")
            sys.exit(1)
    elif "-m" in args:
        try:
            idx = args.index("-m")
            metadata_file = args[idx + 1]
            args.pop(idx + 1)
            args.pop(idx)
        except IndexError:
            print("Error: -m option requires a file path argument.")
            sys.exit(1)
            
    if not args or len(args) < 1:
        print("Usage: python scripts/ingest.py <path-to-raw-file> [--force] [--metadata <path-to-json>]")
        sys.exit(1)
        
    raw_path = args[0]
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
    
    source_filename = project_relative_path(raw_path)
        
    duplicate_path = check_duplicate(checksum, source_filename)
    if duplicate_path and not force:
        print(f"Source asset already compiled! Checksum/Filename match: {duplicate_path}")
        print("Skipping ingestion to prevent duplication. Use --force to override.")
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
    # Image and table extraction is disabled.
            
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

    data = None
    if metadata_file:
        print(f"Loading pre-generated cognitive metadata from: {metadata_file}")
        try:
            import json
            with open(metadata_file, "r", encoding="utf-8") as mf:
                data = json.load(mf)
        except Exception as e:
            print(f"Error: Failed to load metadata from '{metadata_file}': {e}")
            sys.exit(1)
    else:
        try:
            data = process_deepseek(raw_content, os.path.basename(raw_path), version=raw_version)
        except Exception as e:
            print(f"DeepSeek compilation failed: {e}. Falling back to offline pipeline...")
            data = None

    if not data:
        from ingest.local_fallback import PRE_TRANSLATED_SUMMARIES
        if filename_base not in PRE_TRANSLATED_SUMMARIES and not os.environ.get("TESTING"):
            print("\n" + "!" * 80)
            print("⚠️  API KEY MISSING OR OFFLINE - COGNITIVE ACTION REQUIRED BY AGENT")
            print("   The document is UNRECOGNIZED offline and no LLM API key is configured.")
            print("   Exiting with Code 2 to signal your AI agent (Antigravity) to handle the ")
            print("   cognitive ingestion steps (chunk reading, summarization, relations) directly.")
            print("!" * 80 + "\n")
            sys.exit(2)
        data = process_offline(raw_content, filename_base, version=raw_version)
        
    current_date = datetime.now().strftime("%Y-%m-%d")
    source_name_en = f"source-{filename_base}"
    source_name_id = f"source-{filename_base}-id"
    
    en_src_dir = os.path.join(EN_DIR, "sources")
    id_src_dir = os.path.join(ID_DIR, "sources")
    os.makedirs(en_src_dir, exist_ok=True)
    os.makedirs(id_src_dir, exist_ok=True)
        
    source_path_en = os.path.join(en_src_dir, f"{source_name_en}.md")
    source_path_id = os.path.join(id_src_dir, f"{source_name_id}.md")
    
    created_concepts = []
    created_entities = []
    concepts = data.get("concepts", []) or []
    entities = data.get("entities", []) or []
    
    # Pre-sanitize all concept and entity names, as well as relation targets
    for c in concepts:
        c["name"] = sanitize_concept_name(c.get("name") or c.get("title_en", ""))
        for r in c.get("relations", []) or []:
            if "target" in r:
                r["target"] = sanitize_concept_name(r["target"])
    for e in entities:
        e["name"] = sanitize_concept_name(e.get("name") or e.get("title_en", ""))

    
    # Classification safeguard to reclassify abstract concepts that LLM put under entities
    concepts, entities = reclassify_concepts_and_entities(concepts, entities, os.path.join(EN_DIR, "concepts"))
    
    # Detect cross-references early so we can build the summary tables on source pages
    print("Detecting cross-references with existing vault concepts...")
    en_concepts_dir = os.path.join(EN_DIR, "concepts")
    cross_refs = detect_cross_references(concepts, source_name_en, en_concepts_dir, lang="en")
    
    # Read existing concepts from the vault to identify which concepts are core vs related
    existing_concepts = read_concept_pages(en_concepts_dir)
    id_concepts_dir = os.path.join(ID_DIR, "concepts")
    existing_concepts_id = read_concept_pages(id_concepts_dir)
    
    vault_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    existing_en_pages, existing_id_pages = scan_existing_pages(vault_root_dir)
    
    new_en_pages = {source_name_en.lower()}
    new_id_pages = {source_name_id.lower()}
    for c in concepts:
        c_name = c.get("name")
        if c_name:
            new_en_pages.add(c_name.lower())
            new_id_pages.add(resolve_translation_target(c_name, "id").lower())
    for e in entities:
        e_name = e.get("name")
        if e_name:
            new_en_pages.add(e_name.lower())
            new_id_pages.add(resolve_translation_target(e_name, "id").lower())
            
    valid_en_pages = existing_en_pages | new_en_pages
    valid_id_pages = existing_id_pages | new_id_pages
    
    core_concepts = list(concepts)
    related_concept_names = set()
            
    # Group relations by target and populate related_concept_names
    relations_by_target = {}
    for c_name, rels in cross_refs.items():
        c_obj = next((x for x in concepts if x.get("name") == c_name), None)
        c_relations = list(rels)
        if c_obj and c_obj.get("relations"):
            c_relations.extend(c_obj.get("relations"))
            
        # Merge relations from existing concept pages in the vault
        if c_name in existing_concepts and existing_concepts[c_name].get("relations"):
            c_relations.extend(existing_concepts[c_name]["relations"])
            
        seen_keys = set()
        unique_relations = []
        for r in c_relations:
            target = r.get("target", "")
            if target:
                target = target.replace("[[", "").replace("]]", "").strip()
                r["target"] = target
                r["concept_name"] = c_name
                rel_type = r.get("type", "")
                key = (target, rel_type)
                if key not in seen_keys:
                    seen_keys.add(key)
                    unique_relations.append(r)
                    
        for r in unique_relations:
            target = r["target"]
            related_concept_names.add(target)
            relations_by_target.setdefault(target, []).append(r)
                
    # Exclude core concepts from related connections list
    core_names = {c.get("name") for c in core_concepts}
    related_concept_names = {r for r in related_concept_names if r not in core_names}

    # Format Core Concepts (English)
    core_concepts_section = "## Core Concepts\n\n"
    if core_concepts:
        core_bullets = []
        for c in core_concepts:
            c_name = c.get("name")
            c_title = c.get("title_en") or c_name.replace("-", " ").title()
            if c_name:
                core_bullets.append(f"- **{c_title}:** [[{c_name}]]")
        core_concepts_section += "\n".join(core_bullets)
    else:
        core_concepts_section += "*No core concepts defined.*"

    # Format Related Work Connections (English)
    related_work_section = "## Related Work Connections\n\n"
    if related_concept_names:
        related_bullets = []
        for target in sorted(related_concept_names):
            rels = relations_by_target.get(target, [])
            
            source_page = get_concept_primary_source(target, existing_concepts)
            source_exists = source_page and (source_page.lower() in valid_en_pages)
            if source_exists:
                citation = extract_source_citation(source_page)
                cit_prefix = f"[[{source_page}|{citation}]]"
            else:
                if source_page:
                    cit_prefix = extract_source_citation(source_page)
                elif target.startswith("source-"):
                    citation = extract_source_citation(target)
                    if target.lower() in valid_en_pages:
                        cit_prefix = f"[[{target}|{citation}]]"
                    else:
                        cit_prefix = citation
                else:
                    cit_prefix = target.replace("-", " ").title()
                    
            target_exists = target.lower() in valid_en_pages
            
            if rels:
                rel_strs = []
                for r in rels:
                    rel_type = r.get("type", "")
                    claim = r.get("claim_en") or r.get("claim", "")
                    rel_str = f"({rel_type}): {claim}"
                    if rel_str not in rel_strs:
                        rel_strs.append(rel_str)
                if target.startswith("source-"):
                    related_bullets.append(f"- **{cit_prefix}** — " + "; ".join(rel_strs))
                elif target_exists:
                    related_bullets.append(f"- **{cit_prefix}** — " + "; ".join(rel_strs) + f" (🌐 [[{target}]])")
                else:
                    related_bullets.append(f"- **{cit_prefix}** — " + "; ".join(rel_strs) + f" (🌐 {target.replace('-', ' ').title()})")
            else:
                if target.startswith("source-"):
                    related_bullets.append(f"- **{cit_prefix}**")
                elif target_exists:
                    related_bullets.append(f"- **{cit_prefix}** (🌐 [[{target}]])")
                else:
                    related_bullets.append(f"- **{cit_prefix}** (🌐 {target.replace('-', ' ').title()})")
        related_work_section += "\n".join(related_bullets)
    else:
        related_work_section += "*No related work connections.*"

    # Format Core Concepts (Indonesian)
    core_concepts_section_id = "## Konsep Inti\n\n"
    if core_concepts:
        core_bullets_id = []
        for c in core_concepts:
            c_name = c.get("name")
            c_title = c.get("title_id") or c.get("title_en") or c_name.replace("-", " ").title()
            if c_name:
                target_id = resolve_translation_target(c_name, "id")
                core_bullets_id.append(f"- **{c_title}:** [[{target_id}]]")
        core_concepts_section_id += "\n".join(core_bullets_id)
    else:
        core_concepts_section_id += "*Tidak ada konsep inti yang didefinisikan.*"

    # Format Related Work Connections (Indonesian)
    related_work_section_id = "## Koneksi Penelitian Terkait (Related Work Connections)\n\n"
    if related_concept_names:
        related_bullets_id = []
        for target in sorted(related_concept_names):
            rels = relations_by_target.get(target, [])
            target_id = resolve_translation_target(target, "id")
            
            source_page = get_concept_primary_source(target, existing_concepts)
            source_page_id = resolve_translation_target(source_page, "id") if source_page else None
            
            source_exists = source_page_id and (source_page_id.lower() in valid_id_pages)
            if source_exists:
                citation = extract_source_citation(source_page)
                cit_prefix = f"[[{source_page_id}|{citation}]]"
            else:
                if source_page:
                    cit_prefix = extract_source_citation(source_page)
                elif target.startswith("source-"):
                    citation = extract_source_citation(target)
                    target_id_page = resolve_translation_target(target, "id")
                    if target_id_page.lower() in valid_id_pages:
                        cit_prefix = f"[[{target_id_page}|{citation}]]"
                    else:
                        cit_prefix = citation
                else:
                    cit_prefix = target.replace("-", " ").title()
                    
            target_id_exists = target_id.lower() in valid_id_pages
            
            if rels:
                rel_strs = []
                for r in rels:
                    rel_type = r.get("type", "")
                    rel_type_id = {"supports": "mendukung", "contradicts": "bertentangan", "contrasting": "bertentangan", "extends": "memperluas"}.get(rel_type, rel_type)
                    
                    claim = r.get("claim_id")
                    if not claim:
                        concept_name = r.get("concept_name")
                        if concept_name:
                            concept_name_id = resolve_translation_target(concept_name, "id")
                            if concept_name_id in existing_concepts_id:
                                id_rels = existing_concepts_id[concept_name_id].get("relations", [])
                                target_id_clean = resolve_translation_target(r.get("target", ""), "id")
                                for id_r in id_rels:
                                    id_target_clean = id_r.get("target", "").replace("[[", "").replace("]]", "").strip()
                                    if id_target_clean == target_id_clean and id_r.get("type") == rel_type:
                                        claim = id_r.get("claim")
                                        break
                                        
                    if not claim:
                        claim = r.get("claim_en") or r.get("claim", "")
                        
                    rel_str = f"({rel_type_id}): {claim}"
                    if rel_str not in rel_strs:
                        rel_strs.append(rel_str)
                if target.startswith("source-"):
                    related_bullets_id.append(f"- **{cit_prefix}** — " + "; ".join(rel_strs))
                elif target_id_exists:
                    related_bullets_id.append(f"- **{cit_prefix}** — " + "; ".join(rel_strs) + f" (🌐 [[{target_id}]])")
                else:
                    target_display = target_id.replace("-", " ").title()
                    related_bullets_id.append(f"- **{cit_prefix}** — " + "; ".join(rel_strs) + f" (🌐 {target_display})")
            else:
                if target.startswith("source-"):
                    related_bullets_id.append(f"- **{cit_prefix}**")
                elif target_id_exists:
                    related_bullets_id.append(f"- **{cit_prefix}** (🌐 [[{target_id}]])")
                else:
                    target_display = target_id.replace("-", " ").title()
                    related_bullets_id.append(f"- **{cit_prefix}** (🌐 {target_display})")
        related_work_section_id += "\n".join(related_bullets_id)
    else:
        related_work_section_id += "*Tidak ada koneksi penelitian terkait.*"

    entity_links_en = [f"[[{e.get('name')}]]" for e in entities if e.get('name')]
    entity_links_id = [f"[[{resolve_translation_target(e.get('name'), 'id')}]]" for e in entities if e.get('name')]
    
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
    if data.get("tags"):
        src_fm_en["tags"] = data["tags"]

    src_fm_id = {
        "type": "source",
        "source_file": source_filename,
        "sha256": checksum,
        "created": current_date,
        "updated": current_date,
        "translation": f"[[{source_name_en}]]",
        "tags": ["ingested", filename_base]
    }
    if data.get("tags"):
        src_fm_id["tags"] = data["tags"]

    authors = data.get("authors") or ""
    affiliation = data.get("affiliation") or ""
    published = data.get("published") or ""
    code = data.get("code") or ""

    if data.get("custom_body_en"):
        body_to_format = data["custom_body_en"]
        split_pattern = r'^## (?:Related Work Connections|Koneksi Penelitian Terkait|Linked Entities|Entitas Terkait|Cross-References|Referensi Silang|Core Concepts|Konsep Inti)'
        match = re.search(split_pattern, body_to_format, re.MULTILINE)
        if match:
            base_body_en = body_to_format[:match.start()].strip()
        else:
            base_body_en = body_to_format.strip()
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
        base_body_en = f"{metadata_header}\n---\n\n{summary_en.strip()}"

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
        f"{base_body_en}\n\n"
        f"---\n\n"
        f"{core_concepts_section}\n\n"
        f"{related_work_section}\n\n"
        f"{linked_entities_section}"
    )

    write_wiki_page(source_path_en, src_fm_en, src_body_en)

    if data.get("custom_body_id"):
        body_to_format_id = data["custom_body_id"]
        split_pattern = r'^## (?:Related Work Connections|Koneksi Penelitian Terkait|Linked Entities|Entitas Terkait|Cross-References|Referensi Silang|Core Concepts|Konsep Inti)'
        match = re.search(split_pattern, body_to_format_id, re.MULTILINE)
        if match:
            base_body_id = body_to_format_id[:match.start()].strip()
        else:
            base_body_id = body_to_format_id.strip()
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
        base_body_id = f"{metadata_header_id}\n---\n\n{summary_id.strip()}"

    linked_entities_section_id = "## Entitas Terkait\n\n"
    if entity_links_id:
        entity_bullets_id = []
        for e in entities:
            e_name = e.get("name")
            if e_name:
                target_id = resolve_translation_target(e_name, "id")
                entity_bullets_id.append(f"- [[{target_id}]]")
        linked_entities_section_id += "\n".join(entity_bullets_id)
    else:
        linked_entities_section_id += "*Tidak ada entitas terkait.*"

    src_body_id = (
        f"{base_body_id}\n\n"
        f"---\n\n"
        f"{core_concepts_section_id}\n\n"
        f"{related_work_section_id}\n\n"
        f"{linked_entities_section_id}\n\n"
        f"---\n\n"
        f"## Padanan Bahasa Inggris\n\n"
        f"- [[{source_name_en}]] (Catatan Bahasa Inggris)"
    )

    write_wiki_page(source_path_id, src_fm_id, src_body_id)


    
    print("Scanning vault for wikilink normalization...")
    vault_pages = scan_vault_pages_db()
    en_link_map = build_link_map(vault_pages, concepts, entities, "en")
    id_link_map = build_link_map(vault_pages, concepts, entities, "id")
    print(f"  Built EN link map ({len(en_link_map)} entries), ID link map ({len(id_link_map)} entries)")
    
    # Print summary of detected relations
    all_detected_relations = []  # Collect for source page summary
    for c_name, rels in cross_refs.items():
        if rels:
            print(f"  Found {len(rels)} cross-reference(s) for concept '{c_name}'")
            all_detected_relations.extend([(c_name, r) for r in rels])
    
    for c in concepts:
        c_name_en = c.get("name")
        c_name_id = resolve_translation_target(c_name_en, "id")
        
        # Check if the concept already exists under any domain subfolder in the vault
        existing_domain = find_existing_concept_domain(c_name_en, os.path.join(EN_DIR, "concepts"))
        c_domain = c.get("domain", "other").lower()
        if existing_domain:
            print(f"ℹ️ Found existing concept '{c_name_en}' in domain '{existing_domain}'. Overriding parsed domain '{c_domain}'.")
            c_domain = existing_domain
            c["domain"] = c_domain

        c_tags = c.get("tags", [])
        if "ingest" not in c_tags:
            c_tags.append("ingest")
            
        c_path_en = os.path.join(EN_DIR, "concepts", c_domain, f"{c_name_en}.md")
        c_path_id = os.path.join(ID_DIR, "concepts", c_domain, f"{c_name_id}.md")
        
        see_also_en = [f"- [[{x.get('name')}]]" for x in concepts if x.get('name') != c_name_en and x.get('name')]
        see_also_id = [f"- [[{resolve_translation_target(x.get('name'), 'id')}]]" for x in concepts if x.get('name') != c_name_en and x.get('name')]
        
        c_content_en = c.get('content_en') or c.get('description_en') or ''
        normalized_content_en = normalize_wikilinks(c_content_en, en_link_map)
        normalized_content_en = auto_link_media_and_tables(normalized_content_en, filename_base, "en")
        
        # Build relations for this concept
        c_relations = cross_refs.get(c_name_en, []) + (c.get("relations", []) or [])
        # Deduplicate by target+type
        seen_rel = set()
        unique_relations = []
        for rel in c_relations:
            rel_type = rel.get("type", "")
            if rel_type in {"contrasting", "contrasts"}:
                rel_type = "contradicts"
                rel["type"] = "contradicts"
            key = (rel.get("target", ""), rel_type)
            if key not in seen_rel:
                seen_rel.add(key)
                # Ensure source citation is populated for every relation in the English run
                if not rel.get("source"):
                    rel["source"] = f"[[{source_name_en}]]"
                unique_relations.append(rel)
        
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
        # Only put relations to existing/new pages in frontmatter to satisfy the linter
        valid_fm_relations = [r for r in unique_relations if r.get("target", "").lower() in valid_en_pages]
        if valid_fm_relations:
            c_fm_en["relations"] = valid_fm_relations
        
        # Build cross-references section for concept body
        cross_ref_en = ""
        if unique_relations:
            supports = [r for r in unique_relations if r.get("type") == "supports"]
            contradicts = [r for r in unique_relations if r.get("type") in {"contradicts", "contrasting"}]
            extends = [r for r in unique_relations if r.get("type") == "extends"]
            cross_ref_en = "\n\n## Cross-References\n"
            for heading, items in [("Supports", supports), ("Contradicts", contradicts), ("Extends", extends)]:
                if items:
                    cross_ref_en += f"\n### {heading}\n\n"
                    for r in items:
                        claim = r.get("claim_en", "")
                        source = r.get("source", f"[[{source_name_en}]]")
                        target = r.get("target", "")
                        if target.lower() in valid_en_pages:
                            target_link = f"[[{target}]]"
                        else:
                            target_link = target.replace("-", " ").title()
                        
                        source_clean = source.replace("[[", "").replace("]]", "").strip()
                        if source_clean.lower() in valid_en_pages:
                            source_link = source
                        else:
                            source_link = extract_source_citation(source_clean)
                            
                        cross_ref_en += f"- **{target_link}**: {claim} \u2014 {source_link}\n"
        
        see_also_en_section = f"\n\n## See Also\n\n" + "\n".join(see_also_en) if see_also_en else ""
        c_body_en = f"# {c.get('title_en', c_name_en.replace('-', ' ').title())}\n\n{normalized_content_en}{cross_ref_en}{see_also_en_section}\n\n## Sources\n\n- [[{source_name_en}]]"
        merge_or_write_page(c_path_en, c_fm_en, c_body_en)
        created_concepts.append(c_name_en)
        
        c_title_id = sanitize_indonesian_latex(c.get('title_id') or c.get('title_en', c_name_en.replace('-', ' ').title()))
        c_content_id = sanitize_indonesian_latex(c.get('content_id') or c.get('description_id') or '')
        c_description_id = sanitize_indonesian_latex(c.get('description_id') or c.get('description_en', ''))
        
        normalized_content_id = normalize_wikilinks(c_content_id, id_link_map)
        normalized_content_id = auto_link_media_and_tables(normalized_content_id, filename_base, "id")
        
        # Build ID relations (same relations, translated targets and localized sources)
        id_relations = []
        for rel in unique_relations:
            id_rel = rel.copy()
            target = rel.get("target", "")
            id_rel["target"] = resolve_translation_target(target, "id")
            
            # Localize relation source citation to Indonesian source note version
            id_source = rel.get("source", f"[[{source_name_en}]]")
            source_clean = id_source.replace("[[", "").replace("]]", "").strip()
            if source_clean.startswith("source-"):
                source_id = resolve_translation_target(source_clean, "id")
            else:
                source_id = resolve_translation_target(f"source-{source_clean}", "id")
            id_rel["source"] = f"[[{source_id}]]"
            
            id_relations.append(id_rel)
        
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
        # Only put relations to existing/new pages in frontmatter to satisfy the linter
        valid_fm_relations_id = [r for r in id_relations if r.get("target", "").lower() in valid_id_pages]
        if valid_fm_relations_id:
            c_fm_id["relations"] = valid_fm_relations_id
        
        # Build cross-references section for Indonesian concept body
        cross_ref_id = ""
        if id_relations:
            supports_id = [r for r in id_relations if r.get("type") == "supports"]
            contradicts_id = [r for r in id_relations if r.get("type") in {"contradicts", "contrasting"}]
            extends_id = [r for r in id_relations if r.get("type") == "extends"]
            cross_ref_id = "\n\n## Referensi Silang\n"
            for heading, items in [("Mendukung", supports_id), ("Bertentangan", contradicts_id), ("Memperluas", extends_id)]:
                if items:
                    cross_ref_id += f"\n### {heading}\n\n"
                    for r in items:
                        claim = r.get("claim_id")
                        if not claim:
                            concept_name = r.get("concept_name")
                            if concept_name:
                                concept_name_id = resolve_translation_target(concept_name, "id")
                                if concept_name_id in existing_concepts_id:
                                    id_rels = existing_concepts_id[concept_name_id].get("relations", [])
                                    target_id_clean = r.get("target", "")
                                    for id_r in id_rels:
                                        id_target_clean = id_r.get("target", "").replace("[[", "").replace("]]", "").strip()
                                        if id_target_clean == target_id_clean and id_r.get("type") == rel_type:
                                            claim = id_r.get("claim")
                                            break
                        if not claim:
                            claim = r.get("claim_en") or r.get("claim", "")
                            
                        target_id = r.get("target", "")
                        if target_id.lower() in valid_id_pages:
                            target_link = f"[[{target_id}]]"
                        else:
                            target_link = target_id.replace("-", " ").title()
                            
                        source = r.get("source", f"[[{source_name_id}]]")
                        source_clean = source.replace("[[", "").replace("]]", "").strip()
                        if source_clean.lower() in valid_id_pages:
                            source_link = source
                        else:
                            source_link = extract_source_citation(source_clean)
                            
                        cross_ref_id += f"- **{target_link}**: {claim} \u2014 {source_link}\n"
        
        see_also_id_section = f"\n\n## Lihat Juga\n\n" + "\n".join(see_also_id) if see_also_id else ""
        c_body_id = f"# {c_title_id}\n\n{normalized_content_id}{cross_ref_id}{see_also_id_section}\n\n## Sumber\n\n- [[{source_name_id}]]"    
        merge_or_write_page(c_path_id, c_fm_id, c_body_id)
        
    for e in entities:
        e_name_en = e.get("name")
        e_name_id = resolve_translation_target(e_name_en, "id")
        
        # Check if the entity already exists under any domain subfolder in the vault
        existing_domain = find_existing_concept_domain(e_name_en, os.path.join(EN_DIR, "entities"))
        e_domain = e.get("domain", "other").lower()
        if existing_domain:
            print(f"ℹ️ Found existing entity '{e_name_en}' in domain '{existing_domain}'. Overriding parsed domain '{e_domain}'.")
            e_domain = existing_domain
            e["domain"] = e_domain

        e_category = e.get("category", "other").lower()
        e_tags = e.get("tags", [])
        
        e_path_en = os.path.join(EN_DIR, "entities", e_domain, f"{e_name_en}.md")
        e_path_id = os.path.join(ID_DIR, "entities", e_domain, f"{e_name_id}.md")
        
        related_en = [f"- [[{x.get('name')}]]" for x in entities if x.get('name') != e_name_en and x.get('name')]
        related_id = [f"- [[{resolve_translation_target(x.get('name'), 'id')}]]" for x in entities if x.get('name') != e_name_en and x.get('name')]
        
        e_content_en = e.get('content_en') or e.get('description_en') or ''
        normalized_content_en = normalize_wikilinks(e_content_en, en_link_map)
        normalized_content_en = auto_link_media_and_tables(normalized_content_en, filename_base, "en")
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
        normalized_content_id = auto_link_media_and_tables(normalized_content_id, filename_base, "id")
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
        existing_log = ""
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, "r", encoding="utf-8") as lf:
                existing_log = lf.read()
        
        header_text = (
            "# Chronicle Log\n\n"
            "This is a chronological log of all operations (ingestion, queries, lint passes) "
            "performed on this personal LLM Wiki, with the latest entries at the top.\n\n"
            "---"
        )
        
        body_entries = []
        if existing_log:
            parts = existing_log.split("---")
            if len(parts) >= 2:
                body = "---".join(parts[1:]).strip()
                current_entry = []
                for line in body.split("\n"):
                    if line.strip().startswith("## ["):
                        if current_entry:
                            body_entries.append("\n".join(current_entry).strip())
                        current_entry = [line]
                    else:
                        if current_entry:
                            current_entry.append(line)
                if current_entry:
                    body_entries.append("\n".join(current_entry).strip())
                
        new_entry = log_line.strip()
        all_entries = [new_entry] + body_entries
        
        new_log_content = header_text + "\n\n" + "\n\n".join(all_entries) + "\n"
        with open(LOG_PATH, "w", encoding="utf-8") as lf:
            lf.write(new_log_content)
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
        
    # Run duplicate cleanup safeguard to prevent Obsidian link resolution conflicts
    try:
        cleanup_duplicate_empty_files()
    except Exception as e:
        print(f"Warning: Failed to run cleanup safeguard: {e}")
        
    print("\n🎉 Ingestion workflow finished successfully! 🎉")


if __name__ == "__main__":
    main()
