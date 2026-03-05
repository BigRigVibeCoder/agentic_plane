#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import markdown
from plane_bridge import PlaneHybridClient

def get_id_by_name(items, name, key="name"):
    """Helper to find an ID dynamically by name."""
    for item in items:
        if item.get(key) == name:
            return item.get("id")
    return None

def main():
    parser = argparse.ArgumentParser(description="Run DarkGravity Agentic Pipeline and auto-create Plane issues.")
    parser.add_argument("prompt", help="The task prompt for the agent pipeline.")
    parser.add_argument("--project", default=".", help="The target project directory.")
    parser.add_argument("--api-key", help="Plane API Key (or set PLANE_API_KEY env var)")
    parser.add_argument("--workspace", help="Workspace slug (or set PLANE_WORKSPACE_SLUG)")
    parser.add_argument("--plane-project", help="Plane Project ID (or set PLANE_PROJECT_ID)")
    parser.add_argument("--url", default="http://localhost", help="Plane Base URL")
    
    args = parser.parse_args()
    
    try:
        client = PlaneHybridClient(
            api_key=args.api_key,
            workspace_slug=args.workspace,
            project_id=args.plane_project,
            base_url=args.url
        )
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)

    print("Fetching Plane configuration...")
    try:
        states = client.get_states()
        labels = client.get_labels()
        
        conversation_state_id = get_id_by_name(states, "Conversation")
        researcher_label_id = get_id_by_name(labels, "agent:researcher")

        print("Creating Plane Work Item...")
        title = args.prompt[:60] + "..." if len(args.prompt) > 60 else args.prompt
        description_html = markdown.markdown(f"**DarkGravity Pipeline Run**\n\nPrompt: `{args.prompt}`")
        
        issue = client.create_issue(
            name=title,
            description_html=description_html,
            state_id=conversation_state_id,
            label_ids=[researcher_label_id] if researcher_label_id else []
        )
        
        identifier = issue.get("sequence_id") or issue.get("id", "Unknown")
        print(f" ✓ Created Plane Work Item: {identifier}")
        
    except Exception as e:
        print(f" ✗ API interaction failed: {e}. Launching pipeline anyway...")

    print(f"\nLaunching DarkGravity pipeline for:\n> {args.prompt}\n")
    try:
        # Use shell=False securely to pass the prompt exactly as entered
        subprocess.run(["darkgravity", "run", args.prompt, "--project", args.project], check=False)
    except FileNotFoundError:
        print("Error: 'darkgravity' command not found in PATH.")
        print("Ensure DarkGravity is installed or virtual environment is activated.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nPipeline aborted by user.")

if __name__ == "__main__":
    main()
