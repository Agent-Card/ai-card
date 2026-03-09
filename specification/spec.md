# AI Manifest Specification

**Version**: 1.0
**Status**: Draft
**Authors**: AI Card contributors

---

## Abstract

This specification defines an OCI-native format for publishing and distributing AI agent and artifact metadata. An AI Manifest is a standard OCI Image Manifest that carries AI identity and publisher metadata in a typed config blob, delegates protocol-specific metadata to protocol-governed layer blobs, and distributes natively through any OCI-compliant registry. AI Catalogs are standard OCI Image Indexes that aggregate AI Manifests for discovery. Signing and attestation are handled entirely via the OCI Referrers API.

---

## 1. Conformance

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

An implementation is conformant with this specification if it satisfies the normative requirements in Sections 2 through 8 applicable to its role (producer or consumer). Conformance levels are defined in Section 9.

---

## 2. Scope

This specification defines:

1. OCI manifest structure for AI agent and artifact metadata.
2. Config blob schema for AI identity and publisher metadata.
3. Layer mediaTypes for protocol cards and data asset references.
4. OCI Image Index structure for AI catalogs.
5. Discovery bindings for statically hosted and OCI registry publication.
6. Security model using OCI Referrers for signing and attestation.
7. Conformance levels for gradual adoption.

This specification does not define protocol internals (for example, A2A skills or MCP capabilities). Layer content schemas are owned by their respective upstream projects.

---

## 3. Design Goals

1. AI manifests are first-class OCI artifacts.
2. Protocols are autonomous: each protocol project owns its own layer schema and versioning.
3. OCI distribution is the canonical registry model; the statically hosted binding is a lightweight serving alternative.
4. Signing and attestation are handled entirely via OCI Referrers — no embedded signatures.
5. Content integrity is guaranteed by OCI content-addressable digests.

---

## 4. Media Types

| Type | MediaType | Description |
|---|---|---|
| AI Manifest | `application/vnd.oci.image.manifest.v1+json` | Top-level OCI manifest |
| AI Manifest artifactType | `application/vnd.lf.ai.manifest.v1+json` | Identifies manifest as an AI manifest |
| AI Card Config | `application/vnd.lf.ai.card.config.v1+json` | Config blob with AI identity/publisher metadata |
| A2A Card Layer | `application/vnd.lf.ai.card.a2a.v1+json` | A2A protocol card layer blob |
| MCP Card Layer | `application/vnd.lf.ai.card.mcp.v1+json` | MCP protocol card layer blob |
| Dataset Layer | `application/vnd.cncf.model.dataset.v1.tar` | Reused from ModelPack spec (+ gzip/zstd variants) |
| AI Catalog | `application/vnd.oci.image.index.v1+json` | OCI Image Index catalog |
| AI Catalog artifactType | `application/vnd.lf.ai.catalog.v1+json` | Identifies index as an AI catalog |

---

## 5. Data Model

### 5.1 AI Manifest

An AI Manifest is a standard OCI Image Manifest. The following fields are normative:

- `schemaVersion`: MUST be `2`.
- `mediaType`: MUST be `application/vnd.oci.image.manifest.v1+json`.
- `artifactType`: MUST be `application/vnd.lf.ai.manifest.v1+json`.
- `config`: MUST be a descriptor pointing to the AI Card Config blob (`application/vnd.lf.ai.card.config.v1+json`).
- `layers`: zero or more layer descriptors with mediaTypes defined in Section 4.
- `annotations`: MUST include the required annotations below; MAY include optional annotations.

**Required annotations:**

- `org.opencontainers.image.title`: human-readable name.
- `org.opencontainers.image.created`: RFC 3339 creation timestamp.
- `org.lf.ai.card.id`: globally unique URI identifying the subject.
- `org.lf.ai.card.specVersion`: the version of this specification, e.g. `"1.0"`.

**Optional annotations:**

- `org.opencontainers.image.description`: concise description.
- `org.opencontainers.image.version`: publisher-controlled version string.
- `org.opencontainers.image.vendor`: publisher name.

Example:

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "artifactType": "application/vnd.lf.ai.manifest.v1+json",
  "config": {
    "mediaType": "application/vnd.lf.ai.card.config.v1+json",
    "digest": "sha256:<config-blob-digest>",
    "size": 1234
  },
  "layers": [
    {
      "mediaType": "application/vnd.lf.ai.card.a2a.v1+json",
      "digest": "sha256:<a2a-layer-digest>",
      "size": 567
    },
    {
      "mediaType": "application/vnd.lf.ai.card.mcp.v1+json",
      "digest": "sha256:<mcp-layer-digest>",
      "size": 890
    }
  ],
  "annotations": {
    "org.opencontainers.image.title": "Acme Finance Agent",
    "org.opencontainers.image.description": "Executes finance workflows through multiple protocol adapters.",
    "org.opencontainers.image.created": "2026-02-22T16:00:00Z",
    "org.opencontainers.image.version": "2026.02.22",
    "org.opencontainers.image.vendor": "Acme Financial Corp",
    "org.lf.ai.card.id": "did:example:agent-finance-001",
    "org.lf.ai.card.specVersion": "1.0"
  }
}
```

### 5.2 AI Card Config Blob

The config blob has mediaType `application/vnd.lf.ai.card.config.v1+json`. It carries AI identity and publisher metadata.

The config blob MUST include:

- `specVersion`: the version of this specification.
- `descriptor`: the identity and publisher metadata object.

`descriptor` MUST include:

- `id`: globally unique URI for the subject, such as a DID or URN. MUST match `org.lf.ai.card.id` in the manifest annotations (see Section 8).
- `name`: human-readable name.
- `description`: concise description.
- `publisher`: publisher identity object (see Section 5.3).
- `createdAt`: RFC 3339 creation timestamp.
- `updatedAt`: RFC 3339 last-updated timestamp.

`descriptor` MAY include:

- `identifierType`: verification domain or scheme hint (e.g. `"did"`, `"urn"`).
- `logoUrl`, `tags`, `domains`, `skills`, `capabilities`, `maturity`.

The config blob MUST NOT include `trust` or `signatures` fields. Signing and attestation are handled via OCI Referrers (Section 7).

Example:

```json
{
  "specVersion": "1.0",
  "descriptor": {
    "id": "did:example:agent-finance-001",
    "identifierType": "did",
    "name": "Acme Finance Agent",
    "description": "Executes finance workflows through multiple protocol adapters.",
    "logoUrl": "https://acme-finance.com/logo.png",
    "tags": ["finance", "trading"],
    "domains": ["finance"],
    "skills": ["stock-analysis"],
    "capabilities": {},
    "maturity": "stable",
    "publisher": {
      "id": "did:example:org-acme",
      "name": "Acme Financial Corp",
      "identifierType": "did"
    },
    "createdAt": "2026-02-22T16:00:00Z",
    "updatedAt": "2026-02-22T16:30:00Z"
  }
}
```

### 5.3 Publisher Object

`publisher` MUST include:

- `id`: globally unique publisher URI.
- `name`: human-readable publisher name.

`publisher` MAY include:

- `identifierType`: verification domain or scheme hint.

### 5.4 Layer Blobs

Each layer is a content-addressable blob stored separately. The content schema for each layer type is defined and owned by the respective upstream project. This specification defines only the mediaType identifier and the governing project reference.

#### A2A Layer (`application/vnd.lf.ai.card.a2a.v1+json`)

Content is an A2A `AgentCard` JSON document as defined by the [A2A specification](https://github.com/a2aproject/A2A).

Example:

```json
{
  "protocolVersions": ["1.0"],
  "name": "Acme Finance Agent",
  "description": "Executes finance workflows through multiple protocol adapters.",
  "supportedInterfaces": [
    {
      "url": "https://api.acme-finance.com/a2a/v1",
      "protocolBinding": "JSONRPC"
    }
  ],
  "provider": {
    "url": "https://acme-finance.com",
    "organization": "Acme Financial Corp"
  },
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": [
    {
      "id": "skill-stock-analysis",
      "name": "Run Stock Analysis",
      "description": "Analyzes stock market data and provides investment insights.",
      "tags": ["finance", "analysis"]
    }
  ]
}
```

#### MCP Layer (`application/vnd.lf.ai.card.mcp.v1+json`)

Content is an MCP server info document as defined by the [Model Context Protocol specification](https://spec.modelcontextprotocol.io).

Example:

```json
{
  "protocolVersion": "2025-03-26",
  "serverInfo": {
    "name": "Acme MCP Server",
    "version": "1.0.0",
    "url": "https://api.acme-finance.com/mcp/v1"
  },
  "capabilities": {
    "tools": { "listChanged": true },
    "resources": { "subscribe": true },
    "prompts": {}
  }
}
```

#### Dataset Layers

Dataset layers reuse mediaTypes from the [CNCF ModelPack specification](https://github.com/modelpack/model-spec):

- `application/vnd.cncf.model.dataset.v1.tar`
- `application/vnd.cncf.model.dataset.v1.tar+gzip`
- `application/vnd.cncf.model.dataset.v1.tar+zstd`

This specification does not redefine these types. Consumers SHOULD follow the ModelPack specification for dataset layer content.

### 5.5 AI Catalog

An AI Catalog is a standard OCI Image Index with:

- `schemaVersion`: MUST be `2`.
- `mediaType`: MUST be `application/vnd.oci.image.index.v1+json`.
- `artifactType`: MUST be `application/vnd.lf.ai.catalog.v1+json`.
- `manifests`: list of OCI descriptor entries for AI Manifests.
- `annotations`: OCI annotations for catalog-level metadata.

Each manifest entry MUST have `artifactType: "application/vnd.lf.ai.manifest.v1+json"`.

Each manifest entry SHOULD include:

- `org.opencontainers.image.title`: name of the referenced agent or asset.
- `org.lf.ai.card.id`: subject identifier.

Example:

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.index.v1+json",
  "artifactType": "application/vnd.lf.ai.catalog.v1+json",
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "artifactType": "application/vnd.lf.ai.manifest.v1+json",
      "digest": "sha256:<manifest-digest>",
      "size": 1234,
      "annotations": {
        "org.opencontainers.image.title": "Acme Finance Agent",
        "org.opencontainers.image.description": "Executes finance workflows through multiple protocol adapters.",
        "org.lf.ai.card.id": "did:example:agent-finance-001"
      }
    }
  ],
  "annotations": {
    "org.opencontainers.image.title": "Acme Services Inc.",
    "org.opencontainers.image.created": "2026-02-22T16:00:00Z"
  }
}
```

---

## 6. Distribution

### 6.1 Statically Hosted Registry

A statically hosted registry is an OCI Distribution Spec–compatible read-only endpoint served from a static file store — an object storage bucket (S3, Azure Blob, GCS), a CDN origin, or a plain web server. No mutable registry process is required. Blobs and manifests are pre-computed offline and uploaded as files; the serving layer has no write path.

The registry MUST be rooted at `/.well-known/ai-registry` on the serving origin. All OCI Distribution API paths are relative to this prefix. For example:

```
https://acme-finance.com/.well-known/ai-registry/v2/default/tags/list
```

#### 6.1.1 Repository Catalog

A statically hosted registry MUST expose a repository listing at:

```
GET /.well-known/ai-registry/v2/_catalog.json
```

The response body MUST be a JSON object listing all repository names available in the registry:

```json
{
  "repositories": ["default", "finance-agent", "market-dataset"]
}
```

This is the static equivalent of the `GET /v2/_catalog` endpoint defined in the OCI Distribution Specification. Consumers use this document as the entry point for zero-configuration discovery of all hosted AI Manifests.

#### 6.1.2 Read-Only Endpoint Subset

A statically hosted registry MUST implement the following subset of the [OCI Distribution Specification](https://github.com/opencontainers/distribution-spec) read endpoints, all prefixed by `/.well-known/ai-registry`:

| ID | Method | Full Path | Description |
|---|---|---|---|
| end-1 | `GET` | `/.well-known/ai-registry/v2/` | Version check — return `{}` with `200 OK` |
| end-2 | `GET` / `HEAD` | `/.well-known/ai-registry/v2/<name>/blobs/<digest>` | Fetch or check a blob by digest |
| end-3 | `GET` / `HEAD` | `/.well-known/ai-registry/v2/<name>/manifests/<reference>` | Fetch or check a manifest by tag or digest |
| end-8a | `GET` | `/.well-known/ai-registry/v2/<name>/tags/list` | List available tags |
| end-12a | `GET` | `/.well-known/ai-registry/v2/<name>/referrers/<digest>` | List referrers for a given digest |
| end-12b | `GET` | `/.well-known/ai-registry/v2/<name>/referrers/<digest>?artifactType=<type>` | Filtered referrer listing |

All write endpoints (end-4 through end-7, end-9 through end-11, end-13 through end-14) are not implemented. The server SHOULD return `405 Method Not Allowed` for any POST, PUT, PATCH, or DELETE request.

#### 6.1.3 File Layout

The entire registry tree is rooted under `/.well-known/ai-registry/`. Content is organised in a content-addressable layout. Each repository `<name>` is a path segment, and blobs are stored keyed by their algorithm-encoded digest:

```
.well-known/ai-registry/
  v2/
    _catalog.json                        # repository listing
    <name>/
      blobs/
        sha256/
          <encoded>                      # blob content (config blob, layer blob)
      manifests/
        <tag>                            # manifest JSON, served by tag
        sha256/
          <encoded>                      # manifest JSON, served by digest
      tags/
        list.json                        # tags/list response body
      referrers/
        sha256:<encoded>/
          index.json                     # referrers image index for each subject digest
```

The URL paths defined in Section 6.1.2 map directly to file paths within this layout. A web server with static file serving, or an object storage bucket with path-based access, is sufficient to serve all required endpoints with no application logic.

#### 6.1.4 Publication Workflow

Because there is no write API, publication is an offline pre-computation step:

1. Serialise each blob (config blob, layer blobs) to canonical JSON.
2. Compute the SHA-256 digest of each blob. Store the blob at `v2/<name>/blobs/sha256/<encoded>`.
3. Construct the AI Manifest referencing each blob descriptor (mediaType, digest, size). Serialise it to canonical JSON and compute its digest. Store at `v2/<name>/manifests/sha256/<encoded>` and `v2/<name>/manifests/<tag>`.
4. Build the tags list response (`{"name":"<name>","tags":["<tag>",…]}`) and store at `v2/<name>/tags/list.json`.
5. Build a referrers image index (an OCI Image Index with `manifests` listing any attached signature or attestation manifests) for the AI Manifest digest. Store at `v2/<name>/referrers/sha256:<encoded>/index.json`. Update this file whenever a new referrer is added.
6. Rebuild `v2/_catalog.json` to include any newly added repository names.
7. Upload the entire tree under `.well-known/ai-registry/` to the file store and configure the web server or bucket to serve files at the matching URL paths.

#### 6.1.5 Consumer Discovery Flow

1. Fetch `GET /.well-known/ai-registry/v2/_catalog.json` to obtain the list of repository names.
2. For each repository `<name>`, fetch `GET /.well-known/ai-registry/v2/<name>/tags/list` to enumerate available tags.
3. For each tag, fetch `GET /.well-known/ai-registry/v2/<name>/manifests/<tag>` to retrieve the AI Manifest.
4. From the AI Manifest, resolve config and layer blobs via `GET /.well-known/ai-registry/v2/<name>/blobs/<digest>`.
5. Enumerate signatures and attestations via `GET /.well-known/ai-registry/v2/<name>/referrers/<manifest-digest>`.

### 6.2 OCI Registry

Producers MAY publish AI Manifests to any OCI-compliant registry using the OCI Distribution Specification.

Publication workflow:

1. Push each layer blob to the registry.
2. Push the config blob to the registry.
3. Push the AI Manifest referencing config and layer descriptors by digest.
4. Optionally push an AI Catalog (OCI Image Index) referencing multiple AI Manifests.

Content-addressable retrieval is guaranteed by OCI digest references. Consumers retrieve AI Manifests by tag or digest using standard OCI Distribution API calls.

---

## 7. Signing and Attestation

Signing and attestation are handled entirely outside the AI Manifest payload using the OCI Referrers API. This eliminates embedded `signatures` arrays and circular digest dependencies.

### 7.1 Signing

Producers SHOULD sign AI Manifests using cosign or notation. A signature is attached as a referrer to the AI Manifest digest. The `subject` field of the referrer manifest points to the AI Manifest descriptor (digest + mediaType + size).

cosign:

```
cosign sign registry.example.com/ai/finance-agent@sha256:<manifest-digest>
```

notation:

```
notation sign registry.example.com/ai/finance-agent@sha256:<manifest-digest>
```

### 7.2 Attestations and Provenance

Producers MAY attach SLSA provenance, SBOMs, or in-toto attestations as referrers:

```
cosign attest --predicate slsa-provenance.json --type slsaprovenance \
  registry.example.com/ai/finance-agent@sha256:<manifest-digest>
```

### 7.3 Verification

Consumers SHOULD verify signatures before trusting AI Manifest content:

```
cosign verify registry.example.com/ai/finance-agent@sha256:<manifest-digest>
```

Consumers MAY enumerate available signatures and attestations via the OCI Referrers API:

```
GET /v2/<name>/referrers/<digest>
```

---

## 8. Identifier Requirements

1. `org.lf.ai.card.id` in manifest annotations and `descriptor.id` in the config blob MUST be identical.
2. `id` MUST be a URI and SHOULD use decentralized or domain-anchored schemes (e.g. `did:` or `urn:`).
3. The identifier namespace SHOULD be verifiable by a trust mechanism appropriate to the scheme.
4. `id` is a stable logical name for the subject. It is distinct from an identity credential that proves control.
5. OCI content-addressable digests provide immutable content integrity; `id` provides stable logical identity.

---

## 9. Conformance

Implementations are classified by conformance level. Each level is cumulative.

- **L0-Base**: Produces or consumes a valid OCI manifest with a valid AI Card Config blob. No layers required.
- **L1-Discovery**: L0 + publishes to an OCI registry or serves a statically hosted registry at `/.well-known/ai-registry`.
- **L2-Signed**: L1 + attaches a cosign or notation signature via the OCI Referrers API.
- **L3-Attested**: L2 + attaches provenance or SBOM referrers (SLSA, in-toto, etc.).

---

## 10. Schemas and Examples

JSON Schemas:

- `schema/schema.json` — AI Manifest (OCI Image Manifest) schema
- `schema/catalog-schema.json` — AI Catalog (OCI Image Index) schema
- `schema/config-schema.json` — AI Card Config blob schema

CDDL definitions:

- `cddl/ai-card-profile.cddl` — AI Manifest CDDL
- `cddl/ai-catalog.cddl` — AI Catalog CDDL

Example payloads:

- `examples/converged-live-service-card.json` — AI Manifest for a live service (A2A + MCP layers)
- `examples/converged-live-service-config.json` — Config blob for the live service example
- `examples/converged-live-service-a2a-layer.json` — A2A layer blob
- `examples/converged-live-service-mcp-layer.json` — MCP layer blob
- `examples/converged-data-asset-card.json` — AI Manifest for a data asset (dataset layer)
- `examples/converged-data-asset-config.json` — Config blob for the data asset example
- `examples/converged-ai-catalog.json` — AI Catalog (OCI Image Index)
