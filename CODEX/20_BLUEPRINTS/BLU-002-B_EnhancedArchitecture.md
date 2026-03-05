---
id: BLU-002-B
title: "Plane Agentic Integration — MCP Audit & Enhanced Architecture"
type: reference
status: DRAFT
owner: architect
agents: [researcher, architect, coder]
tags: [blueprint, research, integration, MCP, plane, audit]
created: 2026-03-05
updated: 2026-03-05
version: 1.0.0
---

# BLU-002-B: Plane Agentic Integration — MCP Audit & Enhanced Architecture

> **BLUF:** After auditing the Plane MCP server source, REST API, Django models, and webhook infrastructure, the integration is **highly viable with caveats**. The MCP server covers Work Items, Cycles, Modules, and Initiatives well (55+ tools), but **lacks tools for Pages, Comments, States, Labels, and Worklogs** — these must go through REST. The webhook system is production-ready with secret-key auth, retry logic, and event logging. No Plane source modifications are needed.

---

## 1. MCP Server Audit Results

### 1.1 Available MCP Tools (55+ confirmed)

| Category | Tools | Coverage |
|:---------|:------|:---------|
| **Projects** | `list`, `create`, `retrieve`, `update`, `delete`, `get_worklog_summary`, `get_members`, `get_features`, `update_features` | ✅ Complete |
| **Work Items** | `list`, `create`, `retrieve`, `retrieve_by_identifier`, `update`, `delete`, `search` | ✅ Complete |
| **Cycles** | `list`, `create`, `retrieve`, `update`, `delete`, `list_archived`, `add_work_items`, `remove_work_item`, `list_work_items`, `transfer_work_items`, `archive`, `unarchive` | ✅ Complete |
| **Modules** | `list`, `create`, `retrieve`, `update`, `delete`, `list_archived`, `add_work_items`, `remove_work_item`, `list_work_items`, `archive`, `unarchive` | ✅ Complete |
| **Initiatives** | `list`, `create`, `retrieve`, `update`, `delete` | ✅ Complete |
| **Intake** | `list`, `create`, `retrieve`, `update`, `delete` | ✅ Complete |
| **Properties** | `list`, `create`, `retrieve`, `update`, `delete` | ✅ Complete |
| **Users** | `get_me` | ✅ Minimal |

### 1.2 Critical MCP Gaps

| Missing Capability | Impact | Workaround |
|:-------------------|:-------|:-----------|
| **Pages** (create/read/update) | Cannot push research briefs or specs to Plane Pages via MCP | Use REST API: `POST /api/v1/workspaces/{slug}/projects/{id}/pages/` |
| **Comments** (add to work items) | Cannot post test results or agent feedback to work items | Use REST API: `POST /api/v1/workspaces/{slug}/projects/{id}/issues/{id}/comments/` |
| **States** (CRUD) | Cannot programmatically create custom Agentic Loop states | Use REST API: `POST /api/v1/workspaces/{slug}/projects/{id}/states/` |
| **Labels** (CRUD) | Cannot create CODEX taxonomy labels programmatically | Use REST API: `POST /api/v1/workspaces/{slug}/labels/` |
| **Worklogs / Time Tracking** | Cannot log agent token costs per work item | Use REST API (if available) or store in Comments |
| **Epics** | Known open issue — MCP cannot work with Epics | Use REST API or wait for upstream fix |
| **Comments retrieval** | Known issue: `get_issue_comments` returns too many tokens | Implement truncation / pagination in the adapter |

### 1.3 Transport Recommendation

For a self-hosted deployment, use **Remote HTTP + PAT (Personal Access Token)**. This avoids OAuth complexity while keeping the MCP server accessible to DarkGravity agents.

---

## 2. Django Model Analysis

### 2.1 State Model — Perfect Agentic Loop Fit

The `State` model uses a `StateGroup` enum with 6 groups:

| StateGroup | Agentic Loop Phase |
|:-----------|:-------------------|
| `backlog` | **Conversation** — Architect + Agent scoping |
| `unstarted` | **Spec Review** — Awaiting approval |
| `started` | **Sprint Active**, **Checkpoint**, **Verification**, **Merge Ready** |
| `completed` | **Deployed** — In production |
| `cancelled` | **Cancelled** — Abandoned |
| `triage` | **Intake** — Emergent work triage |

> [!NOTE]
> Each project gets its own states. States have a `sequence` field for ordering and auto-increment by 15,000. We can create all 8 Agentic states via the REST API on project initialization with no schema changes.

### 2.2 Label Model — Hierarchical CODEX Tags

Labels are `WorkspaceBaseModel`-scoped (not project-scoped) with an optional `parent` ForeignKey for hierarchy. This means we can create:

```
governance (parent)
  ├── GOV-001 (child)
  ├── GOV-002 (child)
  └── ...
agent (parent)
  ├── agent:coder (child)
  ├── agent:tester (child)
  └── ...
priority (parent)
  ├── P0-critical (child)
  └── ...
```

### 2.3 Webhook Model — Production-Ready Event System

The webhook model supports:
- **Event types:** `project`, `issue`, `module`, `cycle`, `issue_comment`
- **Secret key auth:** Auto-generated `plane_wh_` + UUID hex token
- **Retry with logging:** `WebhookLog` stores request/response bodies, headers, status, and retry count
- **Project-level scoping:** `ProjectWebhook` allows webhooks per-project

> [!IMPORTANT]
> Webhooks validate that URLs are not `localhost` or `127.0.0.1`. For self-hosted setups where the listener runs on the same machine, you must use the machine's LAN IP or a Docker network hostname.

### 2.4 Page Model — Rich Knowledge Base

Pages support:
- Rich text (HTML + JSON + Binary descriptions)
- **Versioning** via `PageVersion` model
- **Labels** via `PageLabel` through-model
- **Project linking** via `ProjectPage`
- **Hierarchical pages** via `parent` self-FK
- Public/Private access control

---

## 3. Revised Architecture — The Hybrid MCP+REST Bridge

Given the MCP gaps, the integration architecture should be a **hybrid client**:

```
┌─────────────────────────────────────────────────┐
│            Orchestrator (Antigravity)            │
│                                                 │
│  ┌──────────────┐    ┌────────────────────────┐ │
│  │  DarkGravity  │    │   Plane Hybrid Client  │ │
│  │  MCP Server   │    │                        │ │
│  │               │    │  MCP: Work Items,      │ │
│  │  • Research   │    │       Cycles, Modules, │ │
│  │  • Architect  │    │       Projects         │ │
│  │  • Code       │    │                        │ │
│  │  • Test       │    │  REST: Pages, States,  │ │
│  │               │    │       Labels, Comments │ │
│  └──────────────┘    └────────────────────────┘ │
│                              │                  │
│                    ┌─────────▼────────┐         │
│                    │  Webhook Listener │         │
│                    │  (State changes → │         │
│                    │   trigger swarm)  │         │
│                    └──────────────────┘         │
└─────────────────────────────────────────────────┘
```

### 3.1 Plane Hybrid Client (`plane_bridge.py`)

A thin Python adapter that routes calls optimally:

| Operation | Protocol | Rationale |
|:----------|:---------|:----------|
| Create/update/search Work Items | **MCP** | Full tool support, type-safe |
| Manage Cycles & Modules | **MCP** | Full tool support |
| Create/update Pages | **REST** | No MCP tool available |
| Add Comments to Work Items | **REST** | No MCP tool available |
| Create custom States | **REST** | One-time setup, no MCP tool |
| Create Labels | **REST** | One-time setup, no MCP tool |
| Webhook management | **REST** | Configuration only |

### 3.2 Setup Script (`scripts/plane_agentic_setup.py`)

A one-time setup script that:
1. Creates 8 Agentic Loop states via REST API
2. Creates hierarchical CODEX labels via REST API
3. Registers a webhook for `issue` state changes via REST API
4. Validates the Plane MCP server connectivity

---

## 4. Risk Register (Updated)

| # | Risk | Impact | Likelihood | Mitigation |
|:--|:-----|:-------|:-----------|:-----------|
| R1 | MCP lacks Pages/Comments/States | Medium | **Confirmed** | Hybrid MCP+REST client (§3.1) |
| R2 | MCP lacks Epics support | Low | **Confirmed** | Use Initiatives or REST API |
| R3 | Comments return too many tokens | Medium | **Confirmed** | Truncate responses, paginate |
| R4 | Webhook no-localhost restriction | Low | Medium | Use Docker hostname or LAN IP |
| R5 | CODEX-Plane drift | High | Medium | CODEX remains authority; Plane is operational layer |
| R6 | Context window exhaustion | Medium | Medium | Field filtering + truncation |
| R7 | AGPL license constraints | Low | Low | API-only integration, no source mods |

---

## 5. Honest Feasibility Assessment

### What Will Work Well ✅

1. **Work Item lifecycle automation** — The MCP server's 7 Work Item tools + webhook-triggered pipelines make the core Agentic Loop (create → sprint → verify → deploy) straightforward to implement. This is the highest-value feature and it's well-supported.

2. **Custom states for the Agentic Loop** — Plane's `StateGroup` enum maps cleanly to the GOV-005 phases. No schema changes needed. The REST API handles one-time setup trivially.

3. **Sprint/Cycle management** — Full MCP support with 12 cycle tools. Creating time-bounded sprints, adding work items, transferring incomplete items — all covered.

4. **Webhook-driven automation** — Plane's webhook system is mature: secret key auth, retry with exponential backoff, event logging. Triggering DarkGravity pipelines on state changes is clean.

5. **Self-hosted data sovereignty** — Running Plane on the same infrastructure as DarkGravity means zero external dependencies for the core workflow.

### What Will Need Extra Work ⚠️

1. **The Hybrid Client** — The MCP gaps (Pages, Comments, States, Labels) mean we need a thin REST adapter alongside MCP. This is ~200-300 lines of Python, not a blocker, but it adds a maintenance surface.

2. **Pages as Knowledge Base** — Pages have rich versioning and label support, but no MCP tool. Every research brief and spec push requires REST calls. The `description_binary` field suggests Plane uses a custom binary format for real-time collaboration — we'll need to test whether plain HTML insertion works reliably.

3. **Comment token bloat** — The known issue of comments returning too many tokens is a real concern for the Tester agent posting detailed test results. We'll need aggressive truncation.

### What Might Be Challenging 🔴

1. **Real-time bidirectional sync** — If we want changes in Plane (e.g., Architect manually moves a work item to "Cancelled") to propagate back and stop a running DarkGravity pipeline, we need a persistent webhook listener service. This is architecturally sound but adds an always-on component.

2. **Page binary format** — The `description_binary` field in the Page model is a `BinaryField`. If Plane's frontend relies on this for its collaborative editor (likely Y.js or similar CRDT), inserting content purely via REST `description_html` might cause sync issues. Needs testing.

3. **Multi-agent contention** — If the Coder and Tester agents both try to update the same Work Item state simultaneously, we need optimistic concurrency handling. Plane doesn't appear to have built-in conflict resolution for API-driven state updates.

### Overall Verdict

> **8/10 — High confidence this will work.**

The core automation loop (Work Items + States + Webhooks + DarkGravity) is solid and well-supported. The MCP gaps are annoying but trivially bridgeable with REST. The biggest unknowns are the Page binary format and multi-agent contention, both of which are testable in Phase 1.

The fact that Plane's MCP server is actively maintained (12 releases, Python+FastMCP rewrite) and the platform itself is at v1.2.2 with recent security patches (Feb 2026) means the foundation is stable.

**Estimated time to Phase 1 (working prototype):** 2-3 sprints.
**Estimated time to Phase 2 (production-ready):** 4-5 sprints.

---

*This document was produced through independent research of the Plane MCP server GitHub repository, Plane REST API documentation, Django model source code analysis, and web research. All findings have been verified against the codebase at `apps/api/plane/db/models/`.*
