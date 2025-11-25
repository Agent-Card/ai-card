Here is an example `ai-card.json` file that defines a single **"Stock Trading Agent"** which provides its functions over both A2A and MCP.

Notice here the top-level `name` is for the agent, and the `name` field *inside* each service is just a label for that specific protocol interface.

```json
{
  "$schema": "https://a2a-protocol.org/ai-card/v1/schema.json",
  "specVersion": "1.0.0",
  "id": "did:example:agent-finance-001",
  "name": "Acme Finance Agent",
  "description": "An agent for executing stock trades and getting market analysis. Available via A2A and MCP.",
  "logoUrl": "https://www.acme-finance.com/images/agent-logo.png",
  "tags": ["finance", "stocks", "trading", "a2a", "mcp"],
  "maturity": "stable",
  "signature": "eyJhbGciOiJFUzI1NiJ9..[detached-jws-signature]..",
  
  "publisher": {
    "name": "Acme Financial Corp",
    "identity": {
      "type": "did",
      "id": "did:example:org-acme-finance"
    },
    "attestation": {
      "type": "IdentityProof",
      "credentialUrl": "https://trust.acme.com/identity.jwt"
    }    
  },
  
  "trust": {
    "identity": {
      "type": "did",
      "id": "did:example:agent-finance-001"
    },
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
      "name": "Finance Agent (A2A Interface)",
      "endpoints": [
        {
          "url": "https://api.acme-finance.com/a2a/v1",
          "transport": "http"
        }
      ],
      "authentication": {
        "type": "oauth2",
        "description": "OAuth 2.0 Client Credentials Flow",
        "flows": {
          "clientCredentials": {
            "tokenUrl": "https://auth.acme-finance.com/token",
            "scopes": {
              "stocks:read": "Allows getting stock quotes",
              "stocks:write": "Allows executing trades"
            }
          }
        }
      },
      "protocolSpecific": {
        "protocolVersion": "0.3.0",
        "preferredTransport": "JSONRPC",
        "capabilities": {
          "supportsStreaming": true,
          "supportsPushNotifications": false
        },
        "skills": [
          {
            "name": "runStockAnalysisAndPrediction",
            "description": "Use the latest LLM based technology to run stock analysis and predictions",
            "inputSchema": {
              "type": "object",
              "properties": {
                "symbol": { "type": "string" }
              }
            }
          }
        ]
      }
    },
    "mcp": {
      "type": "mcp",
      "name": "Finance Agent (MCP Interface)",
      "endpoints": [
        {
          "url": "https://api.acme-finance.com/mcp/v1",
          "transport": "http"
        }
      ],
      "authentication": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
      },
      "protocolSpecific": {
        "protocolVersions": ["2025-06-18", "2025-09-19"],
        "transportType": "streamable-http",
        "capabilities": {
          "tools": { "listChanged": true },
          "prompts": { "listChanged": true },
          "resources": { "subscribe": true }
        },
        "requires": {
          "sampling": {}
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