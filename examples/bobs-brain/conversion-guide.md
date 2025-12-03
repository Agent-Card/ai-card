# A2A AgentCard → AI Card Conversion Guide

**Version:** 1.0
**Date:** 2025-12-02
**Purpose:** Guide for migrating existing A2A AgentCards (v0.3.0) to universal AI Card format (v1.0)

---

## Overview

This guide shows how to convert an existing A2A AgentCard to the new universal AI Card format while maintaining backward compatibility with the A2A protocol.

**Key Benefits of AI Card:**
- ✅ **Protocol-agnostic** - Support A2A, MCP, and custom protocols in one card
- ✅ **Trust attestations** - Document compliance, certifications, security posture
- ✅ **Rich identity** - SPIFFE, DID, or custom identity systems
- ✅ **Publisher information** - Clear attribution and organization details
- ✅ **Extensible metadata** - Custom fields for deployment, versioning, metrics

---

## Quick Comparison

### A2A AgentCard (v0.3.0)
```json
{
  "protocol_version": "0.3.0",
  "name": "bobs-brain",
  "version": "0.12.0",
  "description": "...",
  "url": "https://bob.intent.solutions",
  "preferred_transport": "JSONRPC",
  "skills": [...]
}
```

### AI Card (v1.0)
```json
{
  "$schema": "https://a2a-protocol.org/ai-card/v1/schema.json",
  "specVersion": "1.0",
  "id": "spiffe://intent.solutions/agent/bobs-brain/prod/us-central1/0.12.0",
  "identityType": "spiffe",
  "name": "Bob's Brain",
  "services": {
    "a2a": {
      "type": "a2a",
      "protocolSpecific": {
        "protocolVersion": "0.3.0",
        "skills": [...]
      }
    }
  }
}
```

---

## Field Mapping Reference

### Top-Level Fields

| A2A AgentCard (v0.3.0) | AI Card (v1.0) | Notes |
|------------------------|----------------|-------|
| N/A | `$schema` | Required. Points to AI Card JSON schema |
| N/A | `specVersion` | Required. Currently "1.0" |
| `spiffe_id` | `id` | Primary identity. SPIFFE ID recommended |
| N/A | `identityType` | Required. "spiffe", "did", or custom |
| `name` | `name` | Agent/service name |
| `version` | Moved to `metadata.version` | Version now in metadata section |
| `description` | `description` | Description text |
| `icon_url` | `logoUrl` | Logo/icon URL |
| N/A | `maturity` | "experimental", "beta", "stable", "deprecated" |
| N/A | `signature` | Optional. Detached JWS signature |

### Publisher Information

| A2A AgentCard (v0.3.0) | AI Card (v1.0) | Notes |
|------------------------|----------------|-------|
| `provider.organization` | `publisher.name` | Organization name |
| `provider.url` | `publisher.url` | Organization URL |
| N/A | `publisher.id` | Publisher identity (SPIFFE/DID) |
| N/A | `publisher.identityType` | Identity type ("spiffe", etc.) |
| N/A | `publisher.attestation` | Optional identity proof |

### Trust & Attestations

**New in AI Card:**
- `trust.attestations[]` - Array of compliance/security attestations
- `trust.privacyPolicyUrl` - Privacy policy link
- `trust.termsOfServiceUrl` - Terms of service link

**Example Attestations:**
```json
{
  "trust": {
    "attestations": [
      {
        "type": "HardModeCompliance",
        "description": "R1-R8 rules enforced via CI",
        "details": {...}
      },
      {
        "type": "SOC2-Type2",
        "credentialUrl": "https://..."
      }
    ]
  }
}
```

### Services (Protocol-Specific)

**A2A Protocol moves into `services.a2a.protocolSpecific`:**

| A2A AgentCard (v0.3.0) | AI Card (v1.0) | Notes |
|------------------------|----------------|-------|
| `protocol_version` | `services.a2a.protocolSpecific.protocolVersion` | A2A protocol version |
| `url` | `services.a2a.protocolSpecific.supportedInterfaces[0].url` | Endpoint URL |
| `preferred_transport` | `services.a2a.protocolSpecific.supportedInterfaces[0].transport` | JSONRPC, HTTP, etc. |
| `skills[]` | `services.a2a.protocolSpecific.skills[]` | Skills array |
| `security_schemes` | `services.a2a.protocolSpecific.securitySchemes` | OAuth2, API keys, etc. |
| `capabilities` | Moved to skill tags | General capabilities now in skill tags |

### Skills Schema

Skills remain mostly unchanged but are now nested in `services.a2a.protocolSpecific.skills[]`:

```json
{
  "id": "bob.answer_adk_question",
  "name": "Answer ADK Question",
  "description": "...",
  "inputModes": ["application/json"],
  "outputModes": ["application/json", "text/plain"],
  "inputSchema": {...},
  "outputSchema": {...},
  "tags": ["adk", "documentation"]
}
```

### Metadata

**New `metadata` section** for deployment/operational info:

```json
{
  "metadata": {
    "region": "us-central1",
    "environment": "production",
    "version": "0.12.0",
    "runtime": "Vertex AI Agent Engine",
    "custom_field": "custom_value"
  }
}
```

---

## Step-by-Step Conversion

### Step 1: Create AI Card Shell

```json
{
  "$schema": "https://a2a-protocol.org/ai-card/v1/schema.json",
  "specVersion": "1.0",
  "id": "<COPY_FROM_spiffe_id>",
  "identityType": "spiffe",
  "name": "<COPY_FROM_name>",
  "description": "<COPY_FROM_description>",
  "logoUrl": <COPY_FROM_icon_url>,
  "maturity": "stable"
}
```

### Step 2: Add Publisher Information

```json
{
  "publisher": {
    "id": "spiffe://<your-trust-domain>/org/<org-name>",
    "identityType": "spiffe",
    "name": "<COPY_FROM_provider.organization>",
    "url": "<COPY_FROM_provider.url>"
  }
}
```

### Step 3: Add Trust Attestations (Optional but Recommended)

```json
{
  "trust": {
    "attestations": [
      {
        "type": "CustomAttestation",
        "description": "Describe your compliance/security posture"
      }
    ]
  }
}
```

### Step 4: Move A2A Protocol to Services

```json
{
  "services": {
    "a2a": {
      "type": "a2a",
      "name": "<Agent name> A2A Interface",
      "description": "...",
      "protocolSpecific": {
        "protocolVersion": "<COPY_FROM_protocol_version>",
        "supportedInterfaces": [
          {
            "transport": "<COPY_FROM_preferred_transport>",
            "url": "<COPY_FROM_url>"
          }
        ],
        "securitySchemes": <COPY_FROM_security_schemes>,
        "skills": <COPY_FROM_skills>
      }
    }
  }
}
```

### Step 5: Add Timestamps and Metadata

```json
{
  "createdAt": "2025-01-15T10:00:00Z",
  "updatedAt": "2025-12-02T18:00:00Z",
  "metadata": {
    "version": "<COPY_FROM_version>",
    "region": "us-central1",
    "environment": "production",
    "custom_fields": "..."
  }
}
```

---

## SPIFFE Identity Migration

### Current A2A Format
```json
{
  "spiffe_id": "spiffe://intent.solutions/agent/bobs-brain/dev/us-central1/0.11.0"
}
```

### New AI Card Format
```json
{
  "id": "spiffe://intent.solutions/agent/bobs-brain/prod/us-central1/0.12.0",
  "identityType": "spiffe"
}
```

**SPIFFE Best Practices:**
- Use trust domain you control (e.g., `spiffe://yourcompany.com`)
- Follow path pattern: `/agent/<name>/<env>/<region>/<version>`
- Update version in path when agent version changes
- Document SPIFFE setup in deployment docs

---

## Multi-Protocol Support

One AI Card can support multiple protocols:

```json
{
  "services": {
    "a2a": {
      "type": "a2a",
      "protocolSpecific": {...}
    },
    "mcp": {
      "type": "mcp",
      "protocolSpecific": {
        "protocolVersion": "2025-06-18",
        "transport": {...},
        "capabilities": {...}
      }
    },
    "custom": {
      "type": "custom-protocol",
      "protocolSpecific": {...}
    }
  }
}
```

---

## Validation Checklist

Before deploying your converted AI Card:

- [ ] `$schema` points to official AI Card schema URL
- [ ] `specVersion` is "1.0"
- [ ] `id` is unique and follows your identity pattern (SPIFFE/DID)
- [ ] `identityType` matches your `id` format
- [ ] `publisher.id` exists if using organizational identity
- [ ] A2A protocol config is in `services.a2a.protocolSpecific`
- [ ] Skills have `inputModes` and `outputModes` (new requirement)
- [ ] `createdAt` and `updatedAt` timestamps are ISO 8601 format
- [ ] JSON validates against schema (use schema validator)

---

## Backward Compatibility

**During transition period:**

1. **Serve both formats** at different endpoints:
   ```
   /.well-known/agent-card.json       # Original A2A format
   /.well-known/ai-card.json          # New AI Card format
   ```

2. **Content negotiation** - Return format based on client request

3. **Gradual migration** - Update consumers to use new AI Card format

4. **Deprecation timeline** - Announce A2A-only format sunset date

---

## Common Pitfalls

### ❌ Don't Do This

```json
{
  "id": "my-agent",  // ❌ Not a valid SPIFFE/DID
  "identityType": "spiffe",  // ❌ Mismatch
  "services": {
    "a2a": {
      "skills": [...]  // ❌ Skills should be in protocolSpecific
    }
  }
}
```

### ✅ Do This

```json
{
  "id": "spiffe://company.com/agent/my-agent",  // ✅ Valid SPIFFE
  "identityType": "spiffe",  // ✅ Matches
  "services": {
    "a2a": {
      "protocolSpecific": {  // ✅ Correct nesting
        "skills": [...]
      }
    }
  }
}
```

---

## Testing Your Conversion

```bash
# Validate JSON syntax
jq empty ai-card.json

# Validate against schema (once schema is published)
ajv validate -s ai-card-schema.json -d ai-card.json

# Compare fields with original
diff <(jq -S 'keys' agent-card-a2a.json) <(jq -S '.services.a2a.protocolSpecific | keys' ai-card.json)
```

---

## Resources

- **AI Card Spec:** https://github.com/Agent-Card/ai-card
- **A2A Protocol:** https://github.com/google/a2a-protocol
- **SPIFFE:** https://spiffe.io/
- **Bob's Brain Example:** This directory

---

## Questions?

- **Repository:** https://github.com/jeremylongshore/bobs-brain
- **Issues:** https://github.com/Agent-Card/ai-card/issues
- **Contact:** jeremy@intentsolutions.io

---

**Last Updated:** 2025-12-02
**Version:** 1.0
**Status:** Production-ready conversion guide
