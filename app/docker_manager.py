import docker
import asyncio
from app.config import settings
import yaml
import os
from typing import Optional

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self._ensure_network()
    
    def _ensure_network(self):
        """Ensure the app network exists"""
        try:
            self.client.networks.get(settings.APP_NETWORK)
        except docker.errors.NotFound:
            self.client.networks.create(settings.APP_NETWORK, driver="bridge")
    
    async def deploy_feature(self, repo: str, branch: str, domain: str):
        """Deploy a feature branch environment"""
        env_vars = {
            "DOMAIN": domain,
            "BRANCH": branch,
            "DOCKER_REGISTRY": settings.DOCKER_REGISTRY,
            "REPO": repo
        }
        
        await self._deploy_environment("feature", env_vars)
    
    async def deploy_staging(self, repo: str, domain: str):
        """Deploy to staging environment"""
        env_vars = {
            "DOMAIN": domain,
            "DOCKER_REGISTRY": settings.DOCKER_REGISTRY,
            "REPO": repo
        }
        
        await self._deploy_environment("staging", env_vars)
    
    async def deploy_production(self, repo: str, domain: str):
        """Deploy to production environment"""
        env_vars = {
            "DOMAIN": domain,
            "DOCKER_REGISTRY": settings.DOCKER_REGISTRY,
            "REPO": repo
        }
        
        await self._deploy_environment("production", env_vars)
    
    async def _deploy_environment(self, env_type: str, env_vars: dict):
        """Deploy to a specific environment using docker-compose"""
        compose_file = settings.COMPOSE_TEMPLATES[env_type]
        
        # Load and process template
        with open(compose_file, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        # Update compose configuration with environment variables
        self._update_compose_config(compose_config, env_vars)
        
        # Write temporary compose file
        tmp_compose = f"docker-compose-{env_vars.get('BRANCH', env_type)}.yml"
        with open(tmp_compose, 'w') as f:
            yaml.dump(compose_config, f)
        
        try:
            # Run docker-compose up
            process = await asyncio.create_subprocess_exec(
                'docker-compose',
                '-f', tmp_compose,
                'up',
                '-d',
                '--remove-orphans'
            )
            await process.wait()
        finally:
            # Cleanup temporary file
            if os.path.exists(tmp_compose):
                os.remove(tmp_compose)
    
    def _update_compose_config(self, config: dict, env_vars: dict):
        """Update docker-compose configuration with environment variables"""
        for service in config.get('services', {}).values():
            if 'environment' not in service:
                service['environment'] = {}
            
            # Update environment variables
            service['environment'].update(env_vars)
    
    async def cleanup_feature(self, branch: str):
        """Cleanup a feature environment"""
        compose_file = settings.COMPOSE_TEMPLATES['feature']
        tmp_compose = f"docker-compose-{branch}.yml"
        
        try:
            process = await asyncio.create_subprocess_exec(
                'docker-compose',
                '-f', tmp_compose,
                'down',
                '--remove-orphans',
                '--volumes'
            )
            await process.wait()
        except Exception as e:
            print(f"Error cleaning up feature environment: {e}")
        finally:
            if os.path.exists(tmp_compose):
                os.remove(tmp_compose)
    
    async def check_health(self, container_name: str) -> bool:
        """Check if a container is healthy"""
        try:
            container = self.client.containers.get(container_name)
            return container.status == "running"
        except docker.errors.NotFound:
            return False 