import pytest
import hmac
import hashlib
import json
from fastapi.testclient import TestClient
from webhook_listener import app, verify_signature, PLANE_WEBHOOK_SECRET

client = TestClient(app)

@pytest.fixture
def valid_payload():
    return {
        "event": "issue_state_updated",
        "data": {
            "id": "iss-123",
            "name": "Test Issue",
            "state": {"name": "Sprint Active"}
        }
    }

def generate_signature(payload: dict, secret: str) -> str:
    payload_str = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    return hmac.new(secret.encode('utf-8'), payload_str, hashlib.sha256).hexdigest()

@pytest.mark.unit
def test_webhook_invalid_signature(valid_payload):
    """Verify webhook rejects requests with missing or invalid signatures.
    
    Refs: EVO-001
    Requirement: Webhook listener validates signature
    """
    # Act
    # Missing signature
    response_missing = client.post("/webhook", json=valid_payload)
    
    # Invalid signature
    invalid_signature = "sha256=invalid12345"
    response_invalid = client.post(
        "/webhook", 
        json=valid_payload, 
        headers={"X-Plane-Signature": invalid_signature}
    )
    
    # Assert
    assert response_missing.status_code == 401
    assert response_invalid.status_code == 401
    assert "Invalid signature" in response_invalid.json()["detail"]

@pytest.mark.unit
def test_webhook_valid_signature_sprint_active(valid_payload, monkeypatch):
    """Verify webhook processes valid 'Sprint Active' state changes.
    
    Refs: EVO-001
    Requirement: Webhook listener triggers DarkGravity on state change to Sprint Active
    """
    # Arrange
    signature = generate_signature(valid_payload, PLANE_WEBHOOK_SECRET)
    
    # Mock subprocess.run to avoid actually triggering DarkGravity during unit tests
    triggered = False
    def mock_run(cmd, *args, **kwargs):
        nonlocal triggered
        triggered = True
        return None
        
    import subprocess
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    # Act
    response = client.post(
        "/webhook",
        json=valid_payload,
        headers={"X-Plane-Signature": signature}
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert triggered is True
