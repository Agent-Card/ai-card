#!/bin/bash

set -euo pipefail

# All commands are executed relative to the directory of this script
cd "$(dirname "$0")"

# ===========================================================================
# Producer Workflow
# ===========================================================================

echo ">>> Pushing A2A AI Card..."
oras push \
    --oci-layout ai-registry:a2a-card \
    --export-manifest /tmp/manifest.json \
    --artifact-type application/vnd.aaif.ai.card.v1+json \
    --annotation "org.aaif.ai.card.id=did:example:agent-finance-001" \
    --annotation "org.aaif.ai.card.specVersion=1.0" \
    --annotation "org.opencontainers.image.created=2026-03-10T15:00:00Z" \
    --annotation "org.aaif.ai.discovery.domain=finance" \
    --annotation "org.aaif.ai.discovery.a2a.skill=stock-analysis" \
    --config ai-card-metadata.json:application/vnd.aaif.ai.card.metadata.v1+json \
    a2a-card.json:application/vnd.a2a.card.v1+json

echo ">>> Pushing MCP AI Card..."
oras push \
    --oci-layout ai-registry:mcp-card \
    --artifact-type application/vnd.aaif.ai.card.v1+json \
    --annotation "org.aaif.ai.card.id=did:example:agent-finance-001" \
    --annotation "org.aaif.ai.card.specVersion=1.0" \
    --annotation "org.opencontainers.image.created=2026-03-10T15:00:00Z" \
    --annotation "org.aaif.ai.discovery.domain=finance" \
    --config ai-card-metadata.json:application/vnd.aaif.ai.card.metadata.v1+json \
    mcp-server.json:application/vnd.mcp.card.v1+json

echo ">>> Generating signing key..."
notation cert generate-test --default "ai-manifest.test.io" || echo "already exists"

echo ">>> Signing A2A AI Card..."
NOTATION_EXPERIMENTAL=1 notation sign \
    --oci-layout ai-registry:a2a-card

echo ">>> Creating AI Catalog..."
oras manifest index create \
    --oci-layout ai-registry:catalog \
    --artifact-type "application/vnd.aaif.ai.catalog.v1+json" \
    a2a-card \
    mcp-card

# ===========================================================================
# Consumer Workflow
# ===========================================================================

echo ">>> Fetching AI Catalog..."
oras manifest fetch \
    --oci-layout ai-registry:catalog \
    --format go-template --template '{{ toPrettyJson .content }}'

echo ">>> Fetching protocol card from each AI Card..."
for TAG in "a2a-card" "mcp-card"; do
  echo "=== $TAG ==="
  BLOB_DIGEST=$(oras manifest fetch \
      --oci-layout "ai-registry:$TAG" \
      --format go-template \
      --template '{{ range .content.layers }}{{ .digest }}{{ end }}')
  oras blob fetch --no-tty \
      --oci-layout "ai-registry@$BLOB_DIGEST" \
      --output -
done

echo ">>> Discovering OCI referrers for A2A AI Card..."
oras discover \
    --oci-layout ai-registry:a2a-card \
    --format json

echo ">>> Creating trust policy..."
cat <<EOF > /tmp/trustpolicy.json
{
    "version": "1.0",
    "trustPolicies": [
        {
            "name": "ai-registry-policy",
            "registryScopes": [ "local/ai-registry" ],
            "signatureVerification": {
                "level" : "strict"
            },
            "trustStores": [ "ca:ai-manifest.test.io" ],
            "trustedIdentities": [
                "*"
            ]
        }
    ]
}
EOF

echo ">>> Importing trust policy..."
notation policy import --force /tmp/trustpolicy.json

echo ">>> Verifying AI Card signature..."
NOTATION_EXPERIMENTAL=1 notation verify \
    --oci-layout ai-registry:a2a-card \
    --scope "local/ai-registry"

# ===========================================================================
# Autodiscovery Workflow
# ===========================================================================

echo ">>> Pushing empty manifest for autodiscovery anchor..."
oras manifest push \
    --oci-layout ai-registry \
    --media-type application/vnd.oci.image.manifest.v1+json \
    empty.json

echo ">>> Injecting subject into A2A AI Card..."
cat <<EOF | jq -s '.[1] * .[0]' - /tmp/manifest.json > /tmp/manifest-with-subject.json
{
    "subject": {
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "digest": "sha256:ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356",
        "size": 3
    }
}
EOF

echo ">>> Pushing A2A AI Card with subject..."
oras manifest push \
    --oci-layout ai-registry \
    --media-type application/vnd.oci.image.manifest.v1+json \
    /tmp/manifest-with-subject.json

echo ">>> Discovering AI Cards via constant subject..."
oras discover \
    --oci-layout ai-registry@sha256:ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356 \
    --artifact-type "application/vnd.aaif.ai.card.v1+json" \
    --format json

# ===========================================================================
# CDDL Conformance
# ===========================================================================

echo ">>> Validating AI Card metadata..."
cddl validate --cddl ../cddl/ai-card-metadata.cddl --json ./ai-card-metadata.json

echo ">>> Validating A2A AI Card..."
oras manifest fetch \
    --oci-layout ai-registry:a2a-card \
    --format go-template --template '{{ toPrettyJson .content }}' \
    | cddl validate --cddl ../cddl/ai-card.cddl --stdin

echo ">>> Validating AI Catalog..."
oras manifest fetch \
    --oci-layout ai-registry:catalog \
    --format go-template --template '{{ toPrettyJson .content }}' \
    | cddl validate --cddl ../cddl/ai-catalog.cddl --stdin

echo ">>> Done."

