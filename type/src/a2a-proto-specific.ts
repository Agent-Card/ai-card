/**
 * We copied here for illustration purposes only 
 * == It's the same AgentCard in A2A Spec (or we can remove some fields since it's covered in AI card) ==
 * Defines the protocol-specific metadata payload for an A2A service.
 * This is referenced in the A2AService interface's 'protocolSpecific' field.
 * Here we only copied some fields from the A2A Agent Spec as example.
 */
export interface A2AProtocolSpecific {
  /**
   * The version of the A2A protocol this agent supports.
   * @default "0.3.0"
   */
  protocolVersion: string;
  /**
   * A human-readable name for the agent.
   *
   * @TJS-examples ["Recipe Agent"]
   */
  name: string;
  /**
   * A human-readable description of the agent, assisting users and other agents
   * in understanding its purpose.
   *
   * @TJS-examples ["Agent that helps users with recipes and cooking."]
   */
  description: string;
  /**
   * The preferred endpoint URL for interacting with the agent.
   * This URL MUST support the transport specified by 'preferredTransport'.
   *
   * @TJS-examples ["https://api.example.com/a2a/v1"]
   */
  url: string;
  

  /** An optional URL to an icon for the agent. */
  iconUrl?: string;
  /**
   * The agent's own version number. The format is defined by the provider.
   *
   * @TJS-examples ["1.0.0"]
   */
  version: string;
  /** An optional URL to the agent's documentation. */
  documentationUrl?: string;
  /**
   * A list of security requirement objects that apply to all agent interactions. Each object
   * lists security schemes that can be used. Follows the OpenAPI 3.0 Security Requirement Object.
   * This list can be seen as an OR of ANDs. Each object in the list describes one possible
   * set of security requirements that must be present on a request. This allows specifying,
   * for example, "callers must either use OAuth OR an API Key AND mTLS."
   *
   * @TJS-examples [[{"oauth": ["read"]}, {"api-key": [], "mtls": []}]]
   */
  security?: { [scheme: string]: string[] }[];
  /**
   * Default set of supported input MIME types for all skills, which can be
   * overridden on a per-skill basis.
   */
  defaultInputModes: string[];
  /**
   * Default set of supported output MIME types for all skills, which can be
   * overridden on a per-skill basis.
   */
  defaultOutputModes: string[];
  /**
   * If true, the agent can provide an extended agent card with additional details
   * to authenticated users. Defaults to false.
   */
  supportsAuthenticatedExtendedCard?: boolean;
}