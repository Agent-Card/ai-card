# Creating a Catalog

This guide covers everything you need to author a well-formed AI Catalog.

## Catalog structure

An AI Catalog is a JSON object with two required top-level fields:

```json
{
  "specVersion": "1.0",
  "entries": []
}
```

`specVersion`
:   The version of the AI Catalog specification this document conforms to, in `"Major.Minor"` format. Use `"1.0"` for the current version.

`entries`
:   An ordered array of Catalog Entry objects. May be empty.

Two optional top-level fields round out a complete catalog:

`host`
:   Identifies the organization operating this catalog. Required for [Level 2 (Discoverable)](../getting-started.md#what-youve-built) conformance.

`metadata`
:   An open map for custom or vendor-specific properties. See [Metadata extensibility](#metadata-extensibility).

## Adding a `host` object

The `host` object identifies who operates the catalog. Adding it upgrades you to Level 2 (Discoverable):

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Corp",
    "identifier": "did:web:acme-corp.com",
    "documentationUrl": "https://docs.acme-corp.com/ai"
  },
  "entries": [...]
}
```

`displayName` is required on the host. All other host fields are optional:

| Field | Description |
|---|---|
| `identifier` | Verifiable identifier — a DID, domain name, or other URI |
| `documentationUrl` | URL to your AI platform documentation |
| `logoUrl` | URL to your logo. Use a Data URI to avoid leaking client info through image requests |
| `trustManifest` | Trust Manifest for the host itself (see [Adding Trust](adding-trust.md)) |

## Catalog entries

Each entry in the `entries` array describes one AI artifact.

### Required fields

Every entry must have these three things:

```json
{
  "identifier": "urn:air:acme-corp.com:mcp:weather",
  "type": "application/mcp-server-card+json",
  "url": "https://api.acme-corp.com/mcp/server-card"
}
```

`identifier`
:   A stable, globally unique string that identifies this artifact. The `urn:air:{domain}:{namespace}:{name}` format is highly recommended for open or federated systems. The identifier should remain stable across versions and catalog locations.

`type`
:   The media type of the artifact. This is how clients determine what kind of artifact this is without fetching it.

`url` **or** `data`
:   Exactly one of these must be present. Use `url` to reference an external document, or `data` to embed the artifact inline (see [url vs data](#url-vs-data)).

### Choosing a type {#choosing-a-type}

| Artifact | `type` value |
|---|---|
| AI Catalog (nested) | `application/ai-catalog+json` |
| Agent Card (generic) | `application/agent-card+json` |
| A2A Agent Card | `application/a2a-agent-card+json` |
| MCP Server Card | `application/mcp-server-card+json` |
| Agent Skill metadata (JSON) | `application/agent-skills+json` |
| Agent Skill (Markdown) | `application/agent-skills+md` |
| Agent Skill (ZIP bundle) | `application/agent-skills+zip` |
| Agent Skill (gzipped tarball) | `application/agent-skills+gzip` |
| Dataset | `application/parquet`, `text/csv`, or appropriate type |

This list is not exhaustive — AI Catalog accepts any string as a `type` value. The spec is intentionally artifact-agnostic.

### Optional fields

Enrich your entries with additional metadata:

| Field | Type | Description |
|---|---|---|
| `displayName` | string | Human-readable name override (see below) |
| `description` | string | Short description of what this artifact does |
| `tags` | string[] | Keywords for filtering and discovery |
| `version` | string | Artifact version. Semantic versioning recommended |
| `updatedAt` | string | ISO 8601 timestamp of last modification |
| `publisher` | object | Who publishes this artifact (see [Publisher object](#publisher-object)) |
| `trustManifest` | object | Trust and identity metadata (see [Adding Trust](adding-trust.md)) |
| `metadata` | object | Custom key/value pairs (see [Metadata extensibility](#metadata-extensibility)) |
| `extensions` | object | Named extension map. Includes the official `dependencies` extension (see [Declaring dependencies](#declaring-dependencies)) |

### When to set `displayName`

`displayName` is optional and its use depends on the artifact type:

- **Omit it** for artifacts that embed their own canonical name — such as A2A Agent Cards (which have a `name` field) and MCP Server Cards (which have a `title` field). Clients fall back to the artifact's own name when `displayName` is absent.
- **Set it** for artifacts that do not carry a human-readable name — such as datasets (`application/parquet`) or skill bundles (`application/agent-skills+zip`).
- **Set it** when you deliberately want to override the artifact's own name in this catalog context.

When `displayName` is present, it always takes precedence over the artifact's own name.

A fully populated entry for an artifact that benefits from `displayName`:

```json
{
  "identifier": "urn:air:acme-corp.com:data:market-2026q1",
  "displayName": "Market Dataset Q1 2026",
  "type": "application/parquet",
  "url": "https://data.acme-corp.com/market-2026q1.parquet",
  "description": "OHLCV equity data for Q1 2026.",
  "tags": ["finance", "dataset"],
  "version": "1.0.0",
  "updatedAt": "2026-04-01T09:00:00Z",
  "publisher": {
    "identifier": "did:web:acme-corp.com",
    "displayName": "Acme Financial Corp"
  }
}
```

## `url` vs `data`

Each entry must provide its artifact content via exactly one of these fields:

`url`
:   A URL where clients fetch the full artifact. The server at that URL should respond with the content type declared in `type`. This is the recommended approach for most cases.

`data`
:   The complete artifact document embedded directly as a JSON value. The structure is determined by the `type` field and is opaque to the AI Catalog spec.

**Use `url` when:**
- The artifact is large
- The artifact is updated independently of the catalog
- You want to keep the catalog file small

**Use `data` when:**
- You want a fully self-contained catalog
- You're packaging a multi-artifact bundle (see [Organizing Catalogs](organizing-catalogs.md#multi-artifact-packaging))
- The artifact is small and unlikely to change independently

## Identifier best practices

The spec highly recommends the `urn:air:{domain}:{namespace}:{name}` format for open and federated systems:

```
urn:air:acme-corp.com:mcp:weather        # MCP server
urn:air:acme-corp.com:a2a:finance        # A2A agent
urn:air:acme-corp.com:skill:code-review  # skill bundle
urn:air:acme-corp.com:catalog:finance    # nested catalog
finance-agent                            # Avoid: not globally unique
```

- `{domain}` — the domain name of the publishing organization
- `{namespace}` — logical category, can be colon-separated (`finance:agent`)
- `{name}` — stable, unique name within the publisher's namespace

Keep identifiers stable across catalog locations and versions. Anchoring to a domain you own prevents typosquatting.

## Multi-version entries

A catalog may contain multiple entries with the same `identifier` but different `version` values, representing a version history:

```json
{
  "specVersion": "1.0",
  "entries": [
    {
      "identifier": "urn:air:acme-corp.com:a2a:finance",
      "version": "2.1.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://agents.acme-corp.com/finance/v2.1.json",
      "updatedAt": "2026-03-15T10:00:00Z"
    },
    {
      "identifier": "urn:air:acme-corp.com:a2a:finance",
      "version": "2.0.0",
      "type": "application/a2a-agent-card+json",
      "url": "https://agents.acme-corp.com/finance/v2.0.json",
      "updatedAt": "2026-01-20T08:00:00Z"
    }
  ]
}
```

When `version` is present, the combination of `identifier` + `version` must be unique. Clients looking for the latest version should sort by `version` (semver) or `updatedAt` and take the most recent.

## Declaring dependencies

Artifacts rarely stand alone. An agent may need an MCP server for tool access, a
vector store for retrieval, or another agent to delegate work to. The official
**dependencies extension** lets an entry declare what it depends on so consumers
can run pre-flight checks ("can I use this agent — do I hold the required
credentials?"), filter discovery by available credentials, perform impact analysis
("what breaks if I decommission this server?"), and reason about compliance
(user- vs agent-attributed audit).

Dependencies live under the entry's `extensions` map, keyed by the extension URI
`https://ai-catalog.org/extensions/dependencies`:

!!! note "Official extension — no `specVersion` bump"
    The `https://ai-catalog.org/extensions/` prefix marks this as an **official**
    AI Catalog extension, the same tier as the [metadata](#metadata-extensibility)
    extension. It is additive: the core schema is unchanged, `specVersion` stays
    `"1.0"`, and consumers that don't recognize the extension simply ignore it.
    See the [Dependencies Extension](../specification.md)
    section of the specification for the normative contract.

### Extension shape

The extension value has two optional arrays:

`required`
:   **AND semantics.** Every element must be satisfiable for the artifact to
    function. Unresolvable required dependencies are hard blockers.

`optional`
:   Each element is independently droppable — the artifact still works without it,
    with graceful degradation.

Each element of either array is a **Requirement**, which is *either*:

- a single **Dependency** object (the flat, common case), *or*
- a **Dependency Group** — `{ "anyOf": [ <Dependency>, ... ], "purpose": "..." }` —
  expressing **OR semantics**: any one alternative satisfies the slot. State
  `purpose` once for the whole group.

A **Dependency** object has these fields:

| Field | Required? | Description |
|---|---|---|
| `identifier` | **required** | A `urn:air:{publisher}:{namespace}:{name}` reference to another artifact's entry identifier. May be cross-publisher or cross-catalog — dependencies may reference external domains. |
| `type` | optional, recommended | The media type from the entry `type` vocabulary, e.g. `application/mcp-server-card+json` or `application/a2a-agent-card+json` (note the `-card` suffix). |
| `versionConstraint` | optional | A **SemVer range** string, e.g. `">=3.0.0"`, `"^3.1"`, `"3.x"`. It is a matcher, not a literal — not `minVersion`, not `version`. Absent means any version. |
| `credentialPropagation` | optional | Advisory hint about how credentials flow to this dependency (see below). |
| `purpose` | optional | Free text explaining why the dependency exists, e.g. "Read and write Salesforce CRM records". |

!!! warning "`credentialPropagation` is distinct from `identityType`"
    `credentialPropagation` describes **how credentials flow at connect time** and
    is open text with recommended lowercase values: `"obo"` (on-behalf-of — the
    user's identity is propagated, producing user-attributed audit), `"agent"`
    (the agent's own workload identity), `"user"` (a separate interactive user
    credential is required), and `"none"` (public). It is **advisory only** — the
    downstream artifact enforces real credentials at connect time, so never treat
    it as a security control.

    Do **not** conflate it with [`identityType`](#publisher-object), which is a
    completely different field: `identityType` is an identifier *scheme* hint
    (`did`, `dns`, `spiffe`) on a Publisher or Trust Manifest, describing how to
    resolve an identifier — not how credentials propagate.

### Full example

```json
{
  "identifier": "urn:air:acme-corp.com:agent:crm-assistant",
  "type": "application/a2a-agent-card+json",
  "url": "https://api.acme-corp.com/agents/crm-assistant.json",
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
```

Here the `crm-assistant` agent hard-requires the Salesforce MCP server (v3 or
later, called on behalf of the user) *and* one of two vector stores, while the
email sender is optional. Note the cross-publisher reference to
`urn:air:salesforce.com:...` — an external domain.

!!! warning "Consumers must verify trust"
    Consumers **must** handle unresolvable required dependencies gracefully and
    **must not** auto-fetch or install a dependency without trust verification.

## Publisher object

The `publisher` field on an entry identifies who publishes that artifact:

```json
"publisher": {
  "identifier": "did:web:acme-corp.com",
  "displayName": "Acme Financial Corp",
  "identityType": "did"
}
```

`identifier` and `displayName` are required. `identityType` is optional and provides a hint for resolving the identifier (`"did"`, `"dns"`, etc.).

## Metadata extensibility

Both the top-level catalog object and individual entries support a `metadata` field for custom properties:

```json
"metadata": {
  "com.acme.region": "us-east-1",
  "com.acme.sla": "99.9%",
  "license": "Apache-2.0"
}
```

Metadata keys should use reverse-DNS prefixes for vendor-specific keys (`com.acme.*`), or short unqualified names for broadly useful keys (`license`, `homepage`). Avoid shadowing standard fields like `displayName` or `tags`. Clients that don't recognize a key should ignore it.

## Complete example

```json
{
  "specVersion": "1.0",
  "host": {
    "displayName": "Acme Enterprise AI",
    "identifier": "did:web:acme-corp.com",
    "documentationUrl": "https://docs.acme-corp.com/ai"
  },
  "entries": [
    {
      "identifier": "urn:air:acme-corp.com:mcp:weather",
      "type": "application/mcp-server-card+json",
      "description": "Real-time weather data and forecasts.",
      "tags": ["weather", "data"],
      "version": "1.2.0",
      "url": "https://api.acme-corp.com/mcp/server-card",
      "updatedAt": "2026-04-01T09:00:00Z",
      "publisher": {
        "identifier": "did:web:acme-corp.com",
        "displayName": "Acme Corp"
      }
    },
    {
      "identifier": "urn:air:acme-corp.com:a2a:research",
      "type": "application/a2a-agent-card+json",
      "description": "Deep-research agent with citation support.",
      "tags": ["research", "analysis"],
      "url": "https://agents.acme-corp.com/research"
    },
    {
      "identifier": "urn:air:acme-corp.com:data:market-2026q1",
      "displayName": "Market Dataset Q1 2026",
      "type": "application/parquet",
      "description": "OHLCV equity data for Q1 2026.",
      "tags": ["finance", "dataset"],
      "url": "https://data.acme-corp.com/market-2026q1.parquet"
    }
  ]
}
```

## Next steps

- [Serving Your Catalog](serving-your-catalog.md) — deploy and configure hosting
- [Organizing Catalogs](organizing-catalogs.md) — nested catalogs for large inventories
- [Adding Trust](adding-trust.md) — identity, attestations, and provenance
