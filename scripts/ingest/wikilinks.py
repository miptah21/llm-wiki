"""Wikilinks module for scanning the wiki database and normalizing page links."""

import os
import re
import sqlite3
import logging
from typing import Dict, List, Any

# Setup logging
logger = logging.getLogger(__name__)

WIKI_DIR = "wiki"
DB_PATH = os.path.join(WIKI_DIR, ".search_index.db")


def scan_vault_pages_db() -> Dict[str, Dict[str, str]]:
    """Scans the database index instead of recursively reading disk files to build the mapping dict.
    Falls back to a physical file-system scan if the database does not exist.

    Returns:
        A dictionary mapping lowercase keys (title, clean titles, name) to {lang: filename}.
    """
    mapping: Dict[str, Dict[str, str]] = {}
    if not os.path.exists(DB_PATH):
        logger.info(f"Database file not found at '{DB_PATH}'. Falling back to physical file-system scan.")
        try:
            # Recursively scan WIKI_DIR
            for root, _, files in os.walk(WIKI_DIR):
                normalized_root = root.replace("\\", "/")
                if "/en" not in normalized_root and "/id" not in normalized_root:
                    continue
                for file in files:
                    if file.endswith(".md") and file != "index.md":
                        name = os.path.splitext(file)[0]
                        lang = "id" if "/id/" in normalized_root or normalized_root.endswith("/id") else "en"
                        name_lower = name.lower()
                        if name_lower not in mapping:
                            mapping[name_lower] = {}
                        mapping[name_lower][lang] = name
                        
                        # Attempt to parse title from the file
                        try:
                            filepath = os.path.join(root, file)
                            with open(filepath, "r", encoding="utf-8") as f:
                                head = f.read(1000)
                            
                            # Lazy import parser to avoid circular imports
                            from parser import parse_yaml_frontmatter
                            meta = parse_yaml_frontmatter(head)
                            if meta:
                                title = None
                                for line in head.split("\n"):
                                    if line.strip().startswith("# "):
                                        title = line.strip()[2:].replace("**", "").strip()
                                        break
                                if title:
                                    title_clean = title.replace("**", "").strip()
                                    for variant in [title.lower(), title_clean.lower()]:
                                        if variant not in mapping:
                                            mapping[variant] = {}
                                        mapping[variant][lang] = name
                        except Exception:
                            pass
        except Exception as e:
            logger.warning(f"Physical folder scan fallback failed: {e}")
        return mapping
        
    try:
        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.cursor()
            
            # Verify table exists first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_metadata';")
            if not cursor.fetchone():
                return mapping
                
            cursor.execute("SELECT name, lang, title, translation FROM wiki_metadata;")
            rows = cursor.fetchall()
            
            # Track translation pairs: {name: translation_name}
            translation_pairs: Dict[str, str] = {}
            
            for name, lang, title, translation in rows:
                lang = (lang or "").lower()
                name_lower = (name or "").lower()
                
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
        finally:
            conn.close()
    except Exception as e:
        logger.warning(f"Failed to fetch metadata cache from SQLite: {e}")
        
    return mapping


def build_link_map(vault_pages: Dict[str, Dict[str, str]], concepts: List[Dict[str, Any]], entities: List[Dict[str, Any]], target_lang: str) -> Dict[str, str]:
    """Constructs a link mapping dict for the target language.

    Args:
        vault_pages: The mapping dictionary returned by scan_vault_pages_db.
        concepts: List of concepts generated in the active ingestion run.
        entities: List of entities generated in the active ingestion run.
        target_lang: The destination language ('en' or 'id').

    Returns:
        A dictionary mapping lowercase terms/names to their target page file names.
    """
    link_map: Dict[str, str] = {}
    
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
        title_en = e.get("title_en") or en_name.replace("-", " ").title()
        title_id = e.get("title_id", "")
        
        link_map[en_name.lower()] = target
        link_map[title_en.lower()] = target
        link_map[title_en.lower().replace(" ", "-")] = target
        if title_id:
            link_map[title_id.lower()] = target
            link_map[title_id.lower().replace(" ", "-")] = target
            
    return link_map


def normalize_wikilinks(content: str, link_map: Dict[str, str]) -> str:
    """Normalizes wiki links in a document content string using the provided mapping.

    Args:
        content: The text containing wikilinks [[TargetPage]].
        link_map: The mapping dictionary to resolve targets.

    Returns:
        The text with resolved wikilinks.
    """
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
