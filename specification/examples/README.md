## Producer Workflow

### Create AI Manifest

```bash
# Create and push AI Manifest with AI Card config and MCP/A2A layer blobs
oras push \
    --oci-layout ai-registry:example-agent \
    --artifact-type application/vnd.aaif.ai.manifest.v1+json \
    --annotation "org.aaif.ai.card.id=did:example:agent-finance-001" \
    --annotation "org.aaif.ai.card.specVersion=1.0" \
    --annotation "org.opencontainers.image.created=2026-03-10T15:00:00Z" \
    --config ai_config.json:application/vnd.aaif.ai.card.config.v1+json \
    a2a_card.json:application/vnd.a2a.card.v1+json \
    mcp_server.json:application/vnd.mcp.card.v1+json
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

### List AI Manifest OCI Referrers

```bash
# Show all links to OCI Manifest (e.g. signatures, metrics, etc)
oras discover \
    --oci-layout ai-registry:example-agent \
    --format json
```
