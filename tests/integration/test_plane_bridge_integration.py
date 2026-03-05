import pytest
import requests_mock
from plane_bridge import PlaneHybridClient

@pytest.fixture
def plane_client():
    return PlaneHybridClient(
        api_key="test_api_key",
        workspace_slug="test-workspace",
        project_id="test-project",
        base_url="http://test-plane"
    )

@pytest.mark.integration
def test_create_state_rest_payload(plane_client):
    """Verify create_state properly serializes the payload to Plane's REST format.
    
    Refs: EVO-001
    Requirement: Hybrid client can create custom Agentic Loop states.
    """
    with requests_mock.Mocker() as m:
        # Arrange
        url = "http://test-plane/api/v1/workspaces/test-workspace/projects/test-project/states/"
        m.post(url, json={"id": "state-123", "name": "Sprint Active"})
        
        # Act
        result = plane_client.create_state(
            name="Sprint Active",
            group="started",
            color="#F59E0B",
            sequence=35000
        )
        
        # Assert
        assert result["id"] == "state-123"
        assert m.called_once
        
        # Verify the actual request payload sent to the API
        request_body = m.last_request.json()
        assert request_body["name"] == "Sprint Active"
        assert request_body["group"] == "started"
        assert request_body["color"] == "#F59E0B"
        assert request_body["sequence"] == 35000

@pytest.mark.integration
def test_create_label_hierarchical_payload(plane_client):
    """Verify create_label properly handles hierarchical parents.
    
    Refs: EVO-001
    Requirement: Hybrid client can create CODEX taxonomy labels with parents.
    """
    with requests_mock.Mocker() as m:
        # Arrange
        url = "http://test-plane/api/v1/workspaces/test-workspace/projects/test-project/labels/"
        m.post(url, json={"id": "label-child", "name": "GOV-001", "parent": "label-parent"})
        
        # Act
        result = plane_client.create_label(
            name="GOV-001",
            color="#6B7280",
            parent_id="label-parent"
        )
        
        # Assert (Density >= 2)
        assert result["name"] == "GOV-001"
        assert m.called_once
        
        request_body = m.last_request.json()
        assert request_body["parent"] == "label-parent"
        assert request_body["name"] == "GOV-001"
