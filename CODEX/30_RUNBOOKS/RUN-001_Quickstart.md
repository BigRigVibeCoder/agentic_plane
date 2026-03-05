---
id: RUN-001
title: "Plane Agentic Command Center — Quickstart"
author: architect
status: active
tags: [runbook, quickstart, plane, docker]
---

# 🚀 Plane Agentic Command Center — Quickstart

> **You are a human. This guide respects that.** No jargon walls, no assumed knowledge. Just steps. Do them in order. If something breaks, there's a troubleshooting section at the bottom.

---

## 🧠 What Is This Thing?

You're running **Plane** (a project management tool like Jira) locally on your machine using Docker. On top of it, we bolted custom automation scripts that let AI agents create work items, track costs, and sync documentation — automatically.

**The pieces:**

| Thing | What it does | Where it lives |
|-------|-------------|----------------|
| **Plane** | Project board (like Jira) | `http://localhost` in your browser |
| **plane_agentic_setup.py** | Creates custom states & labels | Run from terminal |
| **codex_to_plane_sync.py** | Pushes your CODEX docs to Plane | Run from terminal |
| **agentic_run.py** | Kicks off an AI pipeline + creates a Plane ticket | Run from terminal |
| **agentic_cost_logger.py** | Logs token costs to a Plane ticket | Run from terminal |
| **webhook_listener.py** | Listens for Plane events, triggers pipelines | Run from terminal |

---

## 📋 Prerequisites

You need these installed. If you don't have them, install them first.

- [ ] **Docker** and **Docker Compose** — `sudo apt install docker.io docker-compose-v2`
- [ ] **Python 3.12+** — `python3 --version` (should say 3.12 or higher)
- [ ] **Git** — `git --version`

---

## Step 1: Clone the Repo

```bash
git clone https://github.com/BigRigVibeCoder/agentic_plane.git
cd agentic_plane
```

---

## Step 2: Start Plane

This boots up ~12 Docker containers (database, web server, API, etc). It takes a minute or two.

```bash
sudo docker compose up -d
```

**Wait 30 seconds**, then check everything is running:

```bash
sudo docker ps --format "table {{.Names}}\t{{.Status}}"
```

You should see containers named `web`, `api`, `proxy`, `plane-db`, etc — all with status "Up".

> ⚠️ **If `plane-migrator` shows "Exited (1)"**, just restart it:
> ```bash
> sudo docker restart plane-migrator
> ```
> Wait 30 seconds and check again. It needs the database to be ready first.

> ⚠️ **If `plane-live` keeps restarting**, make sure your `.env` file has these two lines:
> ```
> API_BASE_URL=http://localhost
> LIVE_SERVER_SECRET_KEY=longandsecurelivetokensecret
> ```

---

## Step 3: Log Into Plane

1. Open your browser → **http://localhost**
2. If it's the first time, create an account:
   - Email: `admin@test.com` (or whatever you want)
   - Password: anything you'll remember
3. Complete the onboarding (name, role — just pick anything)
4. Create a **Workspace** — name it whatever, note the **URL slug** (the part after `localhost/`)
5. Create a **Project** — name it "Agentic Integration", set identifier to "AGENT"
6. Go to your **avatar (top right) → Settings → Personal Access Tokens** → generate one

**Write down these three things:**

```
PLANE_API_KEY=plane_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PLANE_WORKSPACE_SLUG=your-workspace-slug
PLANE_PROJECT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

> 💡 **To find your Project ID:** Click into the project, look at the URL:
> `http://localhost/your-workspace/projects/THIS-IS-YOUR-PROJECT-ID/issues/`

---

## Step 4: Set Up the Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests fastapi uvicorn pytest requests-mock markdown pyyaml httpx
```

---

## Step 5: Export Your Credentials

Paste your three values from Step 3:

```bash
export PLANE_API_KEY="plane_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export PLANE_WORKSPACE_SLUG="your-workspace-slug"
export PLANE_PROJECT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

> 💡 You'll need to do this every time you open a new terminal. Or add them to `~/.bashrc`.

---

## Step 6: Provision the Agentic States & Labels

This creates the custom workflow states (Conversation → Sprint Active → Deployed) and taxonomy labels (priority, agent roles, etc.) inside your Plane project:

```bash
python plane_agentic_setup.py \
  --api-key "$PLANE_API_KEY" \
  --workspace "$PLANE_WORKSPACE_SLUG" \
  --project "$PLANE_PROJECT_ID" \
  --url "http://localhost"
```

**You should see:**
```
Setting up Agentic Loop States...
 ✓ Created state: Conversation
 ✓ Created state: Sprint Active
 ...
Setting up CODEX Taxonomy Labels...
 ✓ Created parent label: governance
   ↳ Created child label: GOV-001
 ...
```

> ⚠️ If you run this twice, the states already exist and you'll see errors — that's fine.

**Go check!** Open Plane in your browser, go to your project → Board view. You should see the new state columns.

---

## Step 7: Run the Tests

```bash
pytest tests/ -v
```

**You want to see:**
```
8 passed in 0.33s ✅
```

---

## Step 8: See It In Action (Optional Cool Stuff)

### Create a Work Item Automatically

```bash
python agentic_run.py "Research the best caching strategies for Python APIs" \
  --api-key "$PLANE_API_KEY" \
  --workspace "$PLANE_WORKSPACE_SLUG" \
  --plane-project "$PLANE_PROJECT_ID" \
  --url "http://localhost"
```

Go check Plane — a new issue should appear in the **Conversation** column!

### Start the Webhook Listener

```bash
uvicorn webhook_listener:app --host 0.0.0.0 --port 9000
```

This listens for Plane events. When an issue moves to "Sprint Active", it triggers a DarkGravity pipeline.

---

## 🔥 Troubleshooting

### "This site can't be reached" at localhost
```bash
sudo docker ps  # Are the containers running?
sudo docker compose up -d  # Start them if not
```

### "Authentication failed"
The admin user might not have a password set. Run:
```bash
sudo docker exec api python manage.py shell -c "
from plane.db.models import User
u = User.objects.get(email='admin@test.com')
u.set_password('admin123')
u.is_password_autoset = False
u.save()
print('Password reset!')
"
```

### Labels return 404
Make sure you're using the **Project ID** (UUID), not the project identifier (like "AGENT").

### "plane-migrator Exited (1)"
The database wasn't ready when it tried to run. Just restart it:
```bash
sudo docker restart plane-migrator
```

### Need to start over completely
```bash
sudo docker compose down -v   # ⚠️ This deletes ALL data
sudo docker compose up -d
```

---

## 🧹 Tear It All Down

When you're done and want to delete everything:

```bash
sudo docker compose down -v
```

That removes all containers and data volumes. You're back to a clean slate.

---

## 📁 File Map

```
agentic_plane/
├── plane_bridge.py            ← The API client (talks to Plane)
├── plane_agentic_setup.py     ← Creates states + labels
├── agentic_run.py             ← Auto-creates tickets + runs pipelines
├── agentic_cost_logger.py     ← Logs token costs to tickets
├── codex_to_plane_sync.py     ← Syncs CODEX docs to Plane Pages
├── webhook_listener.py        ← Listens for Plane state changes
├── plane_views_config.json    ← Dashboard view definitions
├── docker-compose.yml         ← Boots up the Plane stack
├── .env                       ← Database/infra secrets (DO NOT COMMIT)
├── apps/api/.env              ← API-specific config (DO NOT COMMIT)
├── tests/                     ← The test suite
└── CODEX/                     ← All the governance docs
```
