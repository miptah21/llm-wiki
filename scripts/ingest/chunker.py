"""Chunker module for splitting text into overlapping chunks and extracting headings/sections."""

import re
from typing import List, Dict, Optional


def chunk_text(text: str, max_chars: int = 15000, overlap: int = 1500, abstract: Optional[str] = None) -> List[str]:
    """Splits a document text into overlapping chunks of a maximum character size.

    Optionally prepends an abstract or summary block to each chunk as context.

    Args:
        text: The source text to split.
        max_chars: The maximum length of each chunk in characters. Defaults to 15000.
        overlap: The amount of character overlap between consecutive chunks. Defaults to 1500.
        abstract: Optional abstract text to prepend to all chunks. Defaults to None.

    Returns:
        A list of string chunks.
    """
    chunks: List[str] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + max_chars
        if end >= text_len:
            raw_chunk = text[start:]
            if abstract:
                chunks.append(f"--- CONTEXT ABSTRACT ---\n{abstract}\n--- ACTIVE CHUNK ---\n{raw_chunk}")
            else:
                chunks.append(raw_chunk)
            break
        chunk_slice = text[start:end]
        last_double_newline = chunk_slice.rfind("\n\n")
        if last_double_newline > max_chars * 0.75:
            end_point = start + last_double_newline
        else:
            last_newline = chunk_slice.rfind("\n")
            if last_newline > max_chars * 0.75:
                end_point = start + last_newline
            else:
                end_point = end
        
        raw_chunk = text[start:end_point]
        if abstract:
            chunks.append(f"--- CONTEXT ABSTRACT ---\n{abstract}\n--- ACTIVE CHUNK ---\n{raw_chunk}")
        else:
            chunks.append(raw_chunk)
        start = end_point - overlap
    return chunks


def extract_sections(content: str) -> List[Dict[str, str]]:
    """Identifies major markdown headers and segments the document into sections.

    Args:
        content: The markdown content to split.

    Returns:
        A list of dictionaries representing sections with 'title' and 'content' keys.
    """
    sections: List[Dict[str, str]] = []
    pattern = re.compile(r"^(#+|##+)\s+(.*?)$", re.MULTILINE)
    matches = list(pattern.finditer(content))
    
    if not matches:
        return [{"title": "General", "content": content}]
        
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i+1].start() if i + 1 < len(matches) else len(content)
        title = match.group(2).strip()
        sec_content = content[start:end].strip()
        sections.append({
            "title": title,
            "content": sec_content
        })
    return sections
