import os
import json
import urllib.request

from langchain_openai import ChatOpenAI


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434/v1"
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:7b"
DEFAULT_OMNIROUTE_URL = "http://localhost:20128/v1"


def get_ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)


def get_ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)


def get_omniroute_url() -> str:
    return os.getenv("OMNIROUTE_URL", DEFAULT_OMNIROUTE_URL)


def model_available_in_ollama(model_name: str) -> bool:
    """Query the local Ollama tags endpoint and return True if model is present."""
    try:
        url = get_ollama_base_url().rstrip('/') + '/api/tags'
        with urllib.request.urlopen(url, timeout=3) as r:
            data = json.load(r)
        names = [m.get('name') for m in data.get('models', [])]
        return model_name in names
    except Exception:
        return False


def build_chat_model(model: str | None = None, temperature: float = 0.2) -> ChatOpenAI:
    """Return a ChatOpenAI-backed model. Prefer local Ollama when the model is installed;
    otherwise fall back to OmniRoute if configured via OMNIROUTE_URL/OMNIROUTE_KEY.
    """
    chosen_model = model or get_ollama_model()

    # Prefer Ollama if model exists locally
    if model_available_in_ollama(chosen_model):
        return ChatOpenAI(
            base_url=get_ollama_base_url(),
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
            model=chosen_model,
            temperature=temperature,
        )

    # Else try OmniRoute if configured
    omniroute_url = os.getenv("OMNIROUTE_URL") or get_omniroute_url()
    omniroute_key = os.getenv("OMNIROUTE_KEY")
    if omniroute_key:
        return ChatOpenAI(
            base_url=omniroute_url,
            api_key=omniroute_key,
            model=chosen_model,
            temperature=temperature,
        )

    # Final attempt: return an Ollama client anyway (will raise a NotFound error when used)
    return ChatOpenAI(
        base_url=get_ollama_base_url(),
        api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
        model=chosen_model,
        temperature=temperature,
    )
