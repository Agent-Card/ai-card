# Bob's Brain - AI Card Reference Implementation

**Status:** Production-grade multi-agent system  
**Tech Stack:** Google ADK 1.18.0, Vertex AI Agent Engine, A2A Protocol 0.3.0  
**Repository:** https://github.com/jeremylongshore/bobs-brain

---

## Overview

Bob's Brain is a **production-grade ADK agent department** that demonstrates comprehensive implementation of both:
- **A2A Protocol 0.3.0** (current AgentCard format)  
- **AI Card Standard v1.0** (new universal format)

This directory contains reference examples showing how to convert existing A2A AgentCards to the new universal AI Card format while maintaining backward compatibility.

---

## What Makes Bob's Brain Notable

### Multi-Agent Architecture
- **1 global orchestrator** (bob) coordinating specialist departments
- **1 foreman agent** (iam-senior-adk-devops-lead) managing department tasks
- **8 specialist agents** (iam-adk, iam-issue, iam-fix-plan, iam-fix-impl, iam-qa, iam-docs, iam-cleanup, iam-index)

### Production Patterns Demonstrated
- ✅ **Hard Mode Rules (R1-R8)** - CI-enforced architectural standards preventing drift
- ✅ **Inline Source Deployment** - Deploy source code directly to Agent Engine (no pickle serialization)
- ✅ **Dual Memory Architecture** - Session Cache + Memory Bank for real agent continuity
- ✅ **A2A Protocol** - Full AgentCard implementation with foreman-worker pattern
- ✅ **SPIFFE Identity** - Immutable identity framework for clean tracing
- ✅ **Workload Identity Federation** - Keyless CI/CD authentication
- ✅ **ARV Gates** - Agent Readiness Verification in deployment pipeline
- ✅ **Comprehensive CI/CD** - 8 GitHub Actions workflows with drift detection

### Standards-Based Documentation
- **141 organized docs** in `000-docs/` following Document Filing System v3.0
- **28 canonical standards** (6767-series) reusable across repos
- **Complete DevOps playbook** generated via `/appaudit` analysis
- **20+ operational guides** for deployment, monitoring, troubleshooting

---

## Files in This Directory

### 1. `ai-card.json` - New Universal AI Card Format (v1.0)
The AI Card standard format showing:
- SPIFFE ID as primary identity
- Trust attestations (Hard Mode compliance, CI/CD gates, WIF auth)
- A2A protocol service with complete skill definitions
- Publisher information and metadata

### 2. `agent-card-a2a.json` - Original A2A AgentCard Format (v0.3.0)
Current A2A protocol AgentCard for comparison showing:
- Protocol version 0.3.0
- Skills with input/output schemas
- SPIFFE identity propagation
- Transport preferences

### 3. `conversion-guide.md` - Migration Guide
Step-by-step guide for converting A2A AgentCards to AI Card format including:
- Field mapping reference
- Identity migration (SPIFFE)
- Service configuration
- Trust attestation examples

---

## Key Implementation Details

### SPIFFE Identity Pattern
```
spiffe://intent.solutions/agent/bobs-brain/prod/us-central1/0.12.0
         └─ trust domain ─┘ └─ workload path (agent/name/env/region/version) ┘
```

### Hard Mode Rules (R1-R8)
1. **R1: ADK-Only** - No LangChain, CrewAI, or mixed frameworks
2. **R2: Agent Engine Runtime** - Vertex AI managed runtime only
3. **R3: Gateway Separation** - Cloud Run proxies, no embedded runners
4. **R4: CI-Only Deployments** - GitHub Actions with WIF, no manual gcloud
5. **R5: Dual Memory Wiring** - Session + Memory Bank required
6. **R6: Single Docs Folder** - All docs in `000-docs/`
7. **R7: SPIFFE ID Propagation** - In AgentCard, logs, headers
8. **R8: Drift Detection** - Runs first in CI, blocks violations

### A2A Protocol Implementation
- **Protocol Version:** 0.3.0
- **Transport:** JSONRPC over HTTPS
- **Skills:** 3 core skills (ADK Q&A, doc search, deployment guidance)
- **Authentication:** OAuth2 client credentials (future)
- **Gateway:** Cloud Run service at https://a2a-gateway.bobs-brain.run.app

### Trust Attestations
- **HardModeCompliance** - R1-R8 enforced via CI drift detection
- **CI-CD-Gates** - Drift detection, ARV validation, WIF authentication
- **InlineDeployment** - Source code deployment (not pickle/serialization)
- **DualMemoryArchitecture** - Session Cache + Memory Bank wired correctly

---

## How to Use This Reference

### For Template Adopters
1. Copy the AI Card structure from `ai-card.json`
2. Update SPIFFE ID with your trust domain and workload path
3. Customize skills and capabilities for your agent
4. Add relevant trust attestations for your deployment

### For A2A → AI Card Migration
1. Start with your existing `agent-card.json` (A2A format)
2. Follow `conversion-guide.md` for field mapping
3. Test backward compatibility with A2A protocol
4. Deploy both formats during transition period

### For New Implementations
1. Start with `ai-card.json` as template
2. Implement A2A protocol in `services.a2a` section
3. Add other protocols (MCP, etc.) as needed in `services`
4. Use SPIFFE for identity where possible

---

## Production Metrics

- **Version:** 0.12.0 (current production)
- **Deployment:** Vertex AI Agent Engine (us-central1)
- **Availability:** 99.9% uptime (Cloud Run + Agent Engine)
- **Response Time:** < 200ms (gateway) + agent processing time
- **Memory:** Dual-layer (Session + Memory Bank) with automatic persistence
- **Test Coverage:** 65%+ across all agents
- **Documentation:** 141 files, 28 canonical standards

---

## Links

- **Repository:** https://github.com/jeremylongshore/bobs-brain
- **Documentation:** See `000-docs/` directory
- **Master Index:** `000-docs/6767-DR-INDEX-bobs-brain-standards-catalog.md`
- **Hard Mode Spec:** `000-docs/6767-DR-STND-adk-agent-engine-spec-and-hardmode-rules.md`
- **Operations Runbook:** `000-docs/6767-RB-OPS-adk-department-operations-runbook.md`
- **DevOps Playbook:** `000-docs/680-AA-AUDT-appaudit-devops-playbook.md`

---

**Reference Implementation for:** Linux Foundation AI Card Standard  
**Last Updated:** 2025-12-02  
**Contact:** jeremy@intentsolutions.io
