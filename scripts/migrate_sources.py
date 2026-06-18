import os
import re
import sys
from datetime import datetime

# Add scripts directory to path to import local package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ingest.persistence import write_wiki_page, parse_yaml_frontmatter
from ingest.conflict_detector import read_concept_pages

WIKI_DIR = "wiki"
EN_DIR = os.path.join(WIKI_DIR, "en")
ID_DIR = os.path.join(WIKI_DIR, "id")

from typing import Optional

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
        sources_str = info.get("sources", "")
        found_sources = re.findall(r'\[\[(.*?)\]\]', sources_str)
        if found_sources:
            return found_sources[0]
    return None

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
        if row and row[0]:
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

def extract_section_content(content, header_names):
    lines = content.split("\n")
    section_lines = []
    in_section = False
    for line in lines:
        if line.strip().startswith("## "):
            h_name = line.strip()[3:].strip().lower()
            # Clean parenthetical notes, e.g. "Abstrak (Abstract)" -> "abstrak"
            h_name_clean = re.sub(r'\(.*?\)', '', h_name).strip()
            if any(target.lower() in h_name_clean for target in header_names):
                in_section = True
                continue
            elif in_section:
                break
        if in_section:
            section_lines.append(line)
    return "\n".join(section_lines).strip()

def migrate_source_page(filepath, lang="en"):
    filename = os.path.basename(filepath)
    source_name = os.path.splitext(filename)[0]
    
    # We want filename_base, e.g. "The Dividend Disconnect" from "source-The Dividend Disconnect"
    filename_base = source_name.replace("source-", "")
    if lang == "id" and filename_base.endswith("-id"):
        filename_base = filename_base[:-3]
        
    source_ref_en = f"source-{filename_base}"
    source_ref_id = f"source-{filename_base}-id"
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    fm = parse_yaml_frontmatter(content)
    if not fm or fm.get("type") != "source":
        return
        
    # Extract base body before any headers
    split_pattern = r'^## (?:Related Work Connections|Koneksi Penelitian Terkait|Linked Entities|Entitas Terkait|Cross-References|Referensi Silang|Core Concepts|Konsep Inti)'
    match = re.search(split_pattern, content, re.MULTILINE)
    if match:
        # We need to strip frontmatter from content to get base body, or write_wiki_page will format it again
        # Actually, write_wiki_page expects markdown_body WITHOUT the frontmatter!
        parts = content.split("---")
        body = "---".join(parts[2:]).strip() if len(parts) >= 3 else content
        # Now search split pattern in the body
        body_match = re.search(split_pattern, body, re.MULTILINE)
        if body_match:
            base_body = body[:body_match.start()].strip()
        else:
            base_body = body.strip()
    else:
        parts = content.split("---")
        base_body = "---".join(parts[2:]).strip() if len(parts) >= 3 else content

    base_body = base_body.strip()
    while base_body.endswith("---"):
        base_body = base_body[:-3].strip()

    # Get all entities from the old page body
    ent_block = extract_section_content(content, ["Linked Entities", "Entitas Terkait"])
    entity_names = re.findall(r'\[\[(.*?)\]\]', ent_block)
    entity_names = [e[:-3] if e.endswith("-id") else e for e in entity_names]
        
    # Get all concepts from the old page body
    con_block = extract_section_content(content, ["Related Work Connections", "Koneksi Penelitian Terkait", "Referensi Silang"])
    concept_names = re.findall(r'\[\[(.*?)\]\]', con_block)
    # Normalize: remove "-id" suffix if in ID
    concept_names = [c[:-3] if c.endswith("-id") else c for c in concept_names]
        
    # Read concepts from vault
    en_concepts_dir = os.path.join(EN_DIR, "concepts")
    existing_concepts = read_concept_pages(en_concepts_dir)
    
    core_concepts = []
    for c_en, info in existing_concepts.items():
        sources_str = info.get("sources", "")
        found_sources = re.findall(r'\[\[(.*?)\]\]', sources_str)
        if any(s in (source_ref_en, source_ref_id) for s in found_sources):
            core_concepts.append(c_en)

    related_concept_names = set()
    relations_by_target = {}
    preserved_lines = []
    
    # 1. Partition based on vault metadata and preserve non-concept lines
    if con_block:
        for line in con_block.split("\n"):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            if line_stripped.startswith("## ") or line_stripped in ("*No related work connections.*", "*Tidak ada koneksi penelitian terkait.*"):
                continue
            
            targets = re.findall(r'\[\[(.*?)\]\]', line_stripped)
            if not targets:
                preserved_lines.append(line_stripped)
                continue
                
            has_vault_concept = False
            for t in targets:
                t_clean = t[:-3] if t.endswith("-id") else t
                t_en = resolve_canonical_en_name(t_clean)
                if t_en in existing_concepts:
                    has_vault_concept = True
                    
            if has_vault_concept:
                for t in targets:
                    t_clean = t[:-3] if t.endswith("-id") else t
                    t_en = resolve_canonical_en_name(t_clean)
                    if t_en in existing_concepts:
                        info = existing_concepts[t_en]
                        sources_str = info.get("sources", "")
                        found_sources = re.findall(r'\[\[(.*?)\]\]', sources_str)
                        if any(s in (source_ref_en, source_ref_id) for s in found_sources):
                            if t_en not in core_concepts:
                                core_concepts.append(t_en)
                        else:
                            related_concept_names.add(t_en)
            else:
                preserved_lines.append(line_stripped)

    # 2. Extract relations of our core concepts
    for c_name in core_concepts:
        if c_name in existing_concepts:
            # We need to read the concept page file directly to get its relations list from frontmatter
            # (since read_concept_pages doesn't parse relations field fully, or does it? It parses frontmatter description and sources)
            # Actually, let's find the file path
            found_path = None
            for domain_dir in os.listdir(en_concepts_dir):
                dpath = os.path.join(en_concepts_dir, domain_dir)
                if os.path.isdir(dpath):
                    fpath = os.path.join(dpath, f"{c_name}.md")
                    if os.path.exists(fpath):
                        found_path = fpath
                        break
            if found_path:
                try:
                    with open(found_path, "r", encoding="utf-8") as cf:
                        cf_content = cf.read()
                    cf_fm = parse_yaml_frontmatter(cf_content)
                    relations = cf_fm.get("relations", [])
                    if isinstance(relations, list):
                        for r in relations:
                            if isinstance(r, dict):
                                target = r.get("target", "").replace("[[", "").replace("]]", "").strip()
                                if target:
                                    # Normalize target to remove -id if present
                                    target_norm = target[:-3] if target.endswith("-id") else target
                                    related_concept_names.add(target_norm)
                                    
                                    # Store relation info
                                    rel_info = {
                                        "target": target_norm,
                                        "type": r.get("type", ""),
                                        "claim_en": r.get("claim", "")
                                    }
                                    # For claim_id, check if there is an ID version of the concept page with ID relation
                                    cf_path_id = found_path.replace("\\en\\", "\\id\\").replace("/en/", "/id/").replace(f"{c_name}.md", f"{c_name}-id.md")
                                    claim_id = ""
                                    if os.path.exists(cf_path_id):
                                        try:
                                            with open(cf_path_id, "r", encoding="utf-8") as cf_id:
                                                cf_id_content = cf_id.read()
                                            cf_id_fm = parse_yaml_frontmatter(cf_id_content)
                                            id_relations = cf_id_fm.get("relations", [])
                                            for id_r in id_relations:
                                                if isinstance(id_r, dict) and id_r.get("target", "").replace("[[", "").replace("]]", "").strip().startswith(target_norm):
                                                    claim_id = id_r.get("claim", "")
                                                    break
                                        except Exception:
                                            pass
                                    rel_info["claim_id"] = claim_id or r.get("claim", "")
                                    relations_by_target.setdefault(target_norm, []).append(rel_info)
                except Exception as ex:
                    print(f"Error reading concept {c_name} relations: {ex}")

    # Remove core concepts from related list
    related_concept_names = {r for r in related_concept_names if r not in core_concepts}

    # Format output sections based on language
    if lang == "en":
        # Core Concepts
        core_sec = "## Core Concepts\n\n"
        if core_concepts:
            core_bullets = []
            for c in core_concepts:
                c_title = c.replace("-", " ").title()
                # Find display title if possible
                if c in existing_concepts:
                    # Parse title from h1
                    for domain_dir in os.listdir(en_concepts_dir):
                        dpath = os.path.join(en_concepts_dir, domain_dir)
                        if os.path.isdir(dpath):
                            fpath = os.path.join(dpath, f"{c}.md")
                            if os.path.exists(fpath):
                                with open(fpath, "r", encoding="utf-8") as cf:
                                    for line in cf:
                                        if line.strip().startswith("# "):
                                            c_title = line.strip()[2:].strip()
                                            break
                core_bullets.append(f"- **{c_title}:** [[{c}]]")
            core_sec += "\n".join(core_bullets)
        else:
            core_sec += "*No core concepts defined.*"

        # Related Work Connections
        rel_sec = "## Related Work Connections\n\n"
        
        related_bullets = []
        for target in sorted(related_concept_names):
            rels = relations_by_target.get(target, [])
            
            source_page = get_concept_primary_source(target, existing_concepts)
            if source_page:
                citation = extract_source_citation(source_page)
                cit_prefix = f"[[{source_page}|{citation}]]"
            else:
                if target.startswith("source-"):
                    citation = extract_source_citation(target)
                    cit_prefix = f"[[{target}|{citation}]]"
                else:
                    cit_prefix = target.replace("-", " ").title()
                    
            if rels:
                rel_strs = []
                for r in rels:
                    rel_type = r.get("type", "")
                    claim = r.get("claim_en", "")
                    rel_str = f"({rel_type}): {claim}"
                    if rel_str not in rel_strs:
                        rel_strs.append(rel_str)
                related_bullets.append(f"- **{cit_prefix}** — " + "; ".join(rel_strs) + f" (🌐 [[{target}]])")
            else:
                related_bullets.append(f"- **{cit_prefix}** (🌐 [[{target}]])")
                
        # Merge preserved lines and new wikilinked bullets
        all_rel_bullets = preserved_lines + related_bullets
        if all_rel_bullets:
            rel_sec += "\n".join(all_rel_bullets)
        else:
            rel_sec += "*No related work connections.*"

        # Linked Entities
        ent_sec = "## Linked Entities\n\n"
        if entity_names:
            ent_sec += "\n".join([f"- [[{e}]]" for e in entity_names])
        else:
            ent_sec += "*No linked entities.*"

        new_body = (
            f"{base_body}\n\n"
            f"---\n\n"
            f"{core_sec}\n\n"
            f"{rel_sec}\n\n"
            f"{ent_sec}"
        )
    else:
        # Indonesian
        core_sec = "## Konsep Inti\n\n"
        if core_concepts:
            core_bullets = []
            for c in core_concepts:
                c_title = c.replace("-", " ").title()
                # Find display title if possible
                if c in existing_concepts:
                    # Look up in ID concepts
                    id_concepts_dir = os.path.join(ID_DIR, "concepts")
                    for domain_dir in os.listdir(id_concepts_dir):
                        dpath = os.path.join(id_concepts_dir, domain_dir)
                        if os.path.isdir(dpath):
                            target_id = resolve_translation_target(c, "id")
                            fpath = os.path.join(dpath, f"{target_id}.md")
                            if os.path.exists(fpath):
                                with open(fpath, "r", encoding="utf-8") as cf:
                                    for line in cf:
                                        if line.strip().startswith("# "):
                                            c_title = line.strip()[2:].strip()
                                            break
                target_id = resolve_translation_target(c, "id")
                core_bullets.append(f"- **{c_title}:** [[{target_id}]]")
            core_sec += "\n".join(core_bullets)
        else:
            core_sec += "*Tidak ada konsep inti yang didefinisikan.*"

        # Related Work Connections
        rel_sec = "## Koneksi Penelitian Terkait (Related Work Connections)\n\n"
                    
        related_bullets = []
        for target in sorted(related_concept_names):
            rels = relations_by_target.get(target, [])
            target_id = resolve_translation_target(target, "id")
            
            source_page = get_concept_primary_source(target, existing_concepts)
            if source_page:
                citation = extract_source_citation(source_page)
                source_page_id = resolve_translation_target(source_page, "id")
                cit_prefix = f"[[{source_page_id}|{citation}]]"
            else:
                if target.startswith("source-"):
                    citation = extract_source_citation(target)
                    target_id_page = resolve_translation_target(target, "id")
                    cit_prefix = f"[[{target_id_page}|{citation}]]"
                else:
                    cit_prefix = target.replace("-", " ").title()
                    
            if rels:
                rel_strs = []
                for r in rels:
                    rel_type = r.get("type", "")
                    rel_type_id = {"supports": "mendukung", "contradicts": "bertentangan", "contrasting": "bertentangan", "extends": "memperluas"}.get(rel_type, rel_type)
                    claim = r.get("claim_id") or r.get("claim_en", "")
                    rel_str = f"({rel_type_id}): {claim}"
                    if rel_str not in rel_strs:
                        rel_strs.append(rel_str)
                related_bullets.append(f"- **{cit_prefix}** — " + "; ".join(rel_strs) + f" (🌐 [[{target_id}]])")
            else:
                related_bullets.append(f"- **{cit_prefix}** (🌐 [[{target_id}]])")
                
        all_rel_bullets = preserved_lines + related_bullets
        if all_rel_bullets:
            rel_sec += "\n".join(all_rel_bullets)
        else:
            rel_sec += "*Tidak ada koneksi penelitian terkait.*"

        # Linked Entities
        ent_sec = "## Entitas Terkait\n\n"
        if entity_names:
            ent_sec += "\n".join([f"- [[{resolve_translation_target(e, 'id')}]]" for e in entity_names])
        else:
            ent_sec += "*Tidak ada entitas terkait.*"

        new_body = (
            f"{base_body}\n\n"
            f"---\n\n"
            f"{core_sec}\n\n"
            f"{rel_sec}\n\n"
            f"{ent_sec}\n\n"
            f"---\n\n"
            f"## Padanan Bahasa Inggris\n\n"
            f"- [[{source_ref_en}]] (Catatan Bahasa Inggris)"
        )
        
    write_wiki_page(filepath, fm, new_body)
    print(f"Migrated: {filepath}")

def main():
    # Process EN sources
    en_sources_dir = os.path.join(EN_DIR, "sources")
    for root, dirs, files in os.walk(en_sources_dir):
        for file in files:
            if file.endswith(".md"):
                fpath = os.path.join(root, file)
                migrate_source_page(fpath, lang="en")
                
    # Process ID sources
    id_sources_dir = os.path.join(ID_DIR, "sources")
    for root, dirs, files in os.walk(id_sources_dir):
        for file in files:
            if file.endswith(".md"):
                fpath = os.path.join(root, file)
                migrate_source_page(fpath, lang="id")
                
if __name__ == "__main__":
    # Windows encoding safeguard for emoji/special character output
    if sys.platform.startswith("win"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except AttributeError:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    main()
