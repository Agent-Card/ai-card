# SEP 0015 - Converged AI Card Profile (Draft)

Status: Draft proposal
Authors: AI Card contributors
Target: Common profile for service and artifact metadata across protocol ecosystems

## 1. Summary

This proposal defines a converged AI Card profile that:

1. Supports rich metadata for all AI assets (live services and data/model artifacts).
2. Delegates protocol-specific metadata to protocol owners without forcing core-spec changes.
3. Works across multiple registry and transport technologies.
4. Provides verifiable identity and cryptographic provenance.
5. Preserves simple HTTP discovery while enabling registry-native publication.

## 2. Scope

This profile defines:

1. Core card envelope and required common fields.
2. Extension module model for protocol and domain-specific metadata.
3. Discovery bindings for HTTP well-known and registry publication.
4. Security model for card signing and attestation references.
5. Conformance levels for gradual adoption.

This profile does not define protocol internals (for example, A2A skills or MCP capabilities).

## 3. Design Principles

1. Core fields are minimal, stable, and shared.
2. Protocols are autonomous: each protocol owns its own module schema and versioning.
3. Multiple distribution channels are first-class (HTTP and registry-backed).
4. Security is explicit and machine-verifiable.
5. One schema supports both live services and assets at rest.

## 4. Data Model

### 4.1 Card Envelope (AICard)

An AICard document MUST include:

- `$schema`: URI for this profile schema.
- `specVersion`: profile version.
- `cardVersion`: version of this card document (publisher-controlled).
- `id`: globally unique URI for the subject.
- `name`: human-readable name.
- `description`: concise description.
- `publisher`: publisher identity object.
- `createdAt`: RFC 3339 timestamp.
- `updatedAt`: RFC 3339 timestamp.

An AICard MAY include:

- `identifierType`: type hint for `id`.
- `logoUrl`, `tags`, `maturity`, `metadata`.
- `domains`: high-level domain taxonomy for discovery.
- `skills`: problem/skill taxonomy for discovery.
- `capabilities`: optional high-level capability descriptors.
- `trust`: trust and compliance references.
- `signatures`: one or more detached signatures.
- `modules`: extension modules grouped by type.

Discovery labels (`tags`, `domains`, `skills`, `capabilities`) provide a generic, protocol-agnostic index for search and filtering.
Module data remains the authoritative, protocol- or artifact-specific metadata.
Consumers SHOULD use discovery labels to find candidates and then read module data to understand precise protocol behaviors or artifact details.

### 4.2 Protocol and Artifact Cards

Protocol and artifact cards are represented inside the `modules` map.
Each module entry represents a protocol-specific or artifact-specific card and MAY be independently signed.

### 4.3 Publisher Object

`publisher` MUST include:

- `id`: globally unique publisher URI.
- `name`: human-readable publisher name.

`publisher` MAY include:

- `identifierType`.
- `attestation`: optional identity proof reference.

### 4.4 Trust and Provenance

`trust` MAY include:

- `trustSchema`: declaration of the trust model and verification policy used for this card.
- `attestations`: list of trust artifacts (audits, certifications, compliance proofs).
- `provenance`: signed or verifiable lineage links to source artifacts, source cards, and registry records.
- `privacyPolicyUrl`.
- `termsOfServiceUrl`.

If present, `trustSchema` SHOULD include:

- `id`: stable URI for the trust schema/profile.
- `version`: trust schema version.
- optional `governanceUri`: policy or governance document for the trust domain.
- optional `verificationMethods`: supported verification mechanisms (for example `dns-01`, `http-01`, `did`, `x509`, `spiffe`).

Each `provenance` entry SHOULD include:

- `relation`: lineage relationship (for example `derivedFrom`, `materializedFrom`, `publishedFrom`).
- `sourceId`: identifier of the source card or source subject.
- optional `sourceDigest`: immutable digest of the source payload.
- optional `registryUri`: registry record URI used for retrieval.
- optional `statementUri`: URI of a signed provenance statement (for example DSSE/in-toto/SLSA predicate).
- optional `signatureRef`: key or signature reference used to verify the provenance statement.

To avoid self-referential dependency loops, provenance data embedded in the card MUST be reference-oriented.
The card SHOULD carry links to immutable external evidence (for example registry attestations or transparency-log entries) instead of embedding full signed statements whose subject is the same card bytes.

Each attestation SHOULD follow a reference pattern:

- `type`, `uri`, `mediaType`, optional `digest`, optional `size`, optional `description`.

`signatures` is preferred over a single `signature` string and SHOULD support key rotation and multiple signers.

Each signature entry SHOULD include:

- `format` (for example `jws-compact`),
- `value` (detached signature),
- `keyId`,
- `createdAt`.

### 4.5 Modules (Delegated Metadata)

`modules` is the extension mechanism for protocol/domain metadata.

`modules` is a map grouped by type:

- `protocols`: protocol-specific modules (example keys: `a2a`, `mcp`).
- `artifacts`: artifact-specific modules (example keys: `dataset`, `model`).

Each module MUST include:

- `id`: stable module namespace identifier (example: `protocol/a2a`, `protocol/mcp`, `domain/healthcare`).
- `version`: module schema version.
- `data`: JSON object payload validated by the module owner schema.

Each module MAY include:

- `required`: boolean. If `true`, consumers that do not understand the module MUST reject processing.
- `digest`: digest for externalized module data.

Core profile MUST NOT define module-internal fields.

### 4.6 Locators (Discovery and Access)

Locators are protocol- or artifact-card specific and are defined inside the relevant module data.
The core profile does not standardize locator fields because routing is protocol-specific.

### 4.7 Artifacts (At-rest Assets)

Artifacts are described inside artifact-card modules.
Artifact modules SHOULD use the following fields:

- `uri`, `mediaType`.
- `digest`, `size`, `schemaUri`, `description`.

### 4.8 Runtime Materialization Behavior (Data-at-Rest to Live Service)

This profile is intended to support lifecycle transitions where an artifact card can be transformed into a live runtime and exposed as a service.

Target behavior:

1. An artifact-focused card can describe immutable deployable content (for example, OCI-referenced assets).
2. A runtime system can materialize that content into a running workload.
3. The running workload can expose runtime identity (process/container/task identity) and/or service endpoints.
4. A corresponding protocol-focused card can represent the active runtime view.
5. Producers and registries can preserve traceability between the at-rest card and the runtime service card.

OCI-style analogy:

1. A manifest (at-rest reference) identifies immutable image content.
2. A runtime pulls and instantiates that content.
3. The instantiated workload has runtime identity (for example, PID/container/task ID) and can expose a network endpoint.
4. The service-facing metadata is discoverable through a protocol-focused card.

Recommended linkage patterns:

1. Use module-defined locators for immutable artifact references and active endpoints.
2. Include signed provenance references in `trust.attestations` so verifiers can validate source-to-runtime lineage.
3. Use a module (or profile extension) to capture runtime binding details (for example deployment digest, workload identity, startup time, and endpoint activation status).
4. Keep logical subject identity stable when possible; if runtime identity is ephemeral, bind ephemeral runtime identifiers to a stable subject through signed claims.

## 5. Discovery Bindings

### 5.1 HTTP Well-known Binding

Producers SHOULD expose:

- `/.well-known/ai-catalog.json` for collection discovery.
- Optional direct card location via catalog entries.

Catalog records MUST include:

- `id`, `name`, `description`, `cardUrl`, `updatedAt`.

### 5.2 Registry Binding

The same card payload MAY be published to registry technologies.

Registry publication SHOULD preserve:

- Content-addressable retrieval (`digest`).
- Media type declaration.
- Stable linkage from catalog/discovery to immutable card versions.

For generic registries (that do not natively model trust relationships), publishers SHOULD provide explicit lineage links in `trust.provenance` so consumers can reconstruct source-to-card and artifact-to-runtime provenance.

When provenance needs to bind a card publication event, producers SHOULD use an acyclic two-phase flow:

1. Produce and sign the card version.
2. Publish the card to a registry and let registry-native provenance be generated over immutable registry subjects (for example manifest digest).
3. Reference that external provenance from a later card revision or a catalog/registry side record.

This prevents a card version from needing to contain provenance that depends on signatures computed over that same final card version.

## 6. Identifier and Security Requirements

1. `id` is the identifier (the logical name) for the subject and MUST be globally unique and stable over time.
2. `id` MUST be a URI and SHOULD use decentralized or domain-anchored schemes (for example `did:` or `urn:`).
3. The identifier namespace MUST be verifiable by a trust mechanism appropriate to the scheme and publishing domain.
4. Namespace verification MAY include DNS or HTTP challenges, DID method proofs, workload identity systems, or other externally defined trust schemes.
5. The identifier is a name; it is distinct from an identity credential or account that proves control.
6. `identifierType` MAY indicate the verification domain or scheme used to validate the identifier or signature binding.
7. Signed cards SHOULD be verifiable without a central trust broker.
8. If `signatures` are present, verifiers MUST validate signature and subject binding.
9. Trust roots and verification policy are external to this profile and SHOULD be referenced through `trust.trustSchema`.
10. Trust assertions without signatures MUST be treated as self-asserted.
11. Verifiers SHOULD prefer immutable external provenance evidence (registry or transparency log) when available, and treat card-embedded provenance as linkage metadata.

### 6.1 Subject Commitment Model (Normative)

To ensure interoperability across registries and prevent circular verification dependencies, this profile defines two digest scopes:

1. **subject scope**: digest over a canonicalized logical payload.
2. **blob scope**: digest over the exact stored bytes in a transport or registry.

Normative requirements:

1. Producers MUST distinguish subject-scope and blob-scope digests and MUST NOT compare them as if they were equivalent values.
2. Producers MUST define one canonicalization method for subject-scope hashing for each profile version.
3. Subject-scope signatures and attestations MUST bind to the canonical subject bytes, not to mutable or transport-specific encodings.
4. Card validity MUST NOT depend on resolving provenance that cryptographically commits to the same full card bytes for that same card revision.
5. Card-embedded provenance MUST be reference-oriented and SHOULD point to immutable external evidence (for example registry attestations or transparency-log entries).
6. If provenance for a card publication event is generated after publication, producers SHOULD reference it from a later card revision or from a side record.
7. Verifiers MUST perform signature and digest checks within the declared scope (`subject` or `blob`) and MUST reject scope-ambiguous claims.

Recommended verifier order:

1. Verify blob-scope integrity for retrieved registry content.
2. Derive and canonicalize the subject payload.
3. Verify subject-scope signatures and attestations.
4. Resolve provenance links and validate lineage constraints.

This model allows different registries to maintain their native blob digests while preserving a portable subject-level trust model for cross-registry verification.

## 7. Conformance Levels

1. `L0-Base`: required core envelope only.
2. `L1-Signed`: `L0` + at least one valid signature.
3. `L2-Trust`: `L1` + trust attestations and policy URLs.
4. `L3-Portable`: `L2` + module-defined locators with immutable digests for registry publication.

## 8. Backward Compatibility and Migration

This profile absorbs previous draft variants using `services`, `interfaces`, or `protocols` by mapping them into `modules`:

1. A prior `protocols.a2a.protocolSpecific` payload maps to module `protocol/a2a`.
2. A prior `protocols.mcp.protocolSpecific` payload maps to module `protocol/mcp`.
3. Existing top-level trust fields remain valid with no semantic change.

## 9. Open Questions

1. Should the profile require one canonical signature format in v1?
2. Should module IDs be centrally registered or convention-based?
3. Should `cardVersion` follow semver or monotonically increasing revision?

## 10. Next Steps

This draft now includes:

1. JSON Schemas for card and catalog payloads:
   - `specification/schema/schema.json`
   - `specification/schema/catalog-schema.json`
2. CDDL definitions for card and catalog payloads:
   - `specification/cddl/ai-card-profile.cddl`
   - `specification/cddl/ai-catalog.cddl`
3. Example payloads for:
   - protocol-focused cards
   - artifact-focused cards
   - mixed catalog entries

Remaining work:

1. Add automated schema validation in CI for all examples.
2. Add a multi-card record example.
3. Run interop tests across at least two protocols and two registry backends.
