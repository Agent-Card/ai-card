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
remains stable across versions and catalog locations. Consumers that do
not recognize its identifier scheme treat the value as opaque.
Identifier syntax alone does not verify publisher identity or establish
trust.

The base format does not require a particular identifier scheme. A
globally unique absolute URI is recommended for open or federated use.
Publisher-controlled `urn:air` identifiers remain recommended when
available.

A registry uses a stateful preserve-or-mint policy:

1. Reuse any primary identifier it previously published for the artifact.
2. Otherwise, preserve a publisher-assigned identifier when the source is
   authorized to use that identifier or namespace.
3. Otherwise, assign and persist a stable identifier in a namespace the
   registry controls.

A registry does not silently replace a primary identifier it has already
published, including when an authorized publisher-assigned identifier
becomes available later. Changing the primary identifier requires an
explicit migration mechanism, which this decision does not define.

The registry assigning an identifier, the catalog `host`, and the
artifact `publisher` are independent roles. A registry-issued identifier
does not imply that the registry published the artifact.

Registry-native coordinates belong in a namespaced entry extension when
needed for lookup or round trips. They do not affect catalog uniqueness
or establish publisher identity, trust, or equivalence with another
identifier.

## Consequences

- Existing authorized publisher identifiers can be preserved across
  registries and mirrors.
- Legacy records can be projected without publisher enrollment by using
  a registry-issued identifier.
- Two registries may assign different identifiers to the same artifact
  when no publisher-assigned identity is available. The model does not
  claim equivalence it cannot establish.
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
