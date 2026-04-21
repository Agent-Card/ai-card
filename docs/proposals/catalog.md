## AI Open Discovery via API Catalog

### 1. Purpose

This document proposes an **API Catalog–based approach for open discovery of AI-related assets**
(such as AI agents, A2A servers, MCP servers, or other AI service endpoints)
served under a shared origin.

In many AI deployments, a single host or gateway exposes multiple AI capabilities,
each accessible under distinct paths (for example, `/a2a/v1/agent1`, `/mcp/v1/tool1`,
or `/ai/search`). While individual endpoints may expose their own metadata documents,
there is no standardized mechanism to **enumerate all AI assets available from a given origin**.

This proposal addresses that gap by leveraging the
[IETF API Catalog specification (RFC 9727)](https://datatracker.ietf.org/doc/rfc9727/),
which provides a standardized, extensible, and interoperable format for publishing
collections of APIs and related resources.

---

### 2. Discovery Mechanism

AI assets are discovered through an **API Catalog document** exposed at a well-known location
on the hosting origin.

- **Well-Known URI:**  
  The catalog is typically published at `/.well-known/api-catalog`, as defined in RFC 9727.

The API Catalog format is based on the
[Linkset specification (RFC 9264)](https://datatracker.ietf.org/doc/rfc9264/)
and represents a collection of *link context objects*.
Each entry may describe an individual AI asset and its associated metadata.

An entry in the catalog may include:

- **An optional `anchor`:**  
  The base URI of a specific AI asset (for example,
  `https://example.org/a2a/v1/agent1` or `https://example.org/mcp/v1/server`).

- **Link relations describing the asset:**  
  Common relation types include `describedby`, `service-desc`, and `service-meta`.
  Implementations may also use a URI identifying a relevant specification section
  (for example, an Agent Card or protocol definition) as the link relation.

This approach enables clients to enumerate AI assets dynamically,
without prior knowledge of asset-specific paths or protocols.

---

### 3. Applicability to Existing AI Protocols

This API Catalog–based discovery mechanism is **protocol-agnostic** and can be applied to:

- **A2A servers**, exposing multiple agents and their Agent Cards
- **MCP servers**, exposing multiple servers and thei MCP Server Cards
- Other AI platforms exposing AI services

For example, in the context of the A2A protocol, catalog entries may link to
Agent Cards as defined in the A2A specification.
In other contexts, the same mechanism may link to protocol-specific metadata documents.

---

### 4. Security Considerations

Publishing an AI Catalog may expose metadata about available AI capabilities,
endpoints, or services.

Operators should carefully consider access control, information disclosure,
and deployment context when exposing catalogs publicly.

General security guidance for API Catalogs is provided in
[RFC 9727 – Security Considerations](https://datatracker.ietf.org/doc/rfc9727/).

---

### 5. Example AI API Catalog

```json
{
  "linkset": [
    {
      "anchor": "https://ai.example.com/a2a/v1/route_planner",
      "describedby": [
        {
          "href": "https://ai.example.com/a2a/v1/route_planner/agent-card.json",
          "type": "application/agent-card+json",
          "title": "GeoSpatial Route Planner Agent (A2A)"
        }
      ]
    },
    {
      "anchor": "https://ai.example.com/a2a/v1/poi_finder",
      "https://a2a-protocol.org/latest/specification/#5-agent-discovery-the-agent-card": [
        {
          "href": "https://ai.example.com/a2a/v1/poi_finder/agent-card.json",
          "type": "application/json",
          "title": "GeoSpatial POI Finder Agent (A2A)"
        }
      ]
    },
    {
      "anchor": "https://ai.example.com/mcp/v1/geocoding",
      "https://modelcontextprotocol.io/specification/#server-card": [
        {
          "href": "https://ai.example.com/mcp/v1/geocoding/mcp-card.json",
          "type": "application/json",
          "title": "GeoSpatial Reverse Geocoding Server (MCP)"
        }
      ]
    }
  ]
}
```

## 6. Pros and Cons of the API Catalog–Based Approach

### Pros

- **Protocol-agnostic discovery**
  The [API Catalog](https://datatracker.ietf.org/doc/rfc9727/) provides a neutral discovery layer
  that works across AI protocols such as A2A, MCP, and future AI-specific interfaces, without requiring
  protocol-specific discovery mechanisms.

- **Standardized and interoperable**
  By reusing existing IETF standards ([RFC 9727](https://datatracker.ietf.org/doc/rfc9727/)),
  this approach avoids introducing new discovery formats and benefits from well-defined semantics,
  existing tooling, and prior operational experience.

- **Supports multi-asset deployments**
  Unlike single-resource discovery mechanisms (for example, one Agent Card per origin),
  the catalog naturally supports hosting and enumerating multiple AI assets under a shared origin
  or gateway.

- **Extensible without central coordination**  
  New AI asset types, metadata formats, or relation types can be added incrementally using URI-based
  link relations, without requiring new global registries or schema changes.

---

### Cons / Open Questions

- **Not AI-specific by design**  
  The [API Catalog](https://datatracker.ietf.org/doc/rfc9727/) was designed for general APIs, not AI
  assets specifically. Some AI-specific concepts may require additional conventions or profiles.

- **Risk of inconsistent conventions**  
  Without additional guidance, different implementations may choose different anchor semantics, or
  relation types, which could reduce interoperability across catalogs. This could be improved through
  further discussion and consensus, for example by recommending specific relation types and stable
  schema URIs for assets such as the A2A Agent Card and the MCP Server Card.

- **Limited expressiveness for rich metadata**  
  The catalog primarily supports discovery and linking. Rich AI metadata must be defined in external
  documents such as A2A Agent Cards or MCP Server Cards. A more general or unifying AI Card
  specification could be discussed and developed separately within this repository in the future.
