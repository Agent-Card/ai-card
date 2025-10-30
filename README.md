# Common AI Card and Registry Standard
Co-Authors: [ToddSegal](https://github.com/ToddSegal), [David Soria Parra](https://github.com/dsp-ant) 

## tl;dr;
A2A and MCP are collaborating on a common AI card standard to benefit the AI Service Ecosystem. 

Contact us via GitHub Discussions, [Issues](https://github.com/Agent-Card/ai-card/issues), and [Pull Requests](https://github.com/Agent-Card/ai-card/pulls). 

## What problem are we solving?
There are multiple evolving standards for communication protocols between AI clients and servers. While these protocols differ in capabilities and technical architecture, there are common ecosystem needs for producers and consumers of services built on top of them. This includes discovery, verifiable metadata, and trusted identity standards. 

Without a common discovery standard, we see duplicative and incompatible efforts in the ecosystem, such as registry, marketplace, identity providers, UI and payments extensions, and others. This increases complexity, risk of vulnerabilities, and harms interop within the developer community. 

## What are we doing?
In this repo, we will establish a new open standard for creating, discovering, securing, and serving AI service metadata called an **AI Card**. This will be immediately adopted as the metadata solution of choice for MCP and A2A. Other protocols are encouraged to adopt this standard as well. 

*Important Note:* The **AI card** standard does not change the underlying protocol architecture. 

### Guiding Requirements

#### Core AI Card Features
The project will define a schema for a secure, tamper-resistant AI Card that includes 

* **Common server metadata** (such as publishing company, links to documentation, description, icon, server version, etc)
* **Verifiable metadata** (such as accreditations, certifications, reputational scores, badges, etc)
* **Identity metadata** (such as DID or SPIFFE)
* **Custom metadata** (used by individual producers or consumers for their own needs)

#### AI Protocol Services
AI Card will include `services` information indicating which AI protocols the server supports, their network addresses, and protocol-specific extension metadata such as capabilities. 

For example, an AI Card that supports MCP, A2A, and a custom “Foo” protocol, would have entries for each of MCP, A2A, and Foo. Each entry would contain their own specific metadata (such as “MCP tools” or “A2A skills”). 

This protocol-specific metadata would NOT be part of the AI Card spec. 

#### Static Discovery
As part of the specification, this project would define a standard for how a server can make an individual card, and a catalog of cards, available at a well-known URL for a given domain (e.g. at `./well-known/ai-card.json`). 

Individual protocols may support dynamic card generation and discovery through their own methods (for example, to provide different card content based on a caller’s identity). This is out of scope for the AI Card standard. 

#### Common Registry Standard

The AI Card project should also define a common “AI Card Registry” standard that provides a standard interface for clients to interact (query, search, CRUDL) with collections of cards. 

### Proposed Mechanics

#### Governance
This is a temporary working repo maintained by the Linux Foundation. Proposals and changes will be made in the public in this repo. 

This project will be moved to a permanent location a later date with a permanent governance model. 

#### Adoption
When the specification is finalized, A2A and MCP plan to both, immediately, adopt the AI Card standard. This would replace existing protocol specific cards (“A2A Agent Card”, “MCP Server Card”). 

Protocol-specific cards would be standardized as a common AI Card structure, with protocol-specific properties available in services as noted earlier. 

#### Ecosystem
MCP and A2A steering committees will recommend duplicative card-adjacent efforts like “Registry”, “Agent Identity”, etc consolidate. 


