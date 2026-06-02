# Unified Compliance & Verification Report
Generated on: 2026-06-03 02:51:02
Target: `C:\Users\mifta\Documents\Obsidian Vault\remote-blog\01-TODO\2026\My-Wiki`

> [!TIP]
> **RTK Token Optimization Active:** Successfully detected `rtk 0.35.0` on the PATH. Native commands are configured to run with compression benefits (60-90% savings).

## Executive Compliance Dashboard

| Script Name | Category | Status | Errors ❌ | Warnings ⚠️ | Passed ✅ |
| :--- | :--- | :--- | :---: | :---: | :---: |
| `api_validator.py` | `code` | ✅ Passed | 0 | 0 | 108 |
| `i18n_checker.py` | `code` | ⚠️ Passed | 0 | 5 | 0 |
| `lint_runner.py` | `code` | ⚠️ Passed | 0 | 1 | 101 |
| `mobile_audit.py` | `code` | ✅ Passed | 0 | 0 | 3 |
| `type_coverage.py` | `code` | ✅ Passed | 0 | 0 | 2 |
| `schema_validator.py` | `db` | ✅ Passed | 0 | 0 | 0 |
| `accessibility_checker.py` | `frontend` | ✅ Passed | 0 | 0 | 0 |
| `ux_audit.py` | `frontend` | ✅ Passed | 0 | 0 | 0 |
| `security_scan.py` | `security` | ✅ Passed | 0 | 0 | 116 |
| `seo_checker.py` | `seo` | ❌ Passed | 1 | 1 | 2 |
| `geo_checker.py` | `seo` | ⚠️ Passed | 0 | 1 | 2 |
| `lighthouse_audit.py` | `frontend` | ✅ Passed | 0 | 0 | 3 |
| `test_runner.py` | `test` | ✅ Passed | 0 | 0 | 11 |
| `playwright_runner.py` | `test` | ✅ Passed | 0 | 0 | 1 |

### Total Aggregated Metrics:
- **Total Errors ❌:** 1
- **Total Warnings ⚠️:** 8
- **Total Checks Passed ✅:** 349

## Detailed Compliance Findings

### Findings for `i18n_checker.py` (code)
## Script Results: i18n_checker.py

### ❌ Errors Found (0 items)

### ⚠️ Warnings (5 items)
- [.superpowers\brainstorm\session-1\content\layout.html] Hardcoded raw text found: "Bagian 1" — consider extracting to i18n file.
- [.superpowers\brainstorm\session-1\content\layout.html] Hardcoded raw text found: "Bagian 2" — consider extracting to i18n file.
- [.superpowers\brainstorm\session-1\content\layout.html] Hardcoded raw text found: "Distilasi menjadi Cheat Sheet" — consider extracting to i18n file.
- [.superpowers\brainstorm\session-1\content\layout.html] Hardcoded raw text found: "Bagian 3" — consider extracting to i18n file.
- [.superpowers\brainstorm\session-1\content\layout.html] Hardcoded raw text found: "Visualizer Terikat Scroll" — consider extracting to i18n file.

### ✅ Passed (0 items)


### Findings for `lint_runner.py` (code)
## Script Results: lint_runner.py

### ❌ Errors Found (0 items)

### ⚠️ Warnings (1 items)
- [scripts\ingest.py:0] File is large (727 lines). Consider modularizing.

### ✅ Passed (101 items)


### Findings for `seo_checker.py` (seo)
## Script Results: seo_checker.py

### ❌ Errors Found (1 items)
- [.superpowers\brainstorm\session-1\content\layout.html] Missing <title> tag on page.

### ⚠️ Warnings (1 items)
- [.superpowers\brainstorm\session-1\content\layout.html] No <h1> tag found. Add exactly one per page.

### ✅ Passed (2 items)


### Findings for `geo_checker.py` (seo)
## Script Results: geo_checker.py

### ❌ Errors Found (0 items)

### ⚠️ Warnings (1 items)
- [.superpowers\brainstorm\session-1\content\layout.html] Missing 'lang' attribute on <html> tag.

### ✅ Passed (2 items)
