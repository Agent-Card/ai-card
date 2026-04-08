# Introduction

The AI ecosystem comprises a growing number of protocols, artifact
formats, and service types. Model Context Protocol (MCP) servers,
Agent-to-Agent (A2A) agents, Claude Code plugins, datasets, model cards,
and other AI artifacts each define their own metadata and discovery
mechanisms. This fragmentation forces clients and registries to
implement bespoke logic for each artifact type, increasing complexity
and reducing interoperability.

This document defines the **AI Catalog**: a typed, nestable JSON
container for discovering heterogeneous AI artifacts. Each entry
declares its artifact type via a media type and may reference or
inline the native artifact metadata. A minimal catalog is simply a
list of entries — names, types, and URLs — requiring no additional
infrastructure.

For environments that need verifiable identity, compliance evidence,
or provenance tracking, this document also defines an optional **Trust
Manifest** extension. A Trust Manifest accompanies an artifact as a
peer element, carrying attestations and provenance metadata without
wrapping or modifying the artifact's native format. Implementations
that do not need trust metadata can ignore the Trust Manifest entirely.

The AI Catalog is intentionally agnostic about the artifacts it
indexes. It does not define or constrain the schema of MCP server
manifests, A2A agent cards, or any other artifact format. Instead, it
relies on media types to identify what each entry is, and delegates
the definition of artifact-specific metadata to the respective protocol
specifications.

## Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and
"OPTIONAL" in this document are to be interpreted as described in
BCP 14 [[RFC2119]] [[RFC8174]] when, and only when, they appear in all
capitals, as shown here.

The following terms are used throughout this document:

AI Catalog
: A JSON document conforming to the `application/ai-catalog+json`
  media type that contains an ordered list of catalog entries.

Catalog Entry
: A single item in an AI Catalog, identified by a media type and
  referencing or inlining an AI artifact.

Trust Manifest
: A JSON object providing verifiable identity, attestation, and
  provenance metadata for an AI artifact.

Artifact
: Any AI resource described by a catalog entry, such as an MCP server
  manifest, an A2A agent card, a Claude Code plugin, a
  dataset descriptor, or a nested AI Catalog.

# Design Goals

1. **Artifact Agnosticism**: The catalog MUST be capable of indexing
   any type of AI artifact without requiring knowledge of the
   artifact's internal schema.

2. **Media Type Identification**: Each catalog entry MUST declare its
   artifact type using a media type, enabling clients to select,
   filter, and route entries without parsing artifact content.

3. **Composability**: The catalog format supports nesting — a catalog
   entry can reference another AI Catalog. This enables plugin-style
   packaging where a single catalog bundles multiple related artifacts.

4. **Progressive Complexity**: The simplest catalog is just entries
   with names and URLs. Trust, identity, and provenance metadata are
   available as optional extensions that never modify the catalog
   structure or artifact formats.

5. **Scalable Federation**: The catalog format enables partitioning
   into sub-catalogs to manage size, and supports delegation to
   sub-catalogs managed by independent publishers. Collections and
   nested catalogs support a federated model where each segment of
   the hierarchy may be authored, hosted, and updated independently.

6. **Location Independence**: An AI Catalog MAY be served from any URL.
   The standard defines a well-known URL convention to enable
   automated discovery, but catalogs are equally valid when hosted at
   arbitrary paths, embedded in registries, or distributed as files.

# AI Catalog

## Media Type

An AI Catalog document is identified by the media type:

    application/ai-catalog+json

## Top-Level Structure

An AI Catalog document is a JSON object that MUST contain the following
members:

`specVersion`
: A string indicating the version of this specification that the
  catalog conforms to, in "Major.Minor" format (e.g., "1.0").

`entries`
: An array of Catalog Entry objects as defined in [Catalog Entry](#catalog-entry).
  This array MAY be empty.

For example, a minimal catalog listing three AI artifacts:

```json
{
  "specVersion": "1.0",
  "entries": [
    {
      "identifier": "urn:example:skill:code-review",
      "displayName": "Code Review Assistant",
      "mediaType": "application/ai-skill",
      "url": "https://skills.example.com/code-review/skill.zip"
    },
    {
      "identifier": "urn:example:mcp:weather",
      "displayName": "Weather Service",
      "mediaType": "application/mcp-server+json",
      "url": "https://api.example.com/.well-known/mcp/server-card.json"
    },
    {
      "identifier": "urn:example:a2a:research",
      "displayName": "Research Assistant",
      "mediaType": "application/a2a-agent-card+json",
      "url": "https://agents.example.com/researchAssitant"
    }
  ]
}
```

The following members are OPTIONAL:

`host`
: A Host Info object as defined in [Host Info](#host-info) identifying the
  operator of this catalog.

`collections`
: An array of Collection Reference objects as defined in
  [Organizing Catalogs](#organizing-catalogs).

`metadata`
: An open map of string keys to arbitrary values for custom or
  non-standard metadata.

## Host Info

The Host Info object identifies the operator of the catalog. It MUST
contain:

`displayName`
: A string containing the human-readable name of the host (e.g., the
  organization name).

The following members are OPTIONAL:

`identifier`
: A string containing a verifiable identifier for the host (e.g., a
  DID or domain name).

`documentationUrl`
: A string containing a URL to the host's documentation.

`logoUrl`
: A string containing a URL to the host's logo.

`trustManifest`
: A Trust Manifest object as defined in [Trust Manifest](#trust-manifest) providing
  verifiable identity and trust metadata for the host itself.

## Catalog Entry

A Catalog Entry object describes a single AI artifact in the catalog.
It MUST contain the following members:

`identifier`
: A string identifying this artifact. This SHOULD be a URN
  [[RFC8141]] or URI [[RFC3986]] (e.g., `urn:example:agent:name`).
  See [Multi-Version Entries](#multi-version-entries) for uniqueness
  rules when multiple versions are present.

`displayName`
: A string containing a human-readable name for the artifact.

`mediaType`
: A string containing the media type that identifies the type of the
  referenced artifact. This is the mechanism by which clients
  determine what kind of AI artifact the entry represents. Well-known
  values include (but are not limited to):

  - `application/ai-catalog+json` — a nested AI Catalog
  - `application/a2a-agent-card+json` — an A2A Agent Card
  - `application/mcp-server+json` — an MCP Server manifest
  - Any other media type defined by a protocol specification (e.g.,
    `application/ai-skill` for skill definitions)

A Catalog Entry MUST contain exactly one of the following members to
provide the artifact content:

`url`
: A string containing a URL where the full artifact document can be
  retrieved. The document served at this URL SHOULD be served with
  the media type declared in the `mediaType` field.

`inline`
: A JSON value containing the complete artifact document inline. The
  structure of this value is determined by the `mediaType` field and
  is opaque to this specification.

The following members are OPTIONAL:

`description`
: A string containing a short description of the artifact.

`tags`
: An array of strings serving as keywords for filtering and discovery.

`version`
: A string containing the version of this artifact.
  [Semantic Versioning](https://semver.org/) is RECOMMENDED but not
  required. See [Multi-Version Entries](#multi-version-entries) for
  how versions interact with `identifier`.

`updatedAt`
: A string containing an ISO 8601 [[RFC3339]] timestamp indicating
  when this entry was last modified.

`metadata`
: An open map of string keys to arbitrary values for custom data.

`publisher`
: A Publisher object as defined in [Publisher Object](#publisher-object)
  identifying the entity that publishes this artifact. This is the
  sole location for publisher information; it is not duplicated in
  the Trust Manifest.

`trustManifest`
: A Trust Manifest object as defined in [Trust Manifest](#trust-manifest)
  providing verifiable identity and trust metadata for this artifact.
  See [Trust Manifest](#trust-manifest) for details.

## Multi-Version Entries

A catalog MAY contain multiple entries with the same `identifier` and
different `version` values, representing a version history for a
single artifact — similar to a package registry.

When `version` is present, the combination of `identifier` and `version`
MUST be unique within the catalog. When `version` is absent, `identifier`
alone MUST be unique. The `identifier` SHOULD be stable across versions
and catalog locations so that the same logical artifact can be
recognized wherever it appears.

Clients that need only the latest version SHOULD sort entries
sharing the same `identifier` by `version` (when parseable as a semantic
version) or by `updatedAt`, and select the most recent. Clients
that need a specific version SHOULD match on both `identifier` and `version`.

## Publisher Object

The Publisher object identifies the entity responsible for an artifact.
It appears on the Catalog Entry and is the canonical location for
publisher information. It MUST contain:

`identifier`
: A string containing a verifiable identifier for the publisher
  organization.

`displayName`
: A string containing the human-readable name of the publisher.

The following members are OPTIONAL:

`identityType`
: A string providing a type hint for the publisher identifier (e.g.,
  "did", "dns").

# Trust Manifest {#trust-manifest}

The Trust Manifest is an OPTIONAL companion to catalog entries and
host objects. It is a JSON object that provides verifiable identity,
attestation, and provenance metadata for AI artifacts.
Implementations that do not require trust metadata MAY ignore this
section entirely — a conformant AI Catalog does not require Trust
Manifests.

The Trust Manifest does NOT wrap the artifact. It sits alongside the
artifact as a peer element within a Catalog Entry, keeping the native
artifact format unmodified. Publisher information is NOT duplicated
in the Trust Manifest — the informational publisher identity is
carried on the Catalog Entry (see [Publisher Object](#publisher-object)).

## Identity

A Trust Manifest MUST contain:

`identity`
: A string containing a globally unique URI [[RFC3986]] that serves as
  the primary subject identifier for this artifact. This SHOULD be a
  DID, SPIFFE ID, or URL.

When a Trust Manifest appears within a Catalog Entry, the `identity`
field MUST match the entry's `identifier` field. This binding ensures trust
claims are unambiguously associated with the catalog artifact.
Consumers MUST reject a Trust Manifest whose `identity` does not
match the containing entry's `identifier`.

When a Trust Manifest appears on a Host Info object, `identity`
SHOULD match the host's `identifier` field when present.

When multiple entries share the same `identifier` (with different `version`
values), each entry MAY carry its own Trust Manifest. There is no
requirement that all versions carry identical trust metadata — trust
properties may evolve across versions.

## Optional Members

The following members are OPTIONAL:

`identityType`
: A string providing a type hint for the identity URI (e.g., "did",
  "spiffe", "dns"). This field is OPTIONAL when the type is evident
  from the URI scheme.

`trustSchema`
: A Trust Schema object as defined in [Trust Schema](#trust-schema-object).

`attestations`
: An array of Attestation objects as defined in [Attestation](#attestation-object).
  This is the mechanism for verifiable claims including publisher
  identity verification (using attestation type "publisher-identity"),
  compliance certifications, and other proofs.

`provenance`
: An array of Provenance Link objects as defined in
  [Provenance Link](#provenance-link-object).

`privacyPolicyUrl`
: A string containing a URL to the privacy policy governing this
  artifact.

`termsOfServiceUrl`
: A string containing a URL to the terms of service.

`signature`
: A string containing a detached JWS [[RFC7515]] signature computed
  over the Trust Manifest content. This enables integrity verification
  of the trust metadata independent of the artifact.

`metadata`
: An open map of string keys to arbitrary values for extending trust
  metadata.

## Trust Schema Object

A Trust Schema object describes the trust framework applied to the
artifact. It MUST contain:

`identifier`
: A string identifying the trust schema.

`version`
: A string indicating the schema version.

The following members are OPTIONAL:

`governanceUri`
: A string containing a URI to the governance policy document.

`verificationMethods`
: An array of strings identifying the verification methods supported
  (e.g., "did", "x509", "dns-01").

## Attestation Object

An Attestation object provides verifiable proof of a claim. It MUST
contain:

`type`
: A string identifying the attestation type (e.g., "SOC2-Type2",
  "HIPAA-Audit", "ISO27001").

`uri`
: A string containing the location of the attestation document.
  This may be an HTTPS URL or an inline Data URI [[RFC2397]].

`mediaType`
: A string indicating the format (e.g., "application/pdf",
  "application/jwt").

The following members are OPTIONAL:

`digest`
: A string containing a cryptographic hash for integrity verification
  (e.g., "sha256:abcd1234...").

`size`
: An unsigned integer indicating the size of the attestation in bytes.

`description`
: A string containing a human-readable label.

## Provenance Link Object

A Provenance Link records lineage information. It MUST contain:

`relation`
: A string describing the relationship (e.g., "materializedFrom",
  "derivedFrom", "publishedFrom").

`sourceId`
: A string identifying the source artifact or data.

The following members are OPTIONAL:

`sourceDigest`
: A string containing the digest of the source.

`registryUri`
: A string containing the URI of the registry holding the source.

`statementUri`
: A string containing the URI of a provenance statement document.

`signatureRef`
: A string referencing the key used to sign the provenance statement.

## Verification Procedures

This section describes how consumers verify the trust metadata
carried by a Trust Manifest. Verification is OPTIONAL — consumers
that do not need trust assurance can skip this entirely.

### Digest Format

Digests in this specification use the format `algorithm:hex-value`,
where `algorithm` is a hash algorithm identifier and `hex-value` is
the lowercase hexadecimal encoding of the hash output. For example:

    sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08

Producers SHOULD use SHA-256 [[RFC6234]] or stronger. Consumers
MUST reject digest values using algorithms shorter than SHA-256.

### Trust Manifest Signatures

The `signature` field carries a detached JWS [[RFC7515]] computed
over the Trust Manifest content. To create or verify a signature:

1. **Canonicalize** the Trust Manifest JSON using JCS (JSON
   Canonicalization Scheme) [[RFC8785]]. Remove the `signature`
   field itself before canonicalization.
2. **Sign** (or verify) the canonical bytes as a detached JWS
   payload using the publisher's private (or public) key.
3. **Encode** the resulting JWS in compact serialization and store
   it in the `signature` field.

This approach ensures the signature is stable regardless of JSON
key ordering or whitespace, and can be verified independently of the
artifact content.

### Key Resolution

Consumers resolve the signer's public key based on the `identity`
URI scheme:

DID (e.g., `did:web:example.com`)
: Resolve the DID Document per the relevant DID method specification
  and extract the verification key from the `verificationMethod`
  array.

HTTPS URL (e.g., `https://example.com/.well-known/jwks.json`)
: Fetch the JWK Set [[RFC7517]] at the specified URL and select the
  key matching the JWS `kid` header.

SPIFFE ID (e.g., `spiffe://example.com/service`)
: Obtain the X.509 SVID from the SPIFFE Workload API and extract
  the public key from the leaf certificate.

DNS
: Resolve the domain's TLS certificate and extract the public key,
  or look up a DNSKEY/TXT record containing the JWK thumbprint.

### Verifying Host Identity

To verify the host of a catalog:

1. Confirm the catalog was retrieved over HTTPS from the expected
   domain.
2. If `host.identifier` is a DID, resolve the DID Document and confirm the
   hosting domain appears in the DID Document's `service` endpoints.
3. If `host.trustManifest` is present and signed, verify the
   signature as described above.

### Verifying Publisher Identity

To verify the publisher of an artifact:

1. Locate the `publisher-identity` attestation in the Trust
   Manifest's `attestations` array.
2. Fetch the attestation document (typically a JWT) from the `uri`.
3. Verify the JWT signature against the publisher's public key
   (resolved from `publisher.identifier`).
4. Confirm the JWT claims bind the `publisher.identifier` to the Trust
   Manifest's `identity`.

### Verifying Artifact Integrity

When a Trust Manifest includes `provenance` entries with `sourceDigest`:

1. Fetch the artifact content from the entry's `url`.
2. Compute the digest using the algorithm specified in the
   `sourceDigest` field.
3. Compare the computed digest to the declared value. Reject the
   artifact if they differ.

### Verifying Attestations

For each attestation in the `attestations` array:

1. Fetch the attestation document from `uri`.
2. If `digest` is present, verify the fetched document matches the
   declared digest.
3. Validate the attestation per its `type` (e.g., verify a JWT
   signature, confirm a PDF certificate is current).

# Organizing Catalogs

As catalogs grow, a flat list of entries becomes unwieldy. This
specification provides two complementary mechanisms for structuring
catalogs at scale: **bundles** and **collections**. They serve
fundamentally different purposes and appear in different parts of
the document.

## Bundles (Nested Catalog Entries)

A bundle is a catalog entry whose `mediaType` is
`application/ai-catalog+json`. The entry's content (via `url` or
`inline`) is itself an AI Catalog document containing the bundled
artifacts. Bundles express **dependency**: the artifacts inside
are related and intended to be acquired or deployed together.

Use bundles when:

- A skill requires a companion MCP server to function
- A plugin ships with a dataset it depends on
- A vendor distributes a suite of agents as a single installable package

```
Vendor Catalog
  └── Entry: "Finance Plugin" (mediaType: application/ai-catalog+json)
        ├── Entry: Finance A2A Agent
        ├── Entry: Finance MCP Server
        └── Entry: Market Dataset
```

A bundle is a regular catalog entry — it has an `identifier`, may carry a
`trustManifest`, and may include a `publisher`. An entry inside a
bundle MAY reuse the same `identifier` as an entry elsewhere; this
indicates the same logical artifact.

Clients processing bundles SHOULD impose a maximum nesting depth to
prevent circular references. A depth limit of 8 is RECOMMENDED.

## Collections (Catalog Hierarchy) {#collection-reference}

Collections are an OPTIONAL top-level array on the AI Catalog. Each
element is a Collection Reference that points to a child AI Catalog
at a different URL. Collections express **organization**: they
partition a large catalog into browsable subcategories without
implying any dependency between the referenced catalogs.

Use collections when:

- An enterprise has thousands of artifacts spread across departments
- A registry wants to offer a top-level directory of vendor catalogs
- A catalog needs to be partitioned for performance or governance

A Collection Reference object MUST contain:

`displayName`
: A string containing a human-readable name for this collection
  (e.g., "Finance Services", "ML Models").

`url`
: A string containing a URL where the child AI Catalog document can
  be retrieved. The document at this URL MUST be a valid AI Catalog.

The following members are OPTIONAL:

`description`
: A string describing what this collection contains.

`tags`
: An array of strings serving as keywords for filtering and navigation.

```
Enterprise Catalog
  ├── Collection: "Finance Services" → https://acme.com/catalogs/finance.json
  ├── Collection: "ML Models"        → https://acme.com/catalogs/ml.json
  └── Collection: "DevOps Tools"     → https://acme.com/catalogs/devops.json
        ├── Collection: "CI/CD"      → https://acme.com/catalogs/devops/cicd.json
        └── Collection: "Monitoring" → https://acme.com/catalogs/devops/monitoring.json
```

Collections are recursive — a child catalog MAY itself contain
`collections`, enabling multi-level organizational hierarchies.
Clients SHOULD impose a maximum traversal depth.

## Bundles vs. Collections

| | Bundle | Collection |
|---|---|---|
| **Where** | An entry in `entries[]` | An element in `collections[]` |
| **Content** | Inline or referenced AI Catalog | URL to a separate AI Catalog |
| **Semantics** | Dependency — artifacts are consumed together | Organization — catalogs are browsed independently |
| **Identity** | Has an `identifier`, may carry `trustManifest` | Named pointer, no artifact identity |
| **Example** | "Finance Plugin" shipping agent + server + data | "Finance Department" grouping 50 artifacts |
| **Trust** | Bundle entry may have its own publisher and trust | Child catalog has its own host and publisher(s) |

A single catalog MAY use both mechanisms. For example, an enterprise
catalog could use collections to partition by department, while
individual department catalogs contain bundle entries that package
related artifacts together.

# Discovery

## Location Independence

An AI Catalog document MAY be served from any URL. It is identified
by its media type (`application/ai-catalog+json`) and its `specVersion`
field, not by its URL path. Catalogs are equally valid when hosted at
an arbitrary path, embedded in a registry response, bundled in a
package, or distributed as a local file.

When served over HTTP, the document SHOULD be served with the media
type `application/ai-catalog+json`.

## Well-Known URI

To support automated discovery, hosts MAY serve an AI Catalog at the
following well-known URI [[RFC8615]]:

    /.well-known/ai-catalog.json

Clients performing domain-level discovery SHOULD attempt to retrieve
this well-known URL. If a valid AI Catalog document is returned, the
client SHOULD use the `url` entries to retrieve individual artifacts
and their associated Trust Manifests.

Use of the well-known URI is OPTIONAL. Hosts that publish catalogs at
other locations (e.g., as part of an API response or a package
registry) are fully conformant.

## Dynamic Discovery

Implementing protocols MAY support dynamic catalog generation through
their own mechanisms, such as providing different catalog content based
on a caller's identity or query parameters. Defining dynamic discovery
behavior is out of scope for this specification.

## Link Relation Discovery

Websites MAY advertise their AI Catalog by including an `ai-catalog`
link relation in HTTP responses or HTML documents. This enables AI
agents, crawlers, and other automated clients to discover the catalog
associated with any website without prior knowledge of its location.

**HTTP Link header.** A server MAY include a `Link` header [[RFC8288]]
in HTTP responses:

    Link: <https://example.com/catalog/ai.json>; rel="ai-catalog"

**HTML `<link>` element.** An HTML page MAY include a link element in
the document head:

```html
<link rel="ai-catalog" href="/catalog/ai.json"
      type="application/ai-catalog+json">
```

**Agent-driven discovery.** AI agents that interact with websites
(for example, agents following user instructions to "find tools on
this site" or browsing on behalf of a user) SHOULD check for the
`ai-catalog` link relation on the target website. The discovery
procedure is:

1. Fetch the target URL and inspect the HTTP response headers for
   a `Link` header with `rel="ai-catalog"`.
2. If no `Link` header is present and the response is an HTML
   document, parse the document for a `<link>` element with
   `rel="ai-catalog"`.
3. If neither is found, optionally fall back to the well-known URI
   `/.well-known/ai-catalog.json` as described in
   [Well-Known URI](#well-known-uri).
4. Retrieve the discovered URL. If the response has a media type of
   `application/ai-catalog+json` and contains a valid `specVersion`
   field, treat it as the site's AI Catalog.

This mechanism allows any website to surface its AI tools, agents,
and services to visiting agents through a standard, machine-readable
pointer — without requiring changes to the site's visible content.

# Conformance Levels

This specification defines three conformance levels. Each level builds
on the previous one. Implementations MUST satisfy all requirements of
their declared level.

## Level 1: Minimal Catalog

A conformant Minimal Catalog is a JSON document with media type
`application/ai-catalog+json` that contains:

- `specVersion` — the specification version string
- `entries` — an array of Catalog Entry objects, each containing at
  minimum `identifier`, `displayName`, `mediaType`, and exactly one of `url` or
  `inline`

All other fields (`host`, `collections`, `publisher`, `trustManifest`,
`metadata`) are OPTIONAL. This level is sufficient for use cases that
only need a simple list of AI artifacts — for example, a catalog of
MCP servers or A2A agents.

## Level 2: Discoverable Catalog

In addition to Level 1 requirements, a Discoverable Catalog:

- Includes a `host` object identifying the catalog operator
- MAY be served at the well-known URI `/.well-known/ai-catalog.json`
  to enable automated domain-level discovery
- MAY include `collections` for organizational hierarchy

## Level 3: Trusted Catalog

In addition to Level 2 requirements, a Trusted Catalog:

- Includes `trustManifest` objects on entries and/or the host, as
  defined in [Trust Manifest](#trust-manifest)
- MAY include `publisher` objects on entries with verifiable identifiers
- Enables verifiable identity, compliance attestations, and provenance
  tracking

Implementations at any level are fully conformant with this
specification. Consumers MAY ignore fields defined at higher
conformance levels and SHOULD gracefully handle their absence.

# Security Considerations

## Transport Security

AI Catalogs, artifacts, and Trust Manifests MUST be served over HTTPS
(TLS 1.2 or later) to prevent tampering and eavesdropping.

## Nested Catalog Depth

Clients processing nested catalogs MUST enforce a maximum recursion
depth to prevent denial-of-service attacks via deeply nested or
circular catalog references. A maximum depth of 8 is RECOMMENDED.

## Privacy Considerations

Logo URLs SHOULD use Data URIs [[RFC2397]] to avoid leaking client
information through image fetch requests. Publishers SHOULD carefully
consider what information is included in `metadata` extension fields.

# Data Model Overview

The following diagram illustrates the relationships between the
core objects defined in this specification:

<pre class="mermaid nohighlight">
classDiagram
    class AICatalog {
        specVersion string
        entries CatalogEntry[]
        host HostInfo
        collections CollectionRef[]
    }
    class HostInfo {
        displayName string
        identifier string
        trustManifest TrustManifest
    }
    class CatalogEntry {
        identifier string
        displayName string
        mediaType string
        url | inline
        version string
        publisher Publisher
        trustManifest TrustManifest
    }
    class CollectionRef {
        displayName string
        url string
        description string
        tags string[]
    }
    class Publisher {
        identifier string
        displayName string
    }
    class TrustManifest {
        identity string
        trustSchema TrustSchema
        attestations Attestation[]
        provenance ProvenanceLink[]
        signature string
    }
    class TrustSchema {
        identifier string
        version string
        verificationMethods string[]
    }
    class Attestation {
        type string
        uri string
        mediaType string
        digest string
    }
    class ProvenanceLink {
        relation string
        sourceId string
        sourceDigest string
    }
    AICatalog --> "*" CatalogEntry : entries
    AICatalog --> "0..1" HostInfo : host
    AICatalog --> "*" CollectionRef : collections
    CatalogEntry --> "0..1" Publisher : publisher
    CatalogEntry --> "0..1" TrustManifest : trustManifest
    HostInfo --> "0..1" TrustManifest : trustManifest
    TrustManifest --> "0..1" TrustSchema : trustSchema
    TrustManifest --> "*" Attestation : attestations
    TrustManifest --> "*" ProvenanceLink : provenance
    CatalogEntry --> "0..1" AICatalog : bundle
    CollectionRef ..> AICatalog : references
</pre>

# IANA Considerations

## Media Type Registration: application/ai-catalog+json

This section registers the `application/ai-catalog+json` media type
[[RFC6838]] in the "Application" registry.

Type name:
: application

Subtype name:
: ai-catalog+json

Required parameters:
: N/A

Optional parameters:
: N/A

Encoding considerations:
: binary (UTF-8 encoded JSON [[RFC8259]])

Security considerations:
: See [Security Considerations](#security-considerations) of this document.

Interoperability considerations:
: This media type identifies a JSON document conforming to the AI
  Catalog schema defined in this specification. The document MUST
  contain `specVersion` and `entries` fields.

Published specification:
: This document

Applications that use this media type:
: AI artifact registries, agent discovery clients, package managers,
  and catalog aggregation services.

Fragment identifier considerations:
: N/A

Person & email address to contact for further information:
: Agent Card Working Group

Intended usage:
: COMMON

Restrictions on usage:
: N/A

## Link Relation Registration: ai-catalog

This section registers the `ai-catalog` link relation type in the
IANA "Link Relations" registry [[RFC8288]].

Relation Name:
: ai-catalog

Description:
: Refers to an AI Catalog document (`application/ai-catalog+json`)
  that describes AI artifacts, agents, and services associated with
  the context resource. See [Link Relation Discovery](#link-relation-discovery).

Reference:
: This document

# CDDL Schema

The following CDDL [[RFC8610]] defines the normative schema for AI
Catalog and Trust Manifest documents.

## AI Catalog

```
AICatalog = {
  specVersion: text,
  ? host: HostInfo,
  entries: [* CatalogEntry],
  ? collections: [* CollectionRef],
  ? metadata: { * text => any }
}

HostInfo = {
  displayName: text,
  ? identifier: text,
  ? documentationUrl: text,
  ? logoUrl: text,
  ? trustManifest: TrustManifest
}

CollectionRef = {
  displayName: text,
  url: text,
  ? description: text,
  ? tags: [* text]
}

CatalogEntry = {
  identifier: text,
  displayName: text,
  mediaType: text,
  (url: text // inline: any),
  ? version: text,
  ? description: text,
  ? tags: [* text],
  ? publisher: Publisher,
  ? trustManifest: TrustManifest,
  ? updatedAt: tdate,
  ? metadata: { * text => any }
}

Publisher = {
  identifier: text,
  displayName: text,
  ? identityType: text
}
```

## Trust Manifest

```
TrustManifest = {
  identity: text,
  ? identityType: text,
  ? trustSchema: TrustSchema,
  ? attestations: [* Attestation],
  ? provenance: [* ProvenanceLink],
  ? privacyPolicyUrl: text,
  ? termsOfServiceUrl: text,
  ? signature: text,
  ? metadata: { * text => any }
}

TrustSchema = {
  identifier: text,
  version: text,
  ? governanceUri: text,
  ? verificationMethods: [* text]
}

Attestation = {
  type: text,
  uri: text,
  mediaType: text,
  ? digest: text,
  ? size: uint,
  ? description: text
}

ProvenanceLink = {
  relation: text,
  sourceId: text,
  ? sourceDigest: text,
  ? registryUri: text,
  ? statementUri: text,
  ? signatureRef: text
}
```

# Example: Multi-Artifact Catalog with Nested Plugin

The following example shows an AI Catalog that contains a mix of
artifact types including a nested catalog acting as a plugin bundle:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Services Inc.",
    "identifier": "did:web:acme-corp.com",
    "documentationUrl": "https://docs.acme-corp.com/ai"
  },
  "entries": [
    {
      "identifier": "urn:acme:agent:finance-a2a",
      "displayName": "Acme Finance A2A Agent",
      "version": "2.1.0",
      "mediaType": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/finance.json",
      "description": "A2A agent for financial workflows.",
      "tags": ["finance", "a2a"],
      "publisher": {
        "identifier": "did:web:acme-corp.com",
        "displayName": "Acme Financial Corp"
      },
      "trustManifest": {
        "identity": "urn:acme:agent:finance-a2a",
        "attestations": [
          {
            "type": "publisher-identity",
            "uri": "https://trust.acme.com/certs/publisher.jwt",
            "mediaType": "application/jwt",
            "description": "Verifies did:web:acme-corp.com as publisher"
          },
          {
            "type": "SOC2-Type2",
            "uri": "https://trust.acme.com/reports/soc2.pdf",
            "mediaType": "application/pdf",
            "digest": "sha256:a1b2c3d4e5f6"
          }
        ],
        "privacyPolicyUrl": "https://acme.com/legal/privacy",
        "termsOfServiceUrl": "https://acme.com/legal/terms"
      },
      "updatedAt": "2026-03-15T10:00:00Z"
    },
    {
      "identifier": "urn:acme:server:finance-mcp",
      "displayName": "Acme Finance MCP Server",
      "version": "1.4.0",
      "mediaType": "application/mcp-server+json",
      "url": "https://api.acme-corp.com/mcp/finance.json",
      "description": "MCP server with finance tools.",
      "tags": ["finance", "mcp"],
      "updatedAt": "2026-03-15T10:00:00Z"
    },
    {
      "identifier": "urn:acme:plugin:finance-suite",
      "displayName": "Acme Finance Suite",
      "mediaType": "application/ai-catalog+json",
      "description": "Plugin bundle: A2A agent + MCP server + dataset.",
      "tags": ["finance", "plugin", "bundle"],
      "inline": {
              "specVersion": "1.0",
        "entries": [
          {
            "identifier": "urn:acme:agent:finance-a2a",
            "displayName": "Finance A2A Agent",
            "mediaType": "application/a2a-agent-card+json",
            "url": "https://api.acme-corp.com/agents/finance.json"
          },
          {
            "identifier": "urn:acme:server:finance-mcp",
            "displayName": "Finance MCP Server",
            "mediaType": "application/mcp-server+json",
            "url": "https://api.acme-corp.com/mcp/finance.json"
          },
          {
            "identifier": "urn:acme:data:market-2026q1",
            "displayName": "Market Dataset Q1 2026",
            "mediaType": "application/parquet",
            "url": "https://data.acme-corp.com/market-2026q1.parquet",
            "trustManifest": {
              "identity": "urn:acme:data:market-2026q1",
              "provenance": [
                {
                  "relation": "publishedFrom",
                  "sourceId": "oci://registry.acme.com/data/market:2026q1",
                  "sourceDigest": "sha256:99998888..."
                }
              ]
            }
          }
        ]
      },
      "trustManifest": {
        "identity": "urn:acme:plugin:finance-suite",
        "signature": "eyJhbGciOiJFUzI1NiJ9..detached"
      },
      "updatedAt": "2026-03-20T14:00:00Z"
    }
  ]
}
```

# Example: Catalog with Collections

The following example shows how an enterprise uses `collections` to
organize a large number of artifacts into browsable categories. Each
collection points to a separate AI Catalog document:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Enterprise AI",
    "identifier": "did:web:acme-corp.com"
  },
  "entries": [
    {
      "identifier": "urn:acme:agent:assistant",
      "displayName": "Acme Corporate Assistant",
      "version": "3.0.0",
      "mediaType": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/assistant.json",
      "description": "General-purpose corporate assistant agent."
    }
  ],
  "collections": [
    {
      "displayName": "Finance Services",
      "url": "https://acme-corp.com/catalogs/finance.json",
      "description": "Financial agents, MCP servers, and datasets.",
      "tags": ["finance", "trading", "compliance"]
    },
    {
      "displayName": "Engineering Tools",
      "url": "https://acme-corp.com/catalogs/engineering.json",
      "description": "CI/CD agents, code review tools, and DevOps servers.",
      "tags": ["engineering", "devops", "ci-cd"]
    },
    {
      "displayName": "ML Models",
      "url": "https://acme-corp.com/catalogs/ml-models.json",
      "description": "Model cards and inference endpoints.",
      "tags": ["ml", "models", "inference"]
    }
  ]
}
```

A catalog MAY contain both `entries` and `collections`. In this
example, the corporate assistant agent is listed directly while
department-specific artifacts are organized into child catalogs.

# Example: Claude Code Plugin Entry

An AI Catalog entry for a Claude Code plugin (per the
[Claude Plugins marketplace](https://github.com/anthropics/claude-plugins-official)):

```json
{
  "identifier": "urn:claude-plugin:endorlabs:ai-plugins",
  "displayName": "ai-plugins",
  "mediaType": "application/vnd.anthropic.claude-plugin+json",
  "url": "https://github.com/endorlabs/ai-plugins.git",
  "description": "Set up endorctl and use Endor Labs to scan, prioritize, and fix security risks across your software supply chain",
  "tags": ["security", "supply-chain"],
  "publisher": {
    "identifier": "did:web:endorlabs.com",
    "displayName": "Endor Labs"
  },
  "trustManifest": {
    "identity": "urn:claude-plugin:endorlabs:ai-plugins",
    "identityType": "did",
    "attestations": [
      {
        "type": "publisher-identity",
        "uri": "https://trust.endorlabs.com/certs/publisher.jwt",
        "mediaType": "application/jwt",
        "description": "Verifies did:web:endorlabs.com as publisher"
      }
    ],
    "provenance": [
      {
        "relation": "publishedFrom",
        "sourceId": "https://github.com/endorlabs/ai-plugins",
        "sourceDigest": "sha1:a0f1d5632b6f9e6c26eaa9806f5d8d454ca5b06f"
      }
    ]
  },
  "metadata": {
    "homepage": "https://www.endorlabs.com"
  }
}
```

# Mapping to OCI Distribution

This appendix describes how AI Catalog documents can be distributed
through OCI registries, enabling content-addressed storage, signing,
and replication using existing container infrastructure.

## Logical Format vs. Physical Distribution

The AI Catalog specification defines a **logical format**: a JSON
document with `entries`, `displayName`, `mediaType`, and `trustManifest`
fields that are immediately meaningful to anyone working with AI
artifacts. Authors write simple JSON. APIs serve simple JSON. Clients
consume simple JSON.

OCI provides a **physical distribution layer**: content-addressed
storage, cryptographic signing via Cosign/Notation, global replication
through registries, and referrer-based metadata association. These are
valuable infrastructure capabilities, but OCI's data model uses
container-oriented vocabulary (`manifests`, `layers`, `config`,
`digest`) that does not naturally describe a catalog of AI artifacts.

This specification treats OCI as one distribution option, not as the
canonical data model. The logical AI Catalog format remains the
authoring and consumption interface. Tooling bridges the two:

```
Authoring                         Distribution                    Consumption
─────────                         ────────────                    ───────────
ai-catalog.json    ──pack──►    OCI Registry     ──unpack──►   ai-catalog.json
  entries[]                       Index/Manifests                  entries[]
  trustManifest                   Referrers                        trustManifest
```

This separation means:

- **Simplicity for authors**: Publishers write AI Catalog JSON using
  domain vocabulary. No knowledge of OCI manifests, digests, or layer
  descriptors is required.
- **Simplicity for consumers**: Clients that fetch from
  `/.well-known/ai-catalog.json` or a registry API receive the logical
  JSON format. They never need to parse OCI structures.
- **Power for infrastructure**: Registries that want content-addressed
  integrity, signing, and replication can store catalogs as OCI
  artifacts using the mapping defined below.

## Conceptual Mapping

The OCI image specification (v1.1+) supports arbitrary artifact types
through the `artifactType` field. The following table maps AI Catalog
concepts to their OCI physical equivalents:

| AI Catalog (Logical) | OCI (Physical) |
|:---|:---|
| AI Catalog document | OCI Image Index with `artifactType: "application/ai-catalog+json"` |
| Catalog Entry | OCI Image Manifest with `artifactType` set to the entry's `mediaType` |
| Entry `mediaType` | Manifest `artifactType` field |
| Entry artifact content | Manifest `layers[0]` blob (the protocol-specific document) |
| Entry metadata (name, tags, publisher) | Manifest `config` blob and/or `annotations` |
| Nested Catalog | Nested OCI Image Index referenced from the parent index |
| Trust Manifest | OCI Referrer artifact with `subject` pointing to the entry manifest |
| Trust Manifest attestations | Individual OCI Referrer artifacts per attestation |
| Signing | Cosign / Notation signatures as OCI Referrers |

## Packing: AI Catalog to OCI

Tooling converts an AI Catalog JSON document into OCI artifacts:

1. **Each catalog entry** becomes an OCI Image Manifest. The entry's
   artifact content (A2A card, MCP manifest, skill definition) is
   stored as a `layers[0]` blob. Common metadata (name, description,
   publisher) is stored as the `config` blob or as `annotations`.

2. **The catalog itself** becomes an OCI Image Index whose `manifests`
   array references the per-entry manifests by digest.

3. **Trust Manifests** become OCI Referrer artifacts attached to their
   entry manifests via the `subject` field. Attestation documents
   (JWTs, PDFs, SLSA provenance) become individual referrer layers.

4. **Nested catalogs** become nested OCI Image Indexes.

```
oci://registry.acme.com/ai-catalog:latest          (Image Index)
  ├── manifest: finance-a2a-agent                   (Manifest)
  │     ├── config: { name, description, publisher }
  │     ├── layers[0]: a2a-card.json
  │     └── referrer: trust-manifest                (Referrer)
  │           ├── config: trust-manifest.json
  │           └── layers: [publisher.jwt, soc2.pdf]
  ├── manifest: finance-mcp-server                  (Manifest)
  │     ├── config: { name, description }
  │     └── layers[0]: mcp-server.json
  └── index: finance-suite                          (Nested Index)
        ├── manifest: suite-a2a-agent
        └── manifest: suite-mcp-server
```

## Unpacking: OCI to AI Catalog

Tooling converts OCI artifacts back to an AI Catalog JSON document:

1. Fetch the OCI Image Index for the catalog.
2. For each manifest in the index, extract the `config` blob
   (entry metadata) and `layers[0]` blob (artifact content).
3. Query the Referrers API for each manifest to discover Trust
   Manifests and attestations.
4. Assemble the logical AI Catalog JSON with `entries[]` and
   `trustManifest` fields.

The result is a standard `application/ai-catalog+json` document
indistinguishable from one authored by hand.

## OCI Image Index Example

The following shows the OCI physical representation of an AI Catalog
containing two entries. Note that this is generated by tooling, not
authored by hand:

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.index.v1+json",
  "artifactType": "application/ai-catalog+json",
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "digest": "sha256:aaa111...",
      "size": 1024,
      "artifactType": "application/a2a-agent-card+json",
      "annotations": {
        "ai-catalog.identifier": "urn:acme:agent:finance-a2a",
        "ai-catalog.displayName": "Acme Finance A2A Agent"
      }
    },
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "digest": "sha256:bbb222...",
      "size": 512,
      "artifactType": "application/mcp-server+json",
      "annotations": {
        "ai-catalog.identifier": "urn:acme:server:finance-mcp",
        "ai-catalog.displayName": "Acme Finance MCP Server"
      }
    }
  ],
  "annotations": {
    "ai-catalog.specVersion": "1.0",
    "ai-catalog.host.displayName": "Acme Services Inc."
  }
}
```

## Signing and Verification

Because OCI distribution uses content-addressed digests, signing is
handled by existing OCI tooling rather than embedded signature fields:

```
# Sign an entry manifest
cosign sign registry.example.com/ai/finance-a2a@sha256:aaa111...

# Verify
cosign verify registry.example.com/ai/finance-a2a@sha256:aaa111...

# Attach SLSA provenance
cosign attest --predicate provenance.json --type slsaprovenance \
  registry.example.com/ai/finance-a2a@sha256:aaa111...
```

These signatures and attestations are discoverable via the OCI
Referrers API and can be mapped back to Trust Manifest attestation
objects during unpacking.

## Relationship to OCI-Native Proposals

Some proposals (such as the AAIF AI Card OCI schema) take an
OCI-native approach where the OCI Image Manifest *is* the data model.
In that model, the AI Card is an OCI Manifest, protocol cards are
OCI layers, and the catalog is an OCI Image Index consumed directly.

This specification takes a different position: the logical JSON format
is the primary interface, and OCI is a distribution substrate. The
tradeoffs are:

| Concern | Logical-first (this spec) | OCI-native |
|:---|:---|:---|
| Authoring | Write simple JSON with domain vocabulary | Write JSON conforming to OCI Manifest schema |
| Vocabulary | `entries`, `displayName`, `mediaType`, `trustManifest` | `manifests`, `layers`, `config`, `annotations` |
| Minimum viable serving | Static JSON file at any URL (optionally well-known) | OCI registry or static OCI layout |
| Signing | Detached JWS in logical format; Cosign/Notation in OCI | Cosign/Notation only |
| Content integrity | Optional digests in Trust Manifest | Guaranteed by OCI content-addressing |
| Ecosystem compatibility | Any HTTP server, any registry, any CDN | OCI-compliant registries |
| Adoption barrier | Low — familiar JSON | Higher — requires OCI familiarity |

Both approaches can coexist. A tooling bridge converts between them
losslessly, allowing simple consumers to work with the logical format
while infrastructure-oriented deployments leverage OCI distribution.

# Mapping to MCP Registry server.json

This appendix describes how the MCP Registry `server.json` format
(see [modelcontextprotocol/registry](https://github.com/modelcontextprotocol/registry))
relates to AI Catalog, enabling MCP servers to be discovered alongside
other AI artifacts through a unified catalog.

## Overview

The MCP Registry defines a `server.json` format for describing MCP
servers. Each `server.json` document captures everything needed to
install, configure, and connect to a single MCP server: package
coordinates (npm, PyPI, NuGet, OCI), remote endpoints (streamable-http,
SSE), transport configuration, environment variables, and CLI arguments.

In AI Catalog terms, a `server.json` document is the **artifact
content** — the native metadata that a Catalog Entry references. The
AI Catalog does not duplicate or redefine `server.json` fields.
Instead, it provides the discovery envelope and trust layer that
`server.json` does not address.

## Conceptual Mapping

| MCP `server.json` | AI Catalog Equivalent |
|:---|:---|
| `server.json` document (whole file) | Artifact content via entry `url` or `inline` |
| `name` (reverse-DNS identifier) | Entry `identifier` (mapped to URI form) |
| `title` | Entry `displayName` |
| `description` | Entry `description` |
| `version` | Entry `version` |
| `repository` | Entry `metadata.repository` |
| `packages[]` (npm, pypi, nuget, oci) | Inside the artifact — not surfaced in catalog |
| `remotes[]` (streamable-http, sse) | Inside the artifact — not surfaced in catalog |
| `environmentVariables[]` | Inside the artifact — not surfaced in catalog |
| `_meta` | Entry `metadata` for catalog-level hints; otherwise stays in artifact |
| *(not in server.json)* | Entry `publisher` |
| *(not in server.json)* | Entry `trustManifest` (identity, attestations, provenance) |
| *(not in server.json)* | Entry `tags` for cross-artifact discovery |
| MCP Registry (centralized service) | AI Catalog (decentralized, any URL) |

## Separation of Concerns

The `server.json` format and AI Catalog address different concerns:

server.json (Operational)
: How do I install this server? What packages, transports, arguments,
  and environment variables does it need?

AI Catalog (Discovery + Trust)
: What servers exist? Who published them? Can I trust them? Where is
  their metadata?

This separation means the AI Catalog entry is thin — it points at the
`server.json` and adds only what `server.json` lacks: publisher
identity, trust verification, and cross-ecosystem discoverability.

## MCP Server as Catalog Entry

An MCP server described by a `server.json` maps to a Catalog Entry
with `mediaType` set to `application/mcp-server+json`:

```json
{
  "identifier": "urn:mcp:io.modelcontextprotocol.anonymous/brave-search",
  "displayName": "Brave Search",
  "version": "1.0.2",
  "mediaType": "application/mcp-server+json",
  "url": "https://registry.modelcontextprotocol.io/servers/brave-search/server.json",
  "description": "MCP server for Brave Search API integration",
  "tags": ["search", "brave", "web"],
  "publisher": {
    "identifier": "did:web:modelcontextprotocol.io",
    "displayName": "Model Context Protocol"
  },
  "trustManifest": {
    "identity": "urn:mcp:io.modelcontextprotocol.anonymous/brave-search",
    "attestations": [
      {
        "type": "publisher-identity",
        "uri": "https://registry.modelcontextprotocol.io/certs/publisher.jwt",
        "mediaType": "application/jwt",
        "description": "Verifies did:web:modelcontextprotocol.io as publisher"
      }
    ],
    "provenance": [
      {
        "relation": "publishedFrom",
        "sourceId": "https://github.com/modelcontextprotocol/servers",
        "registryUri": "https://registry.npmjs.org"
      }
    ]
  },
  "metadata": {
    "repository": "https://github.com/modelcontextprotocol/servers"
  },
  "updatedAt": "2026-03-15T10:00:00Z"
}
```

The `url` points to the complete `server.json`. A client fetches the
catalog entry for discovery and trust evaluation, then retrieves the
`server.json` for operational details (packages, transports, env vars).

## MCP Registry as AI Catalog

The MCP Registry — a centralized index of MCP servers — can be
represented as an AI Catalog. This enables clients that understand
`application/ai-catalog+json` to discover MCP servers alongside A2A
agents, skills, and other artifacts:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "MCP Server Registry",
    "identifier": "did:web:modelcontextprotocol.io",
    "documentationUrl": "https://modelcontextprotocol.io/docs"
  },
  "entries": [
    {
      "identifier": "urn:mcp:io.modelcontextprotocol.anonymous/brave-search",
      "displayName": "Brave Search",
      "version": "1.0.2",
      "mediaType": "application/mcp-server+json",
      "url": "https://registry.modelcontextprotocol.io/servers/brave-search/server.json",
      "description": "MCP server for Brave Search API integration",
      "tags": ["search", "brave"]
    },
    {
      "identifier": "urn:mcp:io.github.modelcontextprotocol/filesystem",
      "displayName": "Filesystem",
      "version": "1.0.2",
      "mediaType": "application/mcp-server+json",
      "url": "https://registry.modelcontextprotocol.io/servers/filesystem/server.json",
      "description": "MCP server for filesystem operations",
      "tags": ["filesystem", "files"]
    },
    {
      "identifier": "urn:mcp:io.github.example/weather-mcp",
      "displayName": "Weather",
      "version": "0.5.0",
      "mediaType": "application/mcp-server+json",
      "url": "https://registry.modelcontextprotocol.io/servers/weather/server.json",
      "description": "Python MCP server for weather data access",
      "tags": ["weather", "python"],
      "publisher": {
        "identifier": "did:web:example.github.io",
        "displayName": "Example Corp"
      }
    }
  ]
}
```

## Decentralized Discovery

The MCP Registry is a centralized service. AI Catalog enables
decentralized discovery: any domain can publish its MCP servers at
`/.well-known/ai-catalog.json` without registering with a central
authority.

A vendor hosting its own MCP servers can publish:

```
https://api.acme-corp.com/.well-known/ai-catalog.json
```

Clients and crawlers discover the catalog via the well-known URL,
find entries with `mediaType: "application/mcp-server+json"`, and
fetch the `server.json` documents for operational details.

The centralized MCP Registry and decentralized AI Catalogs are
complementary. The registry can serve an AI Catalog as its response
format, while individual domains publish their own catalogs for
direct discovery.

## What AI Catalog Adds to server.json

The `server.json` format has no trust or identity layer. AI Catalog
fills this gap:

1. **Publisher identity**: Verifiable publisher with DID or domain
   anchor, absent from `server.json`.
2. **Trust verification**: Attestations (SOC2, HIPAA, publisher
   identity proofs) via the Trust Manifest.
3. **Provenance**: Links to source repositories, registries, and
   build artifacts with cryptographic digests.
4. **Signing**: Detached JWS signature on the Trust Manifest for
   integrity verification.
5. **Cross-ecosystem discovery**: MCP servers become discoverable
   alongside A2A agents, plugins, and datasets through a single
   catalog format.
6. **Composability**: MCP servers can be bundled with related
   artifacts (A2A agents, datasets) in nested catalogs.

## Relationship to MCP Server Cards (SEP-1649)

MCP Server Cards
([SEP-1649](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649))
define a static discovery document for individual HTTP-based MCP
servers at `/.well-known/mcp/server-card.json`. A Server Card mirrors
the MCP initialization handshake response: it carries the server's
name, version, transport configuration, capabilities, authentication
requirements, and optionally the full list of tools, resources, and
prompts.

AI Catalog and MCP Server Cards address different layers of discovery:

MCP Server Card (per-server)
: What does this specific MCP server offer? What transport does it
  use? What tools and resources are available? What authentication
  is required?

AI Catalog (cross-artifact)
: What artifacts does this domain offer? Who published them? Can I
  trust them? What other artifact types are available alongside MCP
  servers?

The two mechanisms layer naturally. An AI Catalog entry for an MCP
server can reference the Server Card as its artifact content:

```json
{
  "identifier": "urn:mcp:example.com:finance-server",
  "displayName": "Acme Finance MCP Server",
  "mediaType": "application/mcp-server-card+json",
  "url": "https://api.acme-corp.com/.well-known/mcp/server-card.json",
  "description": "MCP server for financial data and trading tools",
  "tags": ["finance", "mcp"],
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  },
  "trustManifest": {
    "identity": "urn:mcp:example.com:finance-server",
    "attestations": [
      {
        "type": "publisher-identity",
        "uri": "https://trust.acme-corp.com/certs/publisher.jwt",
        "mediaType": "application/jwt"
      },
      {
        "type": "SOC2-Type2",
        "uri": "https://trust.acme-corp.com/reports/soc2.pdf",
        "mediaType": "application/pdf",
        "digest": "sha256:a1b2c3d4e5f6"
      }
    ]
  }
}
```

A client discovering MCP servers follows this flow:

1. Fetch `/.well-known/ai-catalog.json` to discover all artifacts on
   a domain (MCP servers, A2A agents, plugins, etc.).
2. Filter entries by `mediaType` to find MCP servers.
3. Evaluate the Trust Manifest for publisher identity and attestations.
4. Fetch the Server Card at the entry's `url` for operational details
   (transport, capabilities, tools, authentication).
5. Connect to the MCP server using the transport configuration from
   the Server Card.

This separation ensures that AI Catalog provides the trust and
cross-ecosystem indexing layer, while the MCP Server Card provides the
protocol-specific operational details. A domain with multiple MCP
servers publishes one AI Catalog listing all of them, with each entry
pointing to its respective Server Card.

# Mapping to Claude Code Plugins Marketplace

This appendix describes how the Anthropic Claude Code Plugins
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
| Marketplace `description` | Catalog `metadata.description` |
| Marketplace `owner` | Catalog `host` (with `identifier` derived from owner) |
| `plugins[]` array | Catalog `entries[]` array |
| Plugin `name` | Entry `displayName` and `identifier` (derived as URN) |
| Plugin `description` | Entry `description` |
| Plugin `category` | Entry `tags[]` (first tag) |
| Plugin `tags` | Entry `tags[]` (merged with category) |
| Plugin `author` | Entry `publisher` |
| Plugin `source` (url, git-subdir, or path) | Entry `url` (pointing to the plugin repository) |
| Plugin `source.sha` | Entry `trustManifest.provenance[].sourceDigest` |
| Plugin `homepage` | Entry `metadata.homepage` |
| Plugin `.claude-plugin/plugin.json` | The artifact content (referenced via `url`) |
| *(not in marketplace)* | Entry `trustManifest` (identity, attestations) |
| *(not in marketplace)* | Entry `mediaType` |
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
      "displayName": "agent-sdk-dev",
      "mediaType": "application/vnd.anthropic.claude-plugin+json",
      "url": "https://github.com/anthropics/claude-plugins-official/tree/main/plugins/agent-sdk-dev",
      "description": "Development kit for working with the Claude Agent SDK",
      "tags": ["development"],
      "publisher": {
        "identifier": "did:web:anthropic.com",
        "displayName": "Anthropic"
      },
      "metadata": {
        "homepage": "https://github.com/anthropics/claude-plugins-public/tree/main/plugins/agent-sdk-dev"
      }
    },
    {
      "identifier": "urn:claude-plugin:adspirer:ads-agent",
      "displayName": "adspirer-ads-agent",
      "mediaType": "application/vnd.anthropic.claude-plugin+json",
      "url": "https://github.com/amekala/adspirer-mcp-plugin.git",
      "description": "Cross-platform ad management for Google Ads, Meta Ads, TikTok Ads, and LinkedIn Ads.",
      "tags": ["productivity", "ads"],
      "metadata": {
        "homepage": "https://www.adspirer.com"
      },
      "trustManifest": {
        "identity": "urn:claude-plugin:adspirer:ads-agent",
        "provenance": [
          {
            "relation": "publishedFrom",
            "sourceId": "https://github.com/amekala/adspirer-mcp-plugin",
            "sourceDigest": "sha1:aa70dbdbbbb843e94a794c10c2b13f5dd66b5e40"
          }
        ]
      }
    },
    {
      "identifier": "urn:claude-plugin:aikido:security",
      "displayName": "aikido",
      "mediaType": "application/vnd.anthropic.claude-plugin+json",
      "url": "https://github.com/AikidoSec/aikido-claude-plugin.git",
      "description": "Aikido Security scanning — SAST, secrets, and IaC vulnerability detection.",
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

## Plugin Bundles as Nested Catalogs

A plugin that bundles multiple components (MCP servers, skills,
commands, agents) naturally maps to a nested AI Catalog. This
mirrors the plugin directory structure where a single plugin
contains multiple artifact types:

```json
{
  "identifier": "urn:claude-plugin:anthropic:example-plugin",
  "displayName": "example-plugin",
  "mediaType": "application/ai-catalog+json",
  "description": "Comprehensive plugin with commands, agents, skills, and MCP servers",
  "tags": ["development", "bundle"],
  "publisher": {
    "identifier": "did:web:anthropic.com",
    "displayName": "Anthropic"
  },
  "inline": {
      "specVersion": "1.0",
    "entries": [
      {
        "identifier": "urn:claude-plugin:anthropic:example-plugin:mcp",
        "displayName": "Example Plugin MCP Server",
        "mediaType": "application/mcp-server+json",
        "url": "https://github.com/anthropics/claude-plugins-official/tree/main/plugins/example-plugin/.mcp.json"
      },
      {
        "identifier": "urn:claude-plugin:anthropic:example-plugin:skills",
        "displayName": "Example Plugin Skills",
        "mediaType": "application/vnd.agentskills.skill+md",
        "url": "https://github.com/anthropics/claude-plugins-official/tree/main/plugins/example-plugin/skills"
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

5. **Composability**: Plugin bundles that combine skills, MCP servers,
   and commands can be represented as nested catalogs, making the
   internal structure of a plugin package explicit and independently
   addressable.

6. **Decentralized publishing**: Any domain can publish Claude Code
   plugins via AI Catalog without submitting to the centralized
   marketplace repository.

# Acknowledgments

This specification was developed through collaboration among members of
the A2A and MCP protocol communities under the governance of the Linux
Foundation.