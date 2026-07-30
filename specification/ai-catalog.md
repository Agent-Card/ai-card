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
embed the native artifact metadata. A minimal catalog is simply a
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
  referencing or embedding an AI artifact.

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
   entry can reference another AI Catalog, enabling hierarchical
   organization and multi-artifact packaging.

4. **Progressive Complexity**: The simplest catalog is just entries
   with names and URLs. Trust, identity, and provenance metadata are
   available as optional extensions that never modify the catalog
   structure or artifact formats.

5. **Scalable Federation**: The catalog format enables partitioning
   into sub-catalogs to manage size, and supports delegation to
   sub-catalogs managed by independent publishers. Nested catalog
   entries support a federated model where each segment of the
   hierarchy may be authored, hosted, and updated independently.

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
  See [Version Handling](#version-handling) for compatibility rules.

`entries`
: An array of Catalog Entry objects as defined in [Catalog Entry](#catalog-entry).
  This array MAY be empty.

For example, a minimal catalog listing four AI artifacts:

```json
{
  "specVersion": "1.0",
  "entries": [
    {
      "identifier": "urn:air:example.com:skill:code-review",
      "displayName": "Code Review Assistant",
      "type": "application/agent-skills+zip",
      "url": "https://skills.example.com/code-review/skill.zip"
    },
    {
      "identifier": "urn:air:example.com:mcp:weather",
      "type": "application/mcp-server-card+json",
      "url": "https://api.example.com/mcp/server-card"
    },
    {
      "identifier": "urn:air:example.com:a2a:research",
      "type": "application/a2a-agent-card+json",
      "url": "https://agents.example.com/researchAssistant"
    },
    {
      "identifier": "urn:air:example.com:agent:productivity-plugin",
      "displayName": "Productivity Plugin",
      "type": "application/agent-plugins+zip",
      "description": "Tools for common productivity workflows.",
      "tags": ["productivity", "workflows"],
      "url": "https://plugins.example.com/productivity.zip"
    }
  ]
}
```

The following members are OPTIONAL:

`host`
: A Host Info object as defined in [Host Info](#host-info) identifying the
  operator of this catalog.

`extensions`
: A JSON object (map) containing custom, vendor-specific, or
  non-standard fields. See [Extensions](#extensions) for definitions and
  official extension types.

`signature`
: A string containing a detached JWS [[RFC7515]] signature computed over
  the JCS-canonicalized [[RFC8785]] catalog document (excluding the
  `signature` member itself), providing catalog-level integrity over the
  `entries` array and `host`. It is verified exactly as a Trust Manifest
  signature (see [Trust Manifest Signatures](#trust-manifest-signatures)).
  See [Trust Manifest Substitution](#trust-manifest-substitution).

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

For example:

```json
{
  "displayName": "Acme Enterprise AI",
  "identifier": "did:web:acme-corp.com",
  "documentationUrl": "https://docs.acme-corp.com/ai",
  "logoUrl": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0c..."
}
```

## Catalog Entry

A Catalog Entry object describes a single AI artifact in the catalog.
It MUST contain the following members:

`identifier`
: A string uniquely identifying this artifact. This field is an open text format (e.g., any valid URI or URN is accepted). However, to ensure interoperability, identity uniqueness, and discoverability, the standard `urn:air` naming structure is **HIGHLY RECOMMENDED** and **MUST** be used for open or federated systems.

    **Standard Naming Format:**
    `urn:air:{publisher}:{namespace}:{name}`

    - `{publisher}`: The domain name of the organization publishing the artifact (e.g., `example.com`).
    - `{namespace}`: The logical namespace, which can contain one or more colon-separated categories (e.g., `mcp`, `skill`, `agent`, `finance:agent`).
    - `{name}`: The stable, unique name of the artifact within the publisher's namespace.

    *Examples:*

    - `urn:air:example.com:skill:code-review`
    - `urn:air:example.com:mcp:weather`

    For closed or local systems where a different identifier format is used, client implementations are responsible for parsing and processing the custom format as appropriate.

    See [Multi-Version Entries](#multi-version-entries) for uniqueness rules when multiple versions are present.

`type`
: A string containing the identifier that specifies the type of the
  referenced artifact. This field is an open text format, so any string value is accepted. However, to ensure interoperability, it is RECOMMENDED to use one of the following recognized "known types" in the ecosystem when applicable, partitioned by their respective governance boundaries:

    **Core Protocol Types (Governed by the AI Catalog WG):**

    - `application/ai-catalog+json` — a nested AI Catalog
    - `application/agent-card+json` — reserved for a generic Agent Card format

    **Integrated Ecosystem & Third-Party Types (Governed externally):**

    - `application/a2a-agent-card+json` — an A2A Agent Card
    - `application/mcp-server-card+json` — an MCP Server Card
    - `application/agent-skills+json` — Agent Skill Metadata json file
    - `application/agent-skills+md` — an Agent Skill defined in a standard Markdown file (the suffix `+md` is to be registered)
    - `application/agent-skills+zip` — an Agent Skill bundle (ZIP archive)
    - `application/agent-skills+gzip` — an Agent Skill bundle (gzipped tarball)
    - `application/agent-plugins+zip` — an Agent Plugin bundle (ZIP archive)
    - `application/agent-plugins+gzip` — an Agent Plugin bundle (gzipped tarball)

    These values are designed to align with official IANA media type registration standards. Standard ecosystem types use registered structured syntax suffixes (`+json`, `+zip`, `+gzip`). For any new or custom types not listed here, it is up to the specific client implementation to handle them correctly.

A Catalog Entry MUST contain exactly one of the following members to
provide the artifact content:

`url`
: A string containing a URL where the full artifact document can be
  retrieved. The document served at this URL SHOULD be served with
  the media type declared in the `type` field.

`data`
: A JSON value containing the complete artifact document inline. The
  structure of this value is determined by the `type` field and
  is opaque to this specification.

The following members are OPTIONAL:

`displayName`
: A string containing a human-readable name for the artifact.
  This field SHOULD be set only when the referenced artifact does not
  already carry its own canonical human-readable name — for example a
  raw dataset (`application/parquet`), a model blob, a skill bundle
  (`application/agent-skills+zip`), or an Agent Plugin bundle
  (`application/agent-plugins+zip`), none of which directly expose a
  self-describing name without processing the artifact. When the referenced
  artifact does carry such a name — for
  example the `name` field of an A2A Agent Card or the `title` field of
  an MCP Server Card — that artifact is the authoritative source and
  `displayName` SHOULD be omitted to avoid duplicating a value that can
  drift out of sync. When `displayName` *is* present, however, it takes
  precedence: it is the authoritative value for display, and a consumer
  SHOULD render it as given even when it differs from a name carried by
  the referenced artifact. Setting `displayName` is how a publisher
  deliberately overrides the artifact's own name. See
  [Resolving an Artifact's Display Name](#resolving-an-artifact-s-display-name)
  for the full consumer resolution order.

`description`
: A string containing a short description of the artifact. Like
  `displayName`, `description` is OPTIONAL and follows the same
  authoritative-source rule: when the referenced artifact carries its
  own canonical description — for example the `description` field of an
  A2A Agent Card or an MCP Server Card — that artifact is the
  authoritative source and entry `description` SHOULD be omitted to
  avoid duplicating a value that can drift out of sync. When entry
  `description` *is* present, however, it takes precedence: a consumer
  SHOULD render it as given even when it differs from a description
  carried by the referenced artifact, which is how a publisher provides
  a listing-specific blurb. See
  [Resolving an Artifact's Description](#resolving-an-artifact-s-description)
  for the full consumer resolution order.

`tags`
: An array of strings serving as keywords for filtering and discovery.

`version`
: A string containing the version of this artifact.
  [Semantic Versioning](https://semver.org/) is RECOMMENDED but not
  required. See [Multi-Version Entries](#multi-version-entries) for
  how versions interact with `identifier`.

    Like `displayName` and `description`, `version` can restate a value
    the referenced artifact already carries (an A2A Agent Card
    `version`, an MCP Server Card `version`), and when a single entry
    references such an artifact the entry `version` SHOULD be omitted to
    avoid drift — the consumer can read it from the artifact. Unlike
    `displayName` and `description`, however, `version` is not merely
    cosmetic: it is part of the entry's uniqueness key, so it is
    REQUIRED when a catalog lists multiple versions of the same
    `identifier` (see [Multi-Version Entries](#multi-version-entries)).
    A present `version` is used for catalog-level sorting and selection
    rather than as a free-form display override, so it SHOULD equal the
    version the referenced artifact reports; an entry `version` that
    contradicts the artifact's own version is a publishing error, not a
    deliberate override. See
    [Resolving an Artifact's Version](#resolving-an-artifact-s-version)
    for the full consumer resolution order.

`updatedAt`
: A string containing an ISO 8601 [[RFC3339]] timestamp indicating
  when this entry was last modified.

`extensions`
: A JSON object (map) containing custom data.

`publisher`
: A Publisher object as defined in [Publisher Object](#publisher-object)
  identifying the entity that publishes this artifact. This is the
  sole location for publisher information; it is not duplicated in
  the Trust Manifest.

`trustManifest`
: A Trust Manifest object as defined in [Trust Manifest](#trust-manifest)
  providing verifiable identity and trust metadata for this artifact.
  See [Trust Manifest](#trust-manifest) for details.

### Resolving an Artifact's Display Name

Because `displayName` is OPTIONAL, a consumer rendering a catalog entry
cannot assume it is present. To obtain a human-readable name, a consumer
SHOULD resolve one in the following order:

1. **`displayName` on the entry**, if present. A publisher-supplied
   `displayName` always wins, even when it differs from a name carried by
   the referenced artifact.
2. **The referenced artifact's own canonical name**, if the consumer has
   already fetched or cached the artifact — for example the `name` field
   of an A2A Agent Card or the `title` field of an MCP Server Card.
3. **The trailing segment of the entry's `identifier`** as a last
   resort — the portion after its final `:` or `/` delimiter. For
   example, `urn:air:example.com:mcp:weather` yields `weather` and
   `urn:air:anonymous.modelcontextprotocol.io:mcp:brave-search` yields
   `brave-search`.

A consumer SHOULD NOT dereference an artifact at render time solely to
obtain a name. A registry, directory, or other service built on top of a
catalog SHOULD resolve the name once at ingestion — alongside any other
derived metadata it attaches, such as relevance scores or tags — and
cache the result, rather than fetching artifacts on the rendering path.

This order also covers a referenced MCP Server Card whose `title` is
itself absent: step 2 yields no name, so the consumer falls through to
the `identifier` segment in step 3. A publisher MAY still set
`displayName` on such an entry to provide a better name than the bare
identifier segment.

### Resolving an Artifact's Description

Because `description` is OPTIONAL, a consumer that wants to show a
description cannot assume the entry carries one. It SHOULD resolve one in
the following order:

1. **`description` on the entry**, if present. A publisher-supplied
   `description` always wins, even when it differs from a description
   carried by the referenced artifact.
2. **The referenced artifact's own canonical description**, if the
   consumer has already fetched or cached the artifact — for example the
   `description` field of an A2A Agent Card or an MCP Server Card.
3. **No description**, if neither is available. Unlike a name, a
   description has no identifier-derived fallback; a consumer SHOULD
   simply render the entry without one.

As with name resolution, a consumer SHOULD NOT dereference an artifact at
render time solely to obtain a description. A registry, directory, or
other service built on top of a catalog SHOULD resolve the description
once at ingestion and cache the result, rather than fetching artifacts on
the rendering path.

### Resolving an Artifact's Version

Because `version` is OPTIONAL on a single entry — and present only when
the entry disambiguates others that share its `identifier` (see
[Multi-Version Entries](#multi-version-entries)) or deliberately restates
the artifact's version — a consumer cannot assume every entry carries
one. To obtain a version, a consumer SHOULD resolve one in the following
order:

1. **`version` on the entry**, if present. Unlike `displayName` and
   `description`, a present `version` is not a free-form display
   override: it is authoritative for catalog-level sorting and version
   selection. Within a multi-version listing it is REQUIRED and, combined
   with `identifier`, uniquely addresses the entry.
2. **The referenced artifact's own version**, if the consumer has already
   fetched or cached the artifact — for example the `version` field of an
   A2A Agent Card, an MCP Server Card, or an MCP Registry `server.json`.
   A single entry that omits `version` because the artifact already
   carries it is resolved here.
3. **No version**, if neither is available — the entry represents an
   unversioned artifact. A consumer that needs to order such entries
   SHOULD fall back to `updatedAt`, consistent with
   [Multi-Version Entries](#multi-version-entries).

When both the entry and the referenced artifact carry a `version` and
they disagree, the entry `version` is authoritative for catalog-level
sorting and selection; the mismatch is a publishing error (it breaks
latest-selection) that a consumer MAY surface but SHOULD NOT resolve by
silently preferring the artifact's value.

As with name and description resolution, a consumer SHOULD NOT dereference
an artifact at render time solely to obtain a version. A registry,
directory, or other service built on top of a catalog SHOULD resolve the
version once at ingestion and cache the result, rather than fetching
artifacts on the rendering path.

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

For example, a catalog listing two versions of the same agent:

```json
{
  "specVersion": "1.0",
  "entries": [
    {
      "identifier": "urn:air:acme.com:agent:finance",
      "version": "2.1.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/finance/v2.1.json",
      "updatedAt": "2026-03-15T10:00:00Z"
    },
    {
      "identifier": "urn:air:acme.com:agent:finance",
      "version": "2.0.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/finance/v2.0.json",
      "updatedAt": "2026-01-20T08:00:00Z"
    }
  ]
}
```

Both entries share the same `identifier` but have distinct `version`
values, so the combination is unique.

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

# Trust Manifest

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
  DID, SPIFFE ID, or URL; these are illustrative and the set of
  identity schemes is open.

When a Trust Manifest appears within a Catalog Entry, the `identity`
field's trust domain MUST align with the publisher domain in the
containing entry's `identifier` field. This binding ensures
trust claims are associated with the authorized publisher namespace even
when `identity` and `identifier` use different URI schemes.
Consumers MUST reject a Trust Manifest whose `identity` domain does not
align with the publisher domain in the containing entry's `identifier`.
The `identity` is carried here so domain binding is part of the signed
payload, rather than inferred only from unsigned entry context.

When a Trust Manifest appears on a Host Info object, `identity`
SHOULD match the host's `identifier` field when present.

An artifact may legitimately hold more than one verifiable identity at
the same time, for example a SPIFFE ID for runtime workload identity
and a DID for publisher-anchored organizational identity. Additional
identities are declared through the OPTIONAL `alsoKnownAs` member (see
[Optional Members](#optional-members)). The `identity` field remains the
single canonical subject identifier: consumers MUST use `identity` when
referencing the artifact's trust subject or checking identity
equivalence between entries.

When multiple entries share the same `identifier` (with different `version`
values), each entry MAY carry its own Trust Manifest. There is no
requirement that all versions carry identical trust metadata — trust
properties may evolve across versions.

## Manifest Validity

A Trust Manifest exists to carry verifiable trust evidence; an empty one
adds nothing and misleads consumers into believing trust metadata is
present. Beyond the required `identity`, a Trust Manifest MUST therefore
contain at least one *substantive* trust member:

- a `signature` (with its required `subject` and `issuedAt`),
- a non-empty `attestations` array,
- a non-empty `provenance` array, or
- a `trustSchema`.

The members `identity` and `identityType` (which identify the workload
principal) and the informational members `privacyPolicyUrl`,
`termsOfServiceUrl`, and `extensions` do NOT satisfy this requirement.
`subject`, `issuedAt`, and `expiresAt` are not substantive on their own:
an unsigned `subject` digest is attacker-settable and unverifiable, so
they count only as part of a `signature`.

A Trust Manifest that would carry only non-substantive members MUST be
omitted entirely rather than included empty — the `trustManifest` member
is itself OPTIONAL, so no information is lost. Consumers SHOULD treat a
Trust Manifest that violates this rule as if no Trust Manifest were
present.

## Optional Members

The following members are OPTIONAL:

`identityType`
: A string providing a type hint for the `identity` URI (e.g., "did",
  "spiffe", "dns"). This field is OPTIONAL when the type is evident
  from the URI scheme. It does not describe entries of `alsoKnownAs`.

`alsoKnownAs`
: An array of strings, each containing a globally unique URI
  [[RFC3986]] that identifies the same subject as `identity` under an
  alternative identity scheme. The following rules apply:

    - An alias is an equivalent identity of the subject; `identity`
      alone remains canonical and is used for referencing and
      equivalence checking.
    - The array is an unordered set: it MUST NOT contain duplicate
      values or the value of the `identity` field.
    - The domain-alignment rule defined in [Identity](#identity)
      applies only to `identity`. Aliases MAY belong to different
      trust domains or identity schemes.
    - The `identityType` hint applies only to `identity`; the type of
      an alias is inferred from its URI scheme (e.g., `did:`,
      `spiffe:`).
    - Aliases are publisher claims covered by the Trust Manifest
      `signature`; no per-alias proof is required. Consumers MUST NOT
      rely on an alias from a manifest whose signature is absent or
      fails verification (see
      [Verifying Alternative Identities](#verifying-alternative-identities)).

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

`subject`
: A Subject object as defined in [Subject Binding](#subject-binding) that
  cryptographically binds this Trust Manifest to the specific artifact it
  describes. A Trust Manifest that carries a `signature` MUST include a
  `subject`.

`issuedAt`
: A string containing an ISO 8601 [[RFC3339]] timestamp indicating when
  the Trust Manifest was created and signed. A Trust Manifest that
  carries a `signature` MUST include `issuedAt`.

`expiresAt`
: A string containing an ISO 8601 [[RFC3339]] timestamp after which the
  Trust Manifest MUST be considered stale. Consumers SHOULD reject a
  Trust Manifest whose `expiresAt` is in the past.

`signature`
: A string containing a detached JWS [[RFC7515]] signature computed over
  the canonicalized Trust Manifest content, including the `subject` and
  `issuedAt` members. Because the signed payload commits to the artifact
  digest carried in `subject`, neither the trust claims nor the artifact
  reference can be substituted without detection. See
  [Trust Manifest Signatures](#trust-manifest-signatures).

`extensions`
: A JSON object (map) for extending trust metadata. When the Trust Manifest
  carries a `signature`, this object is part of the signed payload; use it
  for extensions that must be cryptographically bound to the manifest.

For example, a Trust Manifest with identity, attestations, and
provenance:

```json
{
  "identity": "did:web:acme.com:agent:finance",
  "identityType": "did",
  "alsoKnownAs": [
    "spiffe://acme.com/ns/finance/sa/finance-agent-pod"
  ],
  "trustSchema": {
    "identifier": "urn:trust:acme-enterprise-v1",
    "version": "1.0",
    "governanceUri": "https://acme-corp.com/trust/governance.pdf",
    "verificationMethods": ["did", "x509"]
  },
  "attestations": [
    {
      "type": "publisher-identity",
      "uri": "https://trust.acme-corp.com/certs/publisher.jwt",
      "description": "Verifies did:web:acme-corp.com as publisher"
    },
    {
      "type": "SOC2-Type2",
      "uri": "https://trust.acme-corp.com/reports/soc2.pdf",
      "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
    }
  ],
  "provenance": [
    {
      "relation": "publishedFrom",
      "sourceId": "https://github.com/acme-corp/finance-agent",
      "sourceDigest": "sha256:fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321"
    }
  ],
  "privacyPolicyUrl": "https://acme-corp.com/legal/privacy",
  "termsOfServiceUrl": "https://acme-corp.com/legal/terms",
  "subject": {
    "url": "https://api.acme-corp.com/agents/finance/v2.1.json",
    "type": "application/a2a-agent-card+json",
    "digest": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
  },
  "issuedAt": "2026-03-15T10:00:00Z",
  "signature": "eyJhbGciOiJFUzI1NiJ9..detached-jws-signature"
}
```

## Subject Binding

The Subject object binds a Trust Manifest to the specific artifact it
describes, closing the substitution gap in which an attacker who
controls the catalog document leaves a validly-signed Trust Manifest in
place but repoints the entry to a different artifact. Because the
Subject is part of the signed payload, the artifact reference and its
content digest cannot be changed without invalidating the signature.

A Subject object MUST contain:

`type`
: A string containing the media type of the bound artifact. This MUST
  equal the containing Catalog Entry's `type`.

`digest`
: A string containing the cryptographic digest of the artifact content,
  in the format defined in [Digest Format](#digest-format). For an
  artifact referenced by `url`, the digest is computed over the exact
  bytes served. For an artifact embedded in `data`, the digest is
  computed over the JCS-canonicalized [[RFC8785]] JSON value.

The following member is OPTIONAL:

`url`
: A string containing the URL of the bound artifact. When present, it
  MUST equal the containing Catalog Entry's `url`. Consumers MUST reject
  a Trust Manifest whose `subject.url` does not match the entry's `url`.

A Trust Manifest that carries a `signature` MUST include a `subject`.
When verifying such a manifest, consumers MUST confirm that the fetched
artifact's media type and digest match the `subject` before relying on
any claim in the Trust Manifest. See
[Verifying Artifact Integrity](#verifying-artifact-integrity).

The `subject.type` and `subject.url` intentionally restate the
entry's `type` and `url` so that those values fall within the signed
payload. This is a deliberate duplication, not redundant metadata:
without it, an attacker who controls the catalog document could change
the entry's media type or location without invalidating the signature.

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

For example:

```json
{
  "identifier": "urn:trust:acme-enterprise-v1",
  "version": "1.0",
  "governanceUri": "https://acme-corp.com/trust/governance.pdf",
  "verificationMethods": ["did", "x509"]
}
```

## Attestation Object

An Attestation object provides verifiable proof of a claim. It MUST
contain:

`type`
: A string identifying the attestation type (e.g., "SOC2-Type2",
  "HIPAA-Audit", "ISO27001").

`uri`
: A string containing the location of the attestation document.
  This may be an HTTPS URL or an inline Data URI [[RFC2397]].

The following members are OPTIONAL:

`digest`
: A string containing a cryptographic hash for integrity verification
  (e.g., "sha256:abcd1234...").

`size`
: An unsigned integer indicating the size of the attestation in bytes.

`description`
: A string containing a human-readable label.

For example, a compliance attestation with integrity verification:

```json
{
  "type": "SOC2-Type2",
  "uri": "https://trust.acme-corp.com/reports/soc2-2026.pdf",
  "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890",
  "size": 245760,
  "description": "SOC2 Type 2 audit report for Acme Finance Agent (2026)"
}
```

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

For example, a provenance link recording that an artifact was built
from a specific source commit and published through an OCI registry:

```json
{
  "relation": "publishedFrom",
  "sourceId": "https://github.com/acme-corp/finance-agent",
  "sourceDigest": "sha256:fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321",
  "registryUri": "oci://registry.acme-corp.com/agents/finance",
  "statementUri": "https://trust.acme-corp.com/provenance/finance-agent-v2.1.json",
  "signatureRef": "did:web:acme-corp.com#key-1"
}
```

## Verification Procedures

This section describes how consumers verify the trust metadata
carried by a Trust Manifest. Verification is OPTIONAL — consumers
that do not need trust assurance can skip this entirely.

### Safe Fetching

Verification procedures direct consumers to fetch URLs that originate in
the Trust Manifest itself (`attestation.uri`, `statementUri`,
`registryUri`, and key-resolution endpoints). Because a manifest may be
attacker-controlled before its identity is anchored, these fetches are a
server-side request forgery (SSRF) and denial-of-service surface.
Consumers performing verification MUST:

- Resolve and reject URLs targeting private, loopback, link-local, or
  cloud metadata addresses (e.g., `127.0.0.0/8`, `::1`,
  `169.254.0.0/16`, `fc00::/7`, `10.0.0.0/8`, `172.16.0.0/12`,
  `192.168.0.0/16`), and re-check the resolved address after any
  redirect.
- Restrict fetches to the `https` scheme (or inline `data:` URIs) and
  refuse to follow redirects that cross into a disallowed address range.
- Enforce a maximum response size and a request timeout. When
  `attestation.size` is present, reject responses that exceed it; in all
  cases apply a consumer-defined ceiling.
- Treat every fetched document as untrusted input.

Consumers SHOULD prefer inline `data:` attestations and Data-URI logos
to avoid leaking verification activity to third-party endpoints.

### Digest Format

Digests in this specification use the format `algorithm:hex-value`,
where `algorithm` is a hash algorithm identifier and `hex-value` is
the lowercase hexadecimal encoding of the hash output. For example:

    sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08

Producers SHOULD use SHA-256 [[RFC6234]] or stronger. Consumers
MUST reject digest values using algorithms shorter than SHA-256.

### Trust Manifest Signatures

The `signature` field carries a detached JWS [[RFC7515]] computed over
the Trust Manifest content, including the `subject` and `issuedAt`
members. To create or verify a signature:

1. **Canonicalize** the Trust Manifest JSON using JCS (JSON
   Canonicalization Scheme) [[RFC8785]]. Remove the `signature` field
   itself before canonicalization; all other members — including
   `subject` and `issuedAt` — remain in the signed payload.
2. **Select an algorithm** from the allowlist in
   [Signature Algorithms](#signature-algorithms). The JWS `alg` header
   parameter MUST identify the algorithm used.
3. **Sign** (or verify) the canonical bytes as a detached JWS payload
   using the publisher's private (or public) key.
4. **Encode** the resulting JWS in compact serialization and store it
   in the `signature` field.

This approach ensures the signature is stable regardless of JSON key
ordering or whitespace. Because the signed payload includes the
`subject` binding, a verified signature commits the publisher to a
specific artifact digest, not merely to the trust claims.

Producers SHOULD avoid placing numeric values that do not round-trip
under JCS serialization (e.g., integers outside the range exactly
representable as IEEE 754 doubles) in a signed Trust Manifest, as such
values can cause a verifier's canonicalization to differ from the
producer's. Where large integers are required, encode them as strings.

### Signature Algorithms

To prevent signature-forgery attacks, producers and consumers MUST
constrain the JWS algorithms used for Trust Manifest signatures.

- Consumers MUST reject a signature whose JWS `alg` header is `none`.
- Consumers MUST reject symmetric (MAC-based) algorithms such as
  `HS256`; Trust Manifest signatures MUST use an asymmetric algorithm so
  that verification cannot be performed with attacker-supplied secret
  material (preventing public-key-as-HMAC-secret confusion).
- Producers MUST use, and consumers MUST support, one or more of the
  following asymmetric algorithms [[RFC7518]]: `ES256`, `ES384`,
  `EdDSA`, `PS256`, `PS384`, or `RS256`.
- Consumers MUST determine the expected algorithm and key from the
  resolved trust anchor (see [Trust Anchoring](#trust-anchoring)) and
  MUST NOT let the `alg` header alone select a verification algorithm in
  a way that downgrades security. Consumers SHOULD pin the expected key
  via the JWS `kid` header.

These constraints follow the JSON Web Token current best practices
[[RFC8725]].

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

### Trust Anchoring

Verifying a Trust Manifest signature proves that the manifest was signed
by the holder of the key associated with its `identity`. It does NOT, by
itself, prove that the `identity` is the legitimate publisher of the
artifact. An attacker who controls the catalog document can replace both
the `identity` and the key it resolves to, then sign the forged manifest
with their own key — every internal check would still pass.

Consumers MUST therefore anchor the `identity` (or signing key) to a
trust root established out of band, independent of the catalog document.
Acceptable anchors include:

- A pinned allowlist of trusted publisher identities or keys.
- A registry or marketplace that vets publisher identities and serves
  the catalog over a channel the consumer independently trusts.
- An identity method that proves control of a name the consumer already
  trusts (e.g., a `did:web` whose domain matches an expected publisher,
  validated against that domain's TLS-authenticated endpoint).

A verified signature without an anchored identity establishes integrity
and internal consistency only; consumers MUST NOT treat it as proof of
publisher authenticity.

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

The `publisher` object resides on the Catalog Entry, outside the Trust
Manifest signature. Consumers MUST treat `publisher` fields as advisory
unless a verified `publisher-identity` attestation cryptographically
binds `publisher.identifier` to the signed manifest's `identity`.

### Verifying Alternative Identities

Aliases need no verification procedure of their own. Because the
signed payload covers `alsoKnownAs`, verifying the Trust Manifest
`signature` as described in
[Trust Manifest Signatures](#trust-manifest-signatures) also verifies
every listed alias: a valid signature proves that the publisher
controlling the canonical `identity` claims each alias as an
equivalent identity of the subject. Consumers MUST NOT rely on aliases
from a manifest whose signature is absent or fails verification.

Once the signature is verified, a consumer MAY use whichever identity,
canonical or alias, matches the identity schemes it is able to
resolve — for example, using a DID alias for DID-based discovery when
its tooling cannot resolve a canonical SPIFFE ID.

Note that the signature proves the publisher claims the alias, not
that the alias's own trust domain acknowledges the link. Consumers
making authorization decisions inside the alias's trust domain MAY
additionally obtain proof of control native to the alias scheme.

### Verifying Artifact Integrity

When a Trust Manifest carries a `signature`, it MUST include a `subject`
that binds it to the artifact (see [Subject Binding](#subject-binding)).
To verify artifact integrity:

1. Verify the Trust Manifest signature
   ([Trust Manifest Signatures](#trust-manifest-signatures)) and anchor
   the identity ([Trust Anchoring](#trust-anchoring)).
2. Confirm `subject.type` equals the entry's `type`, and, when
   `subject.url` is present, that it equals the entry's `url`.
3. Fetch the artifact content from the entry's `url`, or take it from
   the entry's `data`, observing the limits in
   [Safe Fetching](#safe-fetching).
4. Compute the digest of the fetched bytes (for `url`) or of the
   JCS-canonicalized value (for `data`) using the algorithm named in
   `subject.digest`.
5. Compare the computed digest to `subject.digest`. Reject the artifact
   if they differ.

Because the `subject` is part of the signed payload, this check binds
the publisher's signature to the exact artifact, defeating catalog-level
substitution of the artifact URL or content. The OPTIONAL
`provenance[].sourceDigest` records the digest of an upstream *source*
(e.g., a Git commit) and is complementary to — not a substitute for —
the `subject` digest.

### Verifying Attestations

For each attestation in the `attestations` array:

1. Fetch the attestation document from `uri`.
2. If `digest` is present, verify the fetched document matches the
   declared digest.
3. Validate the attestation per its `type` (e.g., verify a JWT
   signature, confirm a PDF certificate is current).

### Provenance Statements

A Provenance Link MAY reference a signed provenance statement via
`statementUri` and the key that signed it via `signatureRef`. To verify
such a statement:

1. Fetch the statement document from `statementUri`, observing
   [Safe Fetching](#safe-fetching).
2. Resolve the key indicated by `signatureRef` using the procedure in
   [Key Resolution](#key-resolution) and anchor it per
   [Trust Anchoring](#trust-anchoring).
3. Verify the statement's signature using an algorithm from
   [Signature Algorithms](#signature-algorithms).
4. Confirm the statement's subject matches the artifact's `subject`
   digest. Treat an unverifiable statement as absent, not as a failure
   of the artifact itself.

# Organizing Catalogs

As catalogs grow, a flat list of entries becomes unwieldy. Because any
catalog entry can have a `type` of `application/ai-catalog+json`,
catalogs are naturally composable — an entry can reference or inline
another AI Catalog, creating a hierarchy of any depth.

## Nested Catalog Entries

A catalog entry whose `type` is `application/ai-catalog+json`
references (via `url`) or embeds (via `data`) another AI Catalog
document. This mechanism supports two complementary use cases:

**Organizational hierarchy.** An enterprise with thousands of artifacts
can partition its catalog into sub-catalogs by department, product line,
or region. Each sub-catalog is an independent AI Catalog document with
its own `host` and entries:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Enterprise AI",
    "identifier": "did:web:acme-corp.com"
  },
  "entries": [
    {
      "identifier": "urn:air:acme.com:catalog:finance",
      "displayName": "Finance Services",
      "type": "application/ai-catalog+json",
      "url": "https://acme.com/catalogs/finance.json"
    },
    {
      "identifier": "urn:air:acme.com:catalog:ml",
      "displayName": "ML Models",
      "type": "application/ai-catalog+json",
      "url": "https://acme.com/catalogs/ml.json"
    },
    {
      "identifier": "urn:air:acme.com:catalog:devops",
      "displayName": "DevOps Tools",
      "type": "application/ai-catalog+json",
      "url": "https://acme.com/catalogs/devops.json"
    }
  ]
}
```

**Multi-artifact packaging.** An entry with a `publisher` that contains
a nested catalog may be interpreted as a set of items that could be
acquired as a unit. For example, a finance plugin that ships an A2A
agent, an MCP server, and a dataset together:

```json
{
  "identifier": "urn:air:acme.com:plugin:finance-suite",
  "displayName": "Finance Plugin",
  "type": "application/ai-catalog+json",
  "url": "https://acme.com/plugins/finance-suite.json",
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  }
}
```

The document at that URL would itself be an AI Catalog containing
the A2A agent, MCP server, and dataset entries.

A nested catalog entry is a regular catalog entry — it has an
`identifier`, may carry a `trustManifest`, and may include a
`publisher`. An entry inside a nested catalog MAY reuse the same
`identifier` as an entry elsewhere; this indicates the same logical
artifact.

Clients processing nested catalogs SHOULD impose a maximum nesting
depth to prevent circular references. A depth limit of 4 is
RECOMMENDED. Implementations MAY support deeper nesting but SHOULD
document their limit.

# Extensions

The `extensions` property appears on the AI Catalog top-level object,
on Catalog Entry objects, and on Trust Manifest objects. It provides
a single, well-defined extension point for custom or vendor-specific
properties.

## Format and Key Naming

The `extensions` field is a JSON object (map). Each key in the object MUST
represent the extension type (namespace), and the corresponding value contains the extension data.

To avoid collisions between independent publishers, the keys MUST
be a valid URL or a reverse-DNS string:

- **Reverse-DNS prefix** for vendor-specific extensions:
  `com.example.confidenceScore`, `io.acme.deploymentRegion`.
- **URL prefix** for publicly accessible extension schemas:
  `https://cisco.com/extensions/security-scan`.

Consumers that do not recognize an extension key MUST ignore it without
throwing an error.

For example, a catalog entry with `extensions` representing metadata and a custom schema:

```json
{
  "specVersion": "1.0",
  "entries": [
    {
      "identifier": "urn:air:treasury.gov:okf:fiscaldata",
      "type": "text/vnd.okf+markdown",
      "tags": ["finance", "treasury"],
      "extensions": {
        "https://ai-catalog.org/extensions/metadata": {
          "location": "US-West",
          "environment": "staging",
          "version-compatible": [">=1.0.0"]
        },
        "https://openknowledgeformat.org/ns#": {
          "@context": {
            "us-gaap": "https://xbrl.fasb.org/us-gaap/",
            "ifrs": "https://xbrl.ifrs.org/taxonomy/"
          },
          "type": "Financial Dataset",
          "taxonomy": "us-gaap",
          "conformsTo": ["us-gaap:Revenue", "ifrs:Revenue"]
        }
      }
    }
  ]
}
```

## Official Extensions

While publishers are free to create custom extensions, this specification
defines a set of "Official" known types for commonly requested schemas:

1. **Metadata** (`https://ai-catalog.org/extensions/metadata`)
   - Used to store generic, schemaless key-value pairs.

As custom extensions become highly popular, the AI-Catalog TSC may promote
them to Official Known Types or core standard fields in future specification versions.

# Version Handling

The `specVersion` field identifies which version of this specification
a catalog conforms to. This section defines how producers and consumers
handle version differences.

## Version Format

The `specVersion` value is a "Major.Minor" string (e.g., "1.0",
"1.1", "2.0"). Major and minor components are non-negative integers.

## Compatibility Rules

Minor version increments (e.g., 1.0 → 1.1)
: The specification adds new OPTIONAL fields or features. Documents
  conforming to a higher minor version are backward-compatible with
  consumers that understand the same major version. Consumers MUST
  ignore unrecognized fields.

Major version increments (e.g., 1.x → 2.0)
: The specification introduces breaking changes (removed fields,
  changed semantics, new required fields). Consumers that do not
  support the major version SHOULD reject the document with an
  informative error rather than silently misinterpreting it.

## Consumer Behavior

Consumers SHOULD:

- Parse the `specVersion` field before processing the document.
- Accept documents whose major version matches their supported major
  version, regardless of minor version differences.
- Ignore unrecognized fields (forward compatibility within a major
  version).
- Reject documents whose major version is higher than the highest
  major version they support, with an informative error message.

## Producer Behavior

Producers MUST set `specVersion` to the version of this specification
they implement. Producers SHOULD NOT set `specVersion` to a version
higher than they actually conform to.

# Discovery

## Location Independence

An AI Catalog document MAY be served from any URL. It is identified
by its media type (`application/ai-catalog+json`) and its `specVersion`
field, not by its URL path. Catalogs are equally valid when hosted at
an arbitrary path, embedded in a registry response, packaged in an
archive, or distributed as a local file.

When served over HTTP, the document SHOULD be served with the media
type `application/ai-catalog+json`.

## Well-Known URI

To support automated discovery, hosts MAY serve an AI Catalog at the
following well-known URI [[RFC8615]]:

    /.well-known/ai-catalog.json

Clients performing domain-level discovery SHOULD attempt to retrieve
this well-known URL. If a valid AI Catalog document is returned, the
client SHOULD use the entries' `url` values to retrieve individual
artifacts. Trust metadata, when present, is carried inline on the
entries as Trust Manifests.

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
  minimum `identifier`, `type`, and exactly one of `url` or
  `data`

All other fields (`host`, `publisher`, `trustManifest`,
`extensions`) are OPTIONAL. This level is sufficient for use cases that
only need a simple list of AI artifacts — for example, a catalog of
MCP servers or A2A agents. A `trustManifest`, when present at any level,
MUST be substantive (see [Manifest Validity](#manifest-validity)).

## Level 2: Discoverable Catalog

In addition to Level 1 requirements, a Discoverable Catalog:

- Includes a `host` object identifying the catalog operator
- MAY be served at the well-known URI `/.well-known/ai-catalog.json`
  to enable automated domain-level discovery

## Level 3: Trusted Catalog

In addition to Level 2 requirements, a Trusted Catalog:

- Includes a `trustManifest` object on every entry whose trust is to be
  relied upon, and MAY include one on the host, as defined in
  [Trust Manifest](#trust-manifest)
- Each such `trustManifest` MUST carry a `signature`, a `subject`
  binding it to the artifact ([Subject Binding](#subject-binding)), and
  an `issuedAt` timestamp
- Consumers MUST verify the signature, anchor the identity
  ([Trust Anchoring](#trust-anchoring)), and confirm the `subject`
  digest before relying on any claim
- SHOULD provide catalog-level integrity, either by serving the catalog
  through a content-addressed channel (see
  [Security Considerations](#security-considerations)) or by including a
  top-level catalog `signature`
- MAY include `publisher` objects on entries with verifiable identifiers
- Enables verifiable identity, compliance attestations, and provenance
  tracking

Implementations at any level are fully conformant with this
specification. Consumers MAY ignore fields defined at higher
conformance levels and SHOULD gracefully handle their absence.

# Security Considerations

## Trust Layers

This specification supports a progressive trust model. Each layer
builds on the previous one, adding confidence without requiring all
consumers to implement every layer. Consumers choose the level
appropriate to their threat model.

**Layer 0 — Transport Security**
: The catalog and artifacts are served over HTTPS (TLS 1.2 or later).
  The consumer trusts the TLS certificate chain and DNS resolution.
  This prevents passive eavesdropping and casual tampering but does
  not protect against compromised hosting or DNS hijack.

**Layer 1 — Trust Manifest with Provenance**
: The catalog entry includes a Trust Manifest containing provenance
  links with `sourceDigest` values. After fetching an artifact, the
  consumer can hash the content and compare it to the digest recorded
  in the provenance link. This detects artifact tampering in transit.
  However, because the Trust Manifest is a peer element in the catalog
  (not embedded in the artifact), an attacker who controls the catalog
  document can substitute both the artifact URL and the Trust Manifest
  with matching values. **Digest verification without signature
  verification guards against transport-level tampering but not
  catalog-level substitution.**

**Layer 2 — Signed Trust Manifest**
: The Trust Manifest includes a `signature` field (detached JWS) and a
  `subject` that binds the signature to the artifact's content digest
  (see [Subject Binding](#subject-binding)). The consumer verifies the
  signature, anchors the signer's identity to a trust root
  ([Trust Anchoring](#trust-anchoring)), and confirms the `subject`
  digest before trusting any claim. This closes the substitution gap
  from Layer 1: because the signed payload commits to the artifact
  digest, an attacker cannot repoint the entry to a different artifact
  or forge claims without the publisher's private key. Consumers that
  rely on trust metadata MUST verify signatures and MUST reject Trust
  Manifests whose signature does not validate, whose `subject` does not
  match the fetched artifact, or whose identity cannot be anchored.

**Layer 3 — Content-Addressed Distribution (OCI)**
: The catalog is distributed through an OCI registry where all content
  — entries, artifacts, and Trust Manifests — is addressed by
  cryptographic digest. The registry enforces integrity: substitution
  is impossible because any change produces a different digest.
  Cosign or Notation signatures on OCI manifests provide an additional
  layer of publisher authentication.

Consumers that rely on trust metadata for security decisions SHOULD
implement at least Layer 2 (signature verification). Consumers that
only implement Layer 0 or Layer 1 SHOULD treat Trust Manifest content
as advisory, not authoritative.

## Nested Catalog Depth and Circular References

Clients processing nested catalogs SHOULD enforce a maximum recursion
depth to prevent denial-of-service attacks via deeply nested or
circular catalog references. A maximum depth of 4 is RECOMMENDED.

Depth limits alone do not prevent circular references at shallow
depths (e.g., Catalog A → Catalog B → Catalog A). Clients SHOULD
track the set of catalog URLs visited during recursive resolution and
reject any catalog URL that has already been fetched in the current
traversal path.

## Catalog Poisoning

An attacker who can modify a catalog document (e.g., through a
compromised hosting account or DNS hijack) can redirect consumers to
malicious artifacts by changing `url` values or injecting new entries.

The trust layers described above provide progressive defense against
this threat:

- **Layer 0** relies on HTTPS certificate management to prevent
  unauthorized modification.
- **Layer 1** enables post-fetch integrity checks but does not prevent
  whole-entry substitution.
- **Layer 2** binds the signed Trust Manifest to the artifact digest
  via `subject`, preventing both Trust Manifest forgery and artifact
  substitution under a valid signature.
- **Layer 3** makes modification structurally impossible through
  content-addressing.

## Trust Manifest Substitution

Because a Trust Manifest is a peer element of the catalog entry rather
than part of the artifact, an attacker who can write the catalog
document can attempt to substitute the artifact, the Trust Manifest, or
both. This specification defends against substitution with three
compounding mechanisms:

- **Subject binding.** A signed Trust Manifest MUST include a `subject`
  that commits to the artifact's media type and content digest (see
  [Subject Binding](#subject-binding)). The artifact reference therefore
  cannot be changed without invalidating the signature.
- **Trust anchoring.** A signature is only meaningful once the signer's
  identity is anchored to a trust root established out of band (see
  [Trust Anchoring](#trust-anchoring)); otherwise an attacker can sign a
  forged manifest with their own key.
- **Catalog-level integrity.** Per-entry signatures do not prevent an
  attacker from adding, removing, or reordering whole entries. Hosts
  SHOULD additionally provide catalog-level integrity, either by serving
  the catalog through a content-addressed channel (Layer 3) or by
  including a top-level catalog `signature` computed over the
  JCS-canonicalized [[RFC8785]] catalog document (excluding the
  `signature` member itself) and verified exactly as a Trust Manifest
  signature.

## Identifier Typosquatting

Catalog entries are identified by URIs/URNs. An attacker can register
identifiers similar to legitimate ones (e.g., `urn:air:acme.com:agent:financ`
vs. `urn:air:acme.com:agent:finance`) to trick consumers into using a
malicious artifact.

Registries and consumers SHOULD implement similarity checks on
identifiers. Publishers SHOULD use identifiers anchored to domains
they control (e.g., DIDs or domain-scoped URNs).

## Stale Attestations

Attestation documents referenced in Trust Manifests have no built-in
expiry mechanism in this specification. A SOC2 report from a previous
year may no longer reflect current practices.

Consumers SHOULD:

- Check the `updatedAt` field on catalog entries to assess freshness.
- Independently verify attestation documents are current when making
  trust decisions.
- Treat attestations as evidence, not guarantees — the attestation
  indicates a claim was made, not that it remains valid indefinitely.

Future versions of this specification MAY add `validFrom` and
`expiresAt` fields to the Attestation object.

## Embedded Content Safety

When the `data` field contains embedded artifact content, consumers
MUST treat it as untrusted input. In particular:

- Content with HTML or script-capable media types MUST be sandboxed
  and MUST NOT be executed in the consumer's security context.
- Consumers SHOULD validate that the `data` content is well-formed
  JSON (or the expected format for the declared `type`) before
  processing.

## Privacy Considerations

Logo URLs SHOULD use Data URIs [[RFC2397]] to avoid leaking client
information through image fetch requests. Publishers SHOULD carefully
consider what information is included in `extensions` fields.

# Data Model Overview

The following diagram illustrates the relationships between the
core objects defined in this specification:

<pre class="mermaid nohighlight">
classDiagram
    class AICatalog {
        specVersion string
        entries CatalogEntry[]
        host HostInfo
        signature string
    }
    class HostInfo {
        displayName string
        identifier string
        trustManifest TrustManifest
    }
    class CatalogEntry {
        identifier string
        displayName string
        type string
        url | data
        version string
        publisher Publisher
        trustManifest TrustManifest
    }
    class Publisher {
        identifier string
        displayName string
    }
    class TrustManifest {
        identity string
        subject Subject
        alsoKnownAs string[]
        trustSchema TrustSchema
        attestations Attestation[]
        provenance ProvenanceLink[]
        issuedAt string
        signature string
    }
    class Subject {
        url string
        type string
        digest string
    }
    class TrustSchema {
        identifier string
        version string
        verificationMethods string[]
    }
    class Attestation {
        type string
        uri string
        digest string
    }
    class ProvenanceLink {
        relation string
        sourceId string
        sourceDigest string
    }
    AICatalog --> "*" CatalogEntry : entries
    AICatalog --> "0..1" HostInfo : host
    CatalogEntry --> "0..1" Publisher : publisher
    CatalogEntry --> "0..1" TrustManifest : trustManifest
    HostInfo --> "0..1" TrustManifest : trustManifest
    TrustManifest --> "0..1" Subject : subject
    TrustManifest --> "0..1" TrustSchema : trustSchema
    TrustManifest --> "*" Attestation : attestations
    TrustManifest --> "*" ProvenanceLink : provenance
    CatalogEntry --> "0..1" AICatalog : nested
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

## Well-Known URI Registration: ai-catalog.json

This section registers the `ai-catalog.json` well-known URI in the
IANA "Well-Known URIs" registry [[RFC8615]].

URI Suffix:
: ai-catalog.json

Change Controller:
: Agent Card Working Group

Specification Document:
: This document, [Well-Known URI](#well-known-uri)

Related Information:
: The well-known URI returns a JSON document with media type
  `application/ai-catalog+json` conforming to the AI Catalog schema
  defined in this specification.

# CDDL Schema

The following CDDL [[RFC8610]] defines the normative schema for AI
Catalog and Trust Manifest documents.

## AI Catalog

```
AICatalog = {
  specVersion: text,
  ? host: HostInfo,
  entries: [* CatalogEntry],
  ? extensions: { * text => any }
}

HostInfo = {
  displayName: text,
  ? identifier: text,
  ? documentationUrl: text,
  ? logoUrl: text,
  ? trustManifest: TrustManifest
}

CatalogEntry = {
  identifier: text,
  ? displayName: text,
  type: text,
  (url: text // data: any),
  ? version: text,
  ? description: text,
  ? tags: [* text],
  ? publisher: Publisher,
  ? trustManifest: TrustManifest,
  ? updatedAt: tdate,
  ? extensions: { * text => any }
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
  ? alsoKnownAs: [* text],
  ? trustSchema: TrustSchema,
  ? attestations: [* Attestation],
  ? provenance: [* ProvenanceLink],
  ? privacyPolicyUrl: text,
  ? termsOfServiceUrl: text,
  ? signature: text,
  ? extensions: { * text => any }
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

# Example: Multi-Artifact Catalog with Nested Catalog

The following example shows an AI Catalog that contains a mix of
artifact types including a nested catalog packaging related artifacts:

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
      "identifier": "urn:air:acme.com:agent:finance-a2a",
      "version": "2.1.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/finance.json",
      "description": "A2A agent for financial workflows.",
      "tags": ["finance", "a2a"],
      "publisher": {
        "identifier": "did:web:acme-corp.com",
        "displayName": "Acme Financial Corp"
      },
      "trustManifest": {
        "identity": "spiffe://acme.com/ns/finance/sa/finance-a2a-pod",
        "identityType": "spiffe",
        "attestations": [
          {
            "type": "publisher-identity",
            "uri": "https://trust.acme.com/certs/publisher.jwt",
            "description": "Verifies did:web:acme-corp.com as publisher"
          },
          {
            "type": "SOC2-Type2",
            "uri": "https://trust.acme.com/reports/soc2.pdf",
            "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
          }
        ],
        "privacyPolicyUrl": "https://acme.com/legal/privacy",
        "termsOfServiceUrl": "https://acme.com/legal/terms"
      },
      "updatedAt": "2026-03-15T10:00:00Z"
    },
    {
      "identifier": "urn:air:acme.com:server:finance-mcp",
      "version": "1.4.0",
      "type": "application/mcp-server-card+json",
      "url": "https://api.acme-corp.com/mcp/server-card",
      "description": "MCP server with finance tools.",
      "tags": ["finance", "mcp"],
      "updatedAt": "2026-03-15T10:00:00Z"
    },
    {
      "identifier": "urn:air:acme.com:plugin:finance-suite",
      "displayName": "Acme Finance Suite",
      "type": "application/ai-catalog+json",
      "description": "A2A agent + MCP server + dataset for finance workflows.",
      "tags": ["finance", "suite"],
      "data": {
        "specVersion": "1.0",
        "entries": [
          {
            "identifier": "urn:air:acme.com:agent:finance-a2a",
            "type": "application/a2a-agent-card+json",
            "url": "https://api.acme-corp.com/agents/finance.json"
          },
          {
            "identifier": "urn:air:acme.com:server:finance-mcp",
            "type": "application/mcp-server-card+json",
            "url": "https://api.acme-corp.com/mcp/server-card"
          },
          {
            "identifier": "urn:air:acme.com:data:market-2026q1",
            "displayName": "Market Dataset Q1 2026",
            "type": "application/parquet",
            "url": "https://data.acme-corp.com/market-2026q1.parquet",
            "trustManifest": {
              "identity": "urn:air:acme.com:data:market-2026q1",
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
        "identity": "urn:air:acme.com:plugin:finance-suite",
        "signature": "eyJhbGciOiJFUzI1NiJ9..detached"
      },
      "updatedAt": "2026-03-20T14:00:00Z"
    }
  ]
}
```

# Example: Hierarchical Catalog

The following example shows how an enterprise uses nested catalog
entries to organize a large number of artifacts into browsable
categories. Each sub-catalog entry points to a separate AI Catalog
document:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Enterprise AI",
    "identifier": "did:web:acme-corp.com"
  },
  "entries": [
    {
      "identifier": "urn:air:acme.com:agent:assistant",
      "version": "3.0.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://api.acme-corp.com/agents/assistant.json",
      "description": "General-purpose corporate assistant agent."
    },
    {
      "identifier": "urn:air:acme.com:catalog:finance",
      "displayName": "Finance Services",
      "type": "application/ai-catalog+json",
      "url": "https://acme-corp.com/catalogs/finance.json",
      "description": "Financial agents, MCP servers, and datasets.",
      "tags": ["finance", "trading", "compliance"]
    },
    {
      "identifier": "urn:air:acme.com:catalog:engineering",
      "displayName": "Engineering Tools",
      "type": "application/ai-catalog+json",
      "url": "https://acme-corp.com/catalogs/engineering.json",
      "description": "CI/CD agents, code review tools, and DevOps servers.",
      "tags": ["engineering", "devops", "ci-cd"]
    },
    {
      "identifier": "urn:air:acme.com:catalog:ml-models",
      "displayName": "ML Models",
      "type": "application/ai-catalog+json",
      "url": "https://acme-corp.com/catalogs/ml-models.json",
      "description": "Model cards and inference endpoints.",
      "tags": ["ml", "models", "inference"]
    }
  ]
}
```

A catalog MAY contain both direct artifact entries and nested catalog
entries. In this example, the corporate assistant agent is listed
directly while department-specific artifacts are organized into child
catalogs.

# Example: Dual-Protocol Agent (MCP + A2A)

A single agent that supports both MCP and A2A protocols can be
represented as one catalog entry whose content is a nested catalog
containing both protocol-specific entries:

```json
{
  "identifier": "urn:air:acme.com:agent:finance",
  "displayName": "Acme Finance Agent",
  "type": "application/ai-catalog+json",
  "description": "Finance agent accessible via both MCP and A2A protocols.",
  "tags": ["finance", "dual-protocol"],
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  },
  "data": {
    "specVersion": "1.0",
    "entries": [
      {
        "identifier": "urn:air:acme.com:agent:finance:mcp",
        "type": "application/mcp-server-card+json",
        "url": "https://api.acme-corp.com/mcp/server-card"
      },
      {
        "identifier": "urn:air:acme.com:agent:finance:a2a",
        "type": "application/a2a-agent-card+json",
        "url": "https://api.acme-corp.com/agents/finance"
      }
    ]
  },
  "trustManifest": {
    "identity": "spiffe://acme.com/ns/finance/sa/finance-agent-pod",
    "identityType": "spiffe",
    "attestations": [
      {
        "type": "SOC2-Type2",
        "uri": "https://trust.acme-corp.com/reports/soc2.pdf",
        "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
      }
    ]
  }
}
```

The outer entry represents the logical agent as a single discoverable
artifact with its own trust metadata. The `data` field inlines a
catalog with protocol-specific entries, allowing clients to choose
MCP or A2A based on their capabilities.

# Mapping to Distribution Substrates

The AI Catalog specification defines a **logical format**: a JSON
document with `entries`, `displayName`, `type`, and `trustManifest`
fields that are immediately meaningful to anyone working with AI
artifacts. Authors write simple JSON. APIs serve simple JSON. Clients
consume simple JSON.

That logical format can be **physically distributed** over more than one
substrate — an OCI registry, an [[xRegistry]] registry, or a plain HTTP
server. Each substrate has its own data model and its own native
capabilities. To keep the logical format authoritative and to avoid
diverging, substrate-specific dialects, every binding defined by this
specification MUST satisfy the same contract: packing a logical document
into the substrate and unpacking it again MUST reproduce an equivalent
logical document.

```
Authoring                      Distribution                    Consumption
─────────                      ────────────                    ───────────
ai-catalog.json   ──pack──►   OCI / xRegistry / HTTP  ──unpack──►   ai-catalog.json
  entries[]                     substrate-native form                entries[]
  trustManifest                                                      trustManifest
```

This separation keeps authoring and consumption simple: publishers and
clients work with domain vocabulary (`entries`, `displayName`,
`type`, `trustManifest`), while infrastructure that wants
content-addressing, signing, replication, or registry APIs uses whichever
binding below matches its substrate.

## Binding Invariants

A conforming binding MUST preserve each of the following invariants. This
list — not any single substrate's vocabulary — is the conformance bar for
a pack/unpack round-trip.

| Logical concept | Invariant a binding MUST preserve |
|:---|:---|
| Entry identity (`identifier`) | A stable, addressable identity for each entry |
| Artifact content + `type` | The artifact bytes are retrievable together with their media type |
| Catalog structure / nesting | Nested catalogs remain navigable as a hierarchy |
| Trust Manifest association | An entry's Trust Manifest is discoverable from that entry |
| Content integrity | The served bytes are verifiably bound to `trustManifest.subject.digest` |
| Signing | The Trust Manifest's authenticity is cryptographically verifiable |

## Delegate, Don't Duplicate

Substrates differ in what they can express natively. OCI is
content-addressed and has first-class signing (Cosign/Notation);
xRegistry is a hierarchical resource API with versioning and
cross-referencing but no native digest or signature primitive.

To avoid expressing the same guarantee twice, a binding **delegates** an
invariant to a native substrate primitive when one exists, and otherwise
**carries** it in the logical Trust Manifest. A binding MUST NOT restate,
in substrate vocabulary, a guarantee it has delegated, and MUST NOT drop
a guarantee the substrate cannot express.

| Invariant | OCI primitive (delegate) | xRegistry primitive (delegate) | Carried fallback |
|:---|:---|:---|:---|
| Identity | Repository path + digest | `resourceid` / `xid` | `entry.identifier` |
| Content + media type | `layers[0]` + `artifactType` | Resource document + `contenttype` | Entry artifact + `type` |
| Nesting | Nested Image Index | Nested Group / `xref` | Nested entry |
| Manifest association | Referrers API (`subject`) | `xref` / extension attribute | Inline `trustManifest` |
| Content integrity | Content-addressed digest | *(none — carried)* | `subject.digest` |
| Signing | Cosign / Notation referrer | *(none — carried)* | Detached JWS in Trust Manifest |

The two sections that follow are concrete bindings of this contract. The
OCI binding delegates the most (identity, content integrity, signing);
the xRegistry binding delegates structure, identity, and discovery but
carries content integrity and signing because xRegistry has no native
primitive for them.

# Mapping to OCI Distribution

This appendix binds the [Mapping to Distribution
Substrates](#mapping-to-distribution-substrates) contract to OCI
registries, enabling content-addressed storage, signing, and replication
using existing container infrastructure. OCI's data model uses
container-oriented vocabulary (`manifests`, `layers`, `config`, `digest`)
that does not naturally describe a catalog of AI artifacts, so tooling
bridges the logical format and the OCI representation.

Of the binding invariants, the OCI binding **delegates** identity,
content integrity, and signing to OCI's own primitives. Consequently
`trustManifest.subject.digest` is expected to equal the OCI descriptor
digest of the served artifact, and the detached JWS in the Trust Manifest
MAY be omitted from the packed representation because Cosign/Notation
referrers carry signing instead. Unpacking reconstitutes (or re-signs)
the logical Trust Manifest from those referrers.

## Conceptual Mapping

The OCI image specification (v1.1+) supports arbitrary artifact types
through the `artifactType` field. The following table maps AI Catalog
concepts to their OCI physical equivalents:

| AI Catalog (Logical) | OCI (Physical) |
|:---|:---|
| AI Catalog document | OCI Image Index with `artifactType: "application/ai-catalog+json"` |
| Catalog Entry | OCI Image Manifest with `artifactType` set to the entry's `type` |
| Entry `type` | Manifest `artifactType` field |
| Entry artifact content | Manifest `layers[0]` blob (the protocol-specific document) |
| Entry metadata (name, tags, publisher) | Manifest `config` blob and/or `annotations` |
| Nested Catalog Entry | Nested OCI Image Index referenced from the parent index |
| Trust Manifest | OCI Referrer artifact with `subject` pointing to the entry manifest |
| Trust Manifest attestations | Individual OCI Referrer artifacts per attestation |
| Signing | Cosign / Notation signatures as OCI Referrers |

## Packing: AI Catalog to OCI

Tooling converts an AI Catalog JSON document into OCI artifacts:

1. **Each catalog entry** becomes an OCI Image Manifest. The entry's
   artifact content (A2A card, MCP Server Card, skill definition) is
   stored as a `layers[0]` blob. Common metadata (name, description,
   publisher) is stored as the `config` blob or as `annotations`.

2. **The catalog itself** becomes an OCI Image Index whose `manifests`
   array references the per-entry manifests by digest.

3. **Trust Manifests** become OCI Referrer artifacts attached to their
   entry manifests via the `subject` field. Attestation documents
   (JWTs, PDFs, SLSA provenance) become individual referrer layers.

4. **Nested catalog entries** become nested OCI Image Indexes.

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
        "ai-catalog.identifier": "urn:air:acme.com:agent:finance-a2a",
        "ai-catalog.displayName": "Acme Finance A2A Agent"
      }
    },
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "digest": "sha256:bbb222...",
      "size": 512,
      "artifactType": "application/mcp-server-card+json",
      "annotations": {
        "ai-catalog.identifier": "urn:air:acme.com:server:finance-mcp",
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
| Vocabulary | `entries`, `displayName`, `type`, `trustManifest` | `manifests`, `layers`, `config`, `annotations` |
| Minimum viable serving | Static JSON file at any URL (optionally well-known) | OCI registry or static OCI layout |
| Signing | Detached JWS in logical format; Cosign/Notation in OCI | Cosign/Notation only |
| Content integrity | Optional digests in Trust Manifest | Guaranteed by OCI content-addressing |
| Ecosystem compatibility | Any HTTP server, any registry, any CDN | OCI-compliant registries |
| Adoption barrier | Low — familiar JSON | Higher — requires OCI familiarity |

Both approaches can coexist. A tooling bridge converts between them
losslessly, allowing simple consumers to work with the logical format
while infrastructure-oriented deployments leverage OCI distribution.

# Mapping to xRegistry

This appendix binds the [Mapping to Distribution
Substrates](#mapping-to-distribution-substrates) contract to [[xRegistry]],
a hierarchical registry model organized as Registry → Groups → Resources
→ Versions. xRegistry contributes structure, identity, versioning,
cross-referencing, and a registry API; it has no native content-addressing
or signature primitive.

Of the binding invariants, the xRegistry binding **delegates** entry
identity, catalog structure, artifact content, and manifest discovery to
xRegistry's own primitives, but **carries** content integrity and signing
in the Trust Manifest. The detached JWS and `subject.digest` remain
authoritative exactly as in plain-HTTP distribution, because xRegistry
cannot express either guarantee natively.

## Conceptual Mapping

An AI Catalog document maps to an xRegistry **Group** whose **Resources**
are the catalog entries; each entry's artifact is the Resource document.

| AI Catalog (Logical) | xRegistry (Physical) |
|:---|:---|
| AI Catalog document | A Group instance (e.g. in a `aicatalogs` Group type), or the Registry root when serving a single catalog |
| Catalog Entry | A Resource within that Group |
| Entry `identifier` | Resource `<SINGULAR>id` and `xid` |
| Entry `type` | Version `contenttype` (with `format` when a named format applies) |
| Entry artifact content | Resource document — inline (`<RESOURCE>` / `<RESOURCE>base64`) or external (`<RESOURCE>url`) |
| Entry metadata (displayName, description, tags) | `name`, `description`, `labels` |
| Entry version | Version `versionid` |
| Nested Catalog Entry | A nested Group referenced from the entry's Resource via `meta.xref` |
| Trust Manifest | An extension attribute on the Resource (an object), or a related Resource referenced by `xref` |
| Content integrity (`subject.digest`) | Carried in the Trust Manifest (xRegistry has no native digest) |
| Signing | Detached JWS retained in the Trust Manifest (xRegistry has no native signature) |

## Packing: AI Catalog to xRegistry

Tooling converts an AI Catalog JSON document into xRegistry resources:

1. **The catalog** becomes a Group instance. Catalog-level metadata maps
   to Group attributes: `displayName` to `name`, host identity and other
   metadata to `labels` or extension attributes.

2. **Each catalog entry** becomes a Resource in that Group. The entry's
   artifact content is stored as the Resource document — inline via
   `<RESOURCE>` / `<RESOURCE>base64`, or by reference via `<RESOURCE>url`.
   `type` maps to `contenttype`; entry metadata maps to `name`,
   `description`, and `labels`. Multiple entry versions map to Versions.

3. **Trust Manifests** are carried as an extension attribute on the
   Resource (for example `aicatalog_trustmanifest`), or as a related
   Resource referenced from `meta.xref`. The detached JWS and
   `subject.digest` are retained unchanged because xRegistry provides no
   native signing or content-addressing to delegate to.

4. **Nested catalog entries** become nested Groups; the parent entry's
   Resource references the nested Group through `meta.xref`.

## Unpacking: xRegistry to AI Catalog

Tooling converts xRegistry resources back to an AI Catalog JSON document:

1. Retrieve the Group in document view (the xRegistry `?doc` projection),
   which returns a single self-contained JSON document analogous to
   `ai-catalog.json`.
2. For each Resource, read its document (inline or via `<RESOURCE>url`)
   and `contenttype` to recover the entry's artifact content and
   `type`; map `name`, `description`, and `labels` back to entry
   metadata.
3. Read the Trust Manifest from the extension attribute or `xref`'d
   Resource, and verify its detached JWS and `subject.digest` against the
   served bytes.
4. Resolve `xref`'d nested Groups into nested catalog entries.
5. Assemble the logical `application/ai-catalog+json` document.

## xRegistry Document Example

The following shows the xRegistry document-view representation of a Group
holding two entries. This is generated by tooling, not authored by hand:

```json
{
  "aicatalogid": "acme-services",
  "self": "https://registry.acme.com/aicatalogs/acme-services",
  "xid": "/aicatalogs/acme-services",
  "epoch": 1,
  "name": "Acme Services Inc.",
  "entriesurl": "https://registry.acme.com/aicatalogs/acme-services/entries",
  "entriescount": 2,
  "entries": {
    "finance-a2a": {
      "entryid": "finance-a2a",
      "xid": "/aicatalogs/acme-services/entries/finance-a2a",
      "name": "Acme Finance A2A Agent",
      "contenttype": "application/a2a-agent-card+json",
      "labels": {
        "ai-catalog.identifier": "urn:acme:agent:finance-a2a"
      },
      "entryurl": "https://cards.acme.com/finance/a2a-card.json",
      "aicatalog_trustmanifest": {
        "issuedAt": "2025-01-01T00:00:00Z",
        "subject": {
          "type": "application/a2a-agent-card+json",
          "digest": "sha256:aaa111..."
        },
        "signature": "eyJhbGciOiJFUzI1NiJ9..detached-JWS.."
      }
    },
    "finance-mcp": {
      "entryid": "finance-mcp",
      "xid": "/aicatalogs/acme-services/entries/finance-mcp",
      "name": "Acme Finance MCP Server",
      "contenttype": "application/mcp-server-card+json",
      "labels": {
        "ai-catalog.identifier": "urn:acme:server:finance-mcp"
      },
      "entryurl": "https://cards.acme.com/finance/mcp-server.json"
    }
  }
}
```

## Content Integrity and Signing

Because xRegistry has no native content-addressing or signature
primitive, this binding does not delegate those invariants: the Trust
Manifest's detached JWS and `subject.digest` remain the source of truth,
verified against the served Resource document during unpacking — the same
model as plain-HTTP distribution. An implementation MAY additionally
expose the digest as an extension attribute for discovery convenience, but
that copy is advisory; the Trust Manifest remains authoritative.

# Mapping to MCP Servers

This appendix describes how **remote (HTTP-connectable) MCP servers**
map to AI Catalog, enabling them to be discovered alongside other AI
artifacts through a unified catalog. The documented, supported path is
to reference each server's **MCP Server Card**
([SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127))
as the artifact content of a Catalog Entry.

## Overview

An MCP Server Card is a static discovery document for an individual
HTTP-based MCP server, describing its identity and how to connect to it.
A Catalog Entry references the card wherever the server publishes it, as
in the examples below. See
[SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127)
for the Server Card's schema, fields, and hosting conventions.

In AI Catalog terms, the Server Card is the **artifact content** — the
native metadata that a Catalog Entry references via its `url`, declared
with the known type `application/mcp-server-card+json`. The AI Catalog
does not duplicate or redefine Server Card fields; it provides the
discovery and trust layer that the Server Card does not address.

AI Catalog and MCP Server Cards address different layers of discovery:

MCP Server Card (per-server)
: What does this specific MCP server offer? What transport does it
  use? What tools and resources are available? What authentication
  is required?

AI Catalog (cross-artifact)
: What artifacts does this domain offer? Who published them? Can I
  trust them? What other artifact types are available alongside MCP
  servers?

## Conceptual Mapping

| MCP Server Card | AI Catalog Equivalent |
|:---|:---|
| Server Card document (whole file) | Artifact content via entry `url` (type `application/mcp-server-card+json`) or `data` |
| Server `name` (reverse-DNS identifier) | Entry `identifier` (mapped to the `urn:air:{publisher}:{namespace}:{name}` URN form — e.g. `urn:air:acme-corp.com:mcp:finance-server`) |
| `title` | Stays in the Server Card (which carries its own `title`); entry `displayName` is omitted unless the artifact lacks a name |
| `description` | Stays in the Server Card (which carries its own `description`); entry `description` is omitted to avoid duplicating a value that can drift |
| `version` | Stays in the Server Card (which carries its own `version`); entry `version` is omitted to avoid duplicating a value that can drift (a remote MCP server serves one Server Card, so a catalog never lists multiple versions of it) |
| transport / capabilities / tools / resources / auth | Inside the Server Card — not surfaced in the catalog |
| `repository` | Stays in the Server Card (which carries its own `repository`); omitted from the entry to avoid duplicating a value that can drift — catalog-level source/provenance links surface through the Trust Manifest when needed |
| *(not in the Server Card)* | Entry `publisher` |
| *(not in the Server Card)* | Entry `trustManifest` (identity, attestations, provenance) |
| *(not in the Server Card)* | Entry `tags` for cross-artifact discovery |

## MCP Server as Catalog Entry

A remote MCP server maps to a Catalog Entry whose `url` points to the
server's Server Card and whose `type` is the known type
`application/mcp-server-card+json`:

```json
{
  "identifier": "urn:air:acme-corp.com:mcp:finance-server",
  "type": "application/mcp-server-card+json",
  "url": "https://api.acme-corp.com/mcp/server-card",
  "tags": ["finance", "mcp"],
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  },
  "trustManifest": {
    "identity": "urn:air:acme-corp.com:mcp:finance-server",
    "attestations": [
      {
        "type": "publisher-identity",
        "uri": "https://trust.acme-corp.com/certs/publisher.jwt"
      },
      {
        "type": "SOC2-Type2",
        "uri": "https://trust.acme-corp.com/reports/soc2.pdf",
        "digest": "sha256:a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
      }
    ]
  }
}
```

> **Note on `type`:** The `type` member is an open-text type identifier
> ([ADR 0014](https://github.com/Agent-Card/ai-catalog/blob/main/adr/0014-media-type-to-type.md));
> any string is accepted, with a recommended set of "known types." The
> known type for an MCP server referenced by its Server Card is
> `application/mcp-server-card+json`.

## MCP Servers as an AI Catalog

A domain that hosts remote MCP servers can publish them as an AI Catalog,
letting clients that understand `application/ai-catalog+json` discover
those servers alongside A2A agents, skills, and other artifacts. Each
entry points to a server's Server Card:

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme MCP Servers",
    "identifier": "did:web:acme-corp.com",
    "documentationUrl": "https://acme-corp.com/docs"
  },
  "entries": [
    {
      "identifier": "urn:air:acme-corp.com:mcp:finance-server",
      "type": "application/mcp-server-card+json",
      "url": "https://api.acme-corp.com/finance/server-card",
      "tags": ["finance", "mcp"]
    },
    {
      "identifier": "urn:air:acme-corp.com:mcp:docs-search",
      "type": "application/mcp-server-card+json",
      "url": "https://api.acme-corp.com/docs-search/server-card",
      "tags": ["search", "docs"]
    },
    {
      "identifier": "urn:air:acme-corp.com:mcp:ci-cd",
      "type": "application/mcp-server-card+json",
      "url": "https://api.acme-corp.com/ci-cd/server-card",
      "tags": ["ci", "cd", "devops"]
    }
  ]
}
```

## Decentralized Discovery

AI Catalog enables decentralized discovery: any domain can publish its
MCP servers at `/.well-known/ai-catalog.json` without registering with a
central authority.

A vendor hosting its own MCP servers can publish:

```
https://api.acme-corp.com/.well-known/ai-catalog.json
```

The catalog and the Server Card play two complementary roles: the
catalog is how a client *finds* a server's URL in the first place, and
the Server Card is the connection entry point it points at. They are
useful independently — a client that already knows a server's URL can
point at its Server Card directly, with no catalog traversal, while a
client starting from just a domain uses the catalog to enumerate what
that domain offers.

Because of this, there is no single prescribed discovery ordering.
Clients wire discovery in wherever it fits their architecture — probing
a domain's catalog when it enters a session, watching outbound traffic
at an egress boundary, or connecting to a known Server Card directly. A
typical catalog-first path is: fetch `/.well-known/ai-catalog.json`,
filter entries by `type` (`application/mcp-server-card+json`) to find
MCP servers, follow an entry's `url` to its Server Card for connection
details, and connect — evaluating the Trust Manifest (when present) for
publisher identity and attestations along the way. Whatever the path,
the Server Card is advisory: a client reconciles it against the live
connection and MUST NOT treat it as authoritative for access control —
the connection itself remains the source of truth. See the Server Card
[best-practices guidance](https://github.com/modelcontextprotocol/experimental-ext-server-card)
for the range of client integration strategies.

This separation lets AI Catalog provide the trust and cross-ecosystem
indexing layer while the MCP Server Card provides the protocol-specific
operational details. A domain with multiple MCP servers publishes one AI
Catalog listing all of them, with each entry pointing to its respective
Server Card.

## What AI Catalog Adds

A Server Card describes a single server but has no cross-server discovery
or trust layer. AI Catalog fills this gap:

1. **Publisher identity**: Verifiable publisher with DID or domain
   anchor.
2. **Trust verification**: Attestations (SOC2, HIPAA, publisher
   identity proofs) via the Trust Manifest.
3. **Provenance**: Links to source repositories, registries, and
   build artifacts with cryptographic digests.
4. **Signing**: Detached JWS signature on the Trust Manifest for
   integrity verification.
5. **Cross-ecosystem discovery**: MCP servers become discoverable
   alongside A2A agents, plugins, and datasets through a single
   catalog format.
6. **Composability**: MCP servers can be packaged with related
   artifacts (A2A agents, datasets) in nested catalogs.

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
| Plugin `name` | Entry `identifier` (derived as URN); the plugin manifest carries its own name, so entry `displayName` is omitted |
| Plugin `description` | Stays in the plugin manifest (which carries its own `description`); entry `description` is omitted to avoid duplicating a value that can drift |
| Plugin `category` | Entry `tags[]` (first tag) |
| Plugin `tags` | Entry `tags[]` (merged with category) |
| Plugin `author` | Entry `publisher` |
| Plugin `source` (url, git-subdir, or path) | Entry `url` (pointing to the plugin repository) |
| Plugin `source.sha` | Entry `trustManifest.provenance[].sourceDigest` |
| Plugin `homepage` | Entry `metadata.homepage` |
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
      },
      "metadata": {
        "homepage": "https://github.com/anthropics/claude-plugins-public/tree/main/plugins/agent-sdk-dev"
      }
    },
    {
      "identifier": "urn:claude-plugin:adspirer:ads-agent",
      "type": "application/vnd.anthropic.claude-plugin+json",
      "url": "https://github.com/amekala/adspirer-mcp-plugin.git",
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

# Acknowledgments

This specification was developed through collaboration among members of
the A2A and MCP protocol communities under the governance of the Linux
Foundation.
