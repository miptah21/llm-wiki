# The Unreasonable Effectiveness Of HTML

**Source:** [claude.com/blog](https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html)
**Author:** Thariq Shihipar (Anthropic, Claude Code team)
**Date:** May 20, 2026
**Reading time:** 5 min

---

## Summary

Members of the Claude Code team have started preferring **HTML over Markdown** as the output format for agent-generated documents. HTML allows richer visualizations, better readability, easier sharing, and two-way interactivity — all of which keep the human more "in the loop" as agents take on more complex work.

---

## The Problem With Markdown

- Markdown is simple, portable, and easy to edit — but as agents produce longer, more complex outputs, it becomes **increasingly restrictive**.
- Files over ~100 lines rarely get read end-to-end.
- Hard to share (browsers don't render `.md` natively).
- Since the human is no longer editing these files directly (prompting Claude to edit instead), Markdown's editability advantage diminishes.

## Why HTML?

### Information Density

HTML can represent far richer information than Markdown:

- Tabular data via `<table>`
- Design data via CSS
- Illustrations via SVG
- Code snippets via `<script>` tags
- Interactions via HTML elements + JS + CSS
- Workflows via SVG and HTML
- Spatial data via absolute positioning and canvases
- Images via `<img>` tags

> "There is almost no set of information that Claude can read that you cannot efficiently represent with HTML."

Without HTML, the model resorts to ASCII diagrams or estimating colors with Unicode characters.

### Visual Clarity And Ease Of Reading

- Claude can organize HTML visually with tabs, illustrations, links, and even make it mobile-responsive.
- The chance of someone actually reading a spec or report is much higher when it's HTML.

### Ease Of Sharing

- HTML files can be uploaded and shared via link — anyone can open them in a browser.
- Markdown requires attachments or special renderers.

### Two-Way Interactions

- HTML lets you interact with the document: sliders, knobs, adjustable parameters.
- You can copy tuned values back into a prompt for Claude Code.
- Enables **custom editing environments** for specific problems.

### Data Ingestion

- Claude Code has access to the full file system, MCPs (Slack, Linear, etc.), Chrome, and git history.
- This context makes Claude Code's HTML outputs richer than what Claude.ai or Claude Design can produce alone.

## Getting Started

Just prompt:

> "Make an HTML file" or "Make an HTML artifact."

No special setup needed. Over time, build skills around recurring patterns.

## Use Cases

### 1. Specs, Planning, And Exploration

Create a web of HTML files: brainstorm → explore options → mockups → implementation plan. Pass all files into a new session for implementation.

**Example prompts:**
- *"Generate 6 distinctly different approaches for the onboarding screen — vary layout, tone, and density — lay them out as a single HTML file in a grid so I can compare side by side."*
- *"Create a thorough implementation plan in HTML with mockups, data flow, and code snippets."*

### 2. Code Review And Understanding

Render diffs, annotations, flowcharts, and modules in HTML for reviewing code or explaining PRs.

**Example prompt:**
- *"Help me review this PR by creating an HTML artifact. Render the actual diff with inline margin annotations, color-code findings by severity."*

### 3. Design And Prototypes

HTML is incredibly expressive for design, even if your target surface is React, Swift, etc. Prototype interactions with sliders, knobs, and tunable parameters.

**Example prompt:**
- *"Prototype a checkout button with a play animation. Create sliders to try different options, give me a copy button for the parameters."*

### 4. Reports, Research, And Learning

Synthesize information from multiple sources (Slack, codebase, git, internet) into readable HTML reports, interactive explainers, or slideshows.

**Example prompt:**
- *"Read the rate limiter code and produce a single HTML explainer page: token-bucket flow diagram, annotated code snippets, and a gotchas section."*

### 5. Custom Editing Interfaces

Build throwaway editors purpose-built for one piece of data. Always end with an export button ("copy as JSON," "copy as prompt").

**Example prompts:**
- *"Make an HTML file with 30 Linear tickets as draggable cards across Now / Next / Later / Cut columns. Add a 'copy as Markdown' button."*
- *"Build a form-based feature flag editor. Show dependencies, warn on prerequisite conflicts. Add a 'copy diff' button."*
- *"Make a side-by-side system prompt editor: editable prompt left, three sample inputs right that re-render live. Add token counter and copy button."*

## FAQ

**Isn't it less efficient?**
While Markdown uses fewer tokens, the added expressiveness of HTML and higher likelihood of being read means better overall output. With the 1M context window in Opus 4.7, token usage isn't noticeable.

**When do you still use Markdown?**
The author has "honestly stopped using Markdown altogether for almost everything" — self-described as "far on the HTML maximalist side."

**Has this replaced planning?**
Instead of a single plan, multiple HTML files for different parts/stages: implementation plan, UI exploration, design catalog. These persist as references for verification.

## Key Takeaway

> "The real reason I use HTML instead of Markdown is that it helps me feel much more in the loop with Claude. As Claude takes on more, I'd noticed I was reading plans less closely, and I wanted a way to stay engaged with its choices rather than just hand them off. HTML turned out to be exactly that."

---

## Related

- [[Claude Code]]
- [[HTML]]
- [[Agentic Workflows]]
