### AI Card Specification in CDDL format
```ini
; ============================================================================
; AI Card Specification (v1)
; A unified metadata format for AI Services (Agents/Tools)
; ============================================================================

AICard = {
  $schema: text,              ; URI to the JSON schema (e.g. "https://...")
  specVersion: text,          ; Major.Minor version (e.g. "1.0")
  
  identifier: text,           ; agent global unqiue identifier in URN format (see: https://github.com/Agent-Card/ai-card/pull/18)
  ; --- Metadata ---
  displayName: text,                 ; Human-readable name for the AI service
  description: text,          ; Short description of the AI service's purpose
  ? logoUrl: text,            ; URL to logo. Data URL (RFC 2397) recommended for privacy
  ? tags: [* text],           ; List of keywords to aid in discovery
  ? maturity: MaturityLevel,  ; Lifecycle stage of the AI service
  
  ; --- Ownership & Trust ---
  publisher: Publisher,       ; Information about the entity that owns this AI service
  ? trust: Trust,             ; Security and compliance proofs (Optional)
  ? signature: text,          ; Detached JWS signing the card content (Integrity)
  
  ; --- Protocols ---
  ; Map of supported protocol interfaces (e.g. "a2a" => Interface, "mcp" => Interface)
  protocols: { * ProtocolType => ProtocolDetail }, 

  ; --- Housekeeping ---
  createdAt: tdate,           ; ISO 8601 Date when the AI service was first created
  updatedAt: tdate,           ; ISO 8601 Date when this card was last modified
  ? metadata: { * text => any } ; Open slot for custom/non-standard metadata
}

MaturityLevel = "preview" / "stable" / "deprecated"
ProtocolType = "mcp" / "a2a" / text

; --- Core Components ---

Publisher = {
  id: text,                   ; Verifiable ID of the publisher organization
  name: text,                 ; Human-readable name of the publisher
  ? identityType: text,       ; Type hint (e.g. "did", "dns")
  ? attestation: Attestation  ; Proof of the publisher's identity
}

Trust = {
  ; --- Identity (Subject) ---
  identity: text,            ; The Primary Key / Subject of this card, Globally Unique URI (per RFC 3986), (DID, SPIFFE, or URL)
  ? identityType: text,      ; Type hint (e.g. "did", "spiffe"). Optional if clear from ID.

  ? trustSchema: TrustSchema, 
  ? attestations: [* Attestation], ; List of compliance credentials (SOC2, HIPAA, etc.)
  ? provenance: [* ProvenanceLink],
  ? privacyPolicyUrl: text,   ; URL to the privacy policy
  ? termsOfServiceUrl: text   ; URL to the terms of service
}

TrustSchema = {
  id: text,
  version: text,
  ? governanceUri: text,
  ? verificationMethods: [* text]
}

ProvenanceLink = {
  relation: text,
  sourceId: text,
  ? sourceDigest: text,
  ? registryUri: text,
  ? statementUri: text,
  ? signatureRef: text
}

Attestation = {
  type: text,                 ; Type of proof (e.g. "SOC2-Type2", "HIPAA-Audit")
  
  ; Reference Pattern (Generic for Remote or Inline)
  uri: text,                  ; remote location: "https://..." or inline "data:..."
  mediaType: text,            ; Format: "application/pdf", "application/jwt"
  
  ? digest: text,             ; Hash for integrity (e.g. "sha256:...")
  ? size: uint,               ; Size in bytes
  ? description: text         ; Human-readable label
}

; --- Interaction Protocol ---

ProtocolDetail = {
  type: ProtocolType,          ; Protocol ID (matches key in protocols map)
  ? name: text,               ; Human-readable label (e.g. "Fiance Agent A2A")
  
  ; The "Black Box" for protocol-specific data
  ; Endpoints, Auth, and Skills are defined INSIDE here by the protocol spec.
  protocolSpecific: { * text => any } 
}

```