# POC Scripts

This folder contains proof-of-concept scripts for the OCI-native AI Manifest flow in PR #20.

## Scripts

- `run-pr20-demo.sh`
  - Builds an OCI layout locally with ORAS.
  - Uses `specification/examples/ai_config.json`, `specification/examples/agentcard.json`, and `specification/examples/mcp_server.json`.
  - Prints the full manifest JSON.

- `extract-a2a-from-catalog.sh`
  - Reads the OCI index (`poc/output/oci-layout/index.json`).
  - Resolves a manifest descriptor from the catalog.
  - Fetches and prints the A2A layer blob JSON using ORAS.

- `extract-mcp-from-catalog.sh`
  - Reads the OCI index (`poc/output/oci-layout/index.json`).
  - Resolves a manifest descriptor from the catalog.
  - Fetches and prints the MCP layer blob JSON using ORAS.

## Prerequisites

- `oras`
- `jq`
- `shasum`

## Usage

```bash
./poc/run-pr20-demo.sh
./poc/extract-a2a-from-catalog.sh
./poc/extract-mcp-from-catalog.sh
```

Optional: extract by title

```bash
./poc/extract-a2a-from-catalog.sh poc/output/oci-layout "Acme Finance Agent"
./poc/extract-mcp-from-catalog.sh poc/output/oci-layout "Acme Finance Agent"
```

## Sample Output

### Catalog Creation (`run-pr20-demo.sh`)

```text
[1/6] Computing expected OCI digests and sizes for config/layers...
  config: sha256:62e0483c305e461bf045bf4ea7545c40d8917a6952e6e404e345c2e7727bc2f2 (391 bytes)
  a2a:    sha256:73ad9bcca5122bbf6cbe7a8f09288462ce9ff009735daf9ced66394ef320c744 (1062 bytes)
  mcp:    sha256:7ee760e03c7ccf3960a1e4cb78279aad9fb7e4d87f8b6c53729f58215d47e3b4 (420 bytes)
[2/6] Creating OCI artifact with ORAS (and exporting manifest) ...
Pushed [oci-layout] poc/output/oci-layout:pr20-demo
ArtifactType: application/vnd.lf.ai.manifest.v1+json
Digest: sha256:29818ce0f42ed87c53995b83ae11bc2e0ad86ba86023eb09acf96efeac7b7634
[3/6] Verifying ORAS manifest matches expected digests...
[4/6] Verifying ORAS manifest matches expected sizes...
[5/6] Inspecting OCI artifact with ORAS ...
[6/6] Printing full ORAS manifest output ...
```

### A2A Card Extraction (`extract-a2a-from-catalog.sh`)

```text
Catalog:          poc/output/oci-layout/index.json
Manifest digest:  sha256:29818ce0f42ed87c53995b83ae11bc2e0ad86ba86023eb09acf96efeac7b7634
A2A layer digest: sha256:73ad9bcca5122bbf6cbe7a8f09288462ce9ff009735daf9ced66394ef320c744

A2A card JSON:
{
  "name": "Acme Finance Agent",
  "description": "Executes finance workflows through multiple protocol adapters.",
  "version": "1.0.0",
  ...
}
```

### MCP Card Extraction (`extract-mcp-from-catalog.sh`)

```text
Catalog:          poc/output/oci-layout/index.json
Manifest digest:  sha256:29818ce0f42ed87c53995b83ae11bc2e0ad86ba86023eb09acf96efeac7b7634
MCP layer digest: sha256:7ee760e03c7ccf3960a1e4cb78279aad9fb7e4d87f8b6c53729f58215d47e3b4

MCP server card JSON:
{
  "protocolVersion": "2025-03-26",
  "serverInfo": {
    "name": "Acme MCP Server",
    "version": "1.0.0"
  },
  ...
}
```
