#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OCI_LAYOUT_DIR="${1:-$ROOT_DIR/poc/output/oci-layout}"
TITLE_FILTER="${2:-}"
A2A_MEDIA_TYPE="application/vnd.lf.ai.card.a2a.v1+json"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

need_cmd jq
need_cmd oras

INDEX_JSON="$OCI_LAYOUT_DIR/index.json"
if [[ ! -f "$INDEX_JSON" ]]; then
  echo "OCI catalog not found: $INDEX_JSON" >&2
  echo "Run ./poc/run-pr20-demo.sh first, or pass an OCI layout path as arg #1." >&2
  exit 1
fi

if [[ -n "$TITLE_FILTER" ]]; then
  manifest_digest="$(jq -r --arg t "$TITLE_FILTER" '
    .manifests[]
    | select((.annotations["org.opencontainers.image.title"] // "") == $t)
    | .digest
    ' "$INDEX_JSON" | head -n 1)"
else
  manifest_digest="$(jq -r '
    .manifests[]
    | select(.mediaType == "application/vnd.oci.image.manifest.v1+json")
    | .digest
    ' "$INDEX_JSON" | head -n 1)"
fi

if [[ -z "$manifest_digest" || "$manifest_digest" == "null" ]]; then
  echo "No manifest descriptor matched in catalog: $INDEX_JSON" >&2
  if [[ -n "$TITLE_FILTER" ]]; then
    echo "Title filter used: $TITLE_FILTER" >&2
  fi
  exit 1
fi

manifest_json="$(oras blob fetch --oci-layout --output - "$OCI_LAYOUT_DIR@$manifest_digest")"

a2a_digest="$(printf '%s' "$manifest_json" | jq -r --arg mt "$A2A_MEDIA_TYPE" '
  .layers[] | select(.mediaType == $mt) | .digest
' | head -n 1)"

if [[ -z "$a2a_digest" || "$a2a_digest" == "null" ]]; then
  echo "Selected manifest does not contain an A2A layer ($A2A_MEDIA_TYPE)." >&2
  exit 1
fi

echo "Catalog:          $INDEX_JSON"
echo "Manifest digest:  $manifest_digest"
echo "A2A layer digest: $a2a_digest"
echo
echo "A2A card JSON:"
oras blob fetch --oci-layout --output - "$OCI_LAYOUT_DIR@$a2a_digest" | jq .
