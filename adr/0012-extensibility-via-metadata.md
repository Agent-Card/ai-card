# ADR-0012: Extensibility via `metadata` Property

## Status
Accepted

## Date
2026-04-02

## Context
AI Catalog entries need to be extensible so that publishers can attach
custom properties (confidence scores, compliance tags, vendor-specific
attributes) without polluting the core schema.

Several extensibility patterns exist in the API ecosystem:
- **Open schema** (allow any additional properties): simple but makes
  validation impossible and encourages namespace collisions.
- **x-dash prefixed properties** (e.g., `x-custom-field`): used by OpenAPI
  2.0; functional but widely considered ugly and inconsistent.
- **Dedicated extension object** (e.g., `metadata`): keeps the core schema
  closed and validates cleanly while providing a clear extension point.

## Decision
The core catalog entry schema is **closed** (additional top-level properties
are not permitted). All custom or vendor-specific properties go in an optional
`metadata` object on the entry.

```json
{
  "identifier": "urn:example:my-agent",
  "displayName": "My Agent",
  "mediaType": "application/a2a+json",
  "url": "https://example.com/agent.json",
  "metadata": {
    "confidenceScore": 0.95,
    "compliance": ["SOC2", "GDPR"],
    "vendor:deploymentRegion": "us-west-2"
  }
}
```

## Rationale
- A closed core schema enables strict validation and forward-compatible
  evolution—new standardized fields can be added without conflicting with
  existing custom properties.
- The `metadata` object provides a clear, single place for extensions,
  making it easy for consumers to know where to look for non-standard data.
- Avoids the `x-` prefix pattern that OpenAPI later deprecated in favor of
  extensions.
- Registries can define their own metadata schemas for entries they host
  without requiring changes to the core specification.

## Alternatives Considered
- **Open schema with arbitrary properties**: Rejected—no validation, easy
  to collide with future standard fields.
- **x-dash prefixed properties**: Rejected—considered "a little ugly" and
  deprecated in modern API description formats.
- **JSON-LD / linked data extensions**: Too heavyweight for the catalog's
  target audience of simple JSON consumers.

## Meeting Reference
2026-04-02 working group call. Darrel Miller described the approach as
avoiding "the x-dash thing" from OpenAPI while providing a clear extension
point. The group agreed on a closed core schema with `metadata` for
extensibility.
