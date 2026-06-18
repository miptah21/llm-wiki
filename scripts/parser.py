import os
import re

# Regex to extract YAML frontmatter
YAML_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL | re.MULTILINE)

def parse_yaml_frontmatter(content):
    """
    Parses key-value pairs from YAML frontmatter using regex (zero-dependency).
    Handles string values, list formatting like tags: [tag1, tag2] or sources: ["[[source]]"],
    and block sequences like relations.
    """
    match = YAML_PATTERN.match(content)
    if not match:
        return {}
    
    yaml_text = match.group(1)
    metadata = {}
    
    current_list_key = None
    current_dict = None
    
    for line in yaml_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
            
        # Check if this line starts a list item in a block sequence, e.g. "- target: ..."
        if stripped.startswith("- "):
            item_text = stripped[2:].strip()
            if ":" in item_text:
                item_key, item_val = item_text.split(":", 1)
                item_key = item_key.strip().lower()
                item_val = item_val.strip().strip('"').strip("'")
                
                # Start a new list item dictionary
                current_dict = {item_key: item_val}
                if current_list_key:
                    if current_list_key not in metadata or not isinstance(metadata[current_list_key], list):
                        metadata[current_list_key] = []
                    metadata[current_list_key].append(current_dict)
            continue
            
        # Check if this line is part of the current list item dictionary
        leading_spaces = len(line) - len(line.lstrip(' '))
        if leading_spaces >= 4 and current_dict is not None and ":" in stripped:
            item_key, item_val = stripped.split(":", 1)
            item_key = item_key.strip().lower()
            item_val = item_val.strip().strip('"').strip("'")
            current_dict[item_key] = item_val
            continue
            
        if ":" not in stripped:
            continue
            
        key, value = stripped.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        
        # Stop nesting if we hit a new top-level key
        current_dict = None
        
        # Strip trailing inline comments if any
        comment_idx = value.find(" #")
        if comment_idx != -1:
            value = value[:comment_idx].strip()
            
        if not value:
            current_list_key = key
            metadata[key] = []
            continue
            
        current_list_key = None
        
        # Handle double bracket wikilink vs list format
        if value.startswith("[[") and value.endswith("]]"):
            value = value.strip('"').strip("'")
            metadata[key] = value
        elif value.startswith("[") and value.endswith("]"):
            import json
            try:
                # Try parsing as JSON array to respect quotes and commas
                items = json.loads(value)
            except Exception:
                items = []
                raw_items = value[1:-1].split(",")
                for item in raw_items:
                    item = item.strip().strip('"').strip("'")
                    if item:
                        items.append(item)
            metadata[key] = items
        else:
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
            
    # Detect domain (load from config.json dynamically with fallback)
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
