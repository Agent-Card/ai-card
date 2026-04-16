---
name: publish-spec
description: >
  Build and publish the AI Catalog specification. Converts the Markdown source
  to a styled ReSpec HTML document and publishes it via GitHub Pages.
  Trigger phrases include "publish the spec", "deploy the spec", "build the spec",
  "update the website", "rebuild the HTML".
compatibility: Copilot CLI
metadata:
  authors:
    - darrelmiller
  version: 1.0.0
---

# Publish Spec Skill

Build the AI Catalog & Trust Manifest specification from Markdown source and
publish it as a static website via GitHub Pages.

## Source Files

| File | Purpose |
|------|---------|
| `specification/ai-catalog.md` | Markdown source of truth |
| `specification/respec-config.json` | ReSpec configuration (title, abstract, appendix headers) |
| `dist/index.html` | Generated site artifact |
| `.github/workflows/publish-spec.yml` | GitHub Pages build and deploy workflow |

## Build Pipeline

### Step 1: Generate the site locally

```bash
uv run --locked python tools/build_spec.py specification/ai-catalog.md dist/index.html --config specification/respec-config.json
```

This converts the Markdown into the generated HTML site at `dist/index.html`
using the repo's `uv`-managed dependencies.

### Step 2: Publish via GitHub Pages

Push changes to the `ai-catalog-spec` branch to trigger
`.github/workflows/publish-spec.yml`, which rebuilds `dist/index.html` and
deploys it to GitHub Pages at `https://agent-card.github.io/ai-card/`.

## One-Liner (Build + Deploy)

```bash
uv run --locked python tools/build_spec.py specification/ai-catalog.md dist/index.html --config specification/respec-config.json
```

## Prerequisites

- `uv`
- Python 3.12+
- Push access to the `ai-catalog-spec` branch for GitHub Pages publication
