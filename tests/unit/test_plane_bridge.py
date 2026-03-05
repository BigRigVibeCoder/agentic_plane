import pytest
import os
from plane_bridge import PlaneHybridClient

@pytest.mark.unit
def test_hybrid_client_initialization_requires_api_key(monkeypatch):
    """Verify that the client requires a Plane API key to start.
    
    Refs: EVO-001
    Requirement: The Hybrid Client must fail fast if credentials are missing
    to prevent opaque failures during pipeline execution.
    """
    # Ensure no env var leaks into the test
    monkeypatch.delenv("PLANE_API_KEY", raising=False)
    
    # Act & Assert
    with pytest.raises(ValueError, match="PLANE_API_KEY is required"):
        PlaneHybridClient(api_key=None)

@pytest.mark.unit
def test_hybrid_client_initialization_success():
    """Verify the client initializes with valid credentials.
    
    Refs: EVO-001
    Requirement: The Hybrid Client holds state for both REST and MCP connections.
    """
    # Arrange
    api_key = "plane_pat_valid_key"
    workspace = "test-workspace"
    project = "test-project-id"
    
    # Act
    client = PlaneHybridClient(
        api_key=api_key,
        workspace_slug=workspace,
        project_id=project
    )
    
    # Assert (Density requirement: ≥2 per test)
    assert client.api_key == api_key
    assert client.workspace_slug == workspace
    assert client.project_id == project
