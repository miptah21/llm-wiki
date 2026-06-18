import os
import sys
import re
import hashlib
import sqlite3
from datetime import datetime
from typing import Tuple, Dict, Any, Optional

from pathlib import Path

# Ensure scripts folder is in sys.path so we can import parser
scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

from parser import parse_yaml_frontmatter, YAML_PATTERN

WIKI_DIR = "wiki"
DB_PATH = os.path.join(WIKI_DIR, ".search_index.db")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _is_within_path(child_path: str, parent_path: str) -> bool:
    try:
        child = Path(child_path).resolve()
        parent = Path(parent_path).resolve()
        return parent == child or parent in child.parents
    except (ValueError, RuntimeError, OSError):
        return False


def validate_safe_path(filepath: str) -> str:
    """Validates that the given filepath is safe and resides within the project workspace.

    Args:
        filepath (str): The path to validate.

    Returns:
        str: The absolute path of the validated file.

    Raises:
        ValueError: If the path resolves outside the project workspace.
    """
    abs_path = os.path.abspath(filepath)
    if not _is_within_path(abs_path, PROJECT_ROOT):
        raise ValueError(f"Security Alert: Path '{filepath}' resolves outside project workspace.")
    return abs_path


def project_relative_path(filepath: str) -> str:
    """Returns a project-relative path with portable forward slashes."""
    abs_path = validate_safe_path(filepath)
    return os.path.relpath(abs_path, PROJECT_ROOT).replace("\\", "/")


def calculate_sha256(filepath: str) -> str:
    """Calculates the SHA256 checksum of a file.

    Args:
        filepath (str): Path to the file.

    Returns:
        str: The SHA256 hex digest of the file.
    """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def check_duplicate(checksum: str, source_filename: str) -> str:
    """Checks the database to see if a file with the given checksum has already been ingested.

    Args:
        checksum (str): SHA256 checksum of the source file.
        source_filename (str): Name of the source file.

    Returns:
        str: The existing destination path of the wiki page if duplicate, else empty string.
    """
    if not os.path.exists(DB_PATH):
        return ""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Verify metadata table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wiki_metadata';")
        if not cursor.fetchone():
            return ""
        cursor.execute("SELECT path FROM wiki_metadata WHERE type='source' AND sha256 = ?;", (checksum,))
        row = cursor.fetchone()
        if row:
            return row[0]
    except Exception as e:
        print(f"Warning: Failed to query database for duplicate check: {e}")
    finally:
        if conn:
            conn.close()
    return ""


def update_db_metadata(
    filepath: str,
    name: str,
    lang: str,
    page_type: str,
    title: str,
    sha256: Optional[str] = None,
    translation: Optional[str] = None,
) -> None:
    """Updates the wiki metadata database with page attributes.

    Args:
        filepath (str): Destination path of the page.
        name (str): Normalized name/ID of the page.
        lang (str): Language code of the page (e.g., 'en', 'id').
        page_type (str): Type of the page (e.g., 'concept', 'entity').
        title (str): The display title of the page.
        sha256 (Optional[str]): SHA256 checksum of the source file, if any.
        translation (Optional[str]): Link to the translated version of the page, if any.
    """
    conn = None
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
    except Exception as e:
        print(f"Warning: Failed to update SQLite metadata table for {filepath}: {e}")
    finally:
        if conn:
            conn.close()


def parse_version_tuple(v_str: Optional[str]) -> Tuple[int, ...]:
    """Parses a version string (e.g. '1.2.3' or 'v2.0') into an integer tuple.

    Args:
        v_str (Optional[str]): Version string to parse.

    Returns:
        Tuple[int, ...]: Parsed version components, defaulting to (1, 0, 0) on failure/empty.
    """
    if not v_str:
        return (1, 0, 0)
    try:
        v_str = str(v_str).strip().lower().lstrip('v')
        parts = list(map(int, v_str.split(".")))
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts[:3])
    except Exception as e:
        print(f"Warning: Failed to parse version string '{v_str}', falling back to (1, 0, 0): {e}")
        return (1, 0, 0)


def format_frontmatter(metadata: Dict[str, Any]) -> str:
    """Formats a dictionary of metadata attributes into a YAML frontmatter block.

    Args:
        metadata (Dict[str, Any]): Dictionary of attributes.

    Returns:
        str: Formatted YAML frontmatter block.
    """
    lines = ["---"]
    for k, v in metadata.items():
        if k == "relations" and isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                if isinstance(item, dict):
                    target = item.get("target", "")
                    if not target.startswith("[[") and target:
                        target = f"[[{target}]]"
                    source = item.get("source", "")
                    if not source.startswith("[[") and source:
                        source = f"[[{source}]]"
                    
                    lines.append(f"  - target: \"{target}\"")
                    lines.append(f"    type: {item.get('type', '')}")
                    lines.append(f"    source: \"{source}\"")
                    claim_key = "claim_en" if metadata.get("lang") == "en" else "claim_id"
                    claim = item.get(claim_key) or item.get("claim_en") or item.get("claim") or ""
                    claim_escaped = claim.replace('"', '\\"')
                    lines.append(f"    claim: \"{claim_escaped}\"")
        elif isinstance(v, list):
            list_str = ", ".join([f'"{item}"' if "[[" in item else item for item in v])
            lines.append(f"{k}: [{list_str}]")
        else:
            if isinstance(v, str) and (":" in v or "[" in v or "{" in v):
                lines.append(f'{k}: "{v}"')
            else:
                lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def write_wiki_page(filepath: str, frontmatter_dict: Dict[str, Any], markdown_body: str) -> None:
    """Writes a wiki page file with frontmatter and body, updating search metadata.

    Args:
        filepath (str): Output path of the page.
        frontmatter_dict (Dict[str, Any]): Page frontmatter attributes.
        markdown_body (str): Markdown content of the page.

    Raises:
        ValueError: If filepath resolves outside the wiki root.
    """
    abs_filepath = validate_safe_path(filepath)
    if not _is_within_path(abs_filepath, WIKI_DIR):
        raise ValueError(f"Security Alert: Destination '{filepath}' is outside the wiki vault.")
    os.makedirs(os.path.dirname(abs_filepath), exist_ok=True)
    full_content = format_frontmatter(frontmatter_dict) + "\n\n" + markdown_body.strip() + "\n"
    with open(abs_filepath, "w", encoding="utf-8") as f:
        f.write(full_content)
    print(f"Created/Updated Page: {abs_filepath}")
    
    # Extract translation target link
    trans = frontmatter_dict.get("translation")
    if trans is None:
        trans = ""
    elif isinstance(trans, list):
         trans = trans[0] if trans else ""
    trans_clean = str(trans).replace("[[", "").replace("]]", "").strip()
    if trans_clean.lower() == "none":
        trans_clean = ""
    
    # Save to database cache
    name = os.path.splitext(os.path.basename(abs_filepath))[0]
    lang = frontmatter_dict.get("lang", "en")
    page_type = frontmatter_dict.get("type", "concept")
    # Extract h1 title from markdown body
    title = name
    for line in markdown_body.split("\n"):
        if line.strip().startswith("# "):
            title = line.strip()[2:].replace("**", "").strip()
            break
    
    update_db_metadata(abs_filepath, name, lang, page_type, title, frontmatter_dict.get("sha256"), trans_clean)


def get_page_path_by_name(name: str, lang: str) -> Optional[str]:
    """Retrieves the filepath of a page from the SQLite metadata database."""
    if not os.path.exists(DB_PATH):
        return None
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM wiki_metadata WHERE name = ? AND lang = ?;", (name, lang))
        row = cursor.fetchone()
        if row:
            return row[0]
    except Exception:
        pass
    finally:
        if conn:
            conn.close()
    return None


def find_concept_or_entity_path(name: str, lang: str) -> Optional[str]:
    """Finds the path of a concept or entity page, checking both SQLite and the filesystem."""
    path = get_page_path_by_name(name, lang)
    if path and os.path.exists(path):
        return path
    
    # Fallback to filesystem scan
    lang_dir = os.path.join(WIKI_DIR, lang)
    for folder in ["concepts", "entities"]:
        folder_path = os.path.join(lang_dir, folder)
        if os.path.exists(folder_path):
            for domain_dir in os.listdir(folder_path):
                domain_path = os.path.join(folder_path, domain_dir)
                if os.path.isdir(domain_path):
                    candidate = os.path.join(domain_path, f"{name}.md")
                    if os.path.exists(candidate):
                        return candidate
    return None


def update_target_reciprocal_relation(
    source_name: str,
    target_name: str,
    lang: str,
    rel_type: str,
    claim: str,
    source_ref: str,
) -> None:
    """Updates a target page to include a reciprocal relation back to the source page."""
    # Strip any wikilink brackets from names
    source_name = source_name.replace("[[", "").replace("]]", "").strip()
    target_name = target_name.replace("[[", "").replace("]]", "").strip()
    
    # Map reciprocal relation type
    recip_type_map = {
        "supports": "supported_by",
        "supported_by": "supports",
        "contradicts": "contradicted_by",
        "contrasting": "contradicted_by",
        "contradicted_by": "contradicts",
        "extends": "extended_by",
        "extended_by": "extends",
    }
    recip_type = recip_type_map.get(rel_type.lower(), rel_type)

    target_path = find_concept_or_entity_path(target_name, lang)
    if not target_path or not os.path.exists(target_path):
        return

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Warning: Failed to read target {target_path} for reciprocal link: {e}")
        return

    fm = parse_yaml_frontmatter(content)
    if not fm:
        return

    source_link = f"[[{source_name}]]"
    source_ref_clean = source_ref if source_ref.startswith("[[") else f"[[{source_ref}]]"

    # Add reciprocal relation to target's metadata list
    relations = fm.get("relations", []) or []
    if isinstance(relations, str):
        relations = []
    
    # Check if reciprocal relation already exists
    exists = False
    for r in relations:
        if isinstance(r, dict):
            r_target = r.get("target", "").replace("[[", "").replace("]]", "").strip()
            if r_target == source_name and r.get("type") == recip_type:
                exists = True
                break

    if not exists:
        print(f"Adding reciprocal relation: {target_name} --{recip_type}--> {source_name}")
        new_rel = {
            "target": source_link,
            "type": recip_type,
            "source": source_ref_clean,
        }
        claim_key = "claim_en" if lang == "en" else "claim_id"
        new_rel[claim_key] = claim
        relations.append(new_rel)
        fm["relations"] = relations

        # Re-write target page by merging frontmatter and core body
        match = YAML_PATTERN.match(content)
        body = content[match.end():].strip() if match else content.strip()
        
        merge_or_write_page(target_path, fm, body)


def merge_or_write_page(filepath: str, frontmatter_dict: Dict[str, Any], markdown_body: str) -> None:
    """Merges new content/metadata with an existing page, or writes a new page if it does not exist.

    Uses versioning logic to archive older page versions when version increases.

    Args:
        filepath (str): Target wiki page filepath.
        frontmatter_dict (Dict[str, Any]): Incoming metadata attributes.
        markdown_body (str): Incoming page body content.
    """
    abs_filepath = validate_safe_path(filepath)
    if not os.path.exists(abs_filepath):
        frontmatter_dict["version"] = frontmatter_dict.get("version") or "1.0.0"
        frontmatter_dict["status"] = frontmatter_dict.get("status") or "active"
        frontmatter_dict["valid_from"] = frontmatter_dict.get("valid_from") or datetime.now().strftime("%Y-%m-%d")
        write_wiki_page(abs_filepath, frontmatter_dict, markdown_body)
        return
        
    print(f"Page already exists, checking version/merging: {abs_filepath}")
    try:
        with open(abs_filepath, "r", encoding="utf-8") as f:
            existing_content = f.read()
    except Exception as e:
        print(f"Warning: Failed to read existing page {abs_filepath} for merging: {e}. Overwriting...")
        write_wiki_page(abs_filepath, frontmatter_dict, markdown_body)
        return
        
    existing_fm = parse_yaml_frontmatter(existing_content)
    existing_ver_str = existing_fm.get("version") or "1.0.0"
    incoming_ver_str = frontmatter_dict.get("version") or "1.0.0"
    
    existing_ver = parse_version_tuple(existing_ver_str)
    incoming_ver = parse_version_tuple(incoming_ver_str)
    
    if incoming_ver > existing_ver:
        filename_base = os.path.splitext(os.path.basename(abs_filepath))[0]
        dir_name = os.path.dirname(abs_filepath)
        lang = frontmatter_dict.get("lang") or "en"
        
        archived_name = f"{filename_base}-v{existing_ver_str}"
        archived_filepath = os.path.join(dir_name, f"{archived_name}.md")
        
        deprecated_fm = existing_fm.copy()
        deprecated_fm["status"] = "deprecated"
        deprecated_fm["valid_to"] = datetime.now().strftime("%Y-%m-%d")
        deprecated_fm["superseded_by"] = f"[[{filename_base}]]"
        
        match = YAML_PATTERN.match(existing_content)
        if match:
            existing_body = existing_content[match.end():].strip()
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
        write_wiki_page(abs_filepath, new_fm, clean_new_body + timeline_content)
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
        if key not in ["created", "updated", "sources", "tags", "translation", "relations"]:
            merged_fm[key] = value

    # Merge relations without duplication
    existing_relations = existing_fm.get("relations", [])
    if isinstance(existing_relations, str):
        existing_relations = []
    new_relations = frontmatter_dict.get("relations", [])
    if isinstance(new_relations, str):
        new_relations = []
    seen_rel_keys = set()
    merged_relations = []
    for rel in existing_relations + new_relations:
        if isinstance(rel, dict):
            key = (rel.get("target", ""), rel.get("type", ""))
            if key not in seen_rel_keys:
                seen_rel_keys.add(key)
                merged_relations.append(rel)
    if merged_relations:
        merged_fm["relations"] = merged_relations

    match = YAML_PATTERN.match(existing_content)
    if match:
        existing_body = existing_content[match.end():].strip()
    else:
        existing_body = existing_content.strip()
        
    split_patterns = [
        r"\n## Cross-References", r"\n## Referensi Silang",
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
        if any(line.strip().startswith(pat) for pat in ["## Cross-References", "## Referensi Silang", "## See Also", "## Lihat Juga", "## Sources", "## Sumber", "## Related Entities", "## Entitas Terkait"]):
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
    exclude_links.add(os.path.splitext(os.path.basename(abs_filepath))[0].lower())
    
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
    
    # Build cross-references section
    cross_ref_section = ""
    if frontmatter_dict.get("type") == "source":
        cr_match = re.search(r"(## (?:Cross-References|Referensi Silang).*?)(?=\n## |$)", markdown_body, re.DOTALL)
        if cr_match:
            cross_ref_section = "\n\n" + cr_match.group(1).strip()
    elif merged_relations:
        is_en = frontmatter_dict.get("lang") == "en"
        cr_heading = "Cross-References" if is_en else "Referensi Silang"
        
        # Categorize relations (including reciprocal ones)
        supports = [r for r in merged_relations if r.get("type") == "supports"]
        supported_by = [r for r in merged_relations if r.get("type") == "supported_by"]
        contradicts = [r for r in merged_relations if r.get("type") in {"contradicts", "contrasting", "contradicted_by"}]
        extends = [r for r in merged_relations if r.get("type") == "extends"]
        extended_by = [r for r in merged_relations if r.get("type") == "extended_by"]
        
        cross_ref_section = f"\n\n## {cr_heading}\n"
        claim_key = "claim_en" if is_en else "claim_id"
        
        sections_to_render = []
        if is_en:
            if supports: sections_to_render.append(("Supports", supports))
            if supported_by: sections_to_render.append(("Supported By", supported_by))
            if contradicts: sections_to_render.append(("Contradicts", contradicts))
            if extends: sections_to_render.append(("Extends", extends))
            if extended_by: sections_to_render.append(("Extended By", extended_by))
        else:
            if supports: sections_to_render.append(("Mendukung", supports))
            if supported_by: sections_to_render.append(("Didukung Oleh", supported_by))
            if contradicts: sections_to_render.append(("Bertentangan", contradicts))
            if extends: sections_to_render.append(("Memperluas", extends))
            if extended_by: sections_to_render.append(("Diperluas Oleh", extended_by))
            
        for section_name, section_items in sections_to_render:
            cross_ref_section += f"\n### {section_name}\n\n"
            for r in section_items:
                target = r.get("target", "")
                target_clean = target.replace("[[", "").replace("]]", "").strip()
                claim = r.get(claim_key) or r.get("claim_en") or r.get("claim") or ""
                source = r.get("source", "")
                cross_ref_section += f"- **[[{target_clean}]]**: {claim} — {source}\n"

    write_wiki_page(abs_filepath, merged_fm, base_body + cross_ref_section + see_also_section + sources_section)

    # After writing the page successfully, update reciprocal relations for all targets
    if merged_relations and frontmatter_dict.get("type") in {"concept", "entity"}:
        source_name = os.path.splitext(os.path.basename(abs_filepath))[0]
        lang = frontmatter_dict.get("lang", "en")
        for rel in merged_relations:
            target = rel.get("target", "")
            rel_type = rel.get("type", "")
            claim = rel.get(claim_key) or rel.get("claim_en") or rel.get("claim") or ""
            source_ref = rel.get("source", "")
            # Only trigger for valid relations that are NOT reciprocal types to avoid infinite trigger loops
            # (though update_target_reciprocal_relation also guards against it via the 'exists' check)
            if target and rel_type and rel_type in {"supports", "contradicts", "contrasting", "extends"}:
                update_target_reciprocal_relation(source_name, target, lang, rel_type, claim, source_ref)
