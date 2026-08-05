# Example: Agent with Dependencies

A catalog entry can declare the downstream artifacts it needs to run using the official [Dependencies extension](../specification.md). This catalog lists a single CRM assistant agent that requires a Salesforce MCP server, needs one of two interchangeable vector stores, and can optionally use an email-sending agent.

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Corp",
    "identifier": "did:web:acme-corp.com"
  },
  "entries": [
    {
      "identifier": "urn:air:acme-corp.com:agent:crm-assistant",
      "displayName": "CRM Assistant",
      "type": "application/a2a-agent-card+json",
      "description": "An agent that reads and writes CRM records and answers questions grounded in retrieved context.",
      "url": "https://api.acme-corp.com/agents/crm-assistant.json",
      "publisher": {
        "identifier": "did:web:acme-corp.com",
        "displayName": "Acme Corp"
      },
      "extensions": {
        "https://ai-catalog.org/extensions/dependencies": {
          "required": [
            {
              "identifier": "urn:air:salesforce.com:mcp:sales-cloud",
              "type": "application/mcp-server-card+json",
              "versionConstraint": ">=3.0.0",
              "credentialPropagation": "obo",
              "purpose": "Read and write Salesforce CRM records"
            },
            {
              "purpose": "Vector store for retrieval",
              "anyOf": [
                {
                  "identifier": "urn:air:acme-corp.com:mcp:pinecone",
                  "type": "application/mcp-server-card+json",
                  "credentialPropagation": "agent"
                },
                {
                  "identifier": "urn:air:acme-corp.com:mcp:pgvector",
                  "type": "application/mcp-server-card+json",
                  "credentialPropagation": "agent"
                }
              ]
            }
          ],
          "optional": [
            {
              "identifier": "urn:air:acme-corp.com:agent:email-sender",
              "type": "application/a2a-agent-card+json",
              "credentialPropagation": "agent",
              "purpose": "Send email notifications"
            }
          ]
        }
      }
    }
  ]
}
```

## How it works

**The extension key** (`https://ai-catalog.org/extensions/dependencies`) is an *official* AI Catalog extension — signalled by the `https://ai-catalog.org/extensions/` prefix, the same tier as the built-in `metadata` extension. It lives under the entry's `extensions` map, not as a core field. The core schema is unchanged, so the document stays a conformant `specVersion` `"1.0"` catalog; a consumer that doesn't recognize the extension simply ignores it.

**`required` is an AND** — every element must be satisfiable for the agent to function. A consumer SHOULD treat an unmet `required` element as a hard blocker. Here the agent has two required slots: the Salesforce MCP server *and* a vector store.

**`anyOf` is an OR** — a Dependency Group whose slot is filled by *any one* of its listed alternatives. The vector-store slot is satisfied by either `pinecone` *or* `pgvector`; the consumer only needs one. The group carries a single `purpose` ("Vector store for retrieval") stated once for all alternatives.

**`optional` is graceful degradation** — each element is independently droppable. If the `email-sender` agent is unavailable, the CRM assistant still works; it just can't send email notifications.

**`credentialPropagation`** is an advisory hint about how the agent authenticates to each dependency at runtime, letting a planner reason upfront about which credentials it (or its caller) must hold:

- `obo` — *on behalf of*: the caller's user identity is propagated to the dependency, so the audit trail is user-attributed. The Salesforce dependency uses `obo` because it reads and writes records as the end user.
- `agent` — the agent uses its own workload identity, so activity is agent-attributed. The vector stores and email sender use `agent`.
- `user` — a distinct interactive user credential for the dependency is required (the caller authenticates separately).
- `none` — the dependency is public and needs no credential.

This is an *advisory* hint only: it MUST NOT be treated as a security control. The depended-on artifact enforces its real credential requirements at connection time. It is also distinct from the `identityType` field on a Publisher or Trust Manifest, which hints at an identifier *scheme* (`did`, `dns`, `spiffe`) — a different, orthogonal axis.

Each Dependency references another artifact by its `identifier` alone (never an embedded copy), and MAY point across publishers or catalogs — the Salesforce dependency lives under `salesforce.com`, not `acme-corp.com`. `type` and `versionConstraint` (a SemVer *range* matcher such as `>=3.0.0`, not a literal version) let a consumer reason about a dependency without dereferencing it.

!!! note "Dependencies enable pre-flight checks"
    Because these edges are declared as discovery metadata, a consumer can answer *"can I use this agent — do I hold the credentials its required dependencies need?"* **before** invoking it, and *"what breaks if I decommission artifact X?"* for impact analysis. See [Consuming Catalogs](../guides/consuming-catalogs.md) for how a client reads and resolves these edges, and [Creating a Catalog](../guides/creating-a-catalog.md) for declaring them on your own entries. Consumers MUST handle an unresolvable `required` dependency gracefully and MUST NOT auto-fetch, install, or invoke a resolved dependency without applying the same trust verification they would apply to any artifact.

## When to use this pattern

Use the Dependencies extension when:

- An artifact relies on other artifacts to function — an agent that calls a downstream MCP server, a skill that requires a specific tool, or a plugin with a companion agent
- You want consumers to run pre-flight credential checks or filter discovery by the credentials they hold
- You need to express interchangeable alternatives (`anyOf`) for one capability slot, or degrade gracefully when an optional dependency is missing
- Governance or compliance tooling needs impact analysis and user- vs agent-attributed audit expectations

## Related guides

- [Dependencies Extension](../specification.md) — the canonical specification
- [Consuming Catalogs](../guides/consuming-catalogs.md) — resolving and verifying dependencies
- [Creating a Catalog](../guides/creating-a-catalog.md) — declaring dependencies on your entries
