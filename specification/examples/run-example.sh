#!/bin/bash

set -euo pipefail

# All commands are executed relative to the directory of this script
cd "$(dirname "$0")"

# ===========================================================================
# Producer Workflow
# ===========================================================================

echo ">>> Pushing AI Manifest..."
oras push \
    --oci-layout ai-registry:example-agent \
    --export-manifest /tmp/manifest.json \
    --artifact-type application/vnd.aaif.ai.manifest.v1+json \
    --annotation "org.aaif.ai.card.id=did:example:agent-finance-001" \
    --annotation "org.aaif.ai.card.specVersion=1.0" \
    --annotation "org.opencontainers.image.created=2026-03-10T15:00:00Z" \
    --config ai-card-metadata.json:application/vnd.aaif.ai.card.metadata.v1+json \
    a2a-card.json:application/vnd.a2a.card.v1+json \
    mcp-server.json:application/vnd.mcp.card.v1+json

echo ">>> Generating signing key..."
notation cert generate-test --default "ai-manifest.test.io" || echo "already exists"

echo ">>> Signing AI Manifest..."
NOTATION_EXPERIMENTAL=1 notation sign \
    --oci-layout ai-registry:example-agent

echo ">>> Creating AI Catalog..."
oras manifest index create \
    --oci-layout ai-registry:catalog \
    --artifact-type "application/vnd.aaif.ai.catalog.v1+json" \
    example-agent

# ===========================================================================
# Consumer Workflow
# ===========================================================================

echo ">>> Fetching AI Catalog..."
oras manifest fetch \
    --oci-layout ai-registry:catalog \
    --format go-template --template '{{ toPrettyJson .content }}'

echo ">>> Fetching protocol blobs..."
for MEDIA_TYPE in "application/vnd.a2a.card.v1+json" "application/vnd.mcp.card.v1+json"; do
  BLOB_DIGEST=$(oras pull --no-tty \
      --oci-layout ai-registry:example-agent \
      --format go-template \
      --template "{{ range .files }}{{ if eq .mediaType \"$MEDIA_TYPE\" }}{{ .digest }}{{ end }}{{ end }}" \
  )

  echo "=== $MEDIA_TYPE ==="
  oras blob fetch --no-tty \
      --oci-layout "ai-registry@$BLOB_DIGEST" \
      --output -
done

echo ">>> Discovering OCI referrers..."
oras discover \
    --oci-layout ai-registry:example-agent \
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
notation policy import /tmp/trustpolicy.json

echo ">>> Verifying AI Manifest signature..."
NOTATION_EXPERIMENTAL=1 notation verify \
    --oci-layout ai-registry:example-agent \
    --scope "local/ai-registry"

# ===========================================================================
# Autodiscovery Workflow
# ===========================================================================

echo ">>> Pushing empty manifest for autodiscovery anchor..."
oras manifest push \
    --oci-layout ai-registry \
    --media-type application/vnd.oci.image.manifest.v1+json \
    empty.json

echo ">>> Injecting subject into AI Manifest..."
cat <<EOF | jq -s '.[1] * .[0]' - /tmp/manifest.json > /tmp/manifest-with-subject.json
{
    "subject": {
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "digest": "sha256:ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356",
        "size": 3
    }
}
EOF

echo ">>> Pushing AI Manifest with subject..."
oras manifest push \
    --oci-layout ai-registry \
    /tmp/manifest-with-subject.json

echo ">>> Discovering AI Manifests via constant subject..."
oras discover \
    --oci-layout ai-registry@sha256:ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356 \
    --artifact-type "application/vnd.aaif.ai.manifest.v1+json" \
    --format json

# ===========================================================================
# CDDL Conformance
# ===========================================================================

echo ">>> Validating AI Card metadata..."
cddl validate --cddl ../cddl/ai-card-metadata.cddl --json ./ai-card-metadata.json

echo ">>> Validating AI Manifest..."
oras manifest fetch \
    --oci-layout ai-registry:example-agent \
    --format go-template --template '{{ toPrettyJson .content }}' \
    | cddl validate --cddl ../cddl/ai-manifest.cddl --stdin

echo ">>> Validating AI Catalog..."
oras manifest fetch \
    --oci-layout ai-registry:catalog \
    --format go-template --template '{{ toPrettyJson .content }}' \
    | cddl validate --cddl ../cddl/ai-catalog.cddl --stdin

echo ">>> Done."

