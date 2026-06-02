---
type: concept
domain: software-engineering
lang: id
translation: "[[html-maximalism]]"
tags: [html-maximalism, agent-ui, web-development, ingest]
created: 2026-06-02
updated: 2026-06-02
sources: ["[[source-the-unreasonable-effectiveness-of-html-id]]"]
description: Filosofi rekayasa yang memprioritaskan HTML asli daripada Markdown untuk hasil kerja AI agent yang kompleks guna memaksimalkan keterbacaan manusia dan interaksi dua arah.
---

# HTML Maximalism

**HTML Maximalism** adalah sebuah filosofi dokumentasi dan rekayasa perangkat lunak yang dipopulerkan dalam komunitas *agentic coding* (yang awalnya diutarakan oleh tim [[claude-code-id]] di [[anthropic-id]]). Filosofi ini merekomendasikan penggantian total atau utama dari Markdown dengan dokumen HTML asli (*native*) yang memiliki fitur lengkap untuk hampir semua hasil kerja kompleks yang diproduksi oleh AI coding agent.

Kerangka kerja ini menggeser fokus dari menulis dokumen sebagai file teks biasa (*plain text*) menjadi memperlakukannya sebagai aplikasi web interaktif yang ringan dan dibuat khusus untuk keselarasan pengembang (*developer alignment*).

## Prinsip Utama (Core Tenets)

1. **Estetika Mendorong Verifikasi (Aesthetics Drive Verification)**: Dokumen teks biasa atau Markdown standar yang melebihi batas tertentu (sekitar 100 baris) cenderung membuat pembaca bosan. Dengan me-render dokumen secara asli menggunakan *grids*, *accordions*, dan label tingkat keparahan berwarna (*colored severity annotations*), agent meningkatkan kemungkinan pengembang untuk membaca dan memverifikasi file rumit tersebut secara menyeluruh.
2. **Surplus Context Window**: Lingkungan pengembang yang lebih lama dipaksa mengoptimalkan format rendah-token seperti Markdown karena keterbatasan *prompt* yang ketat. Dengan munculnya model-model baru yang memiliki *context window* sebesar 1M+ token (seperti Gemini 1.5, GPT-4o, Claude 3.5), beban kecil dari tag HTML menjadi sangat tidak berarti, sehingga meruntuhkan hambatan konsumsi token.
3. **Interaktivitas Dua Arah (Interactive Agency)**: Dokumen seharusnya tidak hanya menjadi aset pasif. HTML *maximalism* menentang rencana "hanya-baca" dan lebih memilih *interactive artifacts* yang memiliki tombol (*buttons*), *sliders*, panel yang dapat digeser, serta formulir interaktif, yang diakhiri dengan alur ekspor sederhana ("Copy as Prompt", "Copy as JSON").
4. **Integrasi Kemampuan Agent (Agentic Capabilities Integration)**: Agent memiliki akses terminal asli dan lingkungan eksekusi *sandbox*, memungkinkan mereka menelusuri file sistem, saluran MCP, dan log git. HTML *maximalism* memanfaatkan kedalaman integrasi ini dengan menyusun ekosistem *developer* yang kaya (misalnya, peninjau *diff* kode berdampingan, *dashboards* sistem, tiket interaktif) yang melampaui kemampuan aplikasi web generik.

## Perbandingan HTML vs. Markdown

| Atribut | Markdown | HTML Maximalism |
| :--- | :--- | :--- |
| **Struktur** | Linear, satu kolom | Dinamis (*grids*, *flexbox*, kolom) |
| **Desain Visual** | Default browser teks biasa | Tidak terbatas (*CSS styles*, animasi, *dark mode*) |
| **Dukungan Media** | Gambar statis, ASCII dasar | *Inline* SVGs, *canvas*, elemen interaktif |
| **State & Interaksi** | Tidak ada | Logika *JavaScript state*, input, tombol geser |
| **Alur Kerja** | Membaca pasif | Umpan balik dua arah (opsi ekspor) |
| **Biaya Token** | Lebih rendah (teroptimasi) | Sedikit lebih tinggi (tidak terasa pada konteks besar) |

## Konsep Terkait

- [[agent-html-artifacts-id]]

## Entitas Terkait

- [[claude-code-id]]
- [[anthropic-id]]
