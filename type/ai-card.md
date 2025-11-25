### AI Card Specification in CDDL format
```ini
; ============================================================================
; AI Card Specification (v1)
; A unified metadata format for AI Agents
; ============================================================================

AICard = {
  $schema: text,              ; URI to the JSON schema
  specVersion: text,          ; e.g. "1.0.0"
  id: text,                   ; Globally unique ID (DID or stable URL). MUST match trust.identity.id
  name: text,                 ; Human-readable name
  description: text,          ; Short description
  ? logoUrl: text,            ; URL to logo (Data URI recommended)
  ? tags: [* text],           ; Discovery keywords
  ? maturity: MaturityLevel,  ; Lifecycle stage
  ? signature: text,          ; Detached JWS signing the card content
  publisher: Publisher,       ; Who owns this agent
  trust: Trust,               ; Security and Identity proofs
  
  ; Map of supported protocols (e.g. "a2a" => Service, "mcp" => Service)
  services: { * ServiceType => BaseService }, 

  createdAt: tdate,           ; ISO 8601 Date
  updatedAt: tdate,           ; ISO 8601 Date
  ? metadata: { * text => any } ; Extensible metadata bucket
}

; Enum for maturity
MaturityLevel = "preview" / "stable" / "deprecated"

; Service type choices (Standard + Custom)
ServiceType = "mcp" / "a2a" / text

; --- Core Components ---

Publisher = {
  identity: Identity,
  name: text,
  ? attestation: Attestation  ; Identity proof (e.g. verifying the DID)
}

Trust = {
  identity: Identity,         ; The Agent's Identity. MUST match root ID.
  ? attestations: [* Attestation], ; Compliance proofs (SOC2, HIPAA)
  ? privacyPolicyUrl: text,
  ? termsOfServiceUrl: text
}

Identity = {
  type: text,                 ; e.g. "did", "spiffe"
  id: text                    ; The identifier string
}

Attestation = {
  type: text,                 ; e.g. "SOC2-Type2", "HIPAA-Audit"
  ; Verifiable credentials
  ? credentialUrl: text,      ; Remote JWT/Report
  ? credentialValue: text     ; Embedded JWT/Proof
}

; --- Interaction Services ---

BaseService = {
  type: text,                 ; Protocol ID (e.g. "a2a", "mcp")
  name: text,                 ; Human-readable label for this interface  
  endpoints: [* AgentEndpoint],
  ? authentication: any,      ; Recommended: OpenAPI Security Scheme Object
  
  ; The "Black Box" for protocol-specific data
  ; Validated by the protocol's own schema (e.g. A2A or MCP schema)
  protocolSpecific: { * text => any } 
}

AgentEndpoint = {
  url: text,                  ; Full URL
  ? transport: text           ; e.g. "http", "ws", "grpc"
}
```