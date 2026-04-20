# ADR-0013: AI Catalog as Authoring Format, OCI as Distribution Format

## Status
Accepted

## Date
2026-04-02

## Context
Three competing directions emerged for the AI Catalog's role relative to
existing container and package ecosystems:

1. **Pure OCI**: Use OCI registries as the sole mechanism for publishing,
   discovering, and distributing AI artifacts. The AI Catalog would be
   unnecessary.
2. **Pure JSON catalog**: Define the AI Catalog as the single format for
   both human authoring and machine distribution, ignoring OCI.
3. **Complementary formats**: Use AI Catalog for human-readable authoring
   and lightweight discovery, and OCI for trusted distribution with
   content-addressable storage, signing, and provenance.

## Decision
AI Catalog and OCI serve **complementary roles**:

- **AI Catalog** is the **authoring and discovery format**—a human-readable
  JSON document that publishers create and maintain, listing AI artifacts
  with metadata, descriptions, and links.
- **OCI** is the **distribution and trust format**—providing
  content-addressable storage, cryptographic signing (Notary/cosign),
  provenance attestations (SLSA), and enterprise registry infrastructure.

A **mechanical, bidirectional transformation** exists between the two:
- AI Catalog → OCI Index + OCI Manifests (for publishing to registries)
- OCI Index + OCI Manifests → AI Catalog (for generating human-readable views)

Tooling should support this transformation so that publishers author in one
format and distribute in both.

## Rationale
- OCI already solves distribution, signing, and provenance for enterprises.
  Reinventing these capabilities in a JSON catalog would be duplicative and
  less trusted.
- OCI registries are not human-friendly for browsing or lightweight
  discovery. A JSON catalog served from a simple URL fills this gap.
- The transformation is straightforward because both formats share the same
  structural pattern: an index/catalog contains references to
  manifests/entries, each with a media type and a pointer to content.
- Mapping: AI Catalog ≈ OCI Index; Catalog Entry ≈ OCI Manifest.
- Small teams and open-source projects can start with a static JSON file
  and graduate to OCI registries as their trust and distribution needs grow.

## Alternatives Considered
- **OCI-only**: Rejected—OCI registries are not accessible to small teams
  or suitable for simple static hosting scenarios. Discovery UX is poor.
- **JSON-only**: Rejected—enterprises need content-addressable storage,
  signing, and provenance that OCI already provides. Rebuilding these in
  JSON would not reach the same trust level.
- **Separate, incompatible formats**: Rejected—the mapping between
  AI Catalog and OCI should be defined and tooled, not left to each
  implementer.

## Meeting Reference
2026-04-02 working group call. Junjie Bu articulated the split: "use the
AI Catalog to put all the human-readable info, and use OCI for trust info
and enterprise deployment." Darrel Miller confirmed existing tooling for
the transformation. Sam Betts described the OCI structural mapping
(catalog = index, entry = manifest).
