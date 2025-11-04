Here is an example `ai-card.json` file that defines a single **"Stock Trading Agent"** which provides its functions over both A2A and MCP.

Notice here the top-level `name` is for the agent, and the `name` field *inside* each service is just a label for that specific protocol interface.

```json
{
  "$schema": "https://a2a-protocol.org/ai-card/v1/schema.json",
  "specVersion": "1.0.0",
  "id": "did:example:agent-stock-trader-9a",
  "name": "Stock Trading Agent",
  "description": "Helps with stock trading to find best stocks. This agent is available over A2A and MCP.",
  "logoUrl": "https://www.acme-finance.com/images/stock-agent.png",
  "tags": ["finance", "stocks", "trading", "a2a", "mcp"],
  
  "publisher": {
    "id": "did:example:org-acme-finance",
    "name": "Acme Financial Corp"
  },
  
  "trust": {
    "attestations": [
      {
        "type": "SOC2-Type2",
        "description": "Annual SOC 2 Type II Report",
        "credentialUrl": "https://trust.acme-finance.com/reports/soc2-latest.pdf"
      }
    ]
  },
  
  "services": [
    {
      "name": "Stock Trading Agent (A2A Interface)",
      "endpoint": "https://api.acme-finance.com/a2a/v1",
      "type": "a2a",
      "authentication": {
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
      },
      "protocolSpecific": {
        "protocolVersion": "0.3.0",
        "skills": [
          { "name": "getStockQuote" },
          { "name": "executeTrade" }
        ]
      }
    },
    {
      "name": "Stock Trading Agent (MCP Interface)",
      "endpoint": "https://api.acme-finance.com/mcp/v1",
      "type": "mcp",
      "authentication": {
        "type": "oauth2",
        "flows": {
          "clientCredentials": {
            "tokenUrl": "https://auth.acme-finance.com/token",
            "scopes": { "tools:call": "Allows calling MCP tools" }
          }
        }
      },
      "protocolSpecific": {
        "protocolVersion": "2025-06-18",
        "capabilities": {
          "serverFeatures": ["tools"],
          "tools": [
            { "name": "getStockQuote" },
            { "name": "executeTrade" }
          ]
        }
      }
    }
  ],
  
  "createdAt": "2025-01-20T10:00:00Z",
  "updatedAt": "2025-11-01T15:00:00Z"
}
```