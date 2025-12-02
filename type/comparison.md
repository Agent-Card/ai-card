## Comparison of Card Structures

The unified AI Card defines core AI Card Features that's common in both (or more) protocols. It works by:
- "Lifting" all common fields (id, name, description, publisher, authentication, trust, etc) to the top level.
- "Plugging in" all protocol-specific fields (skills for A2A, capabilities for MCP) into the protocolSpecific payload.

This table shows how the fields from A2A and MCP map to the unified AI Card structure.
| Concept | A2A `AgentCard` (Spec) | MCP `Server Card` (Proposal) | **Unified `AI Card` (V1)** |
| :--- | :--- | :--- | :--- |
| **Identity (Subject)** | Implied by Host | `serverInfo.name` | **`id`** (Root URI) + `identityType` |
| **Name** | `name` | `serverInfo.title` | **`name`** |
| **Description** | `description` | `description` | **`description`** |
| **Logo** | `icon_url` | `iconUrl` | **`logoUrl`** (Rec: Data URI) |
| **Publisher** | `provider` (Object) | `serverInfo` | **`publisher`** (Object with `id`, `name`) |
| **Trust / Security** | `signatures` (Optional) | Not Defined | **`trust`** (Optional Object: Proofs, Policies) |
| **Protocol Support** | Implied (A2A Only) | Implied (MCP Only) | **`services`** (Map: `"a2a": {...}`, `"mcp": {...}`) |
| **Endpoint URL** | `url` | `transport.endpoint` | `services[x].protocolSpecific` (**Delegated**) |
| **Authentication** | `securitySchemes` | `authentication` | `services[x].protocolSpecific` (**Delegated**) |
| **Capabilities** | `skills` | `tools`, `resources` | `services[x].protocolSpecific` (**Delegated**) |
| **Versioning** | `version` | `serverInfo.version` | **`specVersion`** (Card Ver) + `updatedAt` |