
/** 
 * This file acts as the lightweight "index" (catalog) file served from a host's well-known URL, 
 * which is /.well-known/ai-catalog.json.
 * Note this is the recommended binding for ** domain-based discovery **, but the AI Card format is 
 * transport-agnostic and intended to be served by SaaS Registry APIs as well.
 */

// --8<-- [start:HostInfo]
/**
 * Basic information about the host of the catalog.
 */
export interface HostInfo {
  /**
   * The human-readable name of the host (e.g., the company name).
   */
  name: string;

  /**
   * A verifiable ID for the host (e.g., a DID).
   */
  id?: string;

  /**
   * A URL to the host's main documentation.
   */
  documentationUrl?: string;

  /**
   * A URL to the host's logo.
   */
  logoUrl?: string;
}
// --8<-- [end:HostInfo]

// --8<-- [start:AgentEntry]
/**
 * A lightweight entry in the catalog, providing basic discovery
 * information and a link to the full AI Card.
 */
export interface AgentEntry {
  /**
   * The primary verifiable ID for the agent (e.g., DID).
   * This MUST match the 'id' in the full AICard.
   */
  id: string;
  
  /**
   * A human-readable name for the agent.
   */
  name: string;

  /**
   * A short description of the agent.
   */
  description: string;

  /**
   * A list of tags for filtering and discovery.
   */
  tags?: string[];
  
  /**
   * The full, absolute URL to this agent's complete ai-card.json file.
   */
  cardUrl: string;

  /**
   * An ISO 8601 timestamp of when the referenced `ai-card.json` file 
   * was last modified.
   * Used by crawlers to determine if they need to re-fetch the full card.
   */
  updatedAt: string;  
}
// --8<-- [end:AgentEntry]

// --8<-- [start:AICatalog]
/**
 * Defines the structure for a host's master agent catalog.
 * This file is expected to be at "/.well-known/ai-catalog.json".
 */
export interface AICatalog {
  /**
   * Declares the schema this catalog adheres to.
   */
  $schema: string;

  /**
   * The version of the AI Catalog specification itself.
   */
  specVersion: string;
  
  /**
   * Information about the host/publisher of the entire catalog.
   */
  host: HostInfo;
  
  /**
   * An array of lightweight entries for all agents on this host.
   */
  agents: AgentEntry[];
}
// --8<-- [end:AICatalog]