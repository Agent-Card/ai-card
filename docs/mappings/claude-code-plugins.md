# Mapping to Claude Code Plugins Marketplace

This guide describes how the Anthropic Claude Code Plugins
marketplace format (see
[claude-plugins-official](https://github.com/anthropics/claude-plugins-official))
maps to AI Catalog, enabling Claude Code plugins to be discovered,
indexed, and distributed through a unified catalog alongside other AI
artifacts.

## Overview

The Claude Code Plugins marketplace is defined by a `marketplace.json`
file that lists available plugins. Each plugin is a directory containing
a `.claude-plugin/plugin.json` metadata file and optional components:
MCP server configurations (`.mcp.json`), slash commands (`commands/`),
agent definitions (`agents/`), and skill definitions (`skills/`).

```
marketplace.json                    # Top-level plugin directory
plugins/
  example-plugin/
    .claude-plugin/
      plugin.json                   # Plugin metadata (name, description, author)
    .mcp.json                       # MCP server config (optional)
    commands/                       # Slash commands (optional)
    agents/                         # Agent definitions (optional)
    skills/                         # Skill definitions (optional)
    README.md
```

## Conceptual Mapping

| Claude Plugins Marketplace | AI Catalog Equivalent |
|:---|:---|
| `marketplace.json` (whole file) | AI Catalog document (top-level) |
| Marketplace `name` | Catalog `host.displayName` |
| Marketplace `owner` | Catalog `host` (with `identifier` derived from owner) |
| `plugins[]` array | Catalog `entries[]` array |
| Plugin `name` | Entry `identifier` (derived as URN); the plugin manifest carries its own name, so entry `displayName` is omitted |
| Plugin `description` | Stays in the plugin manifest (which carries its own `description`); entry `description` is omitted to avoid duplicating a value that can drift |
| Plugin `category` | Entry `tags[]` (first tag) |
| Plugin `tags` | Entry `tags[]` (merged with category) |
| Plugin `author` | Entry `publisher` |
| Plugin `source` (url, git-subdir, or path) | Entry `url` (pointing to the plugin repository) |
| Plugin `source.sha` | Entry `trustManifest.provenance[].sourceDigest` |
| Plugin `.claude-plugin/plugin.json` | The artifact content (referenced via `url`) |
| *(not in marketplace)* | Entry `trustManifest` (identity, attestations) |
| *(not in marketplace)* | Entry `type` |
| Centralized marketplace repo | AI Catalog (decentralized, any URL) |

## Source Types

The marketplace supports three source types for plugins. Each maps
differently to AI Catalog entry fields:

Direct URL source
: `{"source": "url", "url": "https://github.com/org/repo.git", "sha": "..."}`
  maps to entry `url` pointing at the repository, with `sha` captured
  as provenance digest.

Git subdirectory source
: `{"source": "git-subdir", "url": "org/repo", "path": "plugins/name", "ref": "main"}`
  maps to entry `url` constructed from the repository, path, and ref.

Local path source
: `"./plugins/name"` or `"./external_plugins/name"` maps to entry `url`
  pointing at the known repository location for the plugin directory.

## Marketplace as AI Catalog

The `marketplace.json` from
[claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
maps to an AI Catalog where each plugin is an entry:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Claude Code Plugins Directory",
    "identifier": "did:web:anthropic.com",
    "documentationUrl": "https://code.claude.com/docs/en/plugins"
  },
  "entries": [
    {
      "identifier": "urn:claude-plugin:anthropic:agent-sdk-dev",
      "type": "application/vnd.anthropic.claude-plugin+json",
      "url": "https://github.com/anthropics/claude-plugins-official/tree/main/plugins/agent-sdk-dev",
      "tags": ["development"],
      "publisher": {
        "identifier": "did:web:anthropic.com",
        "displayName": "Anthropic"
      }
    },
    {
      "identifier": "urn:claude-plugin:aikido:security",
      "type": "application/vnd.anthropic.claude-plugin+json",
      "url": "https://github.com/AikidoSec/aikido-claude-plugin.git",
      "tags": ["security"],
      "publisher": {
        "identifier": "did:web:aikido.dev",
        "displayName": "Aikido Security"
      },
      "trustManifest": {
        "identity": "urn:claude-plugin:aikido:security",
        "provenance": [
          {
            "relation": "publishedFrom",
            "sourceId": "https://github.com/AikidoSec/aikido-claude-plugin",
            "sourceDigest": "sha1:d7fa8b8e192680d9a26c1a5dcaead7cf5cdb7139"
          }
        ]
      }
    }
  ]
}
```

## Plugin Packages as Nested Catalogs

A plugin that contains multiple components (MCP servers, skills,
commands, agents) naturally maps to a nested AI Catalog. This
mirrors the plugin directory structure where a single plugin
contains multiple artifact types:

```json
{
  "identifier": "urn:claude-plugin:anthropic:example-plugin",
  "displayName": "example-plugin",
  "type": "application/ai-catalog+json",
  "description": "Comprehensive plugin with commands, agents, skills, and MCP servers",
  "tags": ["development"],
  "publisher": {
    "identifier": "did:web:anthropic.com",
    "displayName": "Anthropic"
  },
  "data": {
    "specVersion": "1.0",
    "entries": [
      {
        "identifier": "urn:claude-plugin:anthropic:example-plugin:mcp",
        "type": "application/mcp-server-card+json",
        "url": "https://github.com/anthropics/claude-plugins-official/blob/main/plugins/example-plugin/server-card.json"
      },
      {
        "identifier": "urn:claude-plugin:anthropic:example-plugin:skills",
        "displayName": "Example Plugin Skills",
        "type": "application/agent-skills+zip",
        "url": "https://github.com/anthropics/claude-plugins-official/tree/main/plugins/example-plugin/skills.zip"
      }
    ]
  }
}
```

## What AI Catalog Adds to the Marketplace

The `marketplace.json` format is a lightweight directory focused on
listing available plugins. AI Catalog extends this with:

1. **Trust and identity**: The marketplace has no signing, attestation,
   or publisher verification. Trust Manifests provide verifiable
   publisher identity and compliance metadata.

2. **Source integrity**: The marketplace includes optional `sha` fields
   on source references. AI Catalog formalizes this as provenance links
   with typed relations and cryptographic digests.

3. **Cross-ecosystem discovery**: Plugins become discoverable alongside
   MCP servers, A2A agents, and other artifacts through the standard
   `/.well-known/ai-catalog.json` convention — not only within Claude
   Code's `/plugin` system.

4. **Media type identification**: The marketplace does not type its
   plugins. AI Catalog assigns `application/vnd.anthropic.claude-plugin+json`
   enabling clients to filter and route by artifact type.

5. **Composability**: Plugin packages that combine skills, MCP servers,
   and commands can be represented as nested catalogs, making the
   internal structure of a plugin package explicit and independently
   addressable.

6. **Decentralized publishing**: Any domain can publish Claude Code
   plugins via AI Catalog without submitting to the centralized
   marketplace repository.

