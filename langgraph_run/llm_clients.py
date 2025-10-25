"""
Configuration and client management for various LLM providers.
This module provides swappable client implementations for different frameworks.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import aiplatform


class LLMProvider(Enum):
    """Enumeration of supported LLM providers."""

    VERTEX_AI = "vertex_ai"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class LLMConfig:
    """Configuration class for LLM clients."""

    provider: LLMProvider
    model_name: str
    project_id: Optional[str] = None
    location: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 8192
    top_p: float = 0.95
    top_k: int = 40


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the client connection."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using the LLM."""
        pass

    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Generate structured JSON output using the LLM."""
        pass


class VertexAIClient(BaseLLMClient):
    """Vertex AI implementation of the LLM client."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.model = None

    def initialize(self) -> None:
        """Initialize Vertex AI client."""
        if not self.config.project_id:
            raise ValueError("project_id is required for Vertex AI")

        location = self.config.location or "us-central1"

        # Initialize Vertex AI
        vertexai.init(project=self.config.project_id, location=location)

        # Initialize the model
        self.model = GenerativeModel(
            model_name=self.config.model_name,
            generation_config={
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_tokens,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
            },
        )

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Vertex AI."""
        if not self.model:
            self.initialize()

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

        response = self.model.generate_content(full_prompt)
        return response.text

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Generate structured JSON using Vertex AI."""
        if not self.model:
            self.initialize()

        json_instruction = (
            "\nReturn only valid JSON format. No additional text or explanation."
        )
        if schema:
            json_instruction += f"\nFollow this schema: {schema}"

        full_prompt = prompt + json_instruction
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {full_prompt}"

        response = self.model.generate_content(full_prompt)

        try:
            import json

            return json.loads(response.text.strip())
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON response: {e}\nResponse: {response.text}"
            )


class OpenAIClient(BaseLLMClient):
    """OpenAI implementation of the LLM client (placeholder for future implementation)."""

    def initialize(self) -> None:
        """Initialize OpenAI client."""
        # Placeholder for OpenAI initialization
        raise NotImplementedError("OpenAI client not implemented yet")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using OpenAI."""
        raise NotImplementedError("OpenAI client not implemented yet")

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Generate structured JSON using OpenAI."""
        raise NotImplementedError("OpenAI client not implemented yet")


class AnthropicClient(BaseLLMClient):
    """Anthropic implementation of the LLM client (placeholder for future implementation)."""

    def initialize(self) -> None:
        """Initialize Anthropic client."""
        # Placeholder for Anthropic initialization
        raise NotImplementedError("Anthropic client not implemented yet")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Anthropic."""
        raise NotImplementedError("Anthropic client not implemented yet")

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Generate structured JSON using Anthropic."""
        raise NotImplementedError("Anthropic client not implemented yet")


class LLMClientFactory:
    """Factory class for creating LLM clients."""

    @staticmethod
    def create_client(config: LLMConfig) -> BaseLLMClient:
        """Create an LLM client based on the provider configuration."""
        if config.provider == LLMProvider.VERTEX_AI:
            return VertexAIClient(config)
        elif config.provider == LLMProvider.OPENAI:
            return OpenAIClient(config)
        elif config.provider == LLMProvider.ANTHROPIC:
            return AnthropicClient(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")


# Configuration from environment variables
def get_default_vertex_config() -> LLMConfig:
    """Get default Vertex AI configuration from environment variables."""
    return LLMConfig(
        provider=LLMProvider.VERTEX_AI,
        model_name=os.getenv("VERTEX_MODEL_NAME", "gemini-1.5-pro"),
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("VERTEX_LOCATION", "us-central1"),
        temperature=float(os.getenv("VERTEX_TEMPERATURE", "0.1")),
        max_tokens=int(os.getenv("VERTEX_MAX_TOKENS", "8192")),
        top_p=float(os.getenv("VERTEX_TOP_P", "0.95")),
        top_k=int(os.getenv("VERTEX_TOP_K", "40")),
    )


def get_default_openai_config() -> LLMConfig:
    """Get default OpenAI configuration from environment variables."""
    return LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
        max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "8192")),
    )


def get_default_anthropic_config() -> LLMConfig:
    """Get default Anthropic configuration from environment variables."""
    return LLMConfig(
        provider=LLMProvider.ANTHROPIC,
        model_name=os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-sonnet-20240229"),
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.1")),
        max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "8192")),
    )


# Convenience function to get a client with default configuration
def get_default_client(
    provider: Union[str, LLMProvider] = LLMProvider.VERTEX_AI,
) -> BaseLLMClient:
    """Get a client with default configuration for the specified provider."""
    if isinstance(provider, str):
        provider = LLMProvider(provider)

    if provider == LLMProvider.VERTEX_AI:
        config = get_default_vertex_config()
    elif provider == LLMProvider.OPENAI:
        config = get_default_openai_config()
    elif provider == LLMProvider.ANTHROPIC:
        config = get_default_anthropic_config()
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    return LLMClientFactory.create_client(config)
