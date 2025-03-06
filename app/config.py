from pydantic import BaseModel
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    GITHUB_SECRET: str = os.getenv("GITHUB_SECRET", "")
    DOCKER_REGISTRY: str = os.getenv("DOCKER_REGISTRY", "rohittru")
    BASE_DOMAIN: str = os.getenv("BASE_DOMAIN", "stockBotWars.emerginary.com")
    APP_NETWORK: str = os.getenv("APP_NETWORK", "app-network")
    
    ENVIRONMENTS: Dict[str, str] = {
        "feature": "feature-{}.stockBotWars.emerginary.com",
        "staging": "staging.stockBotWars.emerginary.com",
        "production": "prod.stockBotWars.emerginary.com"
    }
    
    # Docker compose template locations
    COMPOSE_TEMPLATES: Dict[str, str] = {
        "feature": "nginx/templates/feature-compose.yml",
        "staging": "nginx/templates/staging-compose.yml",
        "production": "nginx/templates/prod-compose.yml"
    }

settings = Settings() 