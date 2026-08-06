# Example: Deployment Metadata

A single logical agent often runs in more than one place: production and
staging, `us-east-1` and `eu-west-1`, with different data-residency and
compliance constraints in each region. AI Catalog keeps **identity** ("what
the agent is") separate from **instance** ("where it lives"): the entry has one
stable `identifier`, and the [Deployment official extension](../specification.md)
enumerates the concrete deployment instances behind it.

This lets a consumer deterministically pick an instance that satisfies its
policy — an EU client selecting the GDPR instance in `eu-west-1`, a test harness
targeting `staging`, or a client opting into a `beta` release channel — while
everything stays under one logical identity.

## The extension

The extension key (namespace) is:

```
https://ai-catalog.org/extensions/deployment
```

It lives inside an entry's `extensions` map. Its value is an object with a
required, non-empty `instances` array. Each instance describes one deployment of
the **same** logical artifact — instances are deployments, not distinct
artifacts.

!!! note "The entry `url` stays the default"
    The entry's top-level `url` remains the default entry point. Each instance's
    `url` is an alternative endpoint for the same `identifier`. One instance
    `url` should equal the entry `url` so the default is represented among the
    instances.

## Full example

```json
{
  "identifier": "urn:air:acme-corp.com:agent:invoice-processor",
  "type": "application/a2a-agent-card+json",
  "url": "https://api.acme-corp.com/agents/invoice",
  "tags": ["finance", "a2a"],
  "extensions": {
    "https://ai-catalog.org/extensions/deployment": {
      "instances": [
        {
          "instanceId": "invoice-prod-us",
          "environment": "production",
          "url": "https://api.acme-corp.com/agents/invoice",
          "region": "us-east-1"
        },
        {
          "instanceId": "invoice-prod-eu",
          "environment": "production",
          "url": "https://eu-api.acme-corp.com/agents/invoice",
          "region": "eu-west-1",
          "dataResidency": ["EU"],
          "compliance": ["GDPR"]
        },
        {
          "instanceId": "invoice-staging",
          "environment": "staging",
          "url": "https://staging-api.acme-corp.com/agents/invoice",
          "region": "us-east-1",
          "releaseChannel": "beta"
        }
      ]
    }
  }
}
```

## Instance fields

Each object in the `instances` array supports these fields:

| Field | Type | Required | Description |
|---|---|---|---|
| `instanceId` | string | Required | Stable identifier for this instance, unique within the entry |
| `url` | string | Required | Entry-point URL for this instance |
| `environment` | string | Optional | Deployment environment, e.g. `production`, `staging`, `development` |
| `releaseChannel` | string | Optional | Release maturity track, orthogonal to `environment`, e.g. `stable`, `beta`, `LTS`, `EDGE` |
| `region` | string | Optional | Deployment region, e.g. `us-east-1`, `eu-west-1` |
| `dataResidency` | string[] | Optional | Jurisdictions where data is stored or processed, e.g. `["EU"]`, `["US","CA"]` |
| `compliance` | string[] | Optional | Compliance regimes the instance conforms to, e.g. `["GDPR"]`, `["SOC2","HIPAA"]` |
| `description` | string | Optional | Human-readable label for the instance |

## Selecting an instance

A consumer that understands the extension may select an instance whose
`environment`, `region`, `dataResidency`, or `compliance` satisfies its policy.
If no instance matches, it **should not** fall back to a non-conforming instance.

```python
DEPLOYMENT_KEY = "https://ai-catalog.org/extensions/deployment"

def select_instance(entry, environment=None, release_channel=None,
                    region=None, compliance=None):
    """Pick a deployment instance matching the consumer's policy.

    Returns None when no instance conforms — don't fall back
    to a non-conforming instance (e.g. the entry url) in that case.
    """
    ext = entry.get("extensions", {}).get(DEPLOYMENT_KEY)
    if not ext:
        # Extension unknown/absent: fall back to the entry's default url.
        return {"url": entry["url"]}

    for inst in ext["instances"]:
        if environment and inst.get("environment") != environment:
            continue
        if release_channel and inst.get("releaseChannel") != release_channel:
            continue
        if region and inst.get("region") != region:
            continue
        if compliance and compliance not in inst.get("compliance", []):
            continue
        return inst

    return None  # no conforming instance — do not fall back
```

```python
entry = ...  # the invoice-processor entry above

# EU client bound by GDPR: resolves to the eu-west-1 instance.
eu = select_instance(entry, region="eu-west-1", compliance="GDPR")

# Test harness: resolves to the staging instance.
staging = select_instance(entry, environment="staging")

# Client opting into the beta release channel: resolves to the beta instance.
beta = select_instance(entry, release_channel="beta")
```

!!! warning "Deployment metadata is not a trust control"
    `dataResidency` and `compliance` are producer assertions, not signed
    claims. A consumer that needs assurance verifies them via the entry's Trust
    Manifest (attestations), not via this extension. A consumer that does not
    understand the extension key ignores it and falls back to the entry `url`.

## Related

- [Full Specification](../specification.md)
- [Creating a Catalog](../guides/creating-a-catalog.md#the-deployment-extension)
- [Consuming Catalogs](../guides/consuming-catalogs.md#selecting-a-deployment-instance)
