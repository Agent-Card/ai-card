# ADR 0019: Support Multiple Identities via `alsoKnownAs` in the Trust Manifest

## Status
Proposed

## Date
2026-07-24 (Proposed)

**Participants:** Alexander Shenshin (DSR Corporation), Darrel Miller (Microsoft), Jeffrey Damick (Amazon), Junjie Bu (Google), Ramiz Polic (Cisco), Sam Betts (Cisco)

## Context
A catalog entry can declare exactly one cryptographic identity through the `trustManifest.identity` field (with an optional `identityType` hint). Real artifacts frequently hold more than one verifiable identity at the same time, for example:

- a SPIFFE ID (`spiffe://acme.com/ns/finance/sa/finance-a2a-pod`) for runtime/workload identity, and
- a DID (`did:web:acme-corp.com`) for organizational/publisher-anchored identity.

There is no first-class place to list additional identities. Authors are forced to add them through `attestations[]` or `metadata`, where consumers do not reliably look for them and cannot treat them as verifiable subject identities ([issue #52](https://github.com/Agent-Card/ai-catalog/issues/52)). The workarounds are inadequate:

- **Attestations are limiting.** An `Attestation` is a typed claim with evidence, designed for compliance documents. There is no standard attestation type meaning "this is another identity of the same subject", so alternate identities cannot be discovered or pinned programmatically.
- **Metadata is opaque.** Per the spec, consumers SHOULD ignore metadata keys they do not recognize, so a second identity placed there is invisible and non-interoperable.
- **Conflicts with the domain-alignment rule.** The rule binding the `identity` trust domain to the publisher domain of the entry's `identifier` is written for a single identity and gives no guidance for identities in other trust domains.

Use cases requiring multiple identities include: co-equal runtime and publisher identities, relying parties that can only resolve a subset of identity schemes, and migration/rotation between identity schemes without breaking existing consumers.

A key constraint shaped this decision: **declared identities MUST be verifiable through the trust bundle.** An identity claim a consumer cannot verify is worse than no claim at all.

## Decision
The Trust Manifest gains an OPTIONAL `alsoKnownAs` member: an array of globally unique URIs, each asserting an alternative identity of the **same subject** as the canonical `identity` field.

```json
"trustManifest": {
  "identity": "spiffe://acme.com/ns/finance/sa/finance-agent-pod",
  "identityType": "spiffe",
  "alsoKnownAs": [
    "did:web:acme-corp.com:agent:finance"
  ],
  "signature": "eyJhbGciOiJFUzI1NiJ9..detached-jws-signature"
}
```

Normative rules:

1. `identity` remains the single **canonical** subject identifier, used for referencing and equivalence checking. Aliases are co-equal for verification purposes but never canonical.
2. `alsoKnownAs` MUST NOT contain the value of `identity` and MUST NOT contain duplicates; element order carries no significance.
3. The domain-alignment rule applies only to `identity`. Aliases MAY belong to different trust domains or identity schemes.
4. Aliases are publisher claims verified through the existing Trust Manifest `signature`, which covers `alsoKnownAs` as manifest content — no per-alias proof mechanism is defined. Consumers MUST NOT rely on an alias from a manifest whose signature is absent or fails verification. Because the signature proves the publisher claims the alias (not that the alias's trust domain acknowledges the link), authorization decisions inside the alias's trust domain SHOULD additionally rely on proof of control native to the alias scheme (e.g., a DID Document back-reference or DNS TXT record); such proofs are out of scope.
5. A consumer MAY select any verified identity, canonical or alias, matching the schemes it can resolve, rather than rejecting an entry whose canonical identity uses an unsupported scheme.

### Placement: inside the Trust Manifest, not on the Catalog Entry
We explicitly considered placing `alsoKnownAs` on the parent Catalog Entry (as a sibling of `identifier`) and rejected it:

- **Signature coverage is decisive.** The Trust Manifest is the only signed unit in the specification, the detached JWS is computed over the JCS-canonicalized manifest content. Fields on the Catalog Entry are not covered by any signature, so under the spec's catalog-poisoning threat model an attacker who can modify the catalog document could inject or strip entry-level aliases undetected. Inside the manifest, aliases are forgery-proof at trust Layer 2, satisfying the "verifiable through the trust bundle" constraint.
- **Separation of concerns (ADR-0015).** The entry's `identifier` is a logical *name* (`urn:air:...`) for discovery and routing; cryptographic *identities* live in the Trust Manifest. Alternative identities are identities, so they belong beside `identity`, not beside the URN.
- **Ecosystem precedent.** W3C DID Core defines `alsoKnownAs` on the DID Document with the same publisher-asserted, same-subject semantics adopted here.
- **Reuse for hosts.** Host Info carries a `trustManifest` too, so hosts gain multi-identity support without adding a new field to two parent structures.

The trade-off is that entries without a Trust Manifest cannot declare aliases. This is acceptable because an alias outside the trust bundle would be unverifiable by construction.

## Rationale
- **Interoperability**: A standard, first-class shape means consumers can programmatically discover alternate identities instead of relying on per-publisher attestation or metadata conventions.
- **Simple equivalence checking**: Keeping a single canonical `identity` avoids forcing consumers to choose which of N identities "names" the entry.
- **Backward compatible**: `alsoKnownAs` is OPTIONAL and additive. Existing manifests remain valid; existing consumers that ignore the field lose nothing they had before.
- **Verifiability by construction**: Because the field lives inside the signed manifest content, no new signing mechanism is needed, the existing JCS + detached JWS procedure covers it.

## Alternatives Considered
- **`identities[]`: an array of Identity objects** (each with `identity`, `identityType`, and optionally its own `signature`). Rejected: it makes equivalence checking harder, forces consumers to choose which identity to use when referencing the entry, and multiplies signature-verification paths. The variant dropping the primary `identity` entirely was also rejected as a breaking change to the existing spec.
- **`trustManifests[]`: multiple Trust Manifests per entry.** Fully independent trust metadata per identity (separate attestations, provenance, signatures). Rejected as disproportionate: the motivating use cases need equivalent identities for one subject, not parallel trust bundles, and multiple manifests reintroduce the "which manifest is authoritative?" problem at a larger scale.
- **`alsoKnownAs` on the Catalog Entry (parent structure).** Rejected for the placement reasons above, mainly that entry-level fields fall outside the signed trust bundle and therefore cannot satisfy the verifiability requirement.
- **Status quo (attestations/metadata workarounds).** Rejected as non-interoperable and non-verifiable, per the Context section.

## Consequences
- **Specification**: The Trust Manifest optional members, verification procedures (new "Verifying Alternative Identities" section), CDDL schema, data model diagram, and examples are updated.
- **Consumers**: Clients that verify Trust Manifest signatures automatically gain tamper-proof alias coverage. Clients unaware of the field are unaffected.
- **Publishers**: Publishers currently smuggling secondary identities through `attestations[]` or `metadata` SHOULD migrate them to `alsoKnownAs`.
- **Future work**: If per-alias proofs become necessary (e.g., alias-side attestations or inline alias-specific signatures), a structured object form can be layered on without breaking the URI-array form.

## Meeting Reference
Proposed from [issue #52](https://github.com/Agent-Card/ai-catalog/issues/52) discussion; `alsoKnownAs` was favored over an identities array in issue comments (2026-07). Update the Status and Date once the working group ratifies it.
