#!/usr/bin/env python3
import sys
import argparse
from plane_bridge import PlaneHybridClient

def main():
    parser = argparse.ArgumentParser(description="Log Agentic Pipeline token usage to a Plane Work Item via Worklogs.")
    parser.add_argument("issue_id", help="Plane Issue/Work Item ID to log against.")
    parser.add_argument("--tokens", type=int, required=True, help="Total LLM tokens consumed.")
    parser.add_argument("--cost", type=float, required=True, help="Total cost in USD.")
    parser.add_argument("--agent", default="darkgravity", help="The name of the agent or pipeline.")
    
    parser.add_argument("--api-key", help="Plane API Key (or set PLANE_API_KEY env var)")
    parser.add_argument("--workspace", help="Workspace slug (or set PLANE_WORKSPACE_SLUG env var)")
    parser.add_argument("--project", help="Plane Project ID (or set PLANE_PROJECT_ID env var)")
    parser.add_argument("--url", default="http://localhost", help="Plane Base URL")
    
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

    description = f"**{args.agent} execution**\n- Tokens consumed: {args.tokens:,}\n- Estimated Cost: ${args.cost:.4f}"
    
    # Plane requires duration. We use 1 minute generically to represent 1 agentic cycle execution.
    try:
        worklog = client.add_worklog(
            issue_id=args.issue_id,
            duration_minutes=1,
            description=description
        )
        if worklog.get("id"):
            print(f"✓ Logged ${args.cost:.4f} ({args.tokens:,} tokens) to issue {args.issue_id}")
        else:
            print(f"✗ Failed to log cost. API Response: {worklog}")
    except Exception as e:
        print(f"Error communicating with Plane API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
