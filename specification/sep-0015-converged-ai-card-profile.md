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

### 4.1 Card Envelope

A card document MUST include:

- `$schema`: URI for this profile schema.
- `specVersion`: profile version.
- `cardVersion`: version of this card document (publisher-controlled).
- `cardKind`: `live-service`, `data-asset`, or `hybrid`.
- `id`: globally unique URI for the subject.
- `name`: human-readable name.
- `description`: concise description.
- `publisher`: publisher identity object.
- `createdAt`: RFC 3339 timestamp.
- `updatedAt`: RFC 3339 timestamp.

A card MAY include:

- `identityType`: type hint for `id`.
- `logoUrl`, `tags`, `maturity`, `metadata`.
- `trust`: trust and compliance references.
- `signatures`: one or more detached signatures.
- `modules`: extension modules.
- `locators`: live endpoints and artifact locations.
- `artifacts`: immutable at-rest assets.

### 4.2 Publisher Object

`publisher` MUST include:

- `id`: globally unique publisher URI.
- `name`: human-readable publisher name.

`publisher` MAY include:

- `identityType`.
- `attestation`: optional identity proof reference.

### 4.3 Trust and Provenance

`trust` MAY include:

- `attestations`: list of trust artifacts (audits, certifications, compliance proofs).
- `privacyPolicyUrl`.
- `termsOfServiceUrl`.

Each attestation SHOULD follow a reference pattern:

- `type`, `uri`, `mediaType`, optional `digest`, optional `size`, optional `description`.

`signatures` is preferred over a single `signature` string and SHOULD support key rotation and multiple signers.

Each signature entry SHOULD include:

- `format` (for example `jws-compact`),
- `value` (detached signature),
- `keyId`,
- `createdAt`.

### 4.4 Modules (Delegated Metadata)

`modules` is the extension mechanism for protocol/domain metadata.

Each module MUST include:

- `id`: stable module namespace identifier (example: `protocol/a2a`, `protocol/mcp`, `domain/healthcare`).
- `version`: module schema version.
- `data`: JSON object payload validated by the module owner schema.

Each module MAY include:

- `required`: boolean. If `true`, consumers that do not understand the module MUST reject processing.
- `digest`: digest for externalized module data.

Core profile MUST NOT define module-internal fields.

### 4.5 Locators (Discovery and Access)

`locators` provides normalized references to live services or cards in registries.

Each locator SHOULD include:

- `type`: `https`, `oci`, or other scheme category.
- `uri`: concrete URI.
- `role`: one of `card`, `catalog`, `api`, `artifact`.
- `digest` (recommended for immutable content).
- `mediaType`.

### 4.6 Artifacts (At-rest Assets)

`artifacts` MUST be present when `cardKind = data-asset`.

Each artifact MUST include:

- `uri`, `mediaType`.

Each artifact SHOULD include:

- `digest`, `size`, `schemaUri`, `description`.

## 5. Discovery Bindings

### 5.1 HTTP Well-known Binding

Producers SHOULD expose:

- `/.well-known/ai-catalog.json` for collection discovery.
- Optional direct card location via catalog entries.

Catalog entries MUST include:

- `id`, `name`, `description`, `cardUrl`, `updatedAt`.

### 5.2 Registry Binding

The same card payload MAY be published to registry technologies.

Registry publication SHOULD preserve:

- Content-addressable retrieval (`digest`).
- Media type declaration.
- Stable linkage from catalog/discovery to immutable card versions.

## 6. Identifier and Security Requirements

1. `id` MUST be globally unique and stable over time for the same logical subject.
2. `id` MUST be a URI and SHOULD use decentralized or domain-anchored schemes.
3. Signed cards SHOULD be verifiable without a central trust broker.
4. If `signatures` are present, verifiers MUST validate signature and subject binding.
5. Trust assertions without signatures MUST be treated as self-asserted.

## 7. Conformance Levels

1. `L0-Base`: required core envelope only.
2. `L1-Signed`: `L0` + at least one valid signature.
3. `L2-Trust`: `L1` + trust attestations and policy URLs.
4. `L3-Portable`: `L2` + HTTP and registry locators with immutable digests.

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
   - `live-service`
   - `data-asset`
   - mixed catalog entries

Remaining work:

1. Add automated schema validation in CI for all examples.
2. Add a `hybrid` card example.
3. Run interop tests across at least two protocols and two registry backends.
