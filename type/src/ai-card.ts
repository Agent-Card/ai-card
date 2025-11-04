// --8<-- [start:AICard]
/**
 * The unified AI Card object for a single agent.
 */
export interface AICard {
  /**
   * Declares the schema this card adheres to.
   * e.g., "https://ai-agent-protocol.org/ai-card/v1/schema.json"
   */
  $schema: string;

  /**
   * The version of the AI Card specification itself.
   */
  specVersion: string;
  
  /**
   * The primary verifiable ID for the agent (e.g., DID).
   */
  id: string; 
  
  /**
   * A human-readable name for the agent.
   */
  name: string;

  /**
   * A short, human-readable description of the agent's purpose.
   */
  description: string;

  /**
   * A direct URL to the agent's logo image.
   */
  logoUrl?: string;

  /**
   * A list of keywords to aid in discovery.
   */
  tags?: string[];

  /**
   * Information about the entity (company or individual) that published this agent.
   */
  publisher: Publisher;

  /**
   * Holds all trust, compliance, and identity information.
   */
  trust: Trust;
  
  /**
   * An array of all interaction protocols this agent supports.
   * This is the core of the extensibility model.
   */
  services: BaseService[];

  /**
   * An ISO 8601 timestamp of when the agent was first published.
   */
  createdAt: string; 

  /**
   * An ISO 8601 timestamp of when this card was last updated.
   */
  updatedAt: string; 

  /**
   * An open "black box" for any other non-standard metadata.
   */
  metadata?: Record<string, any>;
}
// --8<-- [end:AICard]

// --- CORE COMPONENTS ---

// --8<-- [start:Publisher]
/**
 * Defines the entity (company, individual) that published the agent.
 */
export interface Publisher {
  /**
   * A verifiable ID for the publisher, e.g., a DID or organization ID.
   */
  id: string;

  /**
   * The human-readable name of the publisher.
   */
  name: string;

  /**
   * A URL to a verifiable credential (e.g., JWT) proving the publisher's identity.
   */
  attestation?: string;
}
// --8<-- [end:Publisher]

// --8<-- [start:Identity]
/**
 * A verifiable identity for the agent or publisher.
 */
export interface Identity {
  /**
   * The type of identity (e.g., "did", "spiffe").
   */
  type: string;

  /**
   * The identity string itself.
   */
  id: string;
}
// --8<-- [end:Identity]

// --8<-- [start:Trust]
/**
 * Defines the security, identity, and compliance posture of the agent.
 */
export interface Trust {
  // NOTE: 'identity' and other fields can be added here later.
  
  /**
   * A list of compliance or other attestations.
   */
  attestations?: Attestation[];
}
// --8<-- [end:Trust]

// --8<-- [start:Attestation]
/**
 * A single compliance, security, or custom attestation.
 */
export interface Attestation {
  /**
   * The type of attestation (e.Go., "SOC2", "HIPAA", "CustomBadge").
   */
  type: string;

  /**
   * (Low-Trust) A URL to a simple JSON "badge" file.
   */
  badgeUrl?: string; 

  /**
   * (High-Trust) A URL to a verifiable credential (e.g., a JWT or PDF report).
   * Use this when the credential is large or hosted remotely.
   */
  credentialUrl?: string; 

  /**
   * (High-Trust) The embedded, base64-encoded credential itself (e.g., a JWT).
   * Use this for self-contained attestations (no extra network call).
   */
  credentialValue?: string;
}
// --8<-- [end:Attestation]

// --8<-- [start:BaseService]
/**
 * A generic representation of an interaction service.
 * All specific service types extend this.
 */
export interface BaseService {
  /**
   * A custom protocol identifier string (e.g., "a2a", "mcp", "foo").
   */
  type: string;
  
  /**
   * A human-readable name for this specific service endpoint.
   */
  name: string;

  /**
   * The full URL to the service endpoint.
   */
  endpoint: string;

  /**
   * The authentication mechanism for this endpoint.
   * (Using 'any' for simplicity, can be similar to A2A SecurityScheme).
   * Add here if we want to standardize authentication across all services. 
   * Otherwise, each protocol would define its own. 
   */
  authentication: any; 

  /**
   * An arbitrary JSON object for protocol-specific data.
   * The AI Card spec does not validate the contents of this, so we keep core schema clean.
   * Each specific service type will define its own structure for this field.
   */
  protocolSpecific: Record<string, any>; // The "black box" for protocol-specific data
}
// --8<-- [end:BaseService]
