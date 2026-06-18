"""Cross-reference and contradiction detection module.

Detects relationships (supports/contradicts/extends) between incoming
concepts from a new paper and existing concepts in the vault.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Valid relation types
RELATION_TYPES = {"supports", "contradicts", "contrasting", "extends"}


from parser import parse_yaml_frontmatter


def read_concept_pages(concepts_dir: str) -> Dict[str, Dict[str, Any]]:
    """Reads all existing concept pages from a vault concepts directory.
    
    Scans all subdomain folders (ai/, finance/, etc.) under the concepts dir.
    
    Args:
        concepts_dir: Path to wiki/<lang>/concepts/ directory.
        
    Returns:
        Dict mapping concept name to {"description": ..., "content": ..., "sources": ..., "domain": ..., "tags": ..., "relations": ...}
    """
    existing = {}
    if not os.path.exists(concepts_dir):
        return existing
    
    for domain_dir in os.listdir(concepts_dir):
        domain_path = os.path.join(concepts_dir, domain_dir)
        if not os.path.isdir(domain_path):
            continue
        for fname in os.listdir(domain_path):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(domain_path, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                metadata = parse_yaml_frontmatter(content)
                description = metadata.get("description", "")
                
                raw_tags = metadata.get("tags", "")
                if isinstance(raw_tags, list):
                    tags = ", ".join(raw_tags)
                else:
                    tags = str(raw_tags) if raw_tags is not None else ""
                    
                raw_sources = metadata.get("sources", "")
                if isinstance(raw_sources, list):
                    sources = ", ".join(raw_sources)
                else:
                    sources = str(raw_sources) if raw_sources is not None else ""
                
                relations = metadata.get("relations", [])
                
                # Extract body (after frontmatter)
                parts = content.split('---')
                body = '---'.join(parts[2:]).strip() if len(parts) >= 3 else ""
                
                concept_name = os.path.splitext(fname)[0]
                existing[concept_name] = {
                    "description": description,
                    "content": body[:1500],  # Limit to avoid huge prompts
                    "sources": sources,
                    "domain": domain_dir,
                    "tags": tags,
                    "relations": relations
                }
            except Exception as e:
                logger.warning(f"Failed to read concept page {fpath}: {e}")
    return existing


def _detect_relations_with_llm(
    incoming_concept: Dict[str, Any],
    existing_concepts: Dict[str, Dict[str, str]],
    incoming_source_name: str
) -> List[Dict[str, str]]:
    """Uses LLM to detect relationships between an incoming concept and existing ones.
    
    Args:
        incoming_concept: The incoming concept dict with name, description, content.
        existing_concepts: Dict of existing concept pages.
        incoming_source_name: The source name of the new paper.
        
    Returns:
        List of relation dicts: [{"target": ..., "type": ..., "claim_en": ..., "claim_id": ...}]
    """
    from deepseek_helper import call_deepseek
    from .llm_pipeline import extract_and_parse_json
    
    concept_name = incoming_concept.get("name", "")
    concept_desc = incoming_concept.get("description_en") or incoming_concept.get("content_en", "")
    incoming_domain = incoming_concept.get("domain", "")
    
    # Build a summary of existing concepts for comparison, prioritizing same domain
    same_domain_summaries = []
    other_domain_summaries = []
    
    for name, data in existing_concepts.items():
        # Skip self
        if name == concept_name or name == f"{concept_name}-id":
            continue
        # Skip version-archived pages
        if re.match(r'.*-v\d+\.\d+\.\d+$', name):
            continue
        # Skip Indonesian translations (we compare EN only)
        if name.endswith('-id'):
            continue
            
        desc = data.get("description", "")
        domain = data.get("domain", "")
        tags = data.get("tags", "")
        content = data.get("content", "")
        
        if not desc and not content:
            continue
            
        tags_str = f" [Tags: {tags}]" if tags else ""
        
        if domain and incoming_domain and domain.lower() == incoming_domain.lower():
            # Same domain gets richer context (first 350 chars of content body) to help LLM verify semantic details
            snippet = content[:350].strip().replace("\n", " ")
            snippet_str = f" (Core Context: {snippet}...)" if snippet else ""
            same_domain_summaries.append(f"- **{name}** (Domain: {domain}{tags_str}): {desc}{snippet_str}")
        else:
            other_domain_summaries.append(f"- **{name}** (Domain: {domain}{tags_str}): {desc}")
            
    # Prioritize same-domain concepts
    existing_summaries = same_domain_summaries + other_domain_summaries
    
    if not existing_summaries:
        return []
    
    # Limit to avoid token overflow
    existing_text = "\n".join(existing_summaries[:50])
    
    prompt = (
        f"You are a knowledge graph relationship detector. Analyze the incoming concept and determine "
        f"if it has any meaningful relationships with the existing concepts listed below.\n\n"
        f"INCOMING CONCEPT:\n"
        f"- Name: {concept_name}\n"
        f"- Description: {concept_desc[:800]}\n"
        f"- Source: {incoming_source_name}\n\n"
        f"EXISTING CONCEPTS IN VAULT:\n{existing_text}\n\n"
        f"For each relationship found, you MUST classify it strictly as one of the following types:\n"
        f"1. 'supports': The incoming concept confirms, reinforces, or provides validating evidence/results for the existing concept. The explanation must state the specific validating evidence/argument.\n"
        f"2. 'contradicts': The incoming concept directly conflicts, challenges, or limits the validity of the existing concept (e.g. shows different/clashing results, disproves a hypothesis, or warns of a failure mode). The explanation must state the conflicting mechanism/finding.\n"
        f"3. 'extends': The incoming concept builds upon, expands, generalizes, or refines the existing concept (e.g. applying it to a new domain, optimizing it, adding a sub-concept, or defining parameters). The explanation must state how it builds upon it.\n\n"
        f"Return a JSON object with a single key 'relations' containing an array. Each item has:\n"
        f"- 'target': kebab-case name of the existing concept\n"
        f"- 'type': 'supports' or 'contradicts' or 'extends'\n"
        f"- 'claim_en': One-sentence English explanation of why this relationship applies. Format as: '[Source concept] [supports/contradicts/extends] [Target concept] because [explain the exact clashing, connecting, or validating mechanism/nuance].' Be academically precise.\n"
        f"- 'claim_id': One-sentence Indonesian explanation of why this relationship applies. Format as: '[Konsep sumber] [mendukung/bertentangan dengan/memperluas] [Konsep target] karena [jelaskan mekanisme/nuansa yang bertentangan, berhubungan, atau memvalidasi secara tepat].' Harus tepat secara akademis.\n\n"
        f"If no meaningful relationships exist, return {{\"relations\": []}}\n"
        f"IMPORTANT: Only return strong, meaningful relationships. Do not force weak connections."
    )
    
    try:
        response = call_deepseek(
            prompt,
            "You are a precise academic knowledge graph builder. Return valid JSON only."
        )
        parsed = extract_and_parse_json(response)
        if parsed and "relations" in parsed:
            # Validate relation types
            valid_relations = []
            for rel in parsed["relations"]:
                if (
                    isinstance(rel, dict)
                    and rel.get("target") in existing_concepts
                    and rel.get("claim_en")
                ):
                    rel_type = rel.get("type", "")
                    if rel_type in {"contrasting", "contrasts"}:
                        rel_type = "contradicts"
                    if rel_type in RELATION_TYPES:
                        valid_relations.append({
                            "target": rel["target"],
                            "type": rel_type,
                            "claim_en": rel["claim_en"],
                            "claim_id": rel.get("claim_id", rel["claim_en"]),
                            "source": f"[[{incoming_source_name}]]"
                        })
                        logger.info(f"Detected relation: {concept_name} --{rel_type}--> {rel['target']}")
            return valid_relations
    except Exception as e:
        logger.warning(f"LLM relation detection failed for '{concept_name}': {e}")
    
    return []


def detect_cross_references(
    incoming_concepts: List[Dict[str, Any]],
    incoming_source_name: str,
    vault_concepts_dir: str,
    lang: str = "en"
) -> Dict[str, List[Dict[str, str]]]:
    """Detects cross-references between incoming concepts and existing vault concepts.
    
    Args:
        incoming_concepts: List of concept dicts from the ingestion pipeline.
        incoming_source_name: The source page name (e.g., 'source-DeepSeek-2025').
        vault_concepts_dir: Path to wiki/<lang>/concepts/ directory.
        lang: Language code ('en' or 'id').
        
    Returns:
        Dict mapping concept name to list of detected relation dicts.
        Each relation dict has keys: target, type, claim_en, claim_id, source.
    """
    from deepseek_helper import has_api_key
    if not has_api_key():
        logger.info("No API key available. Skipping LLM cross-reference detection.")
        return {name: [] for name in [c.get("name", "") for c in incoming_concepts]}
    
    existing_concepts = read_concept_pages(vault_concepts_dir)
    if not existing_concepts:
        logger.info("No existing concepts found in vault. Skipping cross-reference detection.")
        return {name: [] for name in [c.get("name", "") for c in incoming_concepts]}
    
    result = {}
    for concept in incoming_concepts:
        name = concept.get("name", "")
        if not name:
            continue
        
        # Merge explicitly declared relations from LLM pipeline output
        explicit_relations = concept.get("relations", [])
        
        # Detect additional relations via LLM comparison with vault
        detected_relations = _detect_relations_with_llm(
            concept, existing_concepts, incoming_source_name
        )
        
        # Combine, dedup by target+type
        seen = set()
        all_relations = []
        for rel in explicit_relations + detected_relations:
            rel_type = rel.get("type", "")
            if rel_type in {"contrasting", "contrasts"}:
                rel_type = "contradicts"
                rel["type"] = "contradicts"
            key = (rel.get("target", ""), rel_type)
            if key not in seen:
                seen.add(key)
                all_relations.append(rel)
        
        result[name] = all_relations
    
    return result
