#!/usr/bin/env python3
import os
import argparse
import markdown
import yaml
import re
from pathlib import Path
from plane_bridge import PlaneHybridClient

CODEX_DIR = Path("CODEX")
FRONTMATTER_REGEX = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

def parse_markdown_file(file_path: Path):
    """Extract frontmatter and content from a markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = FRONTMATTER_REGEX.match(content)
    metadata = {}
    markdown_content = content

    if match:
        try:
            metadata = yaml.safe_load(match.group(1)) or {}
            markdown_content = content[match.end():].lstrip()
        except yaml.YAMLError as e:
            print(f"Warning: Failed to parse frontmatter in {file_path}: {e}")

    # Fallbacks for title
    title = metadata.get("title")
    if not title:
        title = file_path.stem

    return title, markdown_content

def sync_codex_to_plane(client: PlaneHybridClient):
    """Sync all Markdown files in CODEX to Plane Pages."""
    print("Fetching existing Plane Pages...")
    try:
        existing_pages = client.list_pages()
        # Map title to page_id for quick lookup
        page_map = {p.get("name"): p.get("id") for p in existing_pages if p.get("name")}
    except Exception as e:
        print(f"Error fetching pages: {e}")
        return

    print("Scanning CODEX directory...")
    for root, _, files in os.walk(CODEX_DIR):
        for file in files:
            if not file.endswith(".md"):
                continue

            # Skip templates or ignored directories if necessary
            # For now, we sync everything in CODEX
            if "_templates" in root:
                continue

            file_path = Path(root) / file
            title, markdown_content = parse_markdown_file(file_path)
            
            # Convert markdown to HTML (Plane Pages use HTML under the hood)
            # Plane's rich text editor might strip some complex HTML, but we do our best.
            description_html = markdown.markdown(
                markdown_content, 
                extensions=['tables', 'fenced_code', 'nl2br']
            )

            # Check if page already exists
            page_id = page_map.get(title)
            
            try:
                if page_id:
                    print(f"Updating page: {title}")
                    client.update_page(page_id, title, description_html)
                else:
                    print(f"Creating page: {title}")
                    client.create_page(title, description_html)
            except Exception as e:
                print(f"Failed to sync {title}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync CODEX documentation to Plane Pages.")
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
        exit(1)
        
    sync_codex_to_plane(client)
    print("Sync complete.")
