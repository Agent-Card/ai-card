# ADR-0009: Trust Manifest Substitution Attack Must Be Addressed

**Status:** Proposed

**Date:** 2026-04-02

**Participants:** Pamela Dingle (Microsoft), Sam Betts (Cisco),
Luca Muscariello (Cisco), Darrel Miller (Microsoft)

## Context

Pamela Dingle raised a security concern: "The substitution attack of
changing out the trust manifest is very real, especially if there's no
tamper-proofness built in." An attacker who can modify a catalog in
transit or at rest could replace a legitimate Trust Manifest with a
fraudulent one, making a malicious artifact appear trusted.

Sam Betts noted that the OCI approach of "digests all the way down"
provides content-addressability. Luca added that provenance metadata
builds on integrity: "once you get that, it's easy to append."

The spec already includes a `signature` field (detached JWS) on the
Trust Manifest and digest fields on attestation and provenance objects,
but Pam's feedback indicates the verification story needs expert review.

## Decision

Acknowledge that Trust Manifest substitution is a real threat that must
be addressed. The existing mechanisms (detached JWS signature, digest
fields, verification procedures) are a starting point but need security
review.

## Action Items

- Have a security-focused contributor review the verification
  procedures section.
- Consider whether the Trust Manifest `signature` should be RECOMMENDED
  rather than OPTIONAL for Level 3 (Trusted Catalog) conformance.
- Evaluate whether entry-level digests (binding the entry to its
  artifact content) should be added alongside Trust Manifest signatures.
- Align with OCI content-addressability patterns for the OCI
  distribution mapping.

## Consequences

- The security considerations section must explicitly discuss Trust
  Manifest substitution attacks.
- Level 3 conformance may require signatures to mitigate this threat.
- The verification procedures section should be validated by security
  experts.
