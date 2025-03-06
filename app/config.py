from pydantic_settings import BaseSettings
from typing import Dict

class Settings(BaseSettings):
    GITHUB_SECRET: str = ""  # For webhook verification
    DOCKER_REGISTRY: str = "rohittru"  # Docker Hub registry
    BASE_DOMAIN: str = "stockBotWars.emerginary.com"
    APP_NETWORK: str = "app-network"
    
    ENVIRONMENTS: Dict[str, str] = {
        "feature": "feature-{}.stockBotWars.emerginary.com",
        "staging": "staging.stockBotWars.emerginary.com",
        "production": "prod.stockBotWars.emerginary.com"
    }
    
    # Docker compose template locations
    COMPOSE_TEMPLATES: Dict[str, str] = {
        "feature": "templates/feature-compose.yml",
        "staging": "templates/staging-compose.yml",
        "production": "templates/prod-compose.yml"
    }
    
    class Config:
        env_file = ".env"

settings = Settings() 