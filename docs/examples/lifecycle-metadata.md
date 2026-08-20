# Example: Lifecycle Metadata

Artifacts evolve. A v1 agent is superseded by a breaking v2, an endpoint is
scheduled for shutdown, and a successor is published with a migration guide.
An entry's `version` and `updatedAt` tell you *which* revision this is and
*when the entry changed* — but not whether that revision is a preview,
generally available, deprecated with a scheduled end-of-life, or already
retired. The [Lifecycle official extension](../specification.md) enriches an
entry with that software-lifecycle state, so a consumer can filter deprecated
or retired artifacts at discovery, plan around a known end-of-life date, and
follow a producer-supplied migration path to a successor.

## The extension

The extension key (namespace) is:

```
https://ai-catalog.org/extensions/lifecycle
```

It lives inside an entry's `extensions` map. Its value describes the lifecycle
state of the **artifact version** the entry identifies — so within a
multi-version listing, a v1 entry can be `deprecated` while the v2 entry is
`active`.

!!! note "Lifecycle is per-version"
    Lifecycle metadata describes the version identified by the entry, not the
    logical artifact as a whole. When a catalog lists several versions of the
    same `identifier`, each versioned entry may carry its own Lifecycle
    extension.

## Full example

A deprecated v1 agent, superseded by a v2, with a scheduled end-of-life:

```json
{
  "identifier": "urn:air:acme.com:finance:invoice-processor",
  "version": "1.0.0",
  "type": "application/a2a-agent-card+json",
  "url": "https://api.acme.com/agents/invoice/v1",
  "tags": ["finance", "a2a"],
  "extensions": {
    "https://ai-catalog.org/extensions/lifecycle": {
      "status": "deprecated",
      "releaseDate": "2025-03-15",
      "deprecated": {
        "replacedBy": "urn:air:acme.com:finance:invoice-processor-v2",
        "deprecationDate": "2026-09-01",
        "endOfLifeDate": "2027-01-01",
        "breakingChanges": [
          "Authentication changed from API key to OAuth2",
          "Response schema now uses ISO 8601 dates"
        ],
        "migrationGuide": "https://docs.acme.com/invoice-v2-migration"
      }
    }
  }
}
```

The successor entry carries its own lifecycle status:

```json
{
  "identifier": "urn:air:acme.com:finance:invoice-processor-v2",
  "version": "2.0.0",
  "type": "application/a2a-agent-card+json",
  "url": "https://api.acme.com/agents/invoice/v2",
  "tags": ["finance", "a2a"],
  "extensions": {
    "https://ai-catalog.org/extensions/lifecycle": {
      "status": "active",
      "releaseDate": "2026-06-01"
    }
  }
}
```

## Extension fields

The extension value supports these fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `status` | string | Optional | Lifecycle state. Recommended values: `preview`, `active`, `deprecated`, `retired` — each denotes a version a consumer can actually reach (a not-yet-released "planned" state is intentionally excluded) |
| `releaseDate` | string | Optional | ISO 8601 date/date-time this version was released (distinct from the entry's `updatedAt`) |
| `deprecated` | object | Optional | Deprecation detail (below); present when `status` is `deprecated` or `retired` |

The `deprecated` object supports:

| Field | Type | Required | Description |
|---|---|---|---|
| `replacedBy` | string | Optional | `identifier` of the successor artifact, following the same naming rule as a Catalog Entry `identifier` (`urn:air` highly recommended; required for open or federated systems) |
| `deprecationDate` | string | Optional | ISO 8601 date/date-time the version became (or becomes) deprecated |
| `endOfLifeDate` | string | Optional | ISO 8601 date/date-time after which the version is retired |
| `breakingChanges` | string[] | Optional | Human-readable descriptions of breaking changes to account for when migrating |
| `migrationGuide` | string | Optional | URL to migration documentation |

## Filtering and migrating at discovery

A consumer that understands the extension can read `status` to decide how to
treat an entry — hiding or de-ranking `retired` and `deprecated` artifacts,
warning an operator, and following `replacedBy` to the successor.

Because `status` is open text, its recommended values are not exhaustive. A
consumer may not reject an entry just because the status is unrecognized. A 
value like `sunset` signals a retirement that failing open would miss. An 
agent can do this semantically, and when it can't interpret confidently it 
should apply its own policy on treating the artifact conservatively or assuming `active`:

```python
from datetime import date

LIFECYCLE_KEY = "https://ai-catalog.org/extensions/lifecycle"
RECOMMENDED_STATUSES = {"preview", "active", "deprecated", "retired"}

def lifecycle(entry):
    return entry.get("extensions", {}).get(LIFECYCLE_KEY)

def normalize_status(raw):
    """Map an open-text status onto a recommended state, or None if unclear.

    A rule table handles common synonyms; an agent consumer can replace this
    with semantic interpretation (e.g. an LLM classifying the raw value).
    """
    if raw is None or raw in RECOMMENDED_STATUSES:
        return raw
    synonyms = {
        "sunset": "deprecated", "end-of-support": "deprecated",
        "obsolete": "deprecated", "eol": "retired", "end-of-life": "retired",
        "ga": "active", "generally-available": "active", "stable": "active",
        "beta": "preview", "alpha": "preview", "rc": "preview",
    }
    return synonyms.get(str(raw).strip().lower())

def is_selectable(entry, allow_deprecated=False):
    """Whether an entry should be offered at discovery time."""
    lc = lifecycle(entry)
    if not lc:
        return True  # no lifecycle info — treat as any other entry

    status = normalize_status(lc.get("status"))
    if status == "retired":
        return False
    if status == "deprecated" and not allow_deprecated:
        return False
    if lc.get("status") and status is None:
        return allow_deprecated  # uninterpretable: fail safe, don't assume active
    return True

def successor_id(entry):
    """The identifier a deprecated entry recommends migrating to, if any."""
    lc = lifecycle(entry) or {}
    return (lc.get("deprecated") or {}).get("replacedBy")
```

A consumer may still choose a deprecated artifact deliberately — for a
short-lived task that finishes well before the `endOfLifeDate`, the deprecated
version may be the pragmatic choice:

```python
def usable_until_eol(entry, deadline):
    """A deprecated entry is fine for work that completes before its EOL."""
    lc = lifecycle(entry) or {}
    eol = (lc.get("deprecated") or {}).get("endOfLifeDate")
    if not eol:
        return True
    return deadline < date.fromisoformat(eol[:10])
```

!!! warning "Lifecycle metadata is not a support guarantee"
    The dates and the `replacedBy` reference are producer assertions, not
    signed claims. A consumer that needs a supported-until guarantee
    corroborates them out of band, not via this extension. A consumer that
    does not understand the extension key ignores it and treats the entry as
    any other.

## Related

- [Full Specification](../specification.md)
- [Creating a Catalog](../guides/creating-a-catalog.md#the-lifecycle-extension)
- [Consuming Catalogs](../guides/consuming-catalogs.md#filtering-by-lifecycle-status)
