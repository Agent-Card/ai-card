## Comparison of Card Structures

The unified AI Card defines core AI Card Features that's common in both (or more) protocols. It works by:
- "Lifting" all common fields (id, name, description, publisher, authentication, trust, etc) to the top level.
- "Plugging in" all protocol-specific fields (skills for A2A, capabilities for MCP) into the protocolSpecific payload.

This table shows how the fields from A2A and MCP map to the unified AI Card structure.
| Concept | A2A AgentCard (Spec) | MCP Server Card (Proposal) | Unified AI Card (Our Definition) |
| :--- | :--- | :--- | :--- |
| **Identity** | Implied by host | `serverInfo.name` (ID) | `id` (Top-level, verifiable DID) |
| **Name** | `name` | `serverInfo.title` | `name` (Top-level, human-readable) |
| **Description** | `description` | `description` | `description` (Top-level) |
| **Publisher** | `AgentProvider` (object) | `serverInfo` | `publisher` (Top-level Publisher object) |
| **Trust/ID** | Not explicitly defined | Not explicitly defined | `trust` (Top-level Trust object) |
| **Endpoint** | `url` | `transport.endpoint` | `services` array > `endpoint` |
| **Authentication** | `securitySchemes` (in card) | `authentication` (in card) | `services` array > `authentication` (Common, OpenAPI-based) |
| **Protocol Details** | `skills`, `preferredTransport`, `capabilities` | `capabilities`, `tools`, `prompts`, `resources` | `services` array > `protocolSpecific` |