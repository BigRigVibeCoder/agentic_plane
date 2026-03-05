import os
import requests
from typing import Optional, Dict, Any, List

class PlaneHybridClient:
    """A hybrid client for Plane that uses both REST and MCP APIs.
    
    Provides methods for interacting with Plane Workspaces, Projects,
    Issues (Work Items), States, Labels, comments, and pages.
    """

    def __init__(
        self, 
        api_key: Optional[str] = None, 
        workspace_slug: Optional[str] = None, 
        project_id: Optional[str] = None,
        base_url: str = "http://localhost"
    ):
        self.api_key = api_key or os.environ.get("PLANE_API_KEY")
        if not self.api_key:
            raise ValueError("PLANE_API_KEY is required.")
            
        self.workspace_slug = workspace_slug or os.environ.get("PLANE_WORKSPACE_SLUG")
        self.project_id = project_id or os.environ.get("PLANE_PROJECT_ID")
        self.base_url = base_url.rstrip("/")
        
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        })

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a REST API request to Plane."""
        url = f"{self.base_url}/api/v1{endpoint}"
        response = self.session.request(method, url, **kwargs)
        
        if not response.ok:
            error_msg = f"Plane API Error ({response.status_code}): {response.text}"
            raise requests.exceptions.HTTPError(error_msg, response=response)
            
        # Some endpoints might return empty bodies on success (e.g. DELETE)
        if response.text:
            return response.json()
        return {}
        
    def create_state(self, name: str, group: str, color: str, sequence: int, description: str = "") -> Dict[str, Any]:
        """Create a custom state for the Agentic Loop via REST API."""
        if not self.workspace_slug or not self.project_id:
            raise ValueError("workspace_slug and project_id are required")
            
        endpoint = f"/workspaces/{self.workspace_slug}/projects/{self.project_id}/states/"
        payload = {
            "name": name,
            "color": color,
            "group": group,
            "sequence": sequence,
            "description": description
        }
        return self._request("POST", endpoint, json=payload)
        
    def create_label(self, name: str, color: str = "#000000", parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a CODEX taxonomy label via REST API."""
        if not self.workspace_slug:
            raise ValueError("workspace_slug is required")
            
        endpoint = f"/workspaces/{self.workspace_slug}/labels/"
        payload = {
            "name": name,
            "color": color
        }
        if parent_id:
            payload["parent"] = parent_id
            
        return self._request("POST", endpoint, json=payload)

    def add_comment(self, issue_id: str, comment_html: str) -> Dict[str, Any]:
        """Add a comment to a specific issue/work item via REST API."""
        if not self.workspace_slug or not self.project_id:
            raise ValueError("workspace_slug and project_id are required")
            
        endpoint = f"/workspaces/{self.workspace_slug}/projects/{self.project_id}/issues/{issue_id}/comments/"
        payload = {
            "comment_html": comment_html
        }
        return self._request("POST", endpoint, json=payload)

    def create_page(self, title: str, description_html: str) -> Dict[str, Any]:
        """Create a new page in a project via REST API."""
        if not self.workspace_slug or not self.project_id:
            raise ValueError("workspace_slug and project_id are required")
            
        endpoint = f"/workspaces/{self.workspace_slug}/projects/{self.project_id}/pages/"
        payload = {
            "name": title,
            "description_html": description_html
        }
        return self._request("POST", endpoint, json=payload)
