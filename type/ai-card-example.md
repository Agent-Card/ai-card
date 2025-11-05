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
  
  "publisher": {
    "id": "did:example:org-acme-finance",
    "name": "Acme Financial Corp",
    "attestation": "https://trust.acme-finance.com/publisher.jwt"
  },
  
  "trust": {
    "identity": {
      "type": "did",
      "id": "did:example:agent-finance-001"
    },
    "attestations": [
      {
        "type": "SOC2-Type2",
        "description": "Annual SOC 2 Type II Report (Confidential)",
        "credentialUrl": "https://trust.acme-finance.com/reports/soc2-latest.pdf"
      },
      {
        "type": "FINRA-Audit",
        "description": "FINRA Compliance Attestation (Embedded JWT)",
        "credentialValue": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImZpbnJhLWtleS0xIn0.eyJpc3MiOiJodHRwczovL2F1ZGl0LmZpbnJhLm9yZyIsInN1YiI6ImRpZDpleGFtcGxlOmFnZW50LWZpbmFuY2UtMDAxIiwiZXhwIjoxNzYyMjM2MDAwLCJhdHRlc3RhdGlvbiI6eyJ0eXBlIjoiRklOUkEtQXVkaXQiLCJzdGF0dXMiOiJhY3RpdmUifX0.VGhpcy1pcy1hLXZlcnktc2FtcGxlLXNpZ25hdHVyZQ"
      }
    ]
  },
  
  "services": [
    {
      "type": "a2a",
      "name": "Finance Agent (A2A Interface)",
      "endpoint": "https://api.acme-finance.com/a2a/v1",
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
            "id": "get-stock-analysis-prediction",
            "name": "run stock anaylysis and prediction",
            "description": "Use the latest LLM based technology to run stock analysis and precdictions",
            "tags": ["stock", "analysis", "prediction"],
            "examples": [
              "Run stock prediction for GOOG"
            ],
            "inputModes": ["application/json", "text/plain"],
            "outputModes": [
              "application/json",
              "text/html"
            ]
          },
        ]
      }
    },

    {
      "type": "mcp",
      "name": "MCP Interface",
      "endpoint": "https://api.example.com/mcp/v1",
      "authentication": {
        "type": "bearer",
        "scheme": "MCP-Custom-Auth"
      },
      "protocolSpecific": {
        "protocolVersion": "2025-06-18",
        "transport": "jsonrpc-http",
        "capabilities": {
          "serverFeatures": [
            "prompts",
            "resources",
            "tools"
          ],
          "clientFeatures": [
            "sampling"
          ],
          "supportedModels": [
            "acme-finance-model-v3"
          ]
        }
      }
    },
  ],  
  "createdAt": "2025-01-20T10:00:00Z",
  "updatedAt": "2025-11-01T15:00:00Z",
  
  "metadata": {
    "region": "us-east-1"
  }
}
```