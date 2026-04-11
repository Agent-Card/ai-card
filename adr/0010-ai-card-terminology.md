# ADR-0010: "AI Card" Is the High-Level Concept; "Catalog Entry" Is the Spec Term

**Status:** Proposed

**Date:** 2026-04-02

**Participants:** Luca Muscariello (Cisco), Sam Betts (Cisco),
Junjie Bu (Google), Darrel Miller (Microsoft)

## Context

Luca Muscariello observed that the project is called "AI Card" but the
term does not appear in the specification: "all this stuff is called the
AI card, and the AI card is nowhere... one reading this for the first
time would say, where is the AI card?"

The discussion explored several options:
- Junjie Bu suggested renaming the project to "Discovery"
- Sam Betts proposed that "AI Card" is a high-level concept: "A2A's
  card is an AI card, MCP's server card is an AI card, an agent's
  skill is an AI card"
- Junjie suggested "AI Catalog Card" as a name
- Sam proposed adding a definition to the terminology section

## Decision

No immediate rename. The term "AI Card" remains the project/working
group name. The specification uses "Catalog Entry" as the formal term.
A terminology definition should clarify the relationship.

## Rationale

- The term "AI Card" has brand recognition from prior work and the
  working group name.
- Renaming the project mid-stream would create confusion.
- "Catalog Entry" is precise within the spec and avoids confusion with
  protocol-specific cards (A2A Agent Card, MCP Server Card).
- Adding a terminology entry can bridge the gap for newcomers.

## Consequences

- The spec should define "AI Card" in its terminology section as the
  umbrella concept for any AI artifact metadata document.
- "Catalog Entry" remains the normative term in the specification.
- The project/repo name `ai-card` persists.
