/** 
 * This file acts as the lightweight "index" (catalog) file served from a host's well-known URL, 
 * which is /.well-known/ai-catalog.json.
 * Note this is the recommended binding for ** domain-based discovery **, but the AI Card format is 
 * transport-agnostic and intended to be served by SaaS Registry APIs as well.
 */

// --8<-- [start:HostInfo]
/**
 * Basic information about the host/registry publishing this catalog.
 */
export interface HostInfo {
  /**
   * The human-readable name of the host (e.g., "Acme Enterprise Registry").
   */
  name: string;

  /**
   * A verifiable ID for the host (e.g., a DID or domain).
   */
  id?: string;

  /**
   * A URL to the host's main documentation or landing page.
   */
  documentationUrl?: string;

  /**
   * A URL to the host's logo image.
   */
  logoUrl?: string;
}
// --8<-- [end:HostInfo]

// --8<-- [start:AIServiceEntry]
/**
 * A lightweight entry in the catalog, providing basic discovery
 * information and a link to the full AICard.
 */
export interface AIServiceEntry {
  /**
   * The primary verifiable ID for the AI Service.
   * This MUST match the `id` field in the linked `ai-card.json`.
   */
  id: string;
  
  /**
   * A human-readable name for the AI service.
   */
  name: string;

  /**
   * A short description of the AI service.
   */
  description: string;

  /**
   * A list of tags for filtering and discovery.
   */
  tags?: string[];
  
  /**
   * The full, absolute URL to this AI service's complete `ai-card.json` file.
   */
  cardUrl: string;

  /**
   * An ISO 8601 timestamp of when the referenced `ai-card.json` file 
   * was last modified.
   * Used by crawlers to determine if they need to re-fetch the full card.
   */
  updatedAt: string;
}
// --8<-- [end:ServiceEntry]

// --8<-- [start:AICatalog]
/**
 * Defines the structure for a host's master AI service catalog.
 * This file is expected to be at "/.well-known/ai-catalog.json".
 */
export interface AICatalog {
  /**
   * Declares the schema this catalog adheres to.
   * e.g., "https://ai-service-protocol.org/ai-catalog/v1/schema.json"
   */
  $schema: string;

  /**
   * The version of the AI Catalog specification itself (e.g., "1.0").
   */
  specVersion: string;
  
  /**
   * Information about the host/publisher of the entire catalog.
   */
  host: HostInfo;
  
  /**
   * An array of lightweight entries for all AI Services available on this host.
   */
  services: AIServiceEntry[];
}
// --8<-- [end:AICatalog]