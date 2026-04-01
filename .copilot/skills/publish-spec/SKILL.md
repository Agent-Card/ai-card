---
name: publish-spec
description: >
  Build and publish the AI Catalog specification. Converts the Markdown source
  to a styled ReSpec HTML document and deploys it to Azure Static Website.
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
deploy it as a static website on Azure.

## Source Files

| File | Purpose |
|------|---------|
| `specification/ai-catalog.md` | Markdown source of truth |
| `specification/respec-config.json` | ReSpec configuration (title, abstract, appendix headers) |
| `specification/ai-catalog-respec.html` | Intermediate ReSpec HTML (generated) |
| `specification/ai-catalog-respec-static.html` | Final static HTML with TOC and styling (generated) |

## Build Pipeline

### Step 1: Generate ReSpec HTML from Markdown

```powershell
python "C:\Users\darrmi\.claude\skills\respec\scripts\build_respec.py" `
  "D:\github\agentcard\ai-card\specification\ai-catalog.md" `
  "D:\github\agentcard\ai-card\specification\ai-catalog-respec.html" `
  --config "D:\github\agentcard\ai-card\specification\respec-config.json"
```

This converts the Markdown into a ReSpec-compatible HTML document using the
config for title, abstract, and appendix header detection.

### Step 2: Render static HTML with ReSpec

```powershell
npx respec `
  -s "D:\github\agentcard\ai-card\specification\ai-catalog-respec.html" `
  -o "D:\github\agentcard\ai-card\specification\ai-catalog-respec-static.html" `
  --timeout 60
```

This runs the ReSpec processor to generate a fully self-contained static HTML
with table of contents, section numbering, cross-references, and W3C styling.

The "At least one editor is required" warning is cosmetic and does not affect output.

### Step 3: Deploy to Azure

```powershell
az storage blob upload `
  --account-name aicatalogspec `
  --container-name '$web' `
  --name index.html `
  --file "D:\github\agentcard\ai-card\specification\ai-catalog-respec-static.html" `
  --content-type "text/html" `
  --overwrite
```

## Azure Details

| Property | Value |
|----------|-------|
| Storage Account | `aicatalogspec` |
| Resource Group | `rg-ai-catalog` |
| Region | Canada East |
| Static Website URL | https://aicatalogspec.z27.web.core.windows.net/ |
| Container | `$web` |
| Index Document | `index.html` |

## One-Liner (Build + Deploy)

```powershell
python "C:\Users\darrmi\.claude\skills\respec\scripts\build_respec.py" "D:\github\agentcard\ai-card\specification\ai-catalog.md" "D:\github\agentcard\ai-card\specification\ai-catalog-respec.html" --config "D:\github\agentcard\ai-card\specification\respec-config.json" && npx respec -s "D:\github\agentcard\ai-card\specification\ai-catalog-respec.html" -o "D:\github\agentcard\ai-card\specification\ai-catalog-respec-static.html" --timeout 60 && az storage blob upload --account-name aicatalogspec --container-name '$web' --name index.html --file "D:\github\agentcard\ai-card\specification\ai-catalog-respec-static.html" --content-type "text/html" --overwrite
```

## Prerequisites

- Python 3 (for build_respec.py)
- Node.js + npm (for `npx respec`)
- Azure CLI (`az`) logged in to the Visual Studio Enterprise subscription
- The ReSpec skill's build script at `C:\Users\darrmi\.claude\skills\respec\scripts\build_respec.py`
