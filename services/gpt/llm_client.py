"""
Chat model behind the GPT assistant: OpenAI (default) or a local model served by Ollama.

Ollama offers an OpenAI-compatible API, so both use the OpenAI SDK (with Instructor); only the address, the key and
the model name differ. Structured answers (`response_format` with a Pydantic schema) work with both.

Environment variables (env/api.env):

    LLM_PROVIDER      openai | ollama                       default: openai
    LLM_MODEL         model name                            default: gpt-4o-2024-08-06 (OpenAI), llama3.1 (Ollama)
    OLLAMA_BASE_URL   OpenAI-compatible endpoint of Ollama  default: http://localhost:11434/v1, in Docker
                      http://host.docker.internal:11434/v1 (Ollama on the host)
    OPENAI_API_KEY    only for OpenAI
"""

import logging

import instructor
from openai import OpenAI

from settings.settings import GPTAssistantServiceSettings
from utils.env_loader import get_env_variable, is_running_in_docker, load_env

load_env("api.env")

settings = GPTAssistantServiceSettings()


def llm_provider() -> str:
    provider = (get_env_variable("LLM_PROVIDER") or "openai").strip().lower()
    if provider not in ("openai", "ollama"):
        raise ValueError(f"LLM_PROVIDER must be 'openai' or 'ollama', not '{provider}'")
    return provider


def llm_model(openai_default: str = settings.GPT_MODEL) -> str:
    """Model name: LLM_MODEL, otherwise the default of the provider (scripts may pass their own OpenAI default)."""
    model = (get_env_variable("LLM_MODEL") or "").strip()
    if model:
        return model
    return settings.OLLAMA_DEFAULT_MODEL if llm_provider() == "ollama" else openai_default


def ollama_base_url() -> str:
    default = settings.OLLAMA_DOCKER_BASE_URL if is_running_in_docker() else settings.OLLAMA_LOCAL_BASE_URL
    return (get_env_variable("OLLAMA_BASE_URL") or default).rstrip("/")


def create_openai_client() -> OpenAI:
    """Plain OpenAI SDK client for the configured provider."""
    if llm_provider() == "ollama":
        base_url = ollama_base_url()
        logging.info(f"LLM: Ollama at {base_url}")
        # Ollama ignores the key, but the SDK requires one. Local models are slower: allow long answers.
        return OpenAI(base_url=base_url, api_key="ollama", timeout=settings.OLLAMA_TIMEOUT_SECONDS)
    logging.info("LLM: OpenAI")
    return OpenAI(api_key=get_env_variable("OPENAI_API_KEY"))


def create_llm_client():
    """Client for the configured provider, wrapped by Instructor (structured answers)."""
    return instructor.from_openai(create_openai_client())
