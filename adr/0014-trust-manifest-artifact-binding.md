# ADR-0014: Bind Trust Manifest Signatures to Artifact Content

**Status:** Accepted

**Date:** 2026-06-20

**Participants:** Luca Muscariello (Cisco)

## Context

[ADR-0009](0009-trust-manifest-substitution.md) acknowledged that Trust
Manifest substitution is a real threat and called for a security review.
That review was performed as a STRIDE threat model (see
[trust-manifest-threat-model.md](../specification/trust-manifest-threat-model.md))
and confirmed the central weakness: the `signature` covered only the
Trust Manifest JSON, while the artifact reference (`url`, `data`,
`mediaType`) lived on the Catalog Entry *outside* the signed payload.
The only binding was `identity == identifier`. An attacker who controlled
the catalog document could keep a validly-signed manifest and repoint
`url` to a malicious artifact — the signature would still verify
(threat T1 / finding F1).

The threat model also compared the design against the Sigstore
architecture from which it derives. Sigstore's Cosign signs the artifact
*digest*, Fulcio binds identity through a CA, and Rekor witnesses the
event in a transparency log. The Trust Manifest natively reproduced none
of these; most importantly it lacked Cosign's digest binding.

## Decision

Bind a signed Trust Manifest to the artifact it describes and harden the
verification story:

1. **Subject binding.** A signed Trust Manifest MUST include a `subject`
   object `{ url?, mediaType, digest }` committing to the artifact's
   media type and content digest. `subject` is part of the signed
   payload, so the artifact reference cannot be changed without
   invalidating the signature. (Closes F1; mirrors Cosign.)
2. **Signatures required at Level 3.** A Trusted Catalog MUST carry a
   `signature`, `subject`, and `issuedAt` on each relied-upon entry, and
   consumers MUST verify them. (Closes F2.)
3. **Trust anchoring.** Verification MUST anchor `identity` to an
   out-of-band trust root; a verified signature alone proves internal
   consistency, not publisher authenticity. (Closes F3; substitutes for
   Fulcio's CA-attested identity.)
4. **Algorithm allowlist.** Consumers MUST reject `alg: none` and
   symmetric algorithms and MUST use asymmetric JWS algorithms. (F4)
5. **Freshness.** Add `issuedAt` (REQUIRED when signed) and `expiresAt`,
   with anti-rollback and revocation guidance. (F5)
6. **Catalog-level integrity.** Add an OPTIONAL top-level catalog
   `signature` and recommend content-addressed (OCI) distribution. (F6)
7. **Safe fetching.** Verification MUST defend against SSRF and
   oversized responses. (F7)
8. **Provenance-statement and publisher verification** procedures are
   defined; publisher fields are advisory unless bound. (F8, F9)

## Sigstore convergence

The Trust Manifest remains a *format that carries* trust evidence, not a
replacement for Sigstore services. The specification SHOULD allow
Sigstore evidence to be first-class: a `sigstore-bundle` attestation
(certificate + signature + Rekor inclusion proof), anchoring via the
Sigstore TUF root, and a preference for transparency-log inclusion and
keyless signing over long-lived publisher keys. This lets
trust-sensitive deployments inherit Sigstore's full chain instead of a
weaker re-implementation. Tracked as future work.

## Consequences

- The substitution attack from ADR-0009 is closed for signed manifests.
- Level 3 conformance is stricter: presence of a manifest is no longer
  sufficient; it must be signed and bound.
- Residual gaps versus Sigstore remain (no native transparency log,
  long-lived keys, trust-anchor bootstrapping) and are documented as
  residual risks plus the Sigstore-convergence roadmap.
