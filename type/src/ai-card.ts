// --8<-- [start:AICard]
/**
 * The unified AI Card object for a single agent.
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
   * The primary verifiable ID for the agent (e.g., DID, SPIFFE, or stable URL).
   * This acts as the Subject of the card.
   */
  id: string; 

  /**
   * Optional hint for the identity type (e.g., "did", "spiffe").
   */
  identityType?: string;
  
  /**
   * A human-readable name for the agent.
   */
  name: string;

  /**
   * A short, human-readable description of the agent's purpose.
   */
  description: string;

  /**
   * A URL to the agent's logo image. Data URLs (RFC 2397) are recommended.
   */
  logoUrl?: string;

  /**
   * A list of keywords to aid in discovery.
   */
  tags?: string[];

  /**
   * The lifecycle stage of the agent.
   */
  maturity?: "preview" | "stable" | "deprecated";

  /**
   * Information about the entity (company or individual) that owns this agent.
   */
  publisher: Publisher;

  /**
   * Holds security, compliance, and legal information.
   */
  trust: Trust;
  
  /**
   * A detached JWS compact serialization signing the canonical content of this card.
   */
  signature?: string;

  /**
   * A map of all interaction protocols this agent supports, keyed by protocol type (e.g. 'a2a', 'mcp').
   */
  services: Record<ServiceType, BaseService>;

  /**
   * An ISO 8601 timestamp of when the agent was first published.
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

// --8<-- [start:ServiceType]
/**
 * The protocol identifier for a service.
 * Supports standard protocols ("a2a", "mcp") and custom strings.
 * The `(string & {})` syntax preserves autocomplete for the known values
 * while allowing any other string.
 */
export type ServiceType = "a2a" | "mcp" | (string & {});
// --8<-- [end:ServiceType]

// --8<-- [start:Publisher]
/**
 * Defines the entity (company, individual) that published the agent.
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
 * Defines the security, identity, and compliance posture of the agent.
 */
export interface Trust {
  /**
   * A list of compliance or other attestations.
   */
  attestations?: Attestation[];

  /**
   * A URL to the agent's Privacy Policy.
   */
  privacyPolicyUrl?: string;

  /**
   * A URL to the agent's Terms of Service.
   */
  termsOfServiceUrl?: string;  
}
// --8<-- [end:Trust]

// --8<-- [start:Attestation]
/**
 * A single compliance, security, or custom attestation.
 */
export interface Attestation {
  /**
   * The type of attestation (e.g., "SOC2-Type2", "HIPAA-Audit").
   */
  type: string;

  /**
   * (High-Trust) A URL to a verifiable credential (e.g., a JWT or PDF report).
   */
  credentialUrl?: string; 

  /**
   * (High-Trust) The embedded, base64-encoded credential itself (e.g., a JWT).
   */
  credentialValue?: string;
}
// --8<-- [end:Attestation]

// --8<-- [start:BaseService]
/**
 * A generic wrapper for a specific protocol interface.
 */
export interface BaseService {
  /**
   * The protocol identifier (e.g., "a2a", "mcp"). Must match the key in the services map.
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
// --8<-- [end:BaseService]