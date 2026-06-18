"""Extractor module for retrieving text, tables, and images from PDF documents."""

import os
import re
from typing import Tuple, Optional, List, Dict


def _ocr_page_worker(pdf_path: str, page_num: int, tessdata_path: Optional[str], lang: str) -> Tuple[int, str]:
    """Extract text from a single page of a PDF using OCR as a fallback.

    Args:
        pdf_path: Path to the target PDF file.
        page_num: Zero-indexed page number to extract.
        tessdata_path: Path to the Tesseract data directory, or None if OCR is not configured.
        lang: Language model string for Tesseract.

    Returns:
        A tuple of (page_num, extracted_text).
    """
    import fitz
    try:
        with fitz.open(pdf_path) as doc:
            page = doc[page_num]
            text = page.get_text()
            if len(text.strip()) >= 50:
                return page_num, text
            if tessdata_path and os.path.exists(tessdata_path):
                tp = page.get_textpage_ocr(language=lang, tessdata=tessdata_path)
                ocr_text = page.get_text(textpage=tp)
                return page_num, ocr_text
            return page_num, "[Halaman Terpindai - OCR Tidak Dikonfigurasi]"
    except Exception as e:
        return page_num, f"[Error Halaman {page_num}: {e}]"


def parallel_pdf_ingest(
    pdf_path: str,
    tessdata_path: Optional[str] = None,
    lang: str = "eng+ind+equ",
    max_workers: int = 4,
) -> str:
    """Ingest a PDF file in parallel using process pool workers.

    Args:
        pdf_path: Path to the target PDF file.
        tessdata_path: Path to the Tesseract data directory, or None. Defaults to None.
        lang: Language model string for Tesseract. Defaults to "eng+ind+equ".
        max_workers: Maximum number of worker processes. Defaults to 4.

    Returns:
        The full ordered text extracted from all pages.
    """
    import fitz
    import sys
    from concurrent.futures import ProcessPoolExecutor, as_completed
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)
    
    results: Dict[int, str] = {}
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_ocr_page_worker, pdf_path, page_num, tessdata_path, lang): page_num
            for page_num in range(total_pages)
        }
        for future in as_completed(futures):
            page_num = futures[future]
            try:
                p_num, extracted_text = future.result()
                results[p_num] = extracted_text
            except Exception as exc:
                results[page_num] = f"[Process failed for page {page_num}: {exc}]"
                
    failed_count = 0
    clean_results = {}
    for i in range(total_pages):
        page_text = results.get(i, "")
        is_error = False
        if (page_text.startswith("[Process failed for page") or 
            page_text.startswith("[Error Halaman") or 
            page_text == "[Halaman Terpindai - OCR Tidak Dikonfigurasi]"):
            is_error = True
        
        if is_error:
            failed_count += 1
            print(f"Warning: Failed to extract text from page {i+1}: {page_text}", file=sys.stderr)
            clean_results[i] = ""
        else:
            clean_results[i] = page_text
            
    if total_pages > 0 and (failed_count / total_pages) > 0.15:
        raise RuntimeError(
            f"PDF extraction failed on {failed_count}/{total_pages} pages ({failed_count/total_pages:.1%}). "
            f"Please verify Tesseract installation or PDF health."
        )
        
    full_ordered_text = [clean_results[i] for i in range(total_pages)]
    return "\n\n".join(full_ordered_text)


def _calculate_fill_rate(table: List[List[str]]) -> float:
    """Calculate the ratio of non-empty cells to total cells in a table.

    Args:
        table: List of list of strings representing table cells.

    Returns:
        Float fill rate from 0.0 to 1.0.
    """
    if not table or not table[0]:
        return 0.0
    total_cells = len(table) * len(table[0])
    non_empty = sum(1 for row in table for cell in row if cell and str(cell).strip())
    return non_empty / total_cells if total_cells > 0 else 0.0


def _unpack_table(table: List[List[str]]) -> List[List[str]]:
    """Unpack rows containing cell newlines into separate rows.

    Args:
        table: List of list of strings representing table cells.

    Returns:
        Unpacked table with nested newlines split.
    """
    new_rows = []
    for row in table:
        cell_parts = []
        max_parts = 1
        for cell in row:
            val = str(cell or "").strip()
            # Escape vertical pipes in cell values to prevent markdown breaking
            val = val.replace("|", "\\|")
            parts = val.split("\n") if val else [""]
            cell_parts.append(parts)
            max_parts = max(max_parts, len(parts))
        
        if max_parts > 1:
            for i in range(max_parts):
                new_row = []
                for parts in cell_parts:
                    if i < len(parts):
                        new_row.append(parts[i].strip())
                    else:
                        new_row.append("")
                new_rows.append(new_row)
        else:
            new_rows.append([parts[0].strip() for parts in cell_parts])
    return new_rows


def _find_best_match(body_row: List[str], cropped_rows: List[List[str]]) -> int:
    """Find the index of the best matching row in cropped_rows using token word intersection.

    Args:
        body_row: Cleaned cells of a row from the original table extraction.
        cropped_rows: Cleaned rows from the cropped page table extraction.

    Returns:
        The 0-based index of the matching row in cropped_rows, or -1 if no match.
    """
    # Join row cells and extract alphanumeric words (including decimals/hyphens)
    text = " ".join(body_row).lower()
    words = re.findall(r"\b[a-z0-9.-]+\b", text)
    body_words = set()
    for w in words:
        if len(w) <= 1:
            continue
        # Exclude small integers (0-99) to avoid page numbers or weak indices
        if w.isdigit() and int(w) < 100:
            continue
        body_words.add(w)
        
    if not body_words:
        return -1
        
    best_idx = -1
    best_score = 0.0
    
    for r_idx, crop_row in enumerate(cropped_rows):
        c_text = " ".join(crop_row).lower()
        c_words = re.findall(r"\b[a-z0-9.-]+\b", c_text)
        crop_words = set()
        for w in c_words:
            if len(w) <= 1:
                continue
            if w.isdigit() and int(w) < 100:
                continue
            crop_words.add(w)
            
        if not crop_words:
            continue
            
        intersection = body_words.intersection(crop_words)
        score = float(len(intersection))
        
        # Check for partial/substring word matches (e.g. "openai-o1-mini" vs "o1-mini")
        for bw in body_words:
            for cw in crop_words:
                if bw != cw and (bw in cw or cw in bw):
                    score += 0.5
                    
        if score > best_score:
            best_score = score
            best_idx = r_idx
            
    # Require a minimum score of 1.5 to be a valid match
    if best_score >= 1.5:
        return best_idx
    return -1


def _reconstruct_table_with_headers(page, table_obj) -> Optional[Tuple[List[str], List[List[str]]]]:
    """Crop a PDF page to cover a table's headers and extract the table with headers.

    Args:
        page: The pdfplumber page object.
        table_obj: The pdfplumber Table object found on the page.

    Returns:
        A tuple of (cleaned_headers, final_data_rows) or None if reconstruction fails.
    """
    bbox = table_obj.bbox
    # Expand top coordinate to cover headers (try 38 points)
    expanded_bbox = (bbox[0] - 5, bbox[1] - 38, bbox[2] + 5, bbox[3] + 5)
    
    try:
        cropped_page = page.crop(expanded_bbox)
        cropped_tabs = cropped_page.extract_tables(table_settings={
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
        })
    except Exception as e:
        print(f"Warning: Cropping page failed: {e}")
        return None
        
    if not cropped_tabs:
        return None
        
    cropped_rows = [[str(cell or "").strip() for cell in r] for r in cropped_tabs[0]]
    # Unpack cropped rows to handle newlines
    cropped_rows = _unpack_table(cropped_rows)
    # Filter out empty rows
    cropped_rows = [r for r in cropped_rows if not all(c == "" for c in r)]
    
    body_rows = [[str(cell or "").strip() for cell in r] for r in table_obj.extract()]
    # Unpack body rows to handle newlines
    body_rows = _unpack_table(body_rows)
    body_rows = [r for r in body_rows if not all(c == "" for c in r)]
    
    if not body_rows:
        return None
        
    # Find the first row in body_rows with fill_rate >= 0.35 that has a valid match in cropped_rows
    match_idx = -1
    for k, b_row in enumerate(body_rows):
        rate = _calculate_fill_rate([b_row])
        if rate < 0.35:
            continue
        m_idx = _find_best_match(b_row, cropped_rows)
        if m_idx != -1:
            match_idx = m_idx
            break
            
    if match_idx != -1:
        header_rows = cropped_rows[:match_idx]
        data_rows = cropped_rows[match_idx:]
    else:
        # Fallback if match fails
        header_rows = []
        data_rows = body_rows
        
    # Merge headers vertically
    num_cols = len(data_rows[0]) if data_rows else len(cropped_rows[0])
    merged_headers = []
    for col_idx in range(num_cols):
        col_parts = []
        for h_row in header_rows:
            if col_idx < len(h_row) and h_row[col_idx]:
                col_parts.append(h_row[col_idx])
        # Join parts and sanitize spaces
        h_text = " ".join(col_parts).strip()
        h_text = re.sub(r"\s+", " ", h_text)
        merged_headers.append(h_text)
        
    return merged_headers, data_rows


def extract_pdf_tables(pdf_path: str) -> str:
    """Extracts tables from a PDF using pdfplumber and returns them as Markdown tables.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        A Markdown formatted string representing the extracted tables.
    """
    tables_md: List[str] = []
    try:
        import pdfplumber
        import pandas as pd
    except Exception as e:
        print(f"Warning: Failed to import pdfplumber/pandas: {e}")
        return ""
        
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    # Find tables on the page using default line/grid detector
                    tables = page.find_tables()
                    
                    # Fallback to text strategy if default is empty or returns 1-col tables
                    if not tables or all(len(t.columns) <= 1 for t in tables):
                        tables_fallback = page.find_tables(table_settings={
                            "vertical_strategy": "text",
                            "horizontal_strategy": "lines",
                        })
                        if tables_fallback and not all(len(t.columns) <= 1 for t in tables_fallback):
                            tables = tables_fallback
                            
                    # Filter for valid tables first
                    valid_tables = []
                    if tables:
                        for t in tables:
                            rows = t.extract()
                            if rows and len(rows) > 1 and len(rows[0]) > 1:
                                if _calculate_fill_rate(rows) >= 0.15:
                                    valid_tables.append(t)
                                    
                    # Try to find table caption numbers in the page text
                    raw_text = page.extract_text()
                    page_text = raw_text if isinstance(raw_text, str) else ""
                    table_nums = re.findall(r"\b(?:Table|Tabel)\s+(\d+)", page_text, re.IGNORECASE)
                    unique_table_nums = []
                    for num in table_nums:
                        if num not in unique_table_nums:
                            unique_table_nums.append(num)
                            
                    for table_idx, t_obj in enumerate(valid_tables, 1):
                        # Determine table number label based on page text captions
                        assigned_num = str(table_idx)
                        if len(unique_table_nums) == len(valid_tables):
                            assigned_num = unique_table_nums[table_idx - 1]
                        elif len(unique_table_nums) == 1:
                            assigned_num = unique_table_nums[0]
                            
                        # Try cropped extraction with header recovery
                        res = _reconstruct_table_with_headers(page, t_obj)
                        if res:
                            headers, rows = res
                        else:
                            # Fallback if crop recovery failed
                            table = t_obj.extract()
                            clean_table = [[str(cell or "").strip() for cell in row] for row in table]
                            unpacked_table = _unpack_table(clean_table)
                            if not unpacked_table or len(unpacked_table) <= 1:
                                continue
                            headers = unpacked_table[0]
                            rows = unpacked_table[1:]
                            
                        # Clean duplicate or empty headers to ensure valid DataFrame columns
                        cleaned_headers = []
                        for idx, h in enumerate(headers):
                            h_clean = h.strip()
                            if not h_clean or h_clean == "-":
                                cleaned_headers.append(f"Col_{idx+1}")
                            else:
                                base = h_clean
                                counter = 1
                                while h_clean in cleaned_headers:
                                    h_clean = f"{base}_{counter}"
                                    counter += 1
                                cleaned_headers.append(h_clean)
                                
                        # Remove empty rows in data
                        final_rows = []
                        for r in rows:
                            if all(str(cell or "").strip() == "" for cell in r):
                                continue
                            final_rows.append(r)
                            
                        df = pd.DataFrame(final_rows, columns=cleaned_headers)
                        try:
                            md_table = df.to_markdown(index=False)
                        except Exception:
                            # Fallback custom markdown table formatter
                            header_str = "| " + " | ".join(cleaned_headers) + " |"
                            divider_str = "| " + " | ".join(["---"] * len(cleaned_headers)) + " |"
                            row_strs = []
                            for row in final_rows:
                                padded_row = list(row) + [""] * (len(cleaned_headers) - len(row))
                                padded_row = padded_row[:len(cleaned_headers)]
                                row_strs.append("| " + " | ".join(padded_row) + " |")
                            md_table = "\n".join([header_str, divider_str] + row_strs)
                        tables_md.append(f"### Table {assigned_num} (Page {page_num})\n\n{md_table}")
                except Exception as e:
                    print(f"Warning: Failed to extract tables from page {page_num} of PDF: {e}")
    except Exception as e:
        print(f"Warning: Failed to open PDF '{pdf_path}' for table extraction: {e}")
    return "\n\n".join(tables_md)


def extract_pdf_images(pdf_path: str, source_name: str) -> str:
    """Extracts images from PDF and saves them to global assets directory, returning Obsidian links.

    This function attempts to match extracted images with their closest figure caption
    on the page (e.g. "Figure 1", "Fig. 2") to name them meaningfully.

    Args:
        pdf_path: Path to the PDF file.
        source_name: Name of the source to use for prefixing extracted images.

    Returns:
        Markdown/Obsidian image links separated by double newlines.
    """
    sanitized_source_name = re.sub(r'[\\/:*?"<>|\s]+', "-", source_name)
    ASSETS_DIR = os.path.join("wiki", "assets", "images")
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    image_links: List[str] = []
    try:
        import fitz
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    try:
                        image_list = page.get_images()
                    except Exception:
                        image_list = []
                        
                    # Search text blocks on the page for figure captions
                    captions = []
                    try:
                        text_blocks = page.get_text("blocks")
                        for block in text_blocks:
                            text = block[4].strip()
                            match = re.search(r"\b(?:Figure|Fig\.|Gambar)\s+(\d+)", text, re.IGNORECASE)
                            if match:
                                captions.append({
                                    "rect": fitz.Rect(block[0], block[1], block[2], block[3]),
                                    "text": text,
                                    "number": match.group(1),
                                    "extracted": False
                                })
                    except Exception:
                        pass
                        
                    if not image_list and not captions:
                        continue
                        
                    # Sort captions by vertical position
                    captions.sort(key=lambda x: x["rect"].y0)
                    
                    # Extract raster images and see if they match any captions
                    extracted_xrefs = set()
                    if image_list:
                        for img_idx, img in enumerate(image_list, 1):
                            xref = img[0]
                            if xref in extracted_xrefs:
                                continue
                            extracted_xrefs.add(xref)
                            
                            try:
                                rects = page.get_image_rects(xref)
                                img_rect = rects[0] if rects else None
                                
                                # Find nearest unmatched caption
                                assigned_fig_num = None
                                best_dist = float('inf')
                                best_cap = None
                                
                                if img_rect and captions:
                                    for cap in captions:
                                        if cap["extracted"]:
                                            continue
                                        cap_rect = cap["rect"]
                                        if cap_rect.y0 >= img_rect.y1 - 10:
                                            dist = cap_rect.y0 - img_rect.y1
                                        elif cap_rect.y1 <= img_rect.y0 + 10:
                                            dist = img_rect.y0 - cap_rect.y1
                                        else:
                                            dist = abs(cap_rect.y0 - img_rect.y1)
                                            
                                        if dist < 200 and dist < best_dist:
                                            best_dist = dist
                                            best_cap = cap
                                            
                                base_image = doc.extract_image(xref)
                                image_bytes = base_image["image"]
                                image_ext = base_image["ext"]
                                
                                if best_cap:
                                    assigned_fig_num = best_cap["number"]
                                    best_cap["extracted"] = True
                                    img_name = f"source-{sanitized_source_name}-fig{assigned_fig_num}.{image_ext}"
                                else:
                                    img_name = f"source-{sanitized_source_name}-fig{page_num+1}-{img_idx}.{image_ext}"
                                    
                                img_path = os.path.join(ASSETS_DIR, img_name)
                                with open(img_path, "wb") as f:
                                    f.write(image_bytes)
                                image_links.append(f"![[{img_name}]]")
                            except Exception as e:
                                print(f"Warning: Failed to extract raster image {img_idx} on page {page_num+1}: {e}")
                                
                    # For any captions that were NOT matched to a raster image, check for vector drawings
                    try:
                        drawings = page.get_drawings()
                    except Exception:
                        drawings = []
                        
                    if drawings:
                        try:
                            page_width = page.rect.width
                            page_height = page.rect.height
                        except Exception:
                            page_width = 600
                            page_height = 800
                            
                        for idx, cap in enumerate(captions):
                            if cap["extracted"]:
                                continue
                                
                            cap_rect = cap["rect"]
                            prev_y = captions[idx-1]["rect"].y1 if idx > 0 else 0
                            min_y = max(prev_y, cap_rect.y0 - 450)
                            max_y = cap_rect.y0 + 5
                            
                            fig_bbox = fitz.Rect()
                            for path in drawings:
                                try:
                                    r = fitz.Rect(path["rect"])
                                    if r.width >= page_width * 0.9 or r.height >= page_height * 0.9:
                                        continue
                                    if r.y1 <= max_y and r.y0 >= min_y:
                                        if r.width > 2 and r.height > 2:
                                            fig_bbox.include_rect(r)
                                except Exception:
                                    pass
                                    
                            if fig_bbox.is_valid and not fig_bbox.is_empty and fig_bbox.width > 5 and fig_bbox.height > 5:
                                try:
                                    mat = fitz.Matrix(2, 2) # 2x zoom for high quality
                                    pix = page.get_pixmap(matrix=mat, clip=fig_bbox)
                                    image_bytes = pix.tobytes(output="png")
                                    
                                    img_name = f"source-{sanitized_source_name}-fig{cap['number']}.png"
                                    img_path = os.path.join(ASSETS_DIR, img_name)
                                    with open(img_path, "wb") as f:
                                        f.write(image_bytes)
                                    image_links.append(f"![[{img_name}]]")
                                    cap["extracted"] = True
                                except Exception as e:
                                    print(f"Warning: Failed to extract vector drawing for Figure {cap['number']} on page {page_num+1}: {e}")
                except Exception as e:
                    print(f"Warning: Failed to extract images from page {page_num+1} of PDF: {e}")
    except Exception as e:
        print(f"Warning: Failed to open PDF '{pdf_path}' for image extraction: {e}")
    return "\n\n".join(image_links)
