The lightweighted AI Catalog for: /.well-known/ai-catalog.json

The Client's Workflow
 - Client: "What agents does api.acme-corp.com have?"
 - GET /.well-known/ai-catalog.json
 - Client: "Got the list. I see two agents. I want to use the 'Acme Finance Agent'."
 - (Parses the cardUrl from the catalog): https://api.acme-corp.com/agents/finance-agent/ai-card.json
 - GET /agents/finance-agent/ai-card.json
 - Client: "Got the full AI Card. Now I can see its A2A/MCP endpoints and its trust information."

```json
{
  "$schema": "https://a2a-protocol.org/ai-catalog/v1/schema.json",
  "specVersion": "1.0.0",
  "host": {
    "name": "Acme Services Inc.",
    "id": "did:example:org-acme-corp"
  },
  "agents": [
    {
      "id": "did:example:agent-finance-001",
      "name": "Acme Finance Agent",
      "description": "An agent for executing stock trades.",
      "tags": ["finance", "stocks"],
      "cardUrl": "https://api.acme-corp.com/agents/finance-agent/ai-card.json"
    },
    {
      "id": "did:example:agent-weather-002",
      "name": "Acme Weather Agent",
      "description": "Provides real-time weather forecasts.",
      "tags": ["weather", "forecast"],
      "cardUrl": "https://api.acme-corp.com/agents/weather-agent/ai-card.json"
    }
  ]
}
```