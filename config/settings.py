"""Configuration settings for the GTM Opportunity Agent."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"
    use_local_llm: bool = False
    
    # Arcade Configuration
    arcade_api_key: Optional[str] = None
    arcade_tool_id: Optional[str] = None
    
    # Datadog Configuration
    dd_api_key: Optional[str] = None
    dd_app_key: Optional[str] = None
    dd_service: str = "gtm-opportunity-agent"
    dd_env: str = "production"
    
    # Temporal Configuration
    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"
    
    # Agent Configuration
    poll_interval_seconds: int = 30
    high_intent_threshold: int = 75
    slack_channel: str = "#gtm-opportunities"
    
    # Data paths
    mock_data_path: str = "data/mock_hockeystack_data.json"
    knowledge_base_path: str = "data/knowledge_base"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings() 