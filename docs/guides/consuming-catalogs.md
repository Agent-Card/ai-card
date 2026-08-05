# Consuming Catalogs

This guide covers how to discover, fetch, and process AI Catalog documents as a client developer.

## Discovery flow

When you have a domain and want to find its AI Catalog, follow this sequence:

1. **Fetch the target URL** and inspect HTTP response headers for a `Link` header with `rel="ai-catalog"`:
   ```
   Link: <https://example.com/catalog/ai.json>; rel="ai-catalog"
   ```

2. **If no `Link` header**, and the response is HTML, parse the document for a `<link>` element:
   ```html
   <link rel="ai-catalog" href="/catalog/ai.json">
   ```

3. **If neither**, fall back to the well-known URI:
   ```
   GET https://example.com/.well-known/ai-catalog.json
   ```

4. **Validate the response**: check that `Content-Type` contains `json`, parse the body, and confirm it has a `specVersion` field. If valid, this is the site's AI Catalog.

## Parsing the catalog

A valid catalog has at minimum:

```json
{
  "specVersion": "1.0",
  "entries": [...]
}
```

Always check `specVersion` first:

- If the **major version** matches what you support, proceed (ignore unrecognized fields)
- If the **major version** is higher than you support, reject with an informative error — don't silently misinterpret it
- Minor version differences (e.g., you support 1.0, the catalog says 1.1) are safe to ignore

```python
import json, urllib.request

def fetch_catalog(url):
    with urllib.request.urlopen(url) as resp:
        catalog = json.load(resp)

    major = int(catalog["specVersion"].split(".")[0])
    if major > 1:  # replace 1 with your supported major version
        raise ValueError(f"Unsupported catalog version: {catalog['specVersion']}")

    return catalog
```

## Filtering by type

The `type` field on each entry tells you what kind of artifact it is, without needing to fetch it:

```python
def find_mcp_servers(catalog):
    return [
        entry for entry in catalog["entries"]
        if entry["type"] == "application/mcp-server-card+json"
    ]

def find_a2a_agents(catalog):
    return [
        entry for entry in catalog["entries"]
        if entry["type"] == "application/a2a-agent-card+json"
    ]
```

Ignore entries with unknown `type` values — new types will be added over time.

## Resolving a display name

`displayName` is optional on entries. To get a human-readable name, resolve in this order:

1. `displayName` on the entry, if present — always takes precedence
2. The artifact's own canonical name, if you've already fetched it (e.g., `name` on an A2A Agent Card, `title` on an MCP Server Card)
3. The trailing segment of the `identifier` as a fallback (e.g., `urn:air:example.com:mcp:weather` → `weather`)

Avoid fetching an artifact at render time solely to obtain a name — resolve and cache the name at ingestion instead.

## Resolving artifacts

Each entry provides its artifact via either `url` or `data`:

```python
def resolve_artifact(entry):
    if "data" in entry:
        # Artifact is inline — use directly
        return entry["data"]

    if "url" in entry:
        # Fetch from the URL
        with urllib.request.urlopen(entry["url"]) as resp:
            return json.load(resp)

    raise ValueError("Entry has neither url nor data")
```

When fetching from `url`, the server should respond with the content type declared in the entry's `type` field.

## Pre-flight dependency check

An entry may declare the other artifacts it relies on via the official
[Dependencies extension](../specification.md), keyed by
`https://ai-catalog.org/extensions/dependencies`. Because dependencies live
under `extensions`, they are additive: a catalog carrying them is still a
conformant `1.0` document, and clients that don't recognize the key simply
ignore it.

Before you invoke or deploy an artifact, run a **pre-flight check**: for each
`required` dependency, confirm it is resolvable and that you hold (or can
acquire) the credentials it needs. `optional` dependencies never block use —
skip them or degrade gracefully when they can't be satisfied.

An entry's dependencies value looks like this:

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

A requirement is either a single Dependency object (the flat, common case) or
a **Dependency Group** — an object with an `anyOf` array, where any one
alternative satisfies the slot. The following helpers, written in the same
style as `fetch_catalog` and `collect_all_entries`, resolve each dependency
against a catalog index and check credentials before use:

```python
DEPENDENCIES_EXT = "https://ai-catalog.org/extensions/dependencies"

def get_dependencies(entry):
    """Read the dependencies extension off an entry, if present."""
    ext = entry.get("extensions", {}).get(DEPENDENCIES_EXT)
    if not ext:
        return [], []
    return ext.get("required", []), ext.get("optional", [])

def satisfies(dep, index, held_credentials):
    """A single Dependency is satisfiable if it resolves, the version
    constraint matches, and we hold (or can acquire) any needed credential."""
    target = index.get(dep["identifier"])
    if target is None:
        return False  # unresolvable — not in any catalog we can reach

    constraint = dep.get("versionConstraint")
    if constraint and not version_matches(target.get("version"), constraint):
        return False  # e.g. requires >=3.0.0 but only 2.9 is published

    # credentialPropagation is an advisory hint (see note below): "none" and
    # "obo"/"agent" that we can mint need nothing extra; "user" needs an
    # interactive credential we must already hold or be able to obtain.
    prop = dep.get("credentialPropagation", "none")
    if prop == "user" and dep["identifier"] not in held_credentials:
        return False
    return True

def requirement_satisfied(req, index, held_credentials):
    """A requirement is a single Dependency or an anyOf group; a group is
    satisfied when at least one alternative is satisfiable."""
    if "anyOf" in req:
        return any(
            satisfies(alt, index, held_credentials) for alt in req["anyOf"]
        )
    return satisfies(req, index, held_credentials)

def preflight(entry, index, held_credentials):
    """Return (ok, blockers, degraded). `ok` is False if any required
    dependency is unsatisfiable; `degraded` lists droppable optionals."""
    required, optional = get_dependencies(entry)

    blockers = [
        req for req in required
        if not requirement_satisfied(req, index, held_credentials)
    ]
    degraded = [
        req for req in optional
        if not requirement_satisfied(req, index, held_credentials)
    ]
    return (not blockers, blockers, degraded)
```

Build `index` by mapping each `identifier` to its entry (for example, from
`collect_all_entries`), and supply `version_matches` from a SemVer range
library such as `packaging` or `semver`. `held_credentials` is whatever set
of credentials your client can present or mint.

!!! warning "Never auto-fetch or install a dependency without trust verification"
    A pre-flight check tells you *whether* a dependency is usable; it is not
    permission to pull and run it. Resolve dependencies through catalogs you
    trust and verify each artifact (see [Trust verification](#trust-verification))
    before invoking it.

### Filtering discovery by available credentials

The same check powers discovery filtering. When listing agents, hide the ones
you couldn't actually use — *"hide agents requiring credentials I don't
hold"* — by dropping any entry whose `preflight` reports a blocker:

```python
def usable_entries(entries, index, held_credentials):
    return [
        entry for entry in entries
        if preflight(entry, index, held_credentials)[0]
    ]
```

!!! note "`credentialPropagation` is advisory"
    `credentialPropagation` is an upfront *hint* for planning, not a security
    control. The downstream artifact enforces real credentials at connect
    time — a `"none"` hint does not make a dependency public, and holding a
    credential in your pre-flight set does not guarantee the dependency will
    accept it. Use it to plan and filter, never to authorize. See
    [Adding Trust](adding-trust.md) for how credentials are actually verified.

## Handling nested catalogs

An entry with `type: "application/ai-catalog+json"` is itself a catalog. To get all artifacts, recurse into it:

```python
def collect_all_entries(catalog_url, max_depth=4, _visited=None, _depth=0):
    if _depth >= max_depth:
        return []

    if _visited is None:
        _visited = set()

    if catalog_url in _visited:
        return []  # cycle detected
    _visited.add(catalog_url)

    catalog = fetch_catalog(catalog_url)
    results = []

    for entry in catalog.get("entries", []):
        if entry["type"] == "application/ai-catalog+json":
            # Recurse into nested catalog
            nested_url = entry.get("url")
            if nested_url:
                results.extend(
                    collect_all_entries(
                        nested_url, max_depth, _visited, _depth + 1
                    )
                )
        else:
            results.append(entry)

    return results
```

!!! warning "Enforce depth limits"
    Always enforce a maximum nesting depth (4 is recommended) and track visited URLs to prevent circular references. A malicious or misconfigured catalog could otherwise cause infinite loops.

## Multi-version resolution

When multiple entries share the same `identifier`, they represent different versions of the same artifact. To get the latest:

```python
from packaging.version import Version

def latest_entries(entries):
    """Return only the latest version of each unique identifier."""
    by_id = {}

    for entry in entries:
        eid = entry["identifier"]
        if eid not in by_id:
            by_id[eid] = entry
            continue

        existing = by_id[eid]
        # Prefer by semver version, fall back to updatedAt
        try:
            if Version(entry.get("version", "0")) > Version(existing.get("version", "0")):
                by_id[eid] = entry
        except Exception:
            if entry.get("updatedAt", "") > existing.get("updatedAt", ""):
                by_id[eid] = entry

    return list(by_id.values())
```

## TypeScript example

```typescript
const DEPENDENCIES_EXT = "https://ai-catalog.org/extensions/dependencies";

interface Dependency {
  identifier: string;
  type?: string;
  versionConstraint?: string;
  credentialPropagation?: "obo" | "agent" | "user" | "none" | string;
  purpose?: string;
}

interface DependencyGroup {
  anyOf: Dependency[];
  purpose?: string;
}

type Requirement = Dependency | DependencyGroup;

interface Dependencies {
  required?: Requirement[];
  optional?: Requirement[];
}

interface CatalogEntry {
  identifier: string;
  type: string;
  url?: string;
  data?: unknown;
  displayName?: string;
  version?: string;
  updatedAt?: string;
  tags?: string[];
  description?: string;
  // Extensions are keyed by URI; dependencies live under DEPENDENCIES_EXT.
  extensions?: Record<string, unknown>;
}

function isGroup(req: Requirement): req is DependencyGroup {
  return "anyOf" in req;
}

function readDependencies(entry: CatalogEntry): Dependencies | undefined {
  return entry.extensions?.[DEPENDENCIES_EXT] as Dependencies | undefined;
}

interface AICatalog {
  specVersion: string;
  entries: CatalogEntry[];
  host?: { displayName: string; identifier?: string };
}

async function discoverCatalog(domain: string): Promise<AICatalog | null> {
  const wellKnown = `https://${domain}/.well-known/ai-catalog.json`;
  try {
    const resp = await fetch(wellKnown);
    if (!resp.ok) return null;
    const catalog: AICatalog = await resp.json();
    if (!catalog.specVersion || !Array.isArray(catalog.entries)) return null;
    return catalog;
  } catch {
    return null;
  }
}

function filterByType(catalog: AICatalog, type: string): CatalogEntry[] {
  return catalog.entries.filter(e => e.type === type);
}
```

## Error handling

Be defensive when consuming catalogs from unknown sources:

- **Missing fields**: check for `specVersion` and `entries` before processing; skip entries missing `identifier` or `type`
- **Unknown `type` values**: ignore them — don't fail
- **Unreachable URLs**: log and skip; don't abort the whole catalog
- **Invalid JSON**: catch parse errors and treat the catalog as unavailable
- **Circular references**: track visited URLs and enforce depth limits (see above)
- **Untrusted `data` content**: treat inline `data` as untrusted input; don't execute content with script-capable media types
- **Unresolvable required dependency**: if a `required` dependency's `identifier` resolves to no reachable entry, treat the artifact as a hard blocker — don't invoke it (see [Pre-flight dependency check](#pre-flight-dependency-check))
- **Unavailable credentials for a required dependency**: block use when you can neither present nor acquire a credential a `required` dependency needs; degrade gracefully for `optional` ones
- **`versionConstraint` mismatch**: if the resolved dependency's `version` falls outside the declared range (e.g., requires `>=3.0.0` but only `2.9` is published), treat the requirement as unmet
- **Dependency cycles**: dependencies may reference each other; track visited `identifier`s when walking the dependency graph so a cycle doesn't cause infinite recursion

## Trust verification

If an entry has a `trustManifest`, you can verify its claims before trusting the artifact. See [Adding Trust](adding-trust.md) for details on the trust model and verification steps.
