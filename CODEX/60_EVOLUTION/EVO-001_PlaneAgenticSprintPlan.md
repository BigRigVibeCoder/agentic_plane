---
id: EVO-001
title: "Plane Agentic Command Center — Multi-Phase Sprint Plan"
type: reference
status: APPROVED
owner: architect
agents: [researcher, architect, coder, tester]
tags: [evolution, sprint, integration, MCP, plane]
related: [BLU-002, BLU-002-A, BLU-002-B]
created: 2026-03-05
updated: 2026-03-05
version: 1.0.0
---

> **BLUF:** This document decomposes the BLU-002 blueprint suite into 4 executable sprint phases, transforming Plane from a passive project management tool into the Agentic Development Lifecycle's live command center. Each phase is self-contained, delivers measurable value, and has explicit acceptance criteria.

# EVO-001: Plane Agentic Command Center

> **"The Architect thinks. The agents build. The tests prove. The logs remember."**

---

## Phase Overview

| Phase | Name | Duration | Goal | Dependencies |
|:------|:-----|:---------|:-----|:-------------|
| **1** | Foundation | 1 sprint | Plane running + custom states/labels + MCP verified | GCP VM deployed |
| **2** | Bridge | 1-2 sprints | Hybrid MCP+REST client + webhook listener + first automated flow | Phase 1 |
| **3** | Operations | 2-3 sprints | Full pipeline automation + Pages + cost tracking + dashboards | Phase 2 |
| **4** | Intelligence | Future | Cross-project analytics + velocity forecasting + retrospectives | Phase 3 |

---

## Phase 1: Foundation (1 Sprint)

**Goal:** Plane is live, configured with Agentic Loop states and CODEX labels, and the MCP server is verified.

### Sprint Backlog

| # | Task | Agent | Priority | Est |
|:--|:-----|:------|:---------|:----|
| 1.1 | Deploy Plane (self-hosted Docker Compose on GCP VM) | coder | P0 | 2h |
| 1.2 | Create Agentic Loop custom states via REST API | coder | P0 | 1h |
| 1.3 | Create CODEX label taxonomy via REST API | coder | P0 | 1h |
| 1.4 | Audit & verify Plane MCP server connectivity | researcher | P0 | 2h |
| 1.5 | Create first project + manual work item lifecycle test | architect | P1 | 1h |
| 1.6 | Document setup in `.agent/context.md` | coder | P2 | 30m |

### 1.1 Deploy Plane

| Field | Value |
|:------|:------|
| **Branch** | `feat/EVO-001-phase1-deploy` |
| **Scope** | Infrastructure (Docker Compose on GCP `plane-vm`) |

- Complete the Docker Compose build on the existing `plane-vm` (34.172.108.193)
- Run `setup.sh` to generate `.env` files and Django `SECRET_KEY`
- Verify all containers healthy: `web`, `api`, `worker`, `beat-worker`, `proxy`, `plane-db`, `plane-redis`, `plane-mq`, `plane-minio`
- Access Plane at `http://34.172.108.193`

### 1.2 Create Agentic Loop States

**Script:** `scripts/plane_agentic_setup.py`

| State Name | Group | Sequence | Color |
|:-----------|:------|:---------|:------|
| Conversation | `backlog` | 15000 | `#6366F1` (indigo) |
| Spec Review | `unstarted` | 25000 | `#8B5CF6` (violet) |
| Sprint Active | `started` | 35000 | `#F59E0B` (amber) |
| Checkpoint | `started` | 40000 | `#3B82F6` (blue) |
| Verification | `started` | 45000 | `#06B6D4` (cyan) |
| Merge Ready | `started` | 50000 | `#10B981` (emerald) |
| Deployed | `completed` | 55000 | `#46A758` (green) |
| Cancelled | `cancelled` | 65000 | `#9AA4BC` (grey) |

### 1.3 Create CODEX Labels

| Parent Label | Child Labels |
|:-------------|:-------------|
| `governance` | `GOV-001`, `GOV-002`, `GOV-003`, `GOV-004`, `GOV-005`, `GOV-006` |
| `agent` | `agent:architect`, `agent:researcher`, `agent:coder`, `agent:tester` |
| `priority` | `P0-critical`, `P1-high`, `P2-medium`, `P3-low` |
| `type` | `blueprint`, `defect`, `research`, `evolution`, `feature` |

### 1.4 Audit MCP Server

- Install `plane-mcp-server` locally
- Connect via Remote HTTP + PAT transport
- Verify all 55+ tools respond: `list_projects`, `create_work_item`, `list_cycles`, etc.
- Document any tools that fail or return unexpected responses
- Test `search_work_items` with query parameters

### Acceptance Criteria — Phase 1

- [ ] Plane accessible at `http://34.172.108.193` with login working
- [ ] 8 custom Agentic states visible in project settings
- [ ] CODEX labels created with hierarchical parent structure
- [ ] MCP server responds to `list_projects` and `create_work_item`
- [ ] First work item created and moved through all 8 states manually

---

## Phase 2: Bridge (1-2 Sprints)

**Goal:** DarkGravity agents can create/update Plane work items, and state changes trigger pipelines automatically.

### Sprint Backlog

| # | Task | Agent | Priority | Est |
|:--|:-----|:------|:---------|:----|
| 2.1 | Build Plane Hybrid Client (`plane_bridge.py`) | coder | P0 | 4h |
| 2.2 | Implement webhook listener for state changes | coder | P0 | 3h |
| 2.3 | Prototype: Intake → Work Item → Sprint → Verify → Merge | coder | P0 | 4h |
| 2.4 | Wire DarkGravity pipeline output → Plane Comments | coder | P1 | 2h |
| 2.5 | Add Plane integration to DarkGravity agent context | coder | P2 | 1h |

### 2.1 Plane Hybrid Client

**File:** `scripts/plane_bridge.py` (~200-300 lines)

| Method | Protocol | Description |
|:-------|:---------|:------------|
| `create_work_item()` | MCP | Create issue with state, labels, assignee |
| `update_work_item_state()` | MCP | Transition state (triggers webhook) |
| `search_work_items()` | MCP | Query by state, label, assignee |
| `add_comment()` | REST | Post text comment to work item |
| `create_page()` | REST | Push research/spec to Plane Pages |
| `create_state()` | REST | One-time: create custom states |
| `create_label()` | REST | One-time: create CODEX labels |
| `register_webhook()` | REST | Register webhook for issue events |

### 2.2 Webhook Listener

**File:** `scripts/webhook_listener.py`

- FastAPI/Flask micro-service (~100 lines)
- Listens on port `8081` for Plane webhook POSTs
- Validates `X-Plane-Signature` header against shared secret
- On state change to `Sprint Active`:
  - Extract work item title + description
  - Trigger `darkgravity run "{title}" --project {path}`
- On state change to `Cancelled`:
  - Kill active DarkGravity pipeline for that work item

### 2.3 Prototype Flow

```
Architect types idea in Plane Intake
    → Script creates Work Item (state: Conversation)
    → Architect reviews, moves to Spec Review
    → Architect approves, moves to Sprint Active
    → Webhook fires → DarkGravity pipeline starts
    → Coder builds → Tester tests
    → Pipeline complete → Comment posted with results
    → State auto-moves to Verification
    → Architect reviews, moves to Merge Ready
    → CI/CD webhook fires → Deployed
```

### Acceptance Criteria — Phase 2

- [ ] `plane_bridge.py` can create work items, transition states, and post comments
- [ ] Webhook listener receives state-change events and triggers DarkGravity
- [ ] One complete end-to-end flow works: Intake → Deployed
- [ ] Test results appear as Plane comments on the work item
- [ ] Shared webhook secret validated on every incoming request

---

## Phase 3: Operations (2-3 Sprints)

**Goal:** Full operational integration — every DarkGravity run is tracked in Plane with cost data, knowledge persists as Pages, and dashboards provide real-time visibility.

### Sprint Backlog

| # | Task | Agent | Priority | Est |
|:--|:-----|:------|:---------|:----|
| 3.1 | Auto-create work items from `darkgravity run` | coder | P0 | 3h |
| 3.2 | Push research briefs and specs to Plane Pages | coder | P1 | 3h |
| 3.3 | Implement token/cost tracking via worklogs | coder | P1 | 2h |
| 3.4 | Build CODEX → Plane Pages sync script | coder | P2 | 3h |
| 3.5 | Create Plane Views (dashboards) | coder | P2 | 2h |
| 3.6 | Multi-agent contention handling | coder | P1 | 2h |

### 3.1 Auto-Create Work Items

Every `darkgravity run` automatically:
1. Creates a Plane work item (state: `Conversation`)
2. Attaches the prompt as description
3. Assigns the `agent:researcher` label
4. Links to the target project

### 3.2 Pages as Knowledge Base

- Researcher output → `create_page(title="Research: {topic}", content=brief_html)`
- Architect output → `create_page(title="Spec: {feature}", content=spec_html)`
- Link pages to the parent work item via `ProjectPage`

> ⚠️ **Risk:** Test whether `description_html` insertion works without corrupting `description_binary`. If CRDT sync breaks, fall back to creating Pages as comments or external markdown files.

### 3.5 Plane Views (Dashboards)

| View Name | Filter | Purpose |
|:----------|:-------|:--------|
| Agent Activity | `label:agent:*` + `updated_at:last_24h` | What did agents do today? |
| Active Sprints | `state:Sprint Active OR Verification` | What's running right now? |
| Blocked Items | `state:Checkpoint` + `label:P0-critical` | What needs Architect attention? |
| Cost Report | `worklog:sum(tokens)` | How much did this sprint cost? |

### Acceptance Criteria — Phase 3

- [ ] Every `darkgravity run` creates a Plane work item automatically
- [ ] Research briefs and specs appear as Plane Pages linked to work items
- [ ] Token costs logged per work item
- [ ] CODEX governance docs mirrored to Plane Pages
- [ ] 4 Plane Views created and returning meaningful data
- [ ] No race conditions when Coder + Tester update the same work item

---

## Phase 4: Intelligence (Future)

**Goal:** The system learns from its own history and provides predictive insights.

### Sprint Backlog (Scoped, Not Scheduled)

| # | Task | Description |
|:--|:-----|:------------|
| 4.1 | Sprint velocity forecasting | Analyze past cycle data to predict completion dates |
| 4.2 | Automated retrospectives | Generate sprint summaries from Work Item Activity data |
| 4.3 | Cross-project Initiatives | Track "Improve security" across all repos in one view |
| 4.4 | Agent performance analytics | Compare agent:coder vs agent:tester efficiency |
| 4.5 | Researcher context injection | Researcher queries Plane for project context before researching |

### Acceptance Criteria — Phase 4

- [ ] Velocity chart shows accurate sprint predictions
- [ ] Automated retrospective document generated at cycle close
- [ ] At least 2 Initiatives tracked across multiple projects
- [ ] Agent performance dashboard shows tokens/task, success rate, fix-loop depth

---

## Risk Register (All Phases)

| # | Risk | Phase | Impact | Likelihood | Mitigation |
|:--|:-----|:------|:-------|:-----------|:-----------|
| R1 | MCP lacks Pages/Comments/States tools | 2 | Medium | Confirmed | Hybrid REST+MCP client |
| R2 | Page binary format CRDT corruption | 3 | High | Medium | Test HTML insertion; fall back to comments |
| R3 | Multi-agent state contention | 3 | Medium | Medium | Optimistic locking + retry |
| R4 | Webhook no-localhost restriction | 2 | Low | Confirmed | Use Docker hostname or LAN IP |
| R5 | Comment token bloat | 2 | Medium | Confirmed | Truncate to 2000 chars, link to full output |
| R6 | GCP VM cost | 1 | Low | Low | Use preemptible VM or scale down after testing |

---

## Files To Be Created

| Phase | File | Purpose |
|:------|:-----|:--------|
| 1 | `scripts/plane_agentic_setup.py` | One-time: create states, labels, webhook |
| 2 | `scripts/plane_bridge.py` | Hybrid MCP+REST client |
| 2 | `scripts/webhook_listener.py` | FastAPI webhook → DarkGravity trigger |
| 3 | `scripts/codex_to_plane_sync.py` | CODEX → Plane Pages one-directional sync |
| 3 | `scripts/plane_views_config.json` | Saved Plane View definitions |

---

## Success Metrics

| Metric | Phase 1 | Phase 2 | Phase 3 |
|:-------|:--------|:--------|:--------|
| Work items trackable in Plane | Manual | Automated creation | Auto + cost tracking |
| Agent visibility | None | State transitions visible | Full dashboards |
| Knowledge persistence | Files only | Files + comments | Pages + versioning |
| Architect control | CLI only | CLI + approve gates | CLI + dashboard + gates |
| Time to deploy a feature | ~30 min manual | ~15 min supervised | ~5 min autonomous |

---

*Synthesized from: [BLU-002](file:///home/bdavidriggins/Documents/agentic_plane/CODEX/20_BLUEPRINTS/BLU-002_PlaneForAgenticArchitecture.md), [BLU-002-A](file:///home/bdavidriggins/Documents/agentic_plane/CODEX/20_BLUEPRINTS/BLU-002-A_DarkGravityBacklog.md), [BLU-002-B](file:///home/bdavidriggins/Documents/agentic_plane/CODEX/20_BLUEPRINTS/BLU-002-B_EnhancedArchitecture.md)*
