### AI Catalog Specification in CDDL format
```ini
; ============================================================================
; AI Catalog Specification (v1)
; The "Index" file served at /.well-known/ai-catalog.json
; ============================================================================

AICatalog = {
  $schema: text,              ; URI to the JSON schema
  specVersion: text,          ; Version of the Catalog spec (e.g. "1.0.0")
  host: HostInfo,             ; Who runs this server/registry
  agents: [* AgentCatalogEntry] ; The list of available agents
}

HostInfo = {
  name: text,                 ; The human-readable name of the host (e.g., the company name)
  ? id: text,                 ; Host Identity (DID)
  ? documentationUrl: text,   ; A URL to the host's main documentation
  ? logoUrl: text             ; A URL to the host's logo
}

AgentCatalogEntry = {
  id: text,                   ; Must match the id in the linked AI Card
  name: text,                 ; Human-readable name for the AI Card
  description: text,          ; Short description
  ? tags: [* text],           ; A list of tags for filtering and discovery
  cardUrl: text,              ; URL to the full ai-card.json 
  updatedAt: tdate            ; Last modified time of the AI Card (for crawler optimization)
}
```