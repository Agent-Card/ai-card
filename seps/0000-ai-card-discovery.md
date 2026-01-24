---
SEP: 0000
Title: AI Card Discovery via Well-Known URI
Author: [Simon Heimler] <simon.heimler@sap.com>
Status: draft
Type: Standards Track
Created: 2026-01-24
---

## Abstract

This SEP proposes a standardized discovery mechanism for AI native protocols and their metadata through a [.well-known URI](https://www.rfc-editor.org/rfc/rfc8615) endpoint (`/.well-known/ai-cards.json`). This solves the discovery problem that both [MCP](https://modelcontextprotocol.io) (Model Context Protocol) and [A2A](https://a2a-protocol.org) (Agent-to-Agent) protocols face, eliminating the need for each protocol to define its own discovery mechanism independently.

The proposal recognizes that:
- **A2A** has defined [`/.well-known/agent.json`](https://github.com/protocol-registries/well-known-uris/issues/66) for discovery, but assumes **one agent per host**
- **MCP Server Cards** need to evolve from the existing MCP Registry `server.json` format to include tools, prompts, and resources, proposed as [MCP Server Cards (SEP-2127)](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127), with discovery at `/.well-known/mcp/server-card.json` assuming **one server per host**
- Both protocols face the **same limitation**: the single-service assumption doesn't fit real-world multi-service deployments
- **Discovery** is a shared concern that benefits from a unified, multi-service approach
- **Future-proofing**: The discovery mechanism is designed to support future AI protocols, versions and their metadata formats

By providing a protocol-agnostic discovery layer, this SEP enables a single host to advertise multiple MCP servers and/or multiple A2A agents, while allowing each protocol to maintain full ownership of their card formats, keeping their own autonomy and lifecycle.

## Motivation

### The Current Landscape

**A2A** has defined [`/.well-known/agent.json`](https://github.com/protocol-registries/well-known-uris/issues/66) for agent discovery, with A2A Agent Cards providing comprehensive metadata about agents. However, the endpoint assumes **one agent per host** and the discovery mechanism is exclusive to A2A.

**MCP** has proposed [SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127) defining `/.well-known/mcp/server-card.json` for server discovery, with comprehensive server metadata. However, it also assumes **one MCP server per host** and the discovery mechanism is exclusive to MCP.

Both protocols also have existing metadata formats:
- **A2A Agent Cards**: Already well-defined for agent metadata
- **MCP Registry `server.json`**: Exists for registry entries but is incomplete (missing tools, prompts, resources)

In reality, a single host can and should be able to expose:
- Multiple MCP servers (e.g., a petstore server and an inventory server)
- Multiple A2A agents (e.g., a customer service agent and a sales agent)
- A mix of both protocols

### The Single-Service Assumption Problem

**Both A2A and MCP discovery mechanisms share the same critical limitation:**
- A2A: `/.well-known/agent.json` (singular) → assumes one agent
- MCP: `/.well-known/mcp/server-card.json` (singular) → assumes one server

This breaks down in real-world scenarios:
- A company may host multiple specialized agents (sales, support, analytics)
- A domain may host multiple distinct MCP servers (petstore, inventory, analytics)
- A platform may provide both MCP servers and A2A agents
- Registries need to discover all available services, not just the "primary" one

### The Multi-Protocol Discovery Problem

Beyond the single-service limitation, having separate protocol-specific discovery endpoints creates additional friction:
- **Clients must probe multiple endpoints**: Try `/.well-known/agent.json`, then `/.well-known/mcp/server-card.json`, then future protocols
- **Registries must implement multiple discovery protocols**: Each protocol adds complexity
- **No standard way to discover what protocols a domain supports**: Clients must guess and try each one
- **N+1 HTTP requests**: One request per protocol, with failures for unsupported ones

### This Proposal

This SEP addresses these challenges by:

1. **Solving discovery once**: Provides a single, protocol-agnostic discovery mechanism
2. **Avoiding model proliferation**: Each protocol maintains its own card definitions (A2A Agent Cards, MCP Server Cards)
3. **Supporting multiple servers/agents**: Explicitly designed for hosts exposing multiple services
4. **Reducing coordination overhead**: Protocols only need to agree on discovery, not on card formats
5. **Simplifying the ecosystem**: One endpoint to discover all AI capabilities on a domain

## Specification

### Well-Known URI

Services supporting AI Card discovery MUST provide a JSON document at `/.well-known/ai-cards.json`.

By appending `.json` it is easier to host this and the linked metadata files on a static file server.

### Discovery Document Format

The discovery document MUST be a JSON object following the [ai-card-v0.schema.json](./0000-ai-card-discovery.schema.json) schema.

```json
{
  "$schema": "https://ai-card.org/schemas/ai-card-v0.schema.json",
  "protocols": [
    {
      "type": "a2a",
      "endpoints": [{"url": "https://example.com/a2a-endpoint"}],
      "metadata": {
        "type": "agent-card",
        "url": "https://example.com/.well-known/PetAgent.json"
      }
    },
    {
      "type": "mcp",
      "endpoints": [{"url": "https://example.com/mcp-endpoint"}],
      "metadata": {
        "type": "mcp-server-card",
        "url": "https://example.com/.well-known/petstore.mcp.json"
      }
    },
    {
      "type": "mcp",
      "endpoints": [{"url": "https://example.com/mcp-endpoint-inventory"}],
      "metadata": {
        "type": "mcp-server-card",
        "url": "https://example.com/.well-known/inventory.mcp.json"
      }
    }
  ]
}
```

**Note**: A single host can expose multiple MCP servers or multiple A2A agents. Each should be listed as a separate entry in the `protocols` array, as shown in the example above where two different MCP servers (petstore and inventory) are hosted on the same domain.

### URL Resolution

URLs in the discovery document (both `endpoints[].url` and `metadata.url`) **MAY be relative or absolute**.

#### Absolute URLs
Absolute URLs include the full protocol and authority:
- `https://example.com/mcp-endpoint`
- `https://api.example.com/.well-known/petstore.mcp.json`

#### Relative URLs
Relative URLs are resolved **relative to the location of the discovery document** (`/.well-known/ai-cards.json`), following [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986) URL resolution rules:

**Path-relative URLs** (start with `./` or `../`):
- `./petstore.mcp.json` → resolves to `/.well-known/petstore.mcp.json`
- `./mcp-endpoint` → resolves to `/.well-known/mcp-endpoint`
- `../metadata/server.json` → resolves to `/metadata/server.json`

**Absolute-path URLs** (start with `/`):
- `/api/mcp` → resolves to `/api/mcp` (relative to host root)
- `/metadata/petstore.mcp.json` → resolves to `/metadata/petstore.mcp.json`

For a discovery document served at `https://example.com/.well-known/ai-cards.json`:
- `./mcp` resolves to `https://example.com/.well-known/mcp`
- `./petstore.mcp.json` resolves to `https://example.com/.well-known/petstore.mcp.json`

**Recommendation**: Use relative URLs when metadata and endpoints are co-located with the discovery document. Use absolute URLs when pointing to external services or different domains.

### Metadata Files

The content and structure of metadata files referenced by `metadata.url` are **owned and defined by their respective protocol communities**:

- **MCP Server Cards**: Should evolve from the existing [MCP Registry `server.json` format](https://github.com/modelcontextprotocol/registry) ([JSON Schema](https://github.com/modelcontextprotocol/registry/blob/main/internal/validators/schemas/2025-12-11.json)), enhanced with tools, prompts, and resources as proposed in [SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127). The MCP community maintains full control over this schema.

- **A2A Agent Cards**: Already defined by the A2A specification. The A2A community maintains full control over this schema.

This SEP **intentionally does not mandate** any particular structure for these metadata files. It only defines the discovery mechanism that points to them.
The scope could be increased to also indicating the version(s) of the protocols and metadata files that are provided.

## Rationale

### Why a Well-Known URI?

The `.well-known` URI scheme ([RFC 8615](https://www.rfc-editor.org/rfc/rfc8615)) is a well-established standard for service discovery, making it a natural fit for AI Card discovery. It allows clients to probe a service for capabilities without prior configuration.
Compared to a centralized registry push model, this approach provides local self-description and a decentralized discovery mechanism.

### Why Not a Shared Model?

Creating a shared model between MCP and A2A would require:

1. Ongoing coordination between protocol groups
2. Libraries to support an additional standard
3. Potential compromises that don't serve either protocol well
4. Slower evolution as changes require multi-party consensus

By keeping card definitions protocol-specific, each group maintains autonomy while still enabling discovery.

### Minimal Coordination Surface

This proposal minimizes the coordination surface to just three pieces of information:
1. Protocol type identifier (`protocolType`)
2. Where to connect (`endpoints`)
3. Where to find metadata (`metadata`)

This allows protocols to evolve their metadata formats independently.

### Relationship to Existing Discovery Mechanisms

Both MCP and A2A have defined protocol-specific discovery endpoints:

**A2A: `/.well-known/agent.json`**
- **Status**: [Registered with IANA](https://github.com/protocol-registries/well-known-uris/issues/66)
- **Specification**: [A2A Protocol](https://a2a-protocol.org/latest/specification/)
- **Limitation**: Assumes one agent per host (singular `agent.json`)

**MCP: `/.well-known/mcp/server-card.json`** 
- **Status**: [Proposed in SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127)
- **Limitation**: Assumes one MCP server per host

**This SEP addresses the shared limitations:**

1. **Supporting multiple services per host**: The `protocols` array can list many MCP servers and/or A2A agents
2. **Enabling multi-protocol discovery**: A single request reveals all available AI services
3. **Avoiding discovery fragmentation**: One shared endpoint instead of N protocol-specific endpoints
4. **Backward compatibility**: Can coexist with protocol-specific endpoints (see Integration Path in Alternatives)

### MCP Server Card Format Evolution

This SEP **does not define** the MCP Server Card format itself. Instead MCP Server Cards should evolve to:
- Ideally merge with the existing MCP Registry `server.json` format, by adding the missing elements. We should avoid having two different formats to describe an MCP server, depending on where/how we publish. MCP Server Cards could be a convention on top of the existing format, describing which elements are required and optional.
- **Remain MCP-owned**: The MCP community maintains full control over the MCP Server Card schema
- **Be discoverable via** this shared `/.well-known/ai-cards.json` mechanism

Similarly, **A2A Agent Cards** (already defined) would be discoverable through the same mechanism, allowing both protocols to evolve independently while sharing a common discovery layer.

## Backward Compatibility

This is a new feature and does not introduce backward compatibility concerns. Services that do not implement the well-known URI simply won't be discoverable through this mechanism.

## Reference Implementation

[To be provided]

## Security Implications

1. **HTTPS Required**: Implementations SHOULD require HTTPS for all URLs in the discovery document to prevent man-in-the-middle attacks

2. **URL Validation**: Clients MUST validate that `metadata.url` and endpoint URLs are properly formatted URLs

3. **Size Limits**: Implementations SHOULD enforce reasonable size limits on the discovery document (e.g., 2MB) to prevent denial-of-service attacks

4. **Access Control**: Implementations SHOULD have an unprotected discovery document, but MAY implement access control for the linked metadata files

## Open Questions

1. **Versioning**: Should the protocol `type` field include version information (e.g., "mcp/v1", "a2a/v1")? Or should versioning be handled in the protocol-specific metadata files?

2. **Metadata Definition Versioning**: Should there be a mechanism to indicate which version of the metadata definition format is being used?

3. **Multiple Versions**: If a service supports multiple versions of a protocol, should they be separate entries in `protocols` (e.g. "a2a-v1", "a2a-v2") and metadata types ("a2a-agent-card-v1", "a2a-agent-card-v2") or should version information be only available by actually fetching the metadata files / connecting to the endpoints?

4. **Coordination with MCP SEP-2127**: Should this SEP be proposed to the MCP community, or should it be maintained as a separate cross-protocol specification? If the latter, how do we ensure adoption across both ecosystems?

5. **Registry Support**: How should registries that index both MCP servers and A2A agents handle discovery? Should they require `/.well-known/ai-cards.json` or also support individual protocol discovery endpoints? Ideally they support multiple discovery approaches and MAY optionally support more advanced protocols like e.g. ORD.

6. **Registry Data Model**: For publishing to registries, one protocol should only have one metadata format. But a registry may need to additional metadata (calculated or server-side information) and context. This concern should be separated, so a registry API / data format could be a superset of MCP Cards or A2A Agent Cards. Clarify that registries are optional and can have their own superset model.

7. **Access Control**: Support protection of metadata files? If metadata is protected, should the discovery document give hints how to access it (access strategy)?

8. **Dynamic Metadata**: Can the discovery document or the attached metadata files be dynamic? For example, metadata can be tenant-specific in products that feature heavy customization.

## Alternatives Considered

### Unified Card Model

Creating a single card format that both MCP and A2A adopt. Proposal is to reject this due to the coordination overhead and risk of creating yet another standard.

### Protocol-Specific Discovery (Status Quo)
Having each protocol define its own discovery mechanism:
- MCP: `/.well-known/mcp/server-card.json` ([SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127))
- A2A: `/.well-known/a2a/agent-card.json` (proposed)

**Advantages:**
- Each protocol has full control
- No cross-protocol coordination needed
- Simpler for single-protocol deployments

**Disadvantages:**
- Clients must probe multiple endpoints to discover all capabilities
- Registries must crawl multiple endpoints per domain
- No standard way to discover what protocols a domain supports
- N+1 HTTP requests where N is the number of protocols

**Integration Path:**
This SEP could be implemented **alongside** protocol-specific endpoints:
1. `/.well-known/ai-cards.json` serves as a directory
2. `metadata.url` points to protocol-specific endpoints like `/.well-known/mcp/server-card.json`
3. Single-protocol deployments can skip the directory and only implement their protocol-specific endpoint
4. Multi-protocol deployments and registries benefit from the unified discovery

This allows gradual adoption without breaking existing protocol-specific discovery mechanisms.

### DNS-Based Discovery

Using DNS TXT records for discovery (similar to DKIM or SPF). 
- Only works at domain level, not for path-based or port-based deployments
- Requires DNS infrastructure control
- More complex to implement and query
- Less accessible for web-based clients

This approach could be rejected or be allowed as an alternative to the .well-known URI approach in the future.

## Prior Art

### MCP SEP-2127: MCP Server Cards - HTTP Server Discovery

- **Issue**: [#1649](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1649)
- **Pull Request**: [#2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127)
- **Proposed Endpoint**: `/.well-known/mcp/server-card.json` (single server assumption)

SEP-2127 proposes a comprehensive MCP Server Card format including:
- Server identification and versioning
- Transport configuration (streamable-http, stdio, SSE)
- Capabilities (tools, prompts, resources)
- Authentication requirements
- Static or dynamic primitive declarations
- Protocol version information

**Relationship to this SEP:**
- SEP-2127's card format provides excellent detail on **what metadata to include**
- This SEP addresses **how to discover** that metadata, especially when multiple servers/agents exist
- The MCP Server Card format should evolve from MCP Registry's `server.json`, enhanced with SEP-2127's additions
- Discovery should use this SEP's shared `/.well-known/ai-cards.json` mechanism rather than protocol-specific endpoints

### MCP Registry server.json Format
- **Repository**: [modelcontextprotocol/registry](https://github.com/modelcontextprotocol/registry)
- **JSON Schema**: [2025-12-11.json](https://github.com/modelcontextprotocol/registry/blob/main/internal/validators/schemas/2025-12-11.json)
- **Current use**: Registry entries for MCP servers
- **Limitations**: Missing tools, prompts, resources definitions

**Relationship to this SEP:**
- Provides the foundation for MCP Server Card format
- Needs enhancement with primitives (tools, prompts, resources, etc.) as proposed in SEP-2127
- Would be discoverable via `metadata.url` in this proposal

### A2A: `/.well-known/agent.json`

- **Issue**: [IANA Well-Known URI Registration](https://github.com/protocol-registries/well-known-uris/issues/66)
- **Specification**: [A2A Protocol](https://a2a-protocol.org/latest/specification/)
- **Endpoint**: `/.well-known/agent.json` (singular - one agent assumption)
- **Status**: Registered/In progress with IANA

A2A has defined a well-known URI for agent discovery with comprehensive A2A Agent Cards including:
- Agent identification and metadata
- Capabilities and supported operations
- Authentication and authorization requirements
- Endpoint information

**Relationship to this SEP:**
- A2A's agent card format is well-defined and should remain A2A-owned
- The `/.well-known/agent.json` endpoint assumes one agent per host (singular filename)
- This SEP enables discovery of **multiple agents** on a single host
- The `metadata.url` in this proposal can point to individual A2A Agent Card files

### RFC 9727: `/.well-known/api-catalog`

- **RFC**: [RFC 9727](https://datatracker.ietf.org/doc/rfc9727/)
- **Endpoint**: `/.well-known/api-catalog`
- **Format**: Linkset (application/linkset+json) per RFC 9264
- **Scope**: Generic API discovery across all API types
- **Status**: Published IETF Standards Track (June 2025)

RFC 9727 defines a well-known URI for discovering **any** APIs published by a domain, using a Linkset format that provides:
- Links to API endpoints (`item` relation)
- Links to API descriptions (OpenAPI specs via `service-desc`)
- Links to documentation (`service-doc`)
- Metadata about APIs (`service-meta`)
- Support for nested catalogs

**Relationship to this SEP:**

**Similarities:**
- Both use `.well-known` URIs for discovery
- Both support multiple services per host (RFC 9727 via Linkset arrays)
- Both enable machine-readable discovery

**Key Differences:**

1. **Scope**: 
   - RFC 9727: **Generic API catalog** - works for REST APIs, GraphQL, SOAP, or any API type
   - This SEP: **AI-native protocol discovery** - specifically for MCP servers and A2A agents

2. **Protocol Awareness**:
   - RFC 9727: **Protocol-agnostic** - doesn't specify what protocol or metadata format the APIs use (only mediaType like `application/json`)
   - This SEP: **Protocol-specific** - explicitly identifies `protocolType` (mcp, a2a) and the metadata format and links to protocol-specific metadata

3. **Metadata Structure**:
   - RFC 9727: Links to generic metadata (OpenAPI specs, docs) using standard link relations
   - This SEP: Points to protocol-specific card formats (MCP Server Cards, A2A Agent Cards) that include protocol-specific capabilities

### Open Resource Discovery: `.well-known/open-resource-discovery`

- **Specification**: [Open Resource Discovery (ORD)](https://open-resource-discovery.org/spec-v1)
- **Governance**: Linux Foundation
- **Endpoint**: `/.well-known/open-resource-discovery`
- **Scope**: Enterprise-grade discovery of APIs, Events, Data Products, Domain Objects, Taxonomy and more
- **Complexity**: Comprehensive, feature-rich standard
 
ORD is an **enterprise-grade** discovery protocol that provides comprehensive resource discovery capabilities far beyond simple API discovery:

**ORD Capabilities:**
- **API Resources**: REST APIs, MCP, A2A, OData, GraphQL, etc.
- **Event Resources**: Cloud Events, AsyncAPI, etc.
- **Data Products**: Data sets, data models, Delta Sharing, etc.
- **Domain Objects**: Business entities and domain models
- **Static vs Dynamic Perspectives**: Distinguishes between system-type-level (static) and system-instance-level (tenant-specific, runtime) metadata
- **Aggregation**: Complex aggregation capabilities for multi-system landscapes
- **Access Strategies**: Multiple authentication and authorization patterns

**Relationship to this SEP:**

**ORD can handle AI protocol discovery today:**
- ORD's flexible resource model already represents MCP servers and A2A agents as "API Resources". Agents can be described as dedicated entity to describe and govern the non-technical, product qualities.
- ORD's static/dynamic perspectives can distinguish between server/agent capabilities and tenant-specific configurations
- ORD provides a shared high-level meta-model across API protocols and even resource types
- ORD's taxonomy can categorize AI resources

**Why this SEP is still valuable:**

1. **Simplicity vs Complexity**:
   - ORD: Enterprise-grade with extensive features (perspectives, aggregation, taxonomy, access strategies)
   - This SEP: **Simple, focused** - just protocol type, endpoints, and metadata URL
   - AI Card implementers want **minimal overhead**, not enterprise complexity

2. **Scope Focus**:
   - ORD: **Broad** - APIs, events, data products, domain objects, business taxonomy
   - This SEP: **Narrow** - AI protocols only (MCP, A2A, future AI protocols)
   - AI registries don't need data products, domain objects, or business taxonomy

3. **Adoption Barrier**:
   - ORD: Requires understanding extensive specification, implementing complex data models
   - This SEP: Small JSON Schema contract, 5 required fields per protocol (type, endpoints, metadata with type and url)
   - Lower barrier → faster ecosystem adoption

4. **Protocol Specificity**:
   - ORD: Generic resource discovery (protocol-agnostic)
   - This SEP: **Protocol-aware** - explicitly identifies MCP vs A2A with protocol-specific card links
   - Makes it trivial for AI clients to distinguish tools from agents

5. **Target Audience**:
   - ORD: **Enterprise IT** - managing complex multi-system landscapes holistically with governance requirements
   - This SEP: **AI developers** - building and discovering AI agents and tools quickly

**Could they coexist?**

Yes, they target different audiences:
- **Enterprise environments** with ORD: Could list AI Cards as one category of API resources within ORD
- **AI-focused environments**: Implement lightweight `/.well-known/ai-cards.json` without ORD overhead
- **Hybrid**: Implement both - ORD for comprehensive enterprise discovery, AI Cards for simple AI-specific discovery

## Related Work

- [RFC 8615: Well-Known Uniform Resource Identifiers (URIs)](https://www.rfc-editor.org/rfc/rfc8615.html) - Foundation for .well-known URIs
- [RFC 9727: api-catalog](https://datatracker.ietf.org/doc/rfc9727/) - Generic API discovery (see Prior Art for detailed comparison)
- [Open Resource Discovery (ORD)](https://open-resource-discovery.org/spec-v1) - Enterprise-grade resource discovery (see Prior Art for detailed comparison)
- [RFC 9264: Linkset](https://www.rfc-editor.org/rfc/rfc9264.html) - Link set format used by api-catalog
- [OAuth 2.0 Authorization Server Metadata (RFC 8414)](https://www.rfc-editor.org/rfc/rfc8414.html) - Similar discovery pattern for OAuth servers
- [OpenID Connect Discovery](https://openid.net/specs/openid-connect-discovery-1_0.html) - Well-known endpoint for identity providers
