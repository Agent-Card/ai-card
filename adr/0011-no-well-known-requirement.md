# ADR-0011: Well-Known URI Is Optional for Catalog Discovery

## Status
Accepted

## Date
2026-04-02

## Context
Many discovery mechanisms in the web ecosystem rely on `.well-known` URIs
(RFC 8615) to provide a predictable location for metadata documents (e.g.,
`/.well-known/openid-configuration`, `/.well-known/oauth-authorization-server`).
A similar approach was considered for AI Catalog discovery—placing the catalog
at a fixed, predictable path on a host.

However, enterprise registries and platform-hosted catalogs often cannot
control the `.well-known` path on their domain. Requiring a fixed location
as the sole discovery mechanism would exclude significant deployment scenarios.

## Decision
A `.well-known/ai-catalog` URI **should** be registered as a conventional
discovery location for those who can and wish to use it. However, it is
**not mandatory**—AI Catalogs may be served from any URL and discovered
through multiple mechanisms including links, registry APIs, HTTP headers,
documentation, or other out-of-band means.

## Rationale
- A `.well-known` URI provides a simple, predictable convention for domains
  that support it.
- Enterprise registries operate under paths they control (e.g.,
  `https://registry.example.com/catalogs/org-agents`), not at the domain root.
- Platform marketplaces (VS Code, npm, OCI registries) already have their own
  discovery mechanisms; a `.well-known` path is not always applicable.
- Static file hosting (GitHub Pages, blob storage) can serve catalogs at
  arbitrary paths without server-side configuration.
- Making `.well-known` optional rather than required ensures no deployment
  scenario is excluded.

## Alternatives Considered
- **Require `.well-known/ai-catalog`**: Too restrictive for enterprise and
  platform deployments. Many operators cannot modify `.well-known` on their
  domain.
- **Do not register `.well-known` at all**: Overly dismissive of a useful
  convention. Registering it as optional costs little and benefits domains
  that can use it.

## Meeting Reference
2026-04-02 working group call. Darrel Miller noted that enterprise
registries are not going to be able to use `.well-known` as their
primary discovery mechanism, so it should not be the only option.
