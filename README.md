# **Common AI Card and Registry Standard**

Co-Authors: [ToddSegal](https://github.com/ToddSegal), [David Soria Parra](https://github.com/dsp-ant)

## tl;dr

Members from various AI Protocols (MCP, A2A) are collaborating on a common AI card standard to benefit the AI Service Ecosystem.

Contact us via GitHub Discussions, [Issues](https://github.com/Agent-Card/ai-card/issues), and [Pull Requests](https://github.com/Agent-Card/ai-card/pulls).

## **What problem are we solving?**

There are multiple evolving standards for communication protocols between AI clients and servers. While these protocols differ in capabilities and technical architecture, there are common ecosystem needs for producers and consumers of services built on top of them. This includes discovery, verifiable metadata, and trusted identity standards.

Without a common discovery standard, we see duplicative and incompatible efforts in the ecosystem, such as registry, marketplace, identity providers, UI and payments extensions, and others. This increases complexity, risk of vulnerabilities, and harms interop within the developer community.

## **What are we doing?**

In this repo, we will establish a new open standard for creating, discovering, securing, and serving AI service metadata called an **AI Card**. This standard will be proposed to be adopted by A2A and MCP following their standard governance processes. Other protocols are encouraged to adopt this standard as well.

**Important Note:** The AI Card standard does not change the underlying protocol architecture.

## **Terminology & Scope**

To avoid ambiguity between the "Agent" (the logical entity) and the "Server" (the infrastructure), this specification uses the following definitions:

* **Host:** The infrastructure or domain (e.g., api.example.com) that hosts the services.  
* **AI Service:** The logical entity (often called an "Agent" or "Tool") that implements protocols like MCP or A2A or others.  
* **Protocol Interface:** The specific protocol endpoint exposed by an AI Service (e.g., an "MCP" interface or "A2A" interface).

This repository defines two distinct specifications to address different scopes:

1. **AICard (Identity & Capabilities):** The metadata for a **single AI Service**. It binds a verifiable identity (DID) to its capabilities, security proofs, and protocol interfaces.  
   * *Analogy:* A **Digital Passport**. It belongs to one specific entity and travels with them.  
2. **AICatalog (Discovery):** A lightweight inventory of all AI Services available on a specific **Host**.  
   * *Analogy:* A **Building Directory**. It lists who is in the building today.

## **Guiding Requirements**

### **Core AI Card Features**

The project will define a schema for a secure, tamper-resistant AICard. This schema flattens identity for simplicity while reserving space for high-trust verification. Key components include:

* **Identity:** A globally unique, verifiable identifier (e.g., DID) for the AI Service.  
* **Publisher:** Identity information for the organization or individual that owns the service.  
* **Trust** & **Compliance:** A dedicated section for verifiable credentials (e.g., SOC 2 reports, HIPAA attestations, JWTs) and legal policies (Privacy, Terms of Service).  
* **Interfaces (Protocol Support):** A map of supported protocols (e.g., a2a, mcp). Each entry contains the protocol-specific payload required to connect.  
* **Lifecycle:** Metadata for versioning and maturity status (preview, stable, deprecated).

### **AI Protocol Services (The "Wrapper" Model)**

The AICard acts as a standardized envelope for protocol-specific metadata.

For example, an AI Card that supports MCP, A2A, and a custom “Foo” protocol, would have entries for each of MCP, A2A, and Foo. Each entry would contain their own specific metadata (such as “MCP tools” or “A2A skills”).

This protocol-specific metadata would NOT be part of the AI Card spec. As noted earlier, the card standard will also allow for arbitrary custom data to be defined by a producer.

This architecture allows a single Identity to be interoperable across multiple ecosystems without modifying the core AI Card specification.

### **Static Discovery**

The standard supports both decentralized and centralized discovery patterns:

* **Decentralized:** Hosts can publish a static catalog at /.well-known/ai-catalog.json which links to individual ai-card.json files.  
* **Centralized:** SaaS platforms and Registries can serve these same JSON structures via their own API endpoints.

### **Common Registry Standard**

The AI Card project should also define a common AI Card Registry standard that provides a universal interface for clients to interact (query, search, CRUDL) with AI card collections.

## **Proposed Mechanics**

### **Governance**

This is a temporary working repo maintained by the Linux Foundation. Proposals and changes will be made in public in this repo.

This project will be moved to a permanent location a later date with a permanent governance model.

### **Adoption**

When the specification is finalized, A2A and MCP steering committees will vote on adoption of the AI Card standard, potentially replacing existing protocol-specific standards or proposals.

Protocol-specific cards would be standardized as a common AI Card structure, with protocol-specific properties available in services as noted earlier.

### **Ecosystem**

If adopted, MCP and A2A steering committees will recommend duplicative card-adjacent efforts be consolidated, such as Registry, Agent Identity, and others.