# ADR-0011: No .well-known URI Requirement for Catalog Discovery

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
would exclude significant deployment scenarios.

## Decision
AI Catalogs **may** be served from any URL. There is no requirement to use
a `.well-known` URI or any other fixed path.

Discovery of catalog URLs is out-of-band: consumers learn catalog locations
through links, registry APIs, documentation, or other mechanisms.

## Rationale
- Enterprise registries operate under paths they control (e.g.,
  `https://registry.example.com/catalogs/org-agents`), not at the domain root.
- Platform marketplaces (VS Code, npm, OCI registries) already have their own
  discovery mechanisms; forcing `.well-known` adds no value.
- Static file hosting (GitHub Pages, blob storage) can serve catalogs at
  arbitrary paths without server-side configuration.
- A `.well-known` profile can always be defined later as an optional
  convenience without breaking existing deployments.

## Alternatives Considered
- **Require `.well-known/ai-catalog`**: Too restrictive for enterprise and
  platform deployments. Many operators cannot modify `.well-known` on their
  domain.
- **Recommend `.well-known` as a convention**: Considered but deferred—adds
  complexity without clear benefit given the heterogeneous deployment landscape.

## Meeting Reference
2026-04-02 working group call. Darrel Miller noted: "I have expressed my
dislike for .well-known" and "a lot of us who are building enterprise
registries are just not going to be able to use .well-known."
