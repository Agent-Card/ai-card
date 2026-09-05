# ADR-0024: Define Publisher-Domain Alignment for Entry Trust Manifests

## Status

Proposed

## Date

2026-09-02

## Context

The Trust Manifest required the domain in its `identity` to align with the
publisher domain in the containing Catalog Entry's `identifier` without
defining how to obtain or compare those domains. Non-`urn:air` identifiers do
not necessarily communicate a publisher domain, so implementations could not
apply the requirement interoperably.

Alignment can check consistency between the `{publisher}` domain in the
Catalog Entry's `identifier` and the domain in the Entry Trust Manifest's
`identity`. A Trust Manifest signature covers its `identity`, but does not by
itself authenticate the containing Catalog Entry's `identifier`. Alignment
cannot prove domain control, publisher or signer authorization, or
authenticity; those guarantees require verification and an independent trust
policy.

## Decision

Entry Trust Manifests are supported only on Catalog Entries whose `identifier`
is publisher-authorized and uses the standard `urn:air` syntax defined in
Catalog Entry. Non-`urn:air` identifiers remain valid for Catalog Entries that
do not include an Entry Trust Manifest.

Catalog operators may reproduce an Entry Trust Manifest together with an
identifier assigned by the publisher or its authorized delegate.

AI Catalog defines how to obtain the domain used for publisher-domain
comparison from three identity URI forms:

- the resolution domain of a `did:web` identity, excluding any port;
- the host of an HTTPS identity, excluding any port; and
- the trust domain of a SPIFFE identity when it is an IDNA2008 domain name.

The applicable URN, URI, `did:web`, SPIFFE, and IDNA standards govern syntax
and validity; AI Catalog does not redefine their syntax. AI Catalog compares
complete IDNA2008 domain names serialized in ASCII form exactly after ASCII
case normalization. Ports, paths, queries, and fragments remain part of an
identity and may affect its interpretation or resolution, but they are ignored
when comparing its domain with the publisher domain.

When no comparison domain can be obtained or the domains are not aligned,
consumers disregard the Entry Trust Manifest's claims and apply their policy
for an entry without a usable Trust Manifest. The optional `identityType`
member is informational: consumers obtain the domain from the `identity` URI
itself, not from this hint.

Supporting another identity URI form would require defining how to obtain its
domain for comparison.

## Consequences

- Alignment means consistency, not authentication or authorization.
- Non-`urn:air` identifiers remain valid for Catalog Entries that do not
  include an Entry Trust Manifest.
- Ports, paths, queries, and fragments remain part of an identity even though
  they do not participate in publisher-domain comparison.
