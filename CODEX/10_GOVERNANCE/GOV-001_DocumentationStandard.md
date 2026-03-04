---
id: GOV-001
title: "Documentation Standard"
type: reference
status: APPROVED
owner: architect
agents: [all]
tags: [documentation, standards, naming, frontmatter, templates, governance]
related: [IDX-000]
created: 2026-03-04
updated: 2026-03-04
version: 1.0.0
---

> **BLUF:** This document defines the mandatory documentation standards for all projects built with the Agentic Architect template. All docs must use YAML frontmatter, BLUF-first writing, and follow the Indexed Decimal folder structure. Documentation is a first-class deliverable — not an afterthought.

# Documentation Standard

> **"If it isn't documented, it doesn't exist. If it's documented poorly, it's worse than not existing."**

Documentation is designed for **dual-audience** consumption:
1. **Human Architects** — who need to find and scan docs quickly
2. **AI Agents** — who need to parse, filter, and retrieve docs programmatically

---

## 1. Folder Structure

```
CODEX/
├── 00_INDEX/              # Entry point: README + MANIFEST.yaml
├── 10_GOVERNANCE/         # Standards, protocols, architecture decisions
├── 20_BLUEPRINTS/         # Component specs, system designs, API contracts
├── 30_RUNBOOKS/           # Operational how-to guides, deployment, workflows
├── 40_VERIFICATION/       # Test specs, QA standards, validation reports
├── 50_DEFECTS/            # Bug reports, root cause analysis, forensics
├── 60_EVOLUTION/          # Feature specs, enhancements, roadmaps
├── 70_RESEARCH/           # Whitepapers, investigations, POCs
├── 90_ARCHIVE/            # Deprecated and completed docs
└── _templates/            # Doc templates (reference, how-to, tutorial, explanation)
```

### 1.1 Area Rules

- **Numbered prefixes** ensure deterministic sort order (`ls` always returns the same order)
- **Numbers 00–90** in increments of 10, leaving room for future areas
- **One area, one purpose** — no duplicate numbers, no overlapping scope
- **90 is always Archive** — the graveyard for deprecated docs

---

## 2. File Naming

### 2.1 Format

```
[CATEGORY]-[NNN]_[Title].md
```

| Component | Description | Example |
|:----------|:------------|:--------|
| `CATEGORY` | 3-letter code from area's category codes | `GOV`, `BLU`, `VER` |
| `NNN` | 3-digit serial number | `001`, `042`, `100` |
| `Title` | PascalCase description | `DocumentationStandard` |

**Examples:**
- `GOV-001_DocumentationStandard.md`
- `BLU-003_ArbiterSpec.md`
- `VER-010_E2ETestPlan.md`
- `DEF-005_MemoryLeakRCA.md`

### 2.2 Category Codes

| Area | Primary Code | Secondary Code | Description |
|:-----|:-------------|:---------------|:------------|
| 10_GOVERNANCE | `GOV` | `ADR` | Standards, Architecture Decision Records |
| 20_BLUEPRINTS | `BLU` | `API` | Specs, API Contracts |
| 30_RUNBOOKS | `RUN` | `DEP` | Guides, Deployment Procedures |
| 40_VERIFICATION | `VER` | `QA` | Test Specs, Quality Assurance |
| 50_DEFECTS | `DEF` | `RCA` | Defect Reports, Root Cause Analysis |
| 60_EVOLUTION | `EVO` | `RFC` | Feature Specs, Requests for Change |
| 70_RESEARCH | `RES` | `POC` | Research Papers, Proof of Concepts |
| 90_ARCHIVE | `ARC` | — | Archived docs retain their original code |

### 2.3 ID Ranges

| Range | Purpose | Example |
|:------|:--------|:--------|
| **001–009** | Core/foundational documents | `GOV-001_DocumentationStandard` |
| **010–099** | Standard documents | `BLU-012_DatabaseSchema` |
| **100–199** | Extended/supplementary | `RUN-100_DisasterRecovery` |

---

## 3. YAML Frontmatter (Mandatory)

Every `.md` file **MUST** begin with this metadata block:

```yaml
---
id: GOV-001
title: "Documentation Standard"
type: reference              # Diátaxis: reference | how-to | tutorial | explanation
status: DRAFT                # Lifecycle: DRAFT | REVIEW | APPROVED | DEPRECATED
owner: architect             # Who maintains this doc
agents: [all]                # Which agent roles should read this: [all], [coder], [tester], etc.
tags: [documentation, standards]
related: [IDX-000, BLU-003]  # Cross-references to other doc IDs
created: 2026-03-04
updated: 2026-03-04
version: 1.0.0
---
```

### 3.1 Required Fields

| Field | Type | Description |
|:------|:-----|:------------|
| `id` | string | Unique doc ID (`CATEGORY-NNN`) |
| `title` | string | Human-readable title |
| `type` | enum | `reference`, `how-to`, `tutorial`, `explanation` |
| `status` | enum | `DRAFT`, `REVIEW`, `APPROVED`, `DEPRECATED` |
| `owner` | string | Maintainer role or name |
| `agents` | list | Agent roles that should read this doc |
| `tags` | list | Searchable keywords |
| `related` | list | IDs of related documents |
| `created` | date | Creation date |
| `updated` | date | Last modification date |
| `version` | semver | Semantic version (`MAJOR.MINOR.PATCH`) |

### 3.2 The `agents` Field

This field answers: **"Which AI agent roles should care about this doc?"**

| Value | Meaning |
|:------|:--------|
| `[all]` | Every agent should be aware of this doc |
| `[coder]` | Coding agents building the implementation |
| `[tester]` | Testing agents writing/running tests |
| `[researcher]` | Research agents gathering information |
| `[deployer]` | Deployment agents managing releases |
| `[architect]` | The orchestrating agentic architect only |

### 3.3 The `type` Field (Diátaxis)

Choose the type that matches the doc's purpose:

| Type | Purpose | Example |
|:-----|:--------|:--------|
| `reference` | Factual information — specs, APIs, schemas | Component spec, API contract |
| `how-to` | Solve a specific problem — step-by-step | Deployment guide, debug runbook |
| `tutorial` | Learn by doing — guided exercises | "Getting Started" guide |
| `explanation` | Understand why — concepts and decisions | Architecture explanation, ADR |

---

## 4. Content Standards

### 4.1 BLUF (Bottom Line Up Front)

Immediately after frontmatter, every doc **MUST** include a BLUF blockquote:

```markdown
> **BLUF:** [What is this doc? Why does it matter? Key takeaway. Max 3 sentences.]
```

### 4.2 Writing Rules

1. **≤4 sentences per paragraph** — no walls of text
2. **Tables over prose** — structured data belongs in tables
3. **Code blocks specify language** — always include the language identifier
4. **Mermaid diagrams for architecture** — use `graph`, `sequenceDiagram`, `stateDiagram-v2`
5. **File size guidance**:
   - **≤10KB** — ✅ ideal, easy for agents to retrieve and process
   - **10–30KB** — ⚠️ acceptable if the doc covers one cohesive topic
   - **30KB+** — 🔴 must justify — consider splitting into focused pieces

### 4.3 Callout Boxes

Use GitHub-style alerts: `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`

Include `🧠 **Plain English:**` explanations for complex topics.

---

## 5. MANIFEST.yaml

The `00_INDEX/MANIFEST.yaml` file is the **machine-readable registry** of all documents. It is the single file an agent reads to build a map of the entire knowledge base.

### 5.1 When to Update

- **Creating** a new doc → add an entry (or run `/manage_documents`)
- **Archiving** a doc → update status to `DEPRECATED`, update path to `90_ARCHIVE/`
- **Deleting** a doc → remove entry

---

## 6. Document Lifecycle

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Author creates
    DRAFT --> REVIEW: Ready for review
    REVIEW --> DRAFT: Changes requested
    REVIEW --> APPROVED: Approved
    APPROVED --> REVIEW: Update needed
    APPROVED --> DEPRECATED: Superseded
    DEPRECATED --> [*]: Moved to 90_ARCHIVE
```

### 6.1 Version Numbering (SemVer)

| Change Type | Bump | Example |
|:------------|:-----|:--------|
| Breaking restructure | MAJOR | `1.0.0` → `2.0.0` |
| New section or content | MINOR | `1.0.0` → `1.1.0` |
| Typo fix, clarification | PATCH | `1.0.0` → `1.0.1` |

### 6.2 Archival Protocol

When deprecating a doc:
1. Set `status: DEPRECATED` in frontmatter
2. Add `superseded_by: [NEW-ID]` field to frontmatter
3. Move file to `90_ARCHIVE/`
4. Update MANIFEST.yaml
5. Update README.md master index

---

## 7. Templates

Use the appropriate template from `_templates/` when creating a new doc:

| Template | Diátaxis Type | Use When |
|:---------|:-------------|:---------|
| `template_reference.md` | Reference | Documenting facts: specs, APIs, schemas |
| `template_how-to.md` | How-To | Solving a specific problem step-by-step |
| `template_tutorial.md` | Tutorial | Teaching through guided exercises |
| `template_explanation.md` | Explanation | Explaining concepts and design decisions |

### 7.1 Creating a New Doc

1. Copy the appropriate template to the target area folder
2. Rename using the `[CATEGORY]-[NNN]_[Title].md` convention
3. Fill in all frontmatter fields
4. Write the BLUF
5. Fill content sections (remove irrelevant template sections)
6. Add entry to `00_INDEX/MANIFEST.yaml`
7. Add entry to `00_INDEX/README.md` master index table

---

## 8. AI Agent Instructions

When generating or editing documentation in this system:

1. **Always update frontmatter** — increment version, update `updated` date
2. **Always update MANIFEST.yaml** — keep the registry in sync with reality
3. **Respect the type classification** — don't put step-by-step procedures in a `reference` doc
4. **Use the `agents` field** — tag docs so other agents can filter effectively
5. **Link via `related` field** — build the knowledge graph through explicit cross-references
6. **Stay under 10KB** — split large docs rather than creating monoliths
7. **BLUF first** — every doc must be scannable in 10 seconds

---

## 9. Compliance Checklist

Before marking any doc as APPROVED:

- [ ] YAML frontmatter complete with all required fields
- [ ] BLUF present immediately after frontmatter (≤3 sentences)
- [ ] `type` field matches actual doc content
- [ ] `agents` field populated
- [ ] `tags` field has ≥2 relevant keywords
- [ ] File size reviewed (≤10KB ideal, 10–30KB acceptable, 30KB+ needs justification)
- [ ] No placeholder text (TODO, TBD)
- [ ] Mermaid diagrams render correctly
- [ ] Entry added to MANIFEST.yaml
- [ ] Entry added to README.md master index

---

> **"Documentation is not about recording what you did. It's about enabling what comes next."**
