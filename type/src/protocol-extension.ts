/**
 * This file is not part of the core spec. It's maintained by the protocol 
 * teams (A2A, MCP) to define what goes inside their protocolSpecific.
 * Slightly simplified version from the current A2A AgentCard and MCP Proposal types.
 */

// --8<-- [start:A2AProtocolSpecific]
/**
 * The payload for the 'protocolSpecific' field when type == "a2a".
 * This is defined and maintained by the A2A project.
 */
export interface A2AProtocolSpecific {
  /**
   * From A2A Spec: The version of the A2A protocol.
   */
  protocolVersion: string;

  /**
   * From A2A Spec: The preferred transport (e.g., "JSONRPC").
   */
  preferredTransport?: string;

  /**
   * From A2A Spec: List of alternative transports/URLs.
   */
  additionalInterfaces?: {
    transport: string;
    url: string;
  }[];
  
  /**
   * From A2A Spec: A2A-specific capabilities.
   */
  capabilities?: {
    supportsStreaming?: boolean;
    supportsPushNotifications?: boolean;
  };
  
  /**
   * From A2A Spec: The list of skills this agent provides.
   */
  skills: {
    name: string;
    description: string;
    inputSchema?: Record<string, any>;
  }[];
}
// --8<-- [end:A2AProtocolSpecific]

// --8<-- [start:MCPProtocolSpecific]
/**
 * The payload for the 'protocolSpecific' field when type == "mcp".
 * This is defined and maintained by the MCP project.
 */
export interface MCPProtocolSpecific {
  /**
   * From MCP Proposal: The version of the MCP protocol.
   */
  protocolVersion: string;

  /**
   * From MCP Proposal: The type of transport (e.g., "streamable-http").
   * The 'endpoint' is already in the BaseService.
   */
  transportType?: string;
  
  /**
   * From MCP Proposal: MCP-specific server capabilities.
   */
  capabilities: {
    tools?: { listChanged?: boolean };
    prompts?: { listChanged?: boolean };
    resources?: { subscribe?: boolean; listChanged?: boolean };
  };

  /**
   * From MCP Proposal: Required client capabilities.
   */
  requires?: {
    sampling?: object;
    roots?: object;
  };

  /**
   * From MCP Proposal: Static list of tools, or "dynamic".
   */
  tools: "dynamic" | {
    name: string;
    description: string;
    inputSchema?: Record<string, any>;
  }[];

  /**
   * From MCP Proposal: Static list of prompts, or "dynamic".
   */
  prompts: "dynamic" | { name: string; description: string }[];
  
  /**
   * From MCP Proposal: Static list of resources, or "dynamic".
   */
  resources: "dynamic" | { name: string; uri: string }[];
}
// --8<-- [end:MCPProtocolSpecific]