---
id: BLU-002
title: "Plane as Agentic Command Center — Feasibility & Integration Blueprint"
type: reference
status: DRAFT
owner: architect
agents: [researcher, architect]
tags: [blueprint, research, integration, project-management, MCP, plane]
created: 2026-03-04
updated: 2026-03-04
version: 0.1.0
---

> **BLUF:** Plane (makeplane/plane) is an open-source project management platform with a **native MCP server**, 180+ REST APIs, webhooks, and OAuth — making it the highest-value integration target for turning the Agentic Development Lifecycle (GOV-005) from a document into a **live, queryable, automatable system**. This blueprint analyzes how to adapt Plane for the Architect+Agent workflow and what DarkGravity's swarm can contribute.

# Plane as Agentic Command Center

> **"The Architect thinks. The agents build. The tests prove. The logs remember."**
> — GOV-005 §1

---

## 1. What Is Plane?

[Plane](https://github.com/makeplane/plane) is an open-source alternative to Jira, Linear, Monday, and ClickUp. AGPL-3.0 licensed. Self-hostable via Docker/Kubernetes or available as Plane Cloud.

### 1.1 Plane Entity Model

| Entity | Plane Concept | Agentic Equivalent |
|:-------|:-------------|:-------------------|
| **Work Item** | Issue/task with rich text, sub-items, links, attachments | GOV-005 work items (EVO-*, DEF-*, RES-*, BLU-*) |
| **Cycle** | Time-bounded sprint with burn-down charts | GOV-005 scope-bounded sprint |
| **Module** | Feature grouping across cycles | CODEX component (20_BLUEPRINTS spec) |
| **Epic** | Large initiative spanning multiple work items | Multi-sprint feature arc |
| **Initiative** | Strategic objective spanning projects/epics | Cross-project vision alignment |
| **Page** | Rich-text knowledge document with AI assist | CODEX document (blueprints, research, runbooks) |
| **View** | Saved filter/query over work items | Agent-specific dashboards |
| **Intake** | Triage queue for incoming issues | Emergent work item intake (GOV-005 §9) |
| **State** | Custom workflow states | Agentic Loop phases (Conversation → Spec → Sprint → Verify → Merge → Deploy) |
| **Label** | Taxonomy tags | CODEX tag taxonomy |
| **Time Tracking** | Worklogs per issue | Agent token/cost tracking |
| **Customer** | External stakeholder with custom properties | (Future: multi-Architect workspaces) |

### 1.2 Why Plane Over Linear/Jira/GitHub Issues

| Factor | Plane | Linear/Jira/GitHub |
|:-------|:------|:-------------------|
| **Self-hosted** | ✅ Full data sovereignty | ❌/Partial |
| **Native MCP server** | ✅ [plane-mcp-server](https://github.com/makeplane/plane-mcp-server) | ❌ |
| **REST API** | 180+ endpoints | Varies |
| **Webhooks** | ✅ Real-time event hooks | ✅ |
| **OAuth Apps** | ✅ Build custom integrations | ✅ |
| **Open source** | ✅ AGPL-3.0, fork-friendly | ❌/Partial |
| **Cost** | Free (self-hosted) | $$$$ at scale |

---

## 2. The Vision: GOV-005 Comes Alive

Today, GOV-005 (Agentic Development Lifecycle) is a **governance document**. With Plane, it becomes a **live system**:

### 2.1 Mapping the Agentic Loop to Plane

```
GOV-005 Phase          →  Plane Feature
─────────────────────────────────────────
1. CONVERSATION        →  Page (draft spec) + Intake (new idea triage)
2. SPECIFICATION       →  Work Item (EVO/DEF/RES/BLU) + Page (formal spec)
3. SPRINT              →  Cycle (scope-bounded) + Module (component grouping)
4. VERIFICATION        →  Work Item state transition + Comments (test results)
5. MERGE               →  Work Item state → "Merged" + Activity (audit trail)
6. DEPLOY              →  Work Item state → "Deployed" + Webhook (trigger CI/CD)
```

### 2.2 Custom States (Agentic Workflow)

Replace Plane's default states with the Agentic Loop:

| State | Group | Description |
|:------|:------|:------------|
| `Conversation` | Backlog | Architect + Agent are scoping |
| `Spec Review` | Unstarted | Spec written, awaiting Architect approval |
| `Sprint Active` | Started | Agent is building on a branch |
| `Checkpoint` | Started | Natural stopping point, Architect reviewing |
| `Verification` | Started | Running GOV-002 test suite |
| `Merge Ready` | Started | Tests pass, awaiting Architect merge approval |
| `Deployed` | Completed | In production |
| `Cancelled` | Cancelled | Abandoned or superseded |

### 2.3 Labels = CODEX Tags

Map the [CODEX tag taxonomy](file:///home/bdavidriggins/Documents/agentic_architect/CODEX/00_INDEX/TAG_TAXONOMY.md) directly to Plane labels:

- `governance`, `standards`, `testing`, `blueprint`, `defect`, `research`, `evolution`
- Add agent-specific labels: `agent:coder`, `agent:tester`, `agent:researcher`, `agent:architect`
- Add priority labels: `P0-critical`, `P1-high`, `P2-medium`, `P3-low`

---

## 3. The MCP Integration: Two Brains, One Protocol

This is where it gets powerful. Both Plane **and** DarkGravity speak MCP.

### 3.1 Architecture: The MCP Triangle

```
                    ┌─────────────────────┐
                    │    IDE / Antigravity │
                    │   (Orchestrator)     │
                    └────────┬────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
           ┌───────▼──────┐  ┌───────▼──────┐
           │  Plane MCP   │  │ DarkGravity  │
           │  Server      │  │ MCP Server   │
           │              │  │              │
           │  • Projects  │  │  • Research  │
           │  • Work Items│  │  • Architect │
           │  • Cycles    │  │  • Code      │
           │  • Pages     │  │  • Test      │
           │  • States    │  │  • Swarm     │
           └──────────────┘  └──────────────┘
```

### 3.2 Integration Scenarios

| Scenario | Flow |
|:---------|:-----|
| **Agent creates a work item** | DarkGravity researcher discovers a gap → `plane.create_work_item(title, description, state="Conversation")` |
| **Agent starts a sprint** | Architect approves spec → `plane.update_work_item(state="Sprint Active")` → `darkgravity.run_pipeline(stages=["coder","tester"])` |
| **Agent reports test results** | DarkGravity tester finishes → `plane.add_comment(work_item_id, test_summary)` → `plane.update_work_item(state="Verification")` |
| **Webhook triggers deploy** | Plane work item moves to "Merge Ready" → webhook fires → CI/CD pipeline starts |
| **Agent tracks costs** | DarkGravity pipeline returns `total_cost_usd`, `total_tokens` → `plane.create_worklog(work_item_id, description, duration)` |
| **Research feeds Pages** | DarkGravity researcher output → `plane.create_page(title, content)` for persistent knowledge |

### 3.3 Plane MCP Server — Transport Options

| Transport | Use Case |
|:----------|:---------|
| **Remote HTTP + OAuth** | Plane Cloud — recommended for SaaS |
| **Remote HTTP + PAT** | Self-hosted — API key auth |
| **Local Stdio** | Local dev — same-machine integration |
| **SSE (Legacy)** | Deprecated — avoid |

---

## 4. DarkGravity Swarm Analysis

> **What would DarkGravity's research swarm say about this?**

Running the swarm mentally through Plane integration as a research topic, using the 4-persona adversarial loop:

### 4.1 Draftsman Assessment

**Plane is a near-perfect fit** for the Agentic Development model because:

1. **Native MCP = Zero glue code.** Plane exposes project management as MCP tools. DarkGravity already speaks MCP. The orchestrator (Antigravity/IDE) connects them without custom bridges.
2. **180+ REST endpoints** cover every entity in GOV-005. Work Items, Cycles, Modules, Pages — all programmable.
3. **Webhooks enable reactive patterns.** When a Work Item changes state, fire a webhook to trigger DarkGravity pipelines, run tests, or notify the Architect.
4. **Self-hosted = data sovereignty.** No vendor lock-in, full control of the database. Can run on a Forerunner node alongside DarkGravity.
5. **Pages replace ad-hoc CODEX files** with a rich, searchable, AI-assisted knowledge base.

### 4.2 Cynic Critique

1. **AGPL-3.0 license** — any modifications to Plane itself must be open-sourced. Building a proprietary fork is legally complex. Mitigation: use it as-is via API + MCP, don't modify the source.
2. **Overhead risk.** Plane is a full Django + Next.js application (PostgreSQL, Redis, MinIO). That's a heavy stack for a single-Architect workflow. Consider whether the complexity is justified vs. a lighter tool.
3. **MCP maturity.** Plane's MCP server is new. Unknown how many tools it exposes or how stable it is. Need to audit the [plane-mcp-server](https://github.com/makeplane/plane-mcp-server) repo before committing.
4. **Dual-system drift.** If CODEX documents live in `/CODEX/` AND Pages live in Plane, which is authoritative? Must establish a single source of truth or a synchronization protocol.
5. **Context window cost.** Every Plane API call response consumes agent context. Large work item lists or page contents could blow DarkGravity's context windows, triggering cascades.

### 4.3 Synthesizer Resolution

| Cynic Concern | Resolution |
|:-------------|:-----------|
| AGPL license | Use via API/MCP only. No source modifications needed. |
| Overhead | Self-host on existing Forerunner infrastructure (HP ProBook). Docker Compose makes deployment trivial. Start with Plane Cloud (free tier) for evaluation. |
| MCP maturity | Audit `plane-mcp-server` GitHub repo. If insufficient, fall back to REST API with a thin MCP adapter. |
| Dual-system drift | **CODEX stays authoritative for governance** (GOV-001–006). Plane is the **operational layer** (work items, sprints, tracking). Pages mirror CODEX for discoverability, but CODEX is the source of truth. |
| Context cost | Implement response truncation (like DarkGravity's ObservationPurifier). Query only the fields/items needed. Use Plane's `fields` query parameter. |

### 4.4 Auditor Verdict

**APPROVED_WITH_NOTES.**

Plane is the highest-value project management integration for the Agentic Architect ecosystem. The MCP-to-MCP triangle (Antigravity ↔ Plane ↔ DarkGravity) is architecturally sound and would unlock:

- **Automated work item lifecycle** (GOV-005 becomes enforceable, not just advisory)
- **Real-time sprint tracking** with burn-down data
- **Cross-project visibility** via Initiatives and Epics
- **Auditable agent activity** via Work Item Activity + Comments
- **Knowledge persistence** via Pages

**Gaps to close before implementation:**
1. Audit the `plane-mcp-server` tool inventory
2. Prototype a single flow: Architect creates idea → Agent picks up → Agent reports back
3. Define the CODEX-Plane synchronization contract
4. Measure infrastructure requirements (RAM, disk) for self-hosted deployment

---

## 5. Implementation Roadmap

### Phase 1: Evaluation (1 sprint)
- [ ] Deploy Plane Cloud or self-hosted Docker instance
- [ ] Audit `plane-mcp-server` GitHub repository — list all exposed MCP tools
- [ ] Configure custom states matching the Agentic Loop (§2.2)
- [ ] Create labels matching CODEX tag taxonomy (§2.3)
- [ ] Manual test: create a project, work items, cycle, page

### Phase 2: MCP Bridge (1-2 sprints)
- [ ] Connect Plane MCP server to IDE/Antigravity alongside DarkGravity MCP
- [ ] Build prototype flow: `Intake → Work Item → Sprint (DarkGravity pipeline) → Verify → Merge`
- [ ] Implement webhook listener for state-change-triggered DarkGravity runs
- [ ] Add Plane integration to `.agent/context.md` for agent onboarding

### Phase 3: Operational Integration (2-3 sprints)
- [ ] Automate: DarkGravity pipeline creates/updates Plane work items
- [ ] Automate: test results posted as Plane comments
- [ ] Automate: token/cost tracking via Plane time tracking (worklogs)
- [ ] Build CODEX ↔ Plane Pages sync protocol (one-directional: CODEX → Plane)
- [ ] Create Plane Views for "My Active Sprints", "Agent Activity", "Blocked Items"

### Phase 4: Intelligence Layer (future)
- [ ] DarkGravity researcher queries Plane for project context before pipeline runs
- [ ] Plane Analytics feed into DarkGravity for sprint velocity forecasting
- [ ] Automated sprint retrospectives from Work Item Activity data
- [ ] Multi-project Initiatives tracking across agentic_architect + darkgravity + future projects

---

## 6. Infrastructure Requirements

### Self-Hosted (Docker Compose)

| Component | Purpose | Estimated Resources |
|:----------|:--------|:-------------------|
| `plane-app` | Next.js frontend | 512MB RAM |
| `plane-api` | Django REST API | 1GB RAM |
| `plane-worker` | Celery task queue | 512MB RAM |
| `plane-beat-worker` | Scheduled tasks | 256MB RAM |
| `postgres` | Database | 512MB RAM |
| `redis` | Cache + message broker | 256MB RAM |
| `minio` | Object storage (attachments) | 256MB RAM |

**Total: ~3.3GB RAM** — feasible on a Forerunner node or a dedicated VM.

### Cloud Option

Plane Cloud free tier supports 1 workspace with unlimited members. Good for evaluation. Migrate to self-hosted when data sovereignty becomes critical.

---

## 7. Risk Register

| # | Risk | Impact | Likelihood | Mitigation |
|:--|:-----|:-------|:-----------|:-----------|
| R1 | Plane MCP server lacks critical tools | High | Medium | Fall back to REST API + thin MCP adapter |
| R2 | AGPL forces open-sourcing modifications | Medium | Low | Use via API only, don't modify source |
| R3 | Infrastructure overhead too high | Medium | Low | Start with Plane Cloud, migrate when needed |
| R4 | CODEX-Plane data drift | High | Medium | Define sync contract early; CODEX is authority |
| R5 | Context window exhaustion from API responses | Medium | Medium | Use field filtering + ObservationPurifier pattern |

---

## 8. Conclusion

Plane is not just "another Jira." It's an **open-source, MCP-native, self-hostable project management platform** that maps almost 1:1 to the Agentic Development Lifecycle. The fact that both Plane and DarkGravity speak MCP means the integration is architecturally trivial — it's the **operational workflow design** that matters.

The biggest win isn't automation — it's **visibility**. Today, the Architect's view into agent work is scattered across git commits, test output, and conversation history. Plane centralizes this into a single dashboard with states, comments, activity logs, and analytics.

> **Recommendation:** Start with Plane Cloud evaluation (Phase 1). If the MCP server proves capable, this becomes the highest-priority integration for the Agentic Architect ecosystem in Q2 2026.

---

*This document was produced as a research blueprint. It has not been committed to version control per Architect instructions.*
