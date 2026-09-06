# ADR-0025: Bind Signed Trust Manifests to Artifact Releases

**Status:** Proposed

**Date:** 2026-09-03

## Context

A signed entry Trust Manifest currently binds the signer's claims to an
artifact's media type, content digest, and optionally its URL. The containing
Catalog Entry's `identifier` and `version` remain outside that signature.

ADR-0015 established that the two existing identity fields serve different
purposes. `entry.identifier` is the artifact's logical name in the catalog,
whereas `trustManifest.identity` is the cryptographic identity associated with
the Trust Manifest. They need not be the same URI; their domains need only
align.

The development work that later introduced `subject` temporarily required
those two fields to be exactly equal. Because `trustManifest.identity` is
inside the signed payload, that temporary equality rule also placed
`entry.identifier` under the signature. The accompanying security analysis
could therefore focus on the remaining problem: binding the signature to the
artifact's exact representation through its media type, digest, and optional
URL.

Review subsequently restored the domain-alignment rule from ADR-0015, but the
definition of `subject` remained representation-only. Once those two decisions
were combined, no field inside the signed payload was required to equal
`entry.identifier`. The artifact bytes were still protected, but their logical
catalog identifier was not.

Catalog Entries that share an `identifier` can represent different releases
using `version`. The resolution procedure compares those versions when
selecting the latest release or satisfying a version constraint. A present
`entry.version` can therefore determine which artifact a consumer receives,
even though it remains outside the Trust Manifest signature.

An attacker who can modify a catalog can retain a valid signed manifest and
its exact artifact bytes while changing only the entry's logical identifier or
version. For example, the attacker can label an old, vulnerable release as a
newer version. A consumer requesting the latest release, or requiring a
minimum version containing a security fix, can then receive the vulnerable
code while the signature, URL, media type, and digest all verify.

A top-level catalog signature detects changes to the catalog document, but it
authenticates a different statement. It establishes that the catalog signer
published a particular snapshot, including its identifiers and versions. An
entry Trust Manifest establishes that its signer made claims about a
particular artifact. When the catalog and Trust Manifest have different
signers, the catalog signature does not establish that the Trust Manifest
signer assigned those release coordinates. Conversely, an entry signature
does not protect the catalog's collection-wide structure. The two controls
provide complementary guarantees.

## Decision

For a signed Trust Manifest attached to a Catalog Entry, extend `subject` to
identify both the logical artifact release and its exact representation.

For a signed entry Trust Manifest:

- `subject.identifier` is REQUIRED in every Subject and MUST exactly equal
  `entry.identifier` when the Subject appears on a Catalog Entry.
- `subject.version` is REQUIRED when `entry.version` is present and MUST
  exactly equal it. When `entry.version` is absent, `subject.version` MAY be
  present and no entry-version comparison is required.
- `subject.type` remains REQUIRED and MUST exactly equal `entry.type`.
- `subject.digest` remains REQUIRED and MUST match the artifact content.
- `subject.url` remains OPTIONAL. When present, it MUST exactly equal
  `entry.url`.

Consumers MUST perform the entry-to-subject comparisons in addition to
verifying the signature, anchoring its identity, and checking the artifact
digest. A signature over a mismatched subject does not authenticate the
containing entry.

Catalog-level integrity remains complementary. Per-entry signatures cannot
detect removal of a valid entry, injection of unrelated entries, or
reordering. A catalog signature or trusted content-addressed distribution can
protect the catalog snapshot as a whole. Neither an entry signature nor a
catalog signature alone prevents replay of an older, correctly signed value.
A consumer that must prevent rollback needs either a trusted source of current
release information or local state recording the newest release it has already
accepted.

The release-coordinate comparison rules in this decision are limited to signed
Trust Manifests attached to Catalog Entries. Requiring every Subject to include
an `identifier` does not define what the Subject of a signed Host Trust Manifest
represents. This decision also does not change the meaning of `identity` or
define how an identity resolves to an authorized signing key. Those concerns
require separate decisions.

The specification's CDDL is updated to represent `subject`, `issuedAt`, and
`expiresAt`, which were already defined in the normative prose but missing from
the machine-readable data model.

## Consequences

- A valid signed manifest and artifact cannot be transplanted to another
  logical identifier or relabeled as another version without detection.
- The same signed manifest remains usable in catalogs that omit the optional
  entry `version`; when a catalog supplies a version, it must agree with the
  signed subject.
- Mirrors remain possible because `subject.url` stays optional.
- Catalog signatures continue to protect collection-level decisions and may
  be made by a different principal than the Trust Manifest signer.
- Signing the release coordinates does not by itself prevent rollback to an
  older, correctly labelled and validly signed release. Consumers still need a
  trusted source of current release information or a record of the newest
  release they have already accepted.

## Alternatives Considered

### Rely only on catalog-level integrity

Rejected as the sole mitigation. It protects the catalog operator's snapshot,
but does not establish that the Trust Manifest signer made claims about the
listed identifier and version. It also couples that claim to one catalog.

### Bind only the artifact digest

Rejected. It proves which bytes were endorsed but permits those exact bytes and
claims to be relabeled under another logical artifact or release coordinate.

### Require `subject.url`

Rejected. Location binding would prevent mirrors and does not substitute for a
stable logical identifier. Publishers may opt into location binding by
including the existing optional field.
