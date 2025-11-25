### AI Card Specification in CDDL format
```ini
; ============================================================================
; AI Card Specification (v1)
; A unified metadata format for AI Agents
; ============================================================================

AICard = {
  $schema: text,              ; URI to the JSON schema
  specVersion: text,          ; Version of the AI Card spec (e.g. "1.0.0")
  
  id: text,                   ; Globally unique ID (DID or stable URL). MUST match trust.identity.id
  name: text,                 ; Human-readable name for the agent
  description: text,          ; Short description of the agent's purpose
  
  ? logoUrl: text,            ; URL to logo. Data URLs (RFC 2397) are recommended for privacy
  ? tags: [* text],           ; List of keywords to aid in discovery
  
  ? maturity: MaturityLevel,  ; Lifecycle stage of the agent
  ? signature: text,          ; Detached JWS signing the card content
  
  publisher: Publisher,       ; Information about the entity that owns this agent
  trust: Trust,               ; Security, identity, and compliance proofs
  
  ; Map of supported protocols (e.g. "a2a" => Service, "mcp" => Service)
  services: { * ServiceType => BaseService }, 

  createdAt: tdate,           ; ISO 8601 Date when the agent was published
  updatedAt: tdate,           ; ISO 8601 Date when this card was last modified
  
  ? metadata: { * text => any } ; Open slot for custom/non-standard metadata
}

; Enum for maturity
MaturityLevel = "preview" / "stable" / "deprecated"

; Service type choices (Standard + Custom)
ServiceType = "mcp" / "a2a" / text

; --- Core Components ---

Publisher = {
  identity: Identity,         ; Verifiable ID of the publisher organization
  name: text,                 ; Human-readable name of the publisher
  ? attestation: Attestation  ; Proof of the publisher's identity
}

Trust = {
  identity: Identity,         ; The Agent's Identity. MUST match the root 'id'
  ? attestations: [* Attestation], ; List of compliance credentials (SOC2, HIPAA, etc.)
  ? privacyPolicyUrl: text,   ; URL to the privacy policy
  ? termsOfServiceUrl: text   ; URL to the terms of service
}

Identity = {
  type: text,                 ; Identity type (e.g. "did", "spiffe")
  id: text                    ; The identifier string itself
}

Attestation = {
  type: text,                 ; Type of proof (e.g. "SOC2-Type2", "HIPAA-Audit")
  
  ; Verifiable credentials (High-Trust)
  ? credentialUrl: text,      ; Remote URL to a signed credential (e.g. JWT/PDF)
  ? credentialValue: text     ; Embedded base64-encoded credential (e.g. JWT)
}

; --- Interaction Services ---

BaseService = {
  type: ServiceType,          ; Protocol ID (e.g. "a2a", "mcp"). Matches map key.
  name: text,                 ; Human-readable name for this specific interface
  
  endpoints: [* AgentEndpoint], ; List of physical access points
  
  ? authentication: any,      ; Recommended: OpenAPI Security Scheme Object
  
  ; The "Black Box" for protocol-specific data
  ; Validated by the protocol's own schema (e.g. A2A or MCP schema)
  protocolSpecific: { * text => any } 
}

AgentEndpoint = {
  url: text,                  ; The full URL to the endpoint
  ? transport: text           ; Transport hint (e.g. "http", "ws", "grpc")
}
```