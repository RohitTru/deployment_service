from fastapi import FastAPI, HTTPException, Header, Request
from app.config import settings
from app.docker_manager import DockerManager
import hmac
import hashlib
import json

app = FastAPI(title="Deployment Service")
docker_manager = DockerManager()

@app.post("/webhook")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None)):
    # Get payload
    payload = await request.body()
    
    # Verify webhook signature if secret is set
    if settings.GITHUB_SECRET and not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse webhook data
    data = await request.json()
    event = request.headers.get("X-GitHub-Event")
    
    # Handle different webhook events
    if event == "push":
        await handle_push(data)
    elif event == "delete":
        await handle_branch_deletion(data)
    
    return {"status": "processed"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

async def handle_push(data: dict):
    """Handle push events from GitHub"""
    try:
        # Extract branch name from ref
        branch = data["ref"].split("/")[-1]
        repo = data["repository"]["name"]
        
        # Handle different branch types
        if branch.startswith("feature-"):
            # Deploy to feature environment
            domain = settings.ENVIRONMENTS["feature"].format(branch)
            await docker_manager.deploy_feature(repo, branch, domain)
        
        elif branch == "staging":
            # Deploy to staging
            domain = settings.ENVIRONMENTS["staging"]
            await docker_manager.deploy_staging(repo, domain)
        
        elif branch == "main" or branch == "master":
            # Deploy to production
            domain = settings.ENVIRONMENTS["production"]
            await docker_manager.deploy_production(repo, domain)
            
    except Exception as e:
        print(f"Error handling push event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_branch_deletion(data: dict):
    """Handle branch deletion events"""
    try:
        branch = data["ref"].split("/")[-1]
        if branch.startswith("feature-"):
            await docker_manager.cleanup_feature(branch)
    except Exception as e:
        print(f"Error handling delete event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature"""
    if not settings.GITHUB_SECRET:
        return True
    
    if not signature:
        return False
    
    expected = hmac.new(
        settings.GITHUB_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 