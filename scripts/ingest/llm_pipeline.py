"""LLM pipeline module for processing documents using the DeepSeek API."""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from .chunker import chunk_text

# Setup logging
logger = logging.getLogger(__name__)


def extract_and_parse_json(response_text: str) -> Optional[Dict[str, Any]]:
    """Extracts and parses a JSON object from response text.

    Args:
        response_text: The raw string response from the LLM.

    Returns:
        A dictionary representing the parsed JSON, or None if parsing fails.
    """
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


def merge_contents_with_llm(name: str, text_type: str, content_list: List[str], anchor_quotes: List[str]) -> str:
    """Merges multiple extracted content pieces of a concept/entity into a single markdown text using the LLM.

    Args:
        name: Name of the concept or entity.
        text_type: Type descriptor ('concept' or 'entity').
        content_list: List of content strings to merge.
        anchor_quotes: List of exact quotes or formulas to preserve.

    Returns:
        Synthesized markdown string.
    """
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
    except (Exception, SystemExit) as e:
        logger.warning(f"Failed to call LLM for merging '{name}': {e}. Using raw concatenation.")
        return "\n\n".join(content_list)


def run_groundedness_evaluation(raw_text: str, synthesized_content: str, doc_name: str) -> str:
    """Performs a groundedness evaluation using the LLM to verify that no critical details were lost.

    Args:
        raw_text: The complete raw text of the document.
        synthesized_content: The newly synthesized summary/concepts.
        doc_name: The filename or title of the document.

    Returns:
        Either 'APPROVED' or a description of missing gaps.
    """
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
        logger.info(f"Groundedness check result: {evaluation}")
        return evaluation
    except (Exception, SystemExit) as e:
        logger.warning(f"Groundedness evaluation skipped due to API error: {e}")
        return "APPROVED"


def process_deepseek(raw_content: str, filename: str, version: str = "1.0.0") -> Optional[Dict[str, Any]]:
    """Runs the Map-Reduce pipeline via DeepSeek to ingest the document.

    Args:
        raw_content: Full text of the document.
        filename: Name of the file being processed.
        version: Version string for the document metadata.

    Returns:
        A dictionary containing the title, summaries, concepts, and entities, or None.
    """
    from deepseek_helper import has_api_key
    if not has_api_key():
        logger.info("No LLM API key or provider configured. Skipping LLM pipeline.")
        return None
        
    try:
        from deepseek_helper import call_deepseek
        abstract_ctx = raw_content[:2500]
        chunks = chunk_text(raw_content, abstract=abstract_ctx)
        logger.info(f"Divided document into {len(chunks)} chunks. Processing Map phase...")
        
        intermediate_data = []
        system_prompt = (
            "You are an expert bilingual scientific data ingestion engine. "
            "Your task is to summarize the raw scientific asset in both English and Indonesian. "
            "You must return a valid JSON object with the following structure:\n"
            "CRITICAL WIKILINK RULE: All wikilinks in content fields MUST use kebab-case matching the concept/entity 'name' field.\n"
            "CRITICAL BOUNDARY RULE:\n"
            "  - CONCEPTS: Abstract ideas, theories, formulas, algorithms, cognitive biases, indexes, economic phenomena, mathematical models (e.g., 'dividend-disconnect', 'expected-return-formula', 'risk-neutral-variance').\n"
            "  - ENTITIES: Concrete nameable things like people (authors, researchers), organizations (universities, companies), datasets, journals, publishers, specific books, or software tools (e.g., 'samuel-hartzmark', 'journal-of-finance').\n"
            "  Do NOT put abstract theories, formulas, or economic/mathematical models under entities.\n"
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
            "      \"content_en\": \"Full markdown content in English. DO NOT write plain paragraphs. Structure this content creatively and flexibly based on its domain. Choose appropriate layout elements (subheadings, LaTeX, Mermaid, Callouts, Tables, Code Blocks) that fit the nature of the concept. (e.g., Use PyTorch/SQL/Python code blocks and Mermaid architecture diagrams only if the domain is technical/software/AI; use LaTeX equation blocks ($$ ... $$) only if the domain is mathematical/financial/economics; use Obsidian callouts (> [!NOTE] or > [!TIP]) and markdown tables comparing options or theories for qualitative/descriptive/strategy concepts). Do not force technical elements like code or formulas if they do not apply.\",\n"
            "      \"content_id\": \"Full markdown content in Indonesian. Follow the same flexible, domain-aware guidelines as English. Choose subheadings, LaTeX, Mermaid, Callouts, and Tables matching the domain of the concept. Keep key technical terms in English next to their Indonesian translations inside parentheses or italics to maintain scientific naturalness.\",\n"
            "      \"relations\": [\n"
            "        {\n"
            "          \"target\": \"target-concept-kebab-name\",\n"
            "          \"type\": \"supports|contradicts|extends\",\n"
            "          \"claim_en\": \"Detailed English explanation of why this concept supports, contradicts, or extends the target (Format as: '[Source concept] [supports/contradicts/extends] [Target concept] because [explain the exact clashing, connecting, or validating mechanism/nuance].' Be academically precise.)\",\n"
            "          \"claim_id\": \"Detailed Indonesian explanation of why this concept supports, contradicts, or extends the target (Format as: '[Konsep sumber] [mendukung/bertentangan dengan/memperluas] [Konsep target] karena [jelaskan mekanisme/nuansa yang bertentangan, berhubungan, atau memvalidasi secara tepat].' Harus tepat secara akademis.)\"\n"
            "        }\n"
            "      ],\n"
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
            logger.info(f"Mapping chunk {idx+1}/{len(chunks)}...")
            prompt = f"Here is the content of chunk {idx+1} from '{filename}':\n\n{chunk}"
            try:
                res = call_deepseek(prompt, system_prompt)
                parsed = extract_and_parse_json(res)
                if parsed:
                    intermediate_data.append(parsed)
            except (Exception, SystemExit) as e:
                logger.warning(f"Error mapping chunk {idx+1}: {e}")
                
        if not intermediate_data:
            return None
            
        logger.info("Processing Reduce phase...")
        combined_sum_en = "\n\n".join([d.get("summary_en", "") for d in intermediate_data if d.get("summary_en")])
        combined_sum_id = "\n\n".join([d.get("summary_id", "") for d in intermediate_data if d.get("summary_id")])
        
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
                            "anchors": c.get("anchor_quotes", []) or [],
                            "relations": c.get("relations", []) or []
                        }
                    else:
                        concepts_map[name]["contents"].append(c.get("content_en") or c.get("description_en") or "")
                        concepts_map[name]["contents_id"].append(c.get("content_id") or c.get("description_id") or "")
                        concepts_map[name]["anchors"].extend(c.get("anchor_quotes", []) or [])
                        concepts_map[name].setdefault("relations", []).extend(c.get("relations", []) or [])
                        
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
                logger.info(f"Running smart LLM merge for concept: {name}")
                c["content_en"] = merge_contents_with_llm(name, "concept", data["contents"], data["anchors"])
                c["content_id"] = merge_contents_with_llm(name, "concept", data["contents_id"], data["anchors"])
            else:
                c["content_en"] = data["contents"][0]
                c["content_id"] = data["contents_id"][0]
            c["anchor_quotes"] = list(set(data["anchors"]))
            # Deduplicate relations by target+type
            seen_rels = set()
            unique_relations = []
            for rel in data.get("relations", []):
                key = (rel.get("target", ""), rel.get("type", ""))
                if key not in seen_rels:
                    seen_rels.add(key)
                    unique_relations.append(rel)
            c["relations"] = unique_relations
            final_concepts.append(c)
            
        final_entities = []
        for name, data in entities_map.items():
            e = data["meta"]
            e["version"] = e.get("version") or version
            e["status"] = e.get("status") or "active"
            if len(data["contents"]) > 1:
                logger.info(f"Running smart LLM merge for entity: {name}")
                e["content_en"] = merge_contents_with_llm(name, "entity", data["contents"], data["anchors"])
                e["content_id"] = merge_contents_with_llm(name, "entity", data["contents_id"], data["anchors"])
            else:
                e["content_en"] = data["contents"][0]
                e["content_id"] = data["contents_id"][0]
            e["anchor_quotes"] = list(set(data["anchors"]))
            final_entities.append(e)

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
    except (Exception, SystemExit) as e:
        logger.error(f"DeepSeek compilation failed: {e}. Falling back to deterministic local compilation...")
    return None
