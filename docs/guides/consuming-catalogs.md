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

## Filtering by lifecycle status

An entry may carry the [Lifecycle extension](../examples/lifecycle-metadata.md)
in its `extensions` map, declaring whether the artifact version is a
pre-release (`preview`), generally available (`active`), `deprecated`, or
`retired`. A consumer that understands the extension can filter deprecated or
retired artifacts at discovery and follow the recommended successor:

```python
LIFECYCLE_KEY = "https://ai-catalog.org/extensions/lifecycle"

RECOMMENDED_STATUSES = {"preview", "active", "deprecated", "retired"}

def normalize_status(raw):
    """Map a status value to a recommended state.

    `status` is open text, so a producer may emit a value outside the
    recommended set. Interpret it rather than discard it — an agent can do
    this semantically (e.g. an LLM mapping "sunset" -> "deprecated"). Return
    None only when the value can't be interpreted with confidence.
    """
    if raw is None or raw in RECOMMENDED_STATUSES:
        return raw
    synonyms = {
        "sunset": "deprecated", "end-of-support": "deprecated",
        "obsolete": "deprecated", "eol": "retired", "end-of-life": "retired",
        "ga": "active", "generally-available": "active", "stable": "active",
        "beta": "preview", "alpha": "preview", "rc": "preview",
    }
    return synonyms.get(str(raw).strip().lower())  # None if uninterpretable

def is_selectable(entry, allow_deprecated=False):
    lc = entry.get("extensions", {}).get(LIFECYCLE_KEY)
    if not lc:
        return True  # no lifecycle info — treat as any other entry

    status = normalize_status(lc.get("status"))
    if status == "retired":
        return False
    if status == "deprecated" and not allow_deprecated:
        return False
    if lc.get("status") and status is None:
        # Declared but uninterpretable: fail safe, don't assume "active".
        # Surface the raw value and keep it out of long-lived commitments.
        return allow_deprecated
    return True

def successor_id(entry):
    """The identifier a deprecated entry recommends migrating to, if any."""
    lc = entry.get("extensions", {}).get(LIFECYCLE_KEY) or {}
    return (lc.get("deprecated") or {}).get("replacedBy")
```

- If you **don't** understand the extension key, ignore it and treat the entry
  as any other.
- `status` is open text, so its recommended values are not exhaustive. Never
  reject an entry *just* because its status is unrecognized — but don't
  silently discard the value either, or you fail open: a value like `sunset`
  may signal a retirement you'd then miss.
- Instead, **interpret** an unrecognized status against the recommended states.
  An agent consumer can do this semantically rather than with a fixed synonym
  table. When you can't interpret it confidently, surface the raw value and
  treat the artifact conservatively rather than assuming it is `active`.
- You **may** still select a deprecated artifact deliberately — for a
  short-lived task that completes before its `endOfLifeDate`, for example.
- The dates and `replacedBy` reference are producer assertions, not signed
  claims. Corroborate them out of band when you need a supported-until
  guarantee.

## TypeScript example

```typescript
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

## Trust verification

If an entry has a `trustManifest`, you can verify its claims before trusting the artifact. See [Adding Trust](adding-trust.md) for details on the trust model and verification steps.
