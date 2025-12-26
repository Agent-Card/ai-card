// --8<-- [start:AICard]
/**
 * The unified AI Card object for a single AI Service (Agent or Tool).
 */
export interface AICard {
  /**
   * Declares the schema this card adheres to.
   * e.g., "https://a2a-protocol.org/ai-card/v1/schema.json"
   */
  $schema: string;

  /**
   * The version of the AI Card specification itself (e.g., "1.0").
   * Major.Minor version only.
   */
  specVersion: string;
  
  /**
   * The primary verifiable ID for the service (e.g., DID, SPIFFE, or stable URL).
   * This acts as the Subject of the card.
   */
  id: string; 

  /**
   * Optional hint for the identity type (e.g., "did", "spiffe").
   */
  identityType?: string;
  
  /**
   * A human-readable name for the service.
   */
  name: string;

  /**
   * A short, human-readable description of the service's purpose.
   */
  description: string;

  /**
   * A URL to the service's logo image. Data URLs (RFC 2397) are recommended.
   */
  logoUrl?: string;

  /**
   * A list of keywords to aid in discovery.
   */
  tags?: string[];

  /**
   * The lifecycle stage of the service.
   */
  maturity?: "preview" | "stable" | "deprecated";

  /**
   * Information about the entity (company or individual) that owns this service.
   */
  publisher: Publisher;

  /**
   * Holds security, compliance, and legal information.
   */
  trust?: Trust;
  
  /**
   * A detached JWS compact serialization signing the canonical content of this card.
   */
  signature?: string;

  /**
   * A map of all interaction protocols this service supports, keyed by protocol type (e.g. 'a2a', 'mcp').
   */
  protocols: Record<ProtocolType, ProtocolDetail[]>;

  /**
   * An ISO 8601 timestamp of when the service was first published.
   */
  createdAt: string; 

  /**
   * An ISO 8601 timestamp of when this entire AI Card document was last modified.
   */
  updatedAt: string; 

  /**
   * An open 'black box' for any other non-standard metadata.
   */
  metadata?: Record<string, any>;
}
// --8<-- [end:AICard]

// --- CORE COMPONENTS ---

// --8<-- [start:ProtocolType]
/**
 * The identifier for a supported protocol.
 * Supports standard protocols ("a2a", "mcp") and custom strings.
 * The `(string & {})` syntax preserves autocomplete for the known values
 * while allowing any other string.
 */
export type ProtocolType = "a2a" | "mcp" | (string & {});
// --8<-- [end:ProtocolType]

// --8<-- [start:Publisher]
/**
 * Defines the entity (company, individual) that published the service.
 */
export interface Publisher {
  /**
   * A verifiable ID for the publisher (e.g., DID).
   */
  id: string;

  /**
   * Optional hint for the publisher identity type.
   */
  identityType?: string;

  /**
   * The human-readable name of the publisher.
   */
  name: string;

  /**
   * Proof of the publisher's identity.
   */
  attestation?: Attestation;
}
// --8<-- [end:Publisher]

// --8<-- [start:Trust]
/**
 * Defines the security, identity, and compliance posture of the service.
 */
export interface Trust {
  /**
   * A list of compliance or other attestations.
   */
  attestations?: Attestation[];

  /**
   * A URL to the service's Privacy Policy.
   */
  privacyPolicyUrl?: string;

  /**
   * A URL to the service's Terms of Service.
   */
  termsOfServiceUrl?: string;  
}
// --8<-- [end:Trust]

// --8<-- [start:Attestation]
/**
 * A reference to a compliance or security proof.
 * Uses the "Reference Pattern" (URI + MediaType + Digest) to be format-agnostic.
 */
export interface Attestation {
  /**
   * The semantic type of the attestation (e.g., "SOC2-Type2", "HIPAA-Audit").
   */
  type: string;

  /**
   * The location of the credential.
   * Supports both remote locations (https://) and inline data (data://).
   */
  uri: string; 

  /**
   * The format of the credential file (e.g., "application/jwt", "application/pdf").
   * Allows the verifier to select the correct parser.
   */
  mediaType: string;

  /**
   * (Optional but Recommended) Cryptographic hash of the credential content.
   * e.g., "sha256:..."
   * Critical for remote URLs to ensure the file hasn't been swapped.
   */
  digest?: string;

  /**
   * (Optional) The size of the credential in bytes.
   * Useful for clients to decide whether to download large reports.
   */
  size?: number;

  /**
   * (Optional) A human-readable description of this attestation.
   * e.g., "2025 Annual Security Audit"
   */
  description?: string;
}
// --8<-- [end:Attestation]

// --8<-- [start:ProtocolDetail]
/**
 * The data structure containing specific configuration for a protocol (e.g., endpoints, auth schemes).
 */
export interface ProtocolDetail {
  /**
   * The protocol identifier (e.g., "a2a", "mcp"). Must match the key in the protocols map.
   */
  type: string;
  
  /**
   * A human-readable label for this interface.
   */
  name?: string;

  /**
   * The 'Black Box' for protocol-specific data (Endpoints, Auth, Skills). 
   * Validated by the protocol's own schema.
   */
  protocolSpecific: Record<string, any>; 
}
// --8<-- [end:ProtocolDetail]