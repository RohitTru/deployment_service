# Deployment Service

A lightweight deployment service that manages Docker environments for feature branches, staging, and production deployments.

## Setup

1. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` file:
```bash
GITHUB_SECRET=your-webhook-secret
DOCKER_REGISTRY=your-registry
BASE_DOMAIN=stockBotWars.emerginary.com
```

3. Create Docker network:
```bash
docker network create app-network
```

## Running the Service

Development:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## GitHub Webhook Setup

1. Go to your repository settings
2. Add webhook:
   - Payload URL: `http://your-server:8000/webhook`
   - Content type: `application/json`
   - Secret: Same as GITHUB_SECRET in .env
   - Events: Push and Branch deletion

## Environment Structure

- Feature branches: `feature-{branch}.stockBotWars.emerginary.com`
- Staging: `staging.stockBotWars.emerginary.com`
- Production: `prod.stockBotWars.emerginary.com`

## Docker Compose Templates

Templates for different environments are in `nginx/templates/`:
- `feature-compose.yml`: Feature branch template
- `staging-compose.yml`: Staging environment template
- `prod-compose.yml`: Production environment template

## Health Check

Check service health:
```bash
curl http://localhost:8000/health
```

## Testing Webhooks

Test webhook locally:
```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{
    "ref": "refs/heads/feature-test",
    "repository": {
      "name": "test-repo"
    }
  }'
``` 