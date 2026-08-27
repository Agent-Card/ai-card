# ADR-0021: Separate Artifact Identity from Registry Coordinates

**Status:** Proposed

**Date:** 2026-08-26

**Related:** [Issue #102](https://github.com/Agent-Card/ai-catalog/issues/102)

**Supersedes if accepted:** The federated AIR requirement in
[ADR-0015](0015-agent-identifier-naming.md)

## Context

Existing registries commonly identify artifacts with native coordinates,
such as a registry namespace and artifact name. When projecting those
records as AI Catalog entries, a registry may have no publisher-assigned
`urn:air` identifier.

Using the registry's domain in `urn:air` is easy, but the current format
defines that domain as the artifact publisher. Requiring the publisher's
domain is portable, but prevents automatic projection when the publisher
has not supplied or authorized an identifier.

The existing model already separates most roles: `publisher` identifies
the artifact publisher, `host` identifies the catalog operator, `url`
locates the artifact, and `extensions` can preserve registry-specific
coordinates.

## Decision

`entry.identifier` identifies the artifact represented by the entry and
remains stable across versions. A publisher-authorized `urn:air`
identifier is also portable across catalog locations. Other
identifier schemes remain valid but have no cross-catalog portability
guarantee. Consumers that do not recognize an identifier scheme treat
the value as opaque. Identifier syntax alone does not verify publisher
identity or establish trust.

The base format does not require a particular identifier scheme. A
globally unique absolute URI is recommended for open or federated use.
An artifact publisher that wants an identifier to be preserved when the
artifact appears in other catalogs should use the AI Catalog-specific
`urn:air` format in a namespace it controls.

A publisher-authorized `urn:air` identifier is one assigned by the
artifact publisher or its authorized delegate, with the artifact
publisher's domain in the `{publisher}` segment.

A registry uses a stateful preserve-or-mint policy:

1. If the registry previously published an identifier for the artifact,
   reuse it, even if another identifier becomes available later.
2. Otherwise, if the source entry contains a publisher-authorized
   `urn:air` identifier, preserve it exactly.
3. Otherwise, the registry may preserve or replace a non-`urn:air` source
   identifier. Non-`urn:air` identifiers have no guaranteed portability
   across catalogs.
4. When assigning a new identifier, a registry that becomes the artifact
   publisher should use `urn:air` with its own domain in the `{publisher}`
   segment. A registry acting as an authorized delegate should use
   `urn:air` with the delegating publisher's domain in that segment. An
   independent registry must use a non-`urn:air` identifier under its own
   control.

Merely hosting or aggregating an entry does not make a registry the
artifact publisher.

Changing a previously published primary identifier requires an explicit
migration mechanism, which this decision does not define.

The registry assigning an identifier, the catalog `host`, and the
artifact `publisher` are independent roles. A registry-issued identifier
does not imply that the registry published the artifact.

A registry may retain replaced source identifiers or registry-native
coordinates. When retained, they should be stored in a namespaced entry
extension. They do not affect catalog uniqueness or establish publisher
identity, trust, or equivalence with another identifier.

## Consequences

- Publisher-authorized `urn:air` identifiers are preserved across
  registries and mirrors.
- Non-`urn:air` identifiers remain valid, but registries may replace them
  when they are unsuitable for the destination catalog.
- Legacy records can be projected without publisher enrollment by using
  a registry-issued identifier.
- Two registries may assign different identifiers to the same artifact
  when no publisher-authorized `urn:air` identity is available. The model
  does not claim equivalence it cannot establish.
- No new core field is added; native coordinates use `extensions`.
- Generic aliases and primary-identifier migration remain future work.

## Alternatives Considered

Always using a registry-domain `urn:air` was rejected because it makes the
registry appear to be the artifact publisher under the current format.

Requiring a publisher-domain `urn:air` was rejected as a universal rule
because it makes automatic projection depend on publisher enrollment.

Adding `aliases`, `nativeIdentifier`, or `identifiers[]` was deferred
because registry coordinates do not necessarily assert logical identity
equivalence, and `extensions` is sufficient for the immediate use case.
