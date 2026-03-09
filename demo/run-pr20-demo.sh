#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$ROOT_DIR/demo/output"
OCI_LAYOUT_DIR="$OUT_DIR/oci-layout"
MANIFEST_JSON="$OUT_DIR/ai-manifest.demo.json"
TAG="pr20-demo"

CONFIG_REL="specification/examples/ai_config.json"
A2A_REL="specification/examples/agentcard.json"
MCP_REL="specification/examples/mcp_server.json"
CONFIG="$ROOT_DIR/$CONFIG_REL"
A2A="$ROOT_DIR/$A2A_REL"
MCP="$ROOT_DIR/$MCP_REL"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

sha256_hex() {
  shasum -a 256 "$1" | awk '{print $1}'
}

sha256_digest() {
  echo "sha256:$(sha256_hex "$1")"
}

need_cmd jq
need_cmd oras
need_cmd shasum
need_cmd awk
need_cmd wc

mkdir -p "$OUT_DIR"
rm -rf "$OCI_LAYOUT_DIR"

echo "[1/6] Computing expected OCI digests and sizes for config/layers..."
config_digest="$(sha256_digest "$CONFIG")"
a2a_digest="$(sha256_digest "$A2A")"
mcp_digest="$(sha256_digest "$MCP")"

config_size=$(wc -c < "$CONFIG" | tr -d ' ')
a2a_size=$(wc -c < "$A2A" | tr -d ' ')
mcp_size=$(wc -c < "$MCP" | tr -d ' ')

echo "  config: $config_digest ($config_size bytes)"
echo "  a2a:    $a2a_digest ($a2a_size bytes)"
echo "  mcp:    $mcp_digest ($mcp_size bytes)"

echo "[2/6] Creating OCI artifact with ORAS (and exporting manifest) ..."
cd "$ROOT_DIR"
oras push --oci-layout "$OCI_LAYOUT_DIR:$TAG" \
  --artifact-type application/vnd.lf.ai.manifest.v1+json \
  --config "$CONFIG_REL:application/vnd.lf.ai.card.config.v1+json" \
  --annotation "org.opencontainers.image.title=Acme Finance Agent" \
  --annotation "org.opencontainers.image.description=Executes finance workflows through multiple protocol adapters." \
  --annotation "org.opencontainers.image.created=2026-02-22T16:00:00Z" \
  --annotation "org.opencontainers.image.version=2026.02.22" \
  --annotation "org.opencontainers.image.vendor=Acme Financial Corp" \
  --annotation "org.lf.ai.card.id=did:example:agent-finance-001" \
  --annotation "org.lf.ai.card.specVersion=1.0" \
  --export-manifest "$MANIFEST_JSON" \
  "$A2A_REL:application/vnd.lf.ai.card.a2a.v1+json" \
  "$MCP_REL:application/vnd.lf.ai.card.mcp.v1+json"

echo "[3/6] Verifying ORAS manifest matches expected digests..."
jq -e \
  --arg config_digest "$config_digest" \
  --arg a2a_digest "$a2a_digest" \
  --arg mcp_digest "$mcp_digest" \
  '.config.digest == $config_digest and .layers[0].digest == $a2a_digest and .layers[1].digest == $mcp_digest' \
  "$MANIFEST_JSON" >/dev/null

echo "[4/6] Verifying ORAS manifest matches expected sizes..."
jq -e \
  --argjson config_size "$config_size" \
  --argjson a2a_size "$a2a_size" \
  --argjson mcp_size "$mcp_size" \
  '.config.size == $config_size and .layers[0].size == $a2a_size and .layers[1].size == $mcp_size' \
  "$MANIFEST_JSON" >/dev/null

echo "[5/6] Inspecting OCI artifact with ORAS ..."
oras manifest fetch --oci-layout "$OCI_LAYOUT_DIR:$TAG" \
  | jq -e '.artifactType == "application/vnd.lf.ai.manifest.v1+json"' >/dev/null

echo "[6/6] Printing full ORAS manifest output ..."
oras manifest fetch --oci-layout "$OCI_LAYOUT_DIR:$TAG" \
  | jq .

echo
echo "Demo complete."
echo "  Manifest JSON: $MANIFEST_JSON"
echo "  OCI layout:    $OCI_LAYOUT_DIR"
echo "  ORAS inspect:  oras manifest fetch --oci-layout \"$OCI_LAYOUT_DIR:$TAG\" | jq ."
echo "  Verify again:  oras manifest fetch --oci-layout \"$OCI_LAYOUT_DIR:$TAG\" | jq ."
