# ADR-0008: Media Type Only — No Separate Artifact Type Field

**Status:** Accepted

**Date:** 2026-04-02

**Participants:** Darrel Miller (Microsoft), Sam Betts (Cisco),
Luca Muscariello (Cisco)

## Context

Sam Betts proposed adding an `artifactType` field alongside `mediaType`,
mirroring the OCI distinction between media type (serialization format)
and artifact type (semantic intent). This would allow entries to declare
"this is an agent" (artifact type) whose card happens to be serialized
as a catalog (media type).

The use case: a client wants to find "things that are agents" regardless
of how they are represented (A2A card, MCP server card, or a nested
catalog containing both).

Luca Muscariello argued that in OCI, "media type is about
serialization... artifact type is about intent" and that "the artifact
type, similar to the bundle, is bringing load to the user."

## Decision

Use `mediaType` as the sole type discriminator. Do not add an
`artifactType` field.

## Rationale

- Darrel Miller: "I'm gonna have a hurdle to get people to even accept
  media type as a level of indirection. It's a very open model, and
  people like very closed models. If we try and have two ways, two
  things to define there, we're going to blow people's minds."
- Luca Muscariello agreed: the artifact type "is bringing load to the
  user, saying, okay, I have to say what to do with this stuff
  immediately."
- Sam Betts conceded: "Yeah, let's [start with one]."
- A single `mediaType` field keeps the schema minimal and delegates
  semantic interpretation to the protocol-specific specifications.
- If the need for artifact-level categorization emerges from
  implementation experience, it can be added later as an optional field
  or via `tags`/`metadata` conventions.

## Consequences

- Clients discover artifact types exclusively via `mediaType`.
- There is no built-in way to say "this catalog entry is an agent"
  independently of its card format.
- The `tags` array and `metadata` map remain available for informal
  categorization.
- A future ADR may revisit this if implementations demonstrate a clear
  need for two-level type discrimination.
