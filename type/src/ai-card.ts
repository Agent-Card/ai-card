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
   * A globally unique identifier for the agent.
   * * **Recommendation:** We strongly recommend using a **Verifiable URI**, 
   * like a DID (`did:method:...`).
   * Using a verifiable format allows clients to cryptographically prove 
   * agent identity and ownership.
   * * Simple UUIDs or names are allowed but offer no trust guarantees.
   * **Constraint:** This MUST match the `trust.identity.id` field.
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
   * A URL to the agent's logo.
   * * **Security Note:** We strongly recommend using **Data URLs** (RFC 2397)
   * (e.g., "data:image/png;base64,...") to embed the image binary directly.
   * * While standard HTTP URLs ("https://...") are allowed, they are discouraged 
   * for enterprise/high-security environments because "dereferencing" (fetching) 
   * the URL can leak user IP addresses (tracking) and creates a dependency on 
   * external hosting uptime.
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
   * The agent's lifecycle stage.
   * Useful for registries to filter out experimental or deprecated agents.
   */
  maturity?: "preview" | "stable" | "deprecated";

  /**
   * A detached JWS compact serialization (<header>..<signature>) 
   * signing the canonical content of this card.
   * Used to cryptographically bind the card content to the `id` (DID).
   */
  signature?: string;

  /**
   * A map of interaction protocols this agent supports, keyed by protocol type.
   * e.g., { "a2a": { ... }, "mcp": { ... } }
   */
  services: Record<string, BaseService>;

  /**
   * An ISO 8601 timestamp of when the agent was first published.
   */
  createdAt: string; 

  /**
   * An ISO 8601 timestamp of when this **entire AI Card** was last modified.
   * This includes changes to common metadata OR any of the service definitions.
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
  identity: Identity;

  /**
   * The human-readable name of the publisher.
   */
  name: string;

  /**
   * A verifiable credential proving the publisher's identity.
   * Reuses the Attestation type to support both URLs and embedded tokens.
   */
  attestation?: Attestation;
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
  /**
   * A verifiable ID for the Agent.
   * This MUST match the root `id` of the card.
   */  
  identity: Identity;

  /**
   * A list of compliance or other attestations.
   */
  attestations?: Attestation[];

  /**
   * A URL to the agent's Privacy Policy.
   * Critical for registries to display data handling practices.
   */
  privacyPolicyUrl?: string;

  /**
   * A URL to the agent's Terms of Service.
   * Critical for establishing legal usage rights.
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
   * The type of attestation (e.g., "SOC2", "HIPAA", "CustomBadge").
   */
  type: string;

  /**
   * A URL to a verifiable credential (e.g., a JWT or PDF report).
   * Use this when the credential is large or hosted remotely.
   */
  credentialUrl?: string; 

  /**
   * The embedded, base64-encoded credential itself (e.g., a JWT).
   * Use this for self-contained attestations.
   */
  credentialValue?: string;
}
// --8<-- [end:Attestation]

// --8<-- [start:AgentEndpoint]
/**
 * Defines a physical access point for a service.
 */
export interface AgentEndpoint {
  /**
   * The full URL to the endpoint.
   */
  url: string;

  /**
   * Optional transport type identifier (e.g., "http", "grpc", "ws").
   * Helps clients choose the best endpoint without trying them all.
   */
  transport?: string;
}

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
   * For example, "Travel Agent A2A Endpoint".
   */
  name: string;

  /**
   * A list of endpoints where this service can be accessed.
   * This allows a single service definition (with one set of skills)
   * to be available over multiple transports (e.g., HTTP and WebSocket).
   */
  endpoints: AgentEndpoint[];

  /**
   * The authentication mechanism for this endpoint.
   * (Using 'any' for simplicity, can be similar to A2A SecurityScheme or OpenAPI).
   * Add here if we want to standardize authentication across all services. 
   * Otherwise, each protocol would define its own. 
   */
  authentication: any; 

  /**
   * An arbitrary JSON object for protocol-specific metadata.
   * The AI Card spec does not validate the contents of this, keeping the core schema clean.
   * Each specific service type will define its own structure for this field.
   * For A2A services, this would be the A2AProtocolSpecific type (replacing current AgentCard).
   */
  protocolSpecific: Record<string, any>; // The protocol-specific metadata
}
// --8<-- [end:BaseService]