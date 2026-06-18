import os
import re
import sys


# Directory Paths
WIKI_DIR = "wiki"

from parser import parse_yaml_frontmatter, YAML_PATTERN

# Regex patterns
WIKILINK_PATTERN = re.compile(r"\[\[(.*?)\]\]")

def scan_vault():
    """Recursively scans wiki/ for markdown files and builds the page index."""
    valid_pages = {}
    files_to_check = []
    
    for root, _, files in os.walk(WIKI_DIR):
        for file in files:
            if not file.endswith(".md"):
                continue
            
            filepath = os.path.join(root, file)
            filename_no_ext = os.path.splitext(file)[0]
            
            # Record valid pages mapping to file path (lowercase page name key)
            valid_pages[filename_no_ext.lower()] = filepath
            files_to_check.append((filepath, filename_no_ext))
            
    return valid_pages, files_to_check

def lint_vault():
    print("Running Bilingual LLM Wiki Linter...")
    valid_pages, files_to_check = scan_vault()
    
    broken_links = {}
    broken_translations = {}
    reciprocal_translation_failures = {}
    orphan_candidates = set(valid_pages.keys())
    
    # Exclude logs, index, and sources from being flagged as orphans
    exclusions = {"index", "log", "concepts"}
    for page in list(orphan_candidates):
        if page in exclusions or page.startswith("source-") or page.endswith("-id"):
            orphan_candidates.remove(page)
            
    inbound_links_count = {page: 0 for page in valid_pages.keys()}
    schema_failures = {}
    translation_mappings = {}
    cross_lang_violations = {}
    
    for filepath, pagename in files_to_check:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue
            
        # 1. Schema Frontmatter Validation
        metadata = parse_yaml_frontmatter(content)
        page_type = metadata.get("type", "")
        if isinstance(page_type, list):
            page_type = page_type[0] if page_type else ""
        page_type = page_type.lower()
        
        if pagename.lower() not in exclusions:
            # Sources and source-subpages only need type, created, updated
            if page_type == "source" or page_type == "source-subpage" or "sources" in filepath:
                required_keys = {"type", "created", "updated"}
            else:
                required_keys = {"type", "domain", "lang", "created", "updated"}
                
            missing = required_keys - set(metadata.keys())
            if missing:
                schema_failures[filepath] = f"Missing YAML keys: {', '.join(missing)}"
            elif page_type not in {"concept", "entity", "source", "source-subpage"}:
                schema_failures[filepath] = f"Invalid type '{page_type}' (must be concept, entity, source, or source-subpage)"
            
            # Domain and Lang checks
            if not missing and page_type in {"concept", "entity"}:
                valid_domains = {"finance", "software-engineering", "ai", "economics", "education", "personal-development", "mathematics", "language-learning"}
                try:
                    import json
                    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
                    if os.path.exists(config_path):
                        with open(config_path, "r", encoding="utf-8") as cf:
                            cfg = json.load(cf)
                            valid_domains = set(cfg.get("valid_domains", []))
                except Exception:
                    pass
                valid_langs = {"en", "id"}
                
                if metadata.get("domain") not in valid_domains:
                    schema_failures[filepath] = f"Invalid domain '{metadata.get('domain')}'"
                elif metadata.get("lang") not in valid_langs:
                    schema_failures[filepath] = f"Invalid language '{metadata.get('lang')}'"
                else:
                    # Domain-Path Consistency Check
                    norm_path = filepath.replace("\\", "/")
                    parts = norm_path.split("/")
                    if len(parts) >= 3 and parts[-3] in {"concepts", "entities"}:
                        expected_domain = parts[-2].lower()
                        actual_domain = str(metadata.get("domain", "")).lower()
                        if actual_domain != expected_domain:
                            schema_failures[filepath] = f"Domain path mismatch: Frontmatter domain is '{actual_domain}', but file is located under '{expected_domain}' directory."

                # Frontmatter Relations target and type checks
                relations = metadata.get("relations", [])
                if isinstance(relations, list):
                    for idx, rel in enumerate(relations):
                        if isinstance(rel, dict):
                            target = rel.get("target", "")
                            rel_type = rel.get("type", "")
                            
                            target_clean = target.replace("[[", "").replace("]]", "").strip()
                            target_lower = target_clean.lower().replace(" ", "-")
                            
                            if not target_clean:
                                schema_failures[filepath] = f"Relation at index {idx} has an empty target."
                            elif target_lower not in valid_pages:
                                schema_failures[filepath] = f"Relation at index {idx} points to non-existent target page: [[{target_clean}]]."
                            else:
                                valid_relation_types = {"supports", "supported_by", "contradicts", "contradicted_by", "contrasting", "extends", "extended_by"}
                                if rel_type not in valid_relation_types:
                                    schema_failures[filepath] = f"Relation to [[{target_clean}]] has an invalid type: '{rel_type}'."

            # 1.1 LaTeX Math Formula Subscript Validation (Indonesian Content Integrity Guardrail)
            if metadata.get("lang", "").lower() == "id":
                math_blocks = re.findall(r"\$\$(.*?)\$\$", content, re.DOTALL)
                math_inlines = re.findall(r"\$(.*?)\$", content)
                all_formulas = math_blocks + math_inlines
                
                prohibited_terms = {"keras", "lunak", "uji"}
                detected_violations = []
                
                for formula in all_formulas:
                    for term in prohibited_terms:
                        if (re.search(r"\\text\{\s*" + term + r"\s*\}", formula, re.IGNORECASE) or 
                            re.search(r"\\mathrm\{\s*" + term + r"\s*\}", formula, re.IGNORECASE) or 
                            (term in formula.lower() and "_" in formula)):
                            detected_violations.append(term)
                
                if detected_violations:
                    schema_failures[filepath] = f"LaTeX Translation Failure: Formula contains translated subscripts {list(set(detected_violations))} (must preserve original English terms like 'hard', 'soft', 'test')."

                # 1.2 Prohibited Literal Indonesian Technical Translations Guardrail
                prohibited_literal_translations = {
                    "jendela konteks": "context window",
                    "pelatihan prabayar": "pretraining",
                    "fungsi kehilangan": "loss function"
                }
                detected_literal_violations = []
                for bad_term in prohibited_literal_translations.keys():
                    if bad_term in content.lower():
                        detected_literal_violations.append(bad_term)
                
                if detected_literal_violations:
                    schema_failures[filepath] = f"Awkward Literal Translation Failure: Page contains discouraged literal terms {detected_literal_violations}. Please use standard English terms: {[prohibited_literal_translations[t] for t in detected_literal_violations]} instead."

        # 2. Translation Validation
        translation_val = metadata.get("translation", "")
        if translation_val:
            # Clean brackets if present, e.g. "[[target]]" -> "target"
            clean_trans = translation_val.replace("[[", "").replace("]]", "").strip()
            clean_trans_lower = clean_trans.lower()
            clean_trans_kebab = clean_trans_lower.replace(" ", "-")
            
            if clean_trans_lower in valid_pages:
                translation_mappings[pagename.lower()] = clean_trans_lower
            elif clean_trans_kebab in valid_pages:
                translation_mappings[pagename.lower()] = clean_trans_kebab
            else:
                broken_translations[filepath] = clean_trans

        # 3. Link Validation
        links = WIKILINK_PATTERN.findall(content)
        for link in links:
            clean_link = link.split("|")[0].strip()
            if not clean_link:
                continue
                
            link_lower = clean_link.lower()
            if link_lower.startswith("http") or link_lower.startswith("www"):
                continue
                
            # Skip media and asset files (e.g. embedded figures)
            if any(link_lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf"]):
                continue
                
            link_kebab = link_lower.replace(" ", "-")
            if link_lower in valid_pages:
                matched_key = link_lower
            elif link_kebab in valid_pages:
                matched_key = link_kebab
            else:
                matched_key = None
                
            if matched_key is None:
                if filepath not in broken_links:
                    broken_links[filepath] = []
                broken_links[filepath].append(clean_link)
            else:
                if pagename.lower() not in exclusions and pagename.lower() != matched_key:
                    inbound_links_count[matched_key] += 1

        # 4. Cross-Language Link Contamination Check
        # ID files should link to ID pages (except translation field, which correctly points to EN)
        page_lang = metadata.get("lang", "").lower()
        if not page_lang:
            norm_filepath = filepath.replace("\\", "/")
            if "/id/" in norm_filepath:
                page_lang = "id"
            elif "/en/" in norm_filepath:
                page_lang = "en"
        if page_lang == "id" and pagename.lower() not in {"index", "log"}:
            # Get the translation target so we can exclude it from the check
            trans_target = metadata.get("translation", "").replace("[[", "").replace("]]", "").strip().lower()
            # Also exclude source links (sources are referenced by convention)
            source_refs = [s.replace("[[", "").replace("]]", "").strip().lower() for s in metadata.get("sources", [])]
            
            # Strip frontmatter from body to avoid false positives on translation/sources fields
            match = YAML_PATTERN.match(content)
            if match:
                body_content = content[match.end():]
            else:
                body_content = content
            
            body_links = WIKILINK_PATTERN.findall(body_content)
            for link in body_links:
                clean_link = link.split("|")[0].strip()
                if not clean_link:
                    continue
                link_lower = clean_link.lower()
                link_kebab = link_lower.replace(" ", "-")
                
                # Skip translation and source refs
                if link_lower == trans_target or link_kebab == trans_target:
                    continue
                if link_lower in source_refs or link_kebab in source_refs:
                    continue
                    
                # Check if this link resolves to an EN page (lives in en/ directory)
                resolved_key = link_lower if link_lower in valid_pages else (link_kebab if link_kebab in valid_pages else None)
                if resolved_key and resolved_key in valid_pages:
                    resolved_path = valid_pages[resolved_key].replace("\\", "/")
                    if "/en/" in resolved_path:
                        if filepath not in cross_lang_violations:
                            cross_lang_violations[filepath] = []
                        cross_lang_violations[filepath].append(clean_link)

    # 5. Reciprocal Translation Check
    for source_note, target_note in translation_mappings.items():
        # If Page A translations to Page B, then Page B's translation property must link back to Page A
        recip_trans = translation_mappings.get(target_note)
        if recip_trans != source_note:
            reciprocal_translation_failures[valid_pages[source_note]] = f"Translation link [[{target_note}]] is not reciprocal (target doesn't link back)."

    # Remove non-orphans based on inbound counts
    orphans = []
    for candidate in orphan_candidates:
        if inbound_links_count[candidate] == 0:
            orphans.append(candidate)

    # Output Report
    report = []
    report.append("=== LINTER HEALTH REPORT ===")
    
    # Write Schema Failures
    if schema_failures:
        report.append(f"\n❌ YAML Schema Failures ({len(schema_failures)}):")
        for path, err in schema_failures.items():
            report.append(f"  - `{path}`: {err}")
    else:
        report.append("\n✅ All pages conform to the YAML schema guidelines.")

    # Write Broken Links
    if broken_links:
        report.append(f"\n❌ Broken WikiLinks ({sum(len(v) for v in broken_links.values())}):")
        for path, links in broken_links.items():
            report.append(f"  - `{path}` references missing pages:")
            for l in links:
                report.append(f"    - [[{l}]]")
    else:
        report.append("\n✅ Zero broken wikilinks found in the vault.")

    # Write Broken Translations
    if broken_translations:
        report.append(f"\n❌ Broken Translation Links ({len(broken_translations)}):")
        for path, trans in broken_translations.items():
            report.append(f"  - `{path}` references non-existent translation: [[{trans}]]")
    else:
        report.append("\n✅ All translation notes resolve to existing pages.")

    # Write Reciprocal Translation Mismatch
    if reciprocal_translation_failures:
        report.append(f"\n⚠️ Non-Reciprocal Translations ({len(reciprocal_translation_failures)}):")
        for path, err in reciprocal_translation_failures.items():
            report.append(f"  - `{path}`: {err}")
    else:
        report.append("\n✅ All translations are fully reciprocal!")

    # Write Orphan Pages
    if orphans:
        report.append(f"\n⚠️ Orphan Pages ({len(orphans)}) [No inbound links from other concepts/entities]:")
        for o in sorted(orphans):
            report.append(f"  - [[{o}]] (`{valid_pages[o]}`)")
    else:
        report.append("\n✅ Zero orphan pages found. All concepts and entities are interlinked!")
     # Write Cross-Language Link Contamination
    if cross_lang_violations:
        total_violations = sum(len(v) for v in cross_lang_violations.values())
        report.append(f"\n❌ Cross-Language Link Contamination ({total_violations}):")
        report.append(f"  ID files linking to EN pages instead of their ID equivalents:")
        for path, links in cross_lang_violations.items():
            report.append(f"  - `{path}`:")
            for l in links:
                report.append(f"    - [[{l}]] → should be ID equivalent")
    else:
        report.append("\n✅ No cross-language link contamination detected.")

    print("\n".join(report))
    
    # Return exit code: 1 if critical schema/link issues, 0 if clean
    if schema_failures or broken_links or broken_translations or cross_lang_violations:
        return 1
    return 0

if __name__ == "__main__":
    import sys
    # Windows Encoding Safeguard for non-ASCII characters / emojis
    if sys.platform.startswith("win"):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
    sys.exit(lint_vault())
