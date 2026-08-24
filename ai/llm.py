import os
import json
import logging
import urllib.request
from typing import Any, Optional

from langchain_openai import ChatOpenAI

logger = logging.getLogger("zacma.ai")

DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434/v1"
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:7b"
DEFAULT_OMNIROUTE_URL = "http://localhost:20128/v1"


def get_ai_provider() -> str:
    """Return active AI provider from environment: ollama, openai, anthropic, grok, openrouter, omniroute."""
    return os.getenv("AI_PROVIDER", "ollama").lower().strip()


def get_ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)


def get_ollama_model() -> str:
    return os.getenv("AI_MODEL") or os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)


def get_omniroute_url() -> str:
    return os.getenv("OMNIROUTE_URL", DEFAULT_OMNIROUTE_URL)


def model_available_in_ollama(model_name: str) -> bool:
    """Query the local Ollama tags endpoint and return True if model is present."""
    try:
        url = get_ollama_base_url().rstrip('/') + '/api/tags'
        with urllib.request.urlopen(url, timeout=0.2) as r:
            data = json.load(r)
        names = [m.get('name') for m in data.get('models', [])]
        return model_name in names
    except Exception:
        return False


def build_chat_model(model: Optional[str] = None, temperature: float = 0.2) -> Any:
    """Return a configured chat model supporting multiple providers via AI_PROVIDER env variable:
    - 'gemini': Google Gemini Models (e.g. gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash)
    - 'ollama': Local Ollama inference server (qwen, llama, deepseek)
    - 'openai': OpenAI Official API (e.g. gpt-4o, gpt-4o-mini)
    - 'anthropic': Anthropic Claude models
    - 'grok' / 'xai': xAI Grok API (https://api.x.ai/v1)
    - 'openrouter' / 'omniroute': Multi-model gateway proxy
    """
    provider = get_ai_provider()
    chosen_model = model or get_ollama_model()

    # 0. Google Gemini Provider (Primary Cloud Provider)
    if provider in {"gemini", "google"}:
        api_key = os.getenv("GEMINI_API_KEY", "")
        base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
        target_model = chosen_model if chosen_model and "qwen" not in chosen_model else "gemini-1.5-flash"
        return ChatOpenAI(
            base_url=base_url,
            api_key=api_key or "demo-gemini-key",
            model=target_model,
            temperature=temperature,
        )

    # 1. OpenAI Direct
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        target_model = chosen_model if chosen_model and "qwen" not in chosen_model else "gpt-4o-mini"
        return ChatOpenAI(
            base_url=base_url,
            api_key=api_key or "demo-key",
            model=target_model,
            temperature=temperature,
        )

    # 2. xAI / Grok
    if provider in {"grok", "xai"}:
        api_key = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY", "")
        base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
        target_model = chosen_model if chosen_model and "qwen" not in chosen_model else "grok-beta"
        return ChatOpenAI(
            base_url=base_url,
            api_key=api_key or "demo-key",
            model=target_model,
            temperature=temperature,
        )

    # 3. OpenRouter / OmniRoute Gateway
    if provider in {"openrouter", "omniroute"}:
        gateway_url = os.getenv("OMNIROUTE_URL") or os.getenv("OPENROUTER_BASE_URL", get_omniroute_url())
        gateway_key = os.getenv("OMNIROUTE_KEY") or os.getenv("OPENROUTER_API_KEY", "")
        return ChatOpenAI(
            base_url=gateway_url,
            api_key=gateway_key or "demo-key",
            model=chosen_model,
            temperature=temperature,
        )

    # 4. Ollama (Default & Local Demo Mode)
    if model_available_in_ollama(chosen_model):
        return ChatOpenAI(
            base_url=get_ollama_base_url(),
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
            model=chosen_model,
            temperature=temperature,
        )

    # Fallback to OmniRoute if key exists
    omniroute_key = os.getenv("OMNIROUTE_KEY")
    if omniroute_key:
        return ChatOpenAI(
            base_url=get_omniroute_url(),
            api_key=omniroute_key,
            model=chosen_model,
            temperature=temperature,
        )

    # Final fallback to Ollama client
    return ChatOpenAI(
        base_url=get_ollama_base_url(),
        api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
        model=chosen_model,
        temperature=temperature,
    )

