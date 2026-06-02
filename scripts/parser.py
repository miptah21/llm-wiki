import os
import re

# Regex to extract YAML frontmatter
YAML_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL | re.MULTILINE)

def parse_yaml_frontmatter(content):
    """
    Parses key-value pairs from YAML frontmatter using regex (zero-dependency).
    Handles string values, list formatting like tags: [tag1, tag2] or sources: ["[[source]]"].
    """
    match = YAML_PATTERN.match(content)
    if not match:
        return {}
    
    yaml_text = match.group(1)
    metadata = {}
    
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        
        # Handle double bracket wikilink vs list format
        if value.startswith("[[") and value.endswith("]]"):
            # Clean string values
            value = value.strip('"').strip("'")
            metadata[key] = value
        elif value.startswith("[") and value.endswith("]"):
            items = []
            raw_items = value[1:-1].split(",")
            for item in raw_items:
                item = item.strip().strip('"').strip("'")
                if item:
                    items.append(item)
            metadata[key] = items
        else:
            # Clean string values
            value = value.strip('"').strip("'")
            metadata[key] = value
            
    return metadata

def detect_page_attributes(filepath):
    """
    Infers language (en or id), folder type (concepts, entities, sources),
    and domain from the physical file path.
    """
    normalized_path = os.path.normpath(filepath)
    parts = normalized_path.split(os.sep)
    
    # Defaults
    lang = "en"
    dir_type = "concepts"
    domain = "other"
    
    # Detect language based on 'en' or 'id' directory
    if "id" in parts:
        lang = "id"
    elif "en" in parts:
        lang = "en"
        
    # Detect folder type (concepts, entities, sources)
    for t in ["concepts", "entities", "sources"]:
        if t in parts:
            dir_type = t
            break
            
    # Detect domain (finance, software-engineering, ai, economics)
    valid_domains = {"finance", "software-engineering", "ai", "economics"}
    # The domain folder is usually immediately following 'concepts' or 'entities'
    try:
        for idx, part in enumerate(parts):
            if part in ["concepts", "entities"] and idx + 1 < len(parts):
                next_part = parts[idx + 1].lower()
                if next_part in valid_domains:
                    domain = next_part
                    break
    except Exception:
        pass
        
    return {
        "lang": lang,
        "type": dir_type,
        "domain": domain
    }
