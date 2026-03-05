import os
import hmac
import hashlib
import json
import subprocess
from fastapi import FastAPI, Header, Request, HTTPException

app = FastAPI(title="Plane Agentic Webhook Listener")

# Get secret from environment or use a default for testing
PLANE_WEBHOOK_SECRET = os.environ.get("PLANE_WEBHOOK_SECRET", "test_secret_key")

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify that the webhook payload was signed by Plane."""
    if not signature_header:
        return False
        
    expected_hmac = hmac.new(
        PLANE_WEBHOOK_SECRET.encode('utf-8'),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_hmac, signature_header)

@app.post("/webhook")
async def handle_plane_webhook(request: Request, x_plane_signature: str = Header(None, alias="X-Plane-Signature")):
    """Receive and process webhooks from Plane."""
    
    # Needs the raw byte string for signature verification
    body_bytes = await request.body()
    
    # 1. Verify Authentication
    if not verify_signature(body_bytes, x_plane_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    # 2. Parse Payload
    try:
        payload = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    event_type = payload.get("event")
    data = payload.get("data", {})
    
    # 3. Handle 'issue_state_updated' events
    if event_type == "issue_state_updated":
        new_state = data.get("state", {}).get("name")
        issue_name = data.get("name")
        
        # Trigger DarkGravity when an issue enters "Sprint Active"
        if new_state == "Sprint Active" and issue_name:
            print(f"Triggering DarkGravity pipeline for issue: {issue_name}")
            # Note: In a production environment, this should be dispatched 
            # to a background task queue (like Celery) rather than blocking the webhook response.
            try:
                # We use shell=False for security, assuming darkgravity is in PATH or alias.
                # Project path should be configurable, using cwd for now.
                subprocess.run(
                    ["darkgravity", "run", f'"{issue_name}"', "--project", "."],
                    check=False  # We don't want the webhook to crash if DG fails
                )
            except Exception as e:
                print(f"Failed to trigger DarkGravity: {e}")
                
    return {"status": "processed", "event": event_type}

if __name__ == "__main__":
    import uvicorn
    # Listen on all interfaces, port 8081 per EVO-001 specification
    uvicorn.run(app, host="0.0.0.0", port=8081)
