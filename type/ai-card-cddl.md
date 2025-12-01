### AI Card Specification in CDDL format
```ini
; ============================================================================
; AI Card Specification (v1)
; A unified metadata format for AI Agents
; ============================================================================

AICard = {
  $schema: text,              ; URI to the JSON schema (e.g. "https://...")
  specVersion: text,          ; Major.Minor version (e.g. "1.0")
  
  ; --- Identity (Subject) ---
  id: text,                   ; The Primary Key / Subject of this card (DID, SPIFFE, or URL)
  ? identityType: text,       ; Type hint (e.g. "did", "spiffe"). Optional if clear from ID.

  ; --- Metadata ---
  name: text,                 ; Human-readable name for the agent
  description: text,          ; Short description of the agent's purpose
  ? logoUrl: text,            ; URL to logo. Data URL (RFC 2397) recommended for privacy
  ? tags: [* text],           ; List of keywords to aid in discovery
  ? maturity: MaturityLevel,  ; Lifecycle stage of the agent
  ; --- Ownership & Trust ---
  publisher: Publisher,       ; Information about the entity that owns this agent
  trust: Trust,               ; Security and compliance proofs
  ? signature: text,          ; Detached JWS signing the card content
  
  ; --- Protocols ---
  ; Map of supported protocols (e.g. "a2a" => Service, "mcp" => Service)
  services: { * ServiceType => BaseService }, 

  ; --- Housekeeping ---
  createdAt: tdate,           ; ISO 8601 Date when the agent was created
  updatedAt: tdate,           ; ISO 8601 Date when this card was last modified
  ? metadata: { * text => any } ; Open slot for custom/non-standard metadata
}

; Enum for maturity
MaturityLevel = "preview" / "stable" / "deprecated"

; Service type choices (Standard + Custom)
ServiceType = "mcp" / "a2a" / text

; --- Core Components ---

Publisher = {
  id: text,                   ; Verifiable ID of the publisher organization
  ? identityType: text,       ; Type hint (e.g. "did", "dns")
  name: text,                 ; Human-readable name of the publisher
  ? attestation: Attestation  ; Proof of the publisher's identity
}

Trust = {
  ; Identity is now implicit (matches Root id)
  ? attestations: [* Attestation], ; List of compliance credentials (SOC2, HIPAA, etc.)
  ? privacyPolicyUrl: text,   ; URL to the privacy policy
  ? termsOfServiceUrl: text   ; URL to the terms of service
}

Attestation = {
  type: text,                 ; Type of proof (e.g. "SOC2-Type2", "HIPAA-Audit")
  
  ; Verifiable credentials (High-Trust)
  ? credentialUrl: text,      ; Remote URL to a signed credential (e.g. JWT/PDF)
  ? credentialValue: text     ; Embedded base64-encoded credential (e.g. JWT)
}

; --- Interaction Services ---

BaseService = {
  type: ServiceType,          ; Protocol ID (matches key in services map)
  ? name: text,               ; Human-readable label (e.g. "Primary Interface")
  
  ; The "Black Box" for protocol-specific data
  ; Endpoints, Auth, and Skills are defined INSIDE here by the protocol spec.
  protocolSpecific: { * text => any } 
}
```