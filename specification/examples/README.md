# Example AI Manifest/Catalog usage

## Requirements

- [jq](https://github.com/jqlang/jq)
- [cddl](https://github.com/anweiss/cddl)
- [oras](https://github.com/oras-project/oras)
- [notation](https://github.com/notaryproject/notation)

## Producer Workflow

### Create AI Manifest

```bash
# Create and push AI Manifest with AI Card config and MCP/A2A layer blobs
oras push \
    --oci-layout ai-registry:example-agent \
    --export-manifest ai-registry/manifest.json \
    --artifact-type application/vnd.aaif.ai.manifest.v1+json \
    --annotation "org.aaif.ai.card.id=did:example:agent-finance-001" \
    --annotation "org.aaif.ai.card.specVersion=1.0" \
    --config ai-card-metadata.json:application/vnd.aaif.ai.card.metadata.v1+json \
    a2a-card.json:application/vnd.a2a.card.v1+json \
    mcp-server.json:application/vnd.mcp.card.v1+json
```

### Sign AI Manifest

```bash
# Generate sample signing key
notation cert generate-test --default "ai-manifest.io"

# Sign using notation
NOTATION_EXPERIMENTAL=1 notation sign \
    --oci-layout ai-registry:example-agent
```

### Create AI Catalog

```bash
# Create and push AI Catalog with example-agent
oras manifest index create \
    --oci-layout ai-registry:catalog \
    --artifact-type "application/vnd.aaif.ai.catalog.v1+json" \
    example-agent
```

## Consumer Workflow

### List AI Catalog

```bash
# Get AI Manifests using AI Catalog
oras manifest fetch \
    --oci-layout ai-registry:catalog \
    --format go-template --template '{{ toPrettyJson .content }}'
```

### List auto-discovered AI Manifests

```bash
# Get AI Manifests using constant subject digest for auto-discovery
oras discover \
    --oci-layout ai-registry@sha256:ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356 \
    --artifact-type "application/vnd.aaif.ai.manifest.v1+json" \
    --format json
```

### Get A2A/MCP Data

```bash
# Get protocol blob data from AI Manifest
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
```

### List AI Manifest OCI Referrers

```bash
# Show all links to OCI Manifest (e.g. signatures, metrics, etc)
oras discover \
    --oci-layout ai-registry:example-agent \
    --format json
```

### Verify AI Manifest Signature

```bash
# Create trust policy
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
            "trustStores": [ "ca:ai-manifest.io" ],
            "trustedIdentities": [
                "*"
            ]
        }
    ]
}
EOF

# Import policy
notation policy import /tmp/trustpolicy.json

# Verify using notation
NOTATION_EXPERIMENTAL=1 notation verify \
    --oci-layout ai-registry:example-agent \
    --scope "local/ai-registry"
```

## Autodiscovery Workflow

```bash
# Push empty manifest as constant for auto-discovery.
# The descriptor of this manifest is always the same.
# Digest: sha256:ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356
oras manifest push \
    --oci-layout ai-registry \
    --media-type application/vnd.oci.image.manifest.v1+json \
    empty.json

# Add subject to the AI manifest for autodiscovery via OCI Referrers API
# Use constant manifest to make discovery consistent across APIs.
cat <<EOF | jq -s '.[1] * .[0]' - ai-registry/manifest.json > ai-registry/manifest-with-subject.json
{
    "subject": {
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "digest": "sha256:ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356",
        "size": 3
    }
}
EOF

# Push manifest with subject for auto-discovery.
oras manifest push \
    --oci-layout ai-registry \
    ai-registry/manifest-with-subject.json

# Get AI Manifests using constant subject for auto-discovery
oras discover \
    --oci-layout ai-registry@sha256:ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356 \
    --artifact-type "application/vnd.aaif.ai.manifest.v1+json" \
    --format json
```

## CDDL Conformance

### AI Card metadata

```bash
cddl validate --cddl ../cddl/ai-card-metadata.cddl --json ./ai-card-metadata.json
```

### AI Manifest

```bash
oras manifest fetch \
    --oci-layout ai-registry:example-agent \
    --format go-template --template '{{ toPrettyJson .content }}' \
    | cddl validate --cddl ../cddl/ai-manifest.cddl --stdin
```

### AI Catalog

```bash
oras manifest fetch \
    --oci-layout ai-registry:catalog \
    --format go-template --template '{{ toPrettyJson .content }}' \
    | cddl validate --cddl ../cddl/ai-catalog.cddl --stdin
```
