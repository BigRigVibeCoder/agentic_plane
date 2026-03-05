#!/usr/bin/env python3
import os
import sys
import argparse
from plane_bridge import PlaneHybridClient

AGENTIC_STATES = [
    {"name": "Conversation", "group": "backlog", "color": "#6366F1", "sequence": 15000},
    {"name": "Spec Review", "group": "unstarted", "color": "#8B5CF6", "sequence": 25000},
    {"name": "Sprint Active", "group": "started", "color": "#F59E0B", "sequence": 35000},
    {"name": "Checkpoint", "group": "started", "color": "#3B82F6", "sequence": 40000},
    {"name": "Verification", "group": "started", "color": "#06B6D4", "sequence": 45000},
    {"name": "Merge Ready", "group": "started", "color": "#10B981", "sequence": 50000},
    {"name": "Deployed", "group": "completed", "color": "#46A758", "sequence": 55000},
    {"name": "Cancelled", "group": "cancelled", "color": "#9AA4BC", "sequence": 65000},
]

CODEX_LABELS = {
    "governance": ["GOV-001", "GOV-002", "GOV-003", "GOV-004", "GOV-005", "GOV-006"],
    "agent": ["agent:architect", "agent:researcher", "agent:coder", "agent:tester"],
    "priority": ["P0-critical", "P1-high", "P2-medium", "P3-low"],
    "type": ["blueprint", "defect", "research", "evolution", "feature"]
}

def setup_states(client: PlaneHybridClient):
    print("Setting up Agentic Loop States...")
    for state in AGENTIC_STATES:
        try:
            client.create_state(**state)
            print(f" ✓ Created state: {state['name']}")
        except Exception as e:
            print(f" ✗ Failed to create state {state['name']}: {e}")

def setup_labels(client: PlaneHybridClient):
    print("\nSetting up CODEX Taxonomy Labels...")
    for parent, children in CODEX_LABELS.items():
        try:
            # Create parent label
            parent_resp = client.create_label(name=parent, color="#4B5563")
            parent_id = parent_resp.get("id")
            print(f" ✓ Created parent label: {parent}")
            
            # Create children
            for child in children:
                try:
                    client.create_label(name=child, color="#6B7280", parent_id=parent_id)
                    print(f"   ↳ Created child label: {child}")
                except Exception as e:
                    print(f"   ✗ Failed to create child label {child}: {e}")
        except Exception as e:
            print(f" ✗ Failed to create parent label {parent}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure Plane API with DarkGravity Agentic Loop defaults.")
    parser.add_argument("--api-key", help="Plane API Key (or set PLANE_API_KEY env var)")
    parser.add_argument("--workspace", help="Workspace slug (or set PLANE_WORKSPACE_SLUG env var)")
    parser.add_argument("--project", help="Project ID (or set PLANE_PROJECT_ID env var)")
    parser.add_argument("--url", default="http://localhost", help="Plane Base URL (default: http://localhost)")
    
    args = parser.parse_args()
    
    try:
        client = PlaneHybridClient(
            api_key=args.api_key,
            workspace_slug=args.workspace,
            project_id=args.project,
            base_url=args.url
        )
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
        
    setup_states(client)
    setup_labels(client)
    print("\nSetup complete!")
