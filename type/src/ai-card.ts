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
  services: (
    | A2AService   // For A2A
    | MCPService   // For MCP 
    | CustomService // For "Custom/Foo" protocol
  )[];

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

// --- DEFINITION TO INTERACTION SERVICES ---
// We don't need to change core ai-card schema for adding or editing or removing the specific interaction service protocols.
// Instead, we define each interaction protocol as a separate "service" type that extends a common base.
// This allows us to add new protocols in the future without changing the core schema.

// --8<-- [start:BaseService]
/**
 * A generic representation of an interaction service.
 * All specific service types extend this.
 */
export interface BaseService {
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
   * (Using 'any' for simplicity, can be typed to OpenAPI SecurityScheme later).
   */
  authentication: any; 
}
// --8<-- [end:BaseService]

// --8<-- [start:A2AService]
/**
 * Defines the service entry for an A2A-compliant agent.
 */
export interface A2AService extends BaseService {
  /**
   * The protocol type identifier. Must be "a2a".
   */
  type: "a2a";

  /**
   * A "black box" object containing all A2A-specific data.
   */
  protocolSpecific: A2AProtocolSpecific;
}
// --8<-- [end:A2AService]

// --8<-- [start:MCPService]
/**
 * Defines the service entry for an MCP-compliant agent.
 */
export interface MCPService extends BaseService {
  /**
   * The protocol type identifier. Must be "mcp".
   */
  type: "mcp";

  /**
   * A "black box" object containing all MCP-specific data.
   */
  protocolSpecific: MCPProtocolSpecific;
}
// --8<-- [end:MCPService]

// --8<-- [start:CustomService]
/**
 * Defines the service entry for any custom "Foo" protocol.
 * The 'type' string is custom.
 */
export interface CustomService extends BaseService {
  /**
   * A custom protocol identifier string (e.g., "foo", "my-protocol").
   */
  type: string; 

  /**
   * An arbitrary JSON object for any custom data.
   */
  protocolSpecific: Record<string, any>; 
}
// --8<-- [end:CustomService]

// --- PROTOCOL-SPECIFIC PAYLOADS ---

// --8<-- [start:A2AProtocolSpecific]
/**
 * Protocol-specific payload for an A2A service.
 * The AI Card spec does not validate the contents of this.
 */
export interface A2AProtocolSpecific {
  /**
   * The version of the A2A protocol this endpoint supports.
   */
  protocolVersion: string;
  
  // More A2A specific fields to be defined later
  // (e.g., skills, capabilities, preferredTransport)
}
// --8<-- [end:A2AProtocolSpecific]

// --8<-- [start:MCPProtocolSpecific]
/**
 * Protocol-specific payload for an MCP service.
 * The AI Card spec does not validate the contents of this.
 */
export interface MCPProtocolSpecific {
  /**
   * The version of the MCP protocol this endpoint supports.
   */
  protocolVersion: string;

  // More MCP specific fields to be defined later
  // (e.g., capabilities, supportedModels)
}
// --8<-- [end:MCPProtocolSpecific]