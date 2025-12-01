Here is an example `ai-card.json` file that defines a single **"Stock Trading Agent"** which provides its functions over both A2A and MCP.

Notice here the top-level `name` is for the agent, and the `name` field *inside* each service is just a label for that specific protocol interface.

```json
{
  "$schema": "https://a2a-protocol.org/ai-card/v1/schema.json",
  "specVersion": "1.0",
  
  "id": "did:example:agent-finance-001",
  "identityType": "did",
  "name": "Acme Finance Agent",
  "description": "An agent for executing stock trades and getting market analysis via A2A and MCP.",
  "logoUrl": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iIzRjNTFnZiIgLz48L3N2Zz4=",
  "maturity": "stable",
  "signature": "eyJhbGciOiJFUzI1NiJ9..[detached-jws-signature]..",
  
  "publisher": {
    "id": "did:example:org-acme",
    "identityType": "did",
    "name": "Acme Financial Corp",
    "attestation": { 
      "type": "IdentityProof", 
      "credentialUrl": "https://trust.acme.com/identity.jwt" 
    }
  },
  
  "trust": {
    "attestations": [
      { 
        "type": "SOC2-Type2", 
        "credentialUrl": "https://trust.acme-finance.com/reports/soc2-latest.pdf" 
      },
      { 
        "type": "FINRA-Audit", 
        "credentialValue": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImZpbnJhLWtleS0xIn0.eyJpc3MiOiJodHRwczovL2F1ZGl0LmZpbnJhLm9yZyIsInN1YiI6ImRpZDpleGFtcGxlOmFnZW50LWZpbmFuY2UtMDAxIiwiZXhwIjoxNzYyMjM2MDAwLCJhdHRlc3RhdGlvbiI6eyJ0eXBlIjoiRklOUkEtQXVkaXQiLCJzdGF0dXMiOiJhY3RpdmUifX0.VGhpcy1pcy1hLXZlcnktc2FtcGxlLXNpZ25hdHVyZQ" 
      }
    ],
    "privacyPolicyUrl": "https://acme-finance.com/legal/privacy",
    "termsOfServiceUrl": "https://acme-finance.com/legal/terms"
  },
  
  "services": {
    "a2a": {
      "type": "a2a",
      "name": "Finance A2A Interface",
      "protocolSpecific": {
        "protocolVersion": "0.3.0",
        "supportedInterfaces": [
          {
            "transport": "JSONRPC",
            "url": "https://api.acme-finance.com/a2a/v1"
          }
        ],
        "securitySchemes": {
          "oauth2": {
            "type": "oauth2",
            "flows": {
              "clientCredentials": {
                "tokenUrl": "https://auth.acme-finance.com/token",
                "scopes": {
                  "stocks:read": "Allows getting stock quotes",
                  "stocks:write": "Allows executing trades"
                }
              }
            }
          }
        },
        "skills": [
          {
            "id": "skill-stock-analysis",
            "name": "Run Stock Analysis",
            "description": "Use the latest LLM based technology to run stock analysis and predictions.",
            "inputModes": ["application/json"],
            "outputModes": ["application/json", "text/markdown"],
            "tags": ["finance", "analysis", "prediction"]
          }
        ]
      }
    },
    "mcp": {
      "type": "mcp",
      "name": "Finance MCP Interface",
      "protocolSpecific": {
        "protocolVersion": "2025-06-18",
        "transport": {
          "type": "streamable-http",
          "endpoint": "https://api.acme-finance.com/mcp/v1"
        },
        "authentication": {
          "type": "oauth2",
          "required": true
        },
        "capabilities": {
          "tools": { "listChanged": true },
          "prompts": { "listChanged": true },
          "resources": { "subscribe": true }
        },
        "tools": "dynamic",
        "prompts": "dynamic",
        "resources": "dynamic"
      }
    }
  },
  
  "createdAt": "2025-01-20T10:00:00Z",
  "updatedAt": "2025-11-01T15:00:00Z",
  
  "metadata": {
    "region": "us-east-1"
  }
}
```