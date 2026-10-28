"""
ECHOME Ollama Service

Handles communication with the local Ollama API for text generation.
Connects to llama3.2:3b model running locally via Ollama.

Environment variables (via .env or os.getenv):
  OLLAMA_BASE_URL: http://127.0.0.1:11434 (default)
  DEFAULT_MODEL: llama3.2:3b (default)
"""

import logging
import os
from typing import Any, Dict, Optional

import requests

from app.config import settings

logger = logging.getLogger(__name__)

#: Ollama generation endpoint
OLLAMA_API = f"{settings.ollama_base_url}/api/generate"

#: Timeout for Ollama requests in seconds
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "120"))


class OllamaError(RuntimeError):
    """Raised when Ollama communication fails."""


class ModelNotAvailableError(OllamaError):
    """Raised when the configured model is not found on the Ollama server."""


def check_ollama_health() -> bool:
    """Check if the Ollama server is reachable and healthy."""
    try:
        resp = requests.get(
            f"{settings.ollama_base_url}/api/tags",
            timeout=5.0,
        )
        resp.raise_for_status()
        models = resp.json().get("models", [])
        logger.info("Ollama health check OK, found models: %s", [m.get("name") for m in models])
        return True
    except Exception as e:
        logger.warning("Ollama health check failed: %s", e)
        return False


def model_available(model_name: str = None) -> bool:
    """Check if a specific model is available on the Ollama server."""
    if model_name is None:
        model_name = settings.default_model
    try:
        resp = requests.get(
            f"{settings.ollama_base_url}/api/tags",
            timeout=5.0,
        )
        resp.raise_for_status()
        models = [m.get("name", "") for m in resp.json().get("models", [])]
        available = model_name in models
        logger.info("Model %s available: %s", model_name, available)
        return available
    except Exception as e:
        logger.warning("Failed to check model availability: %s", e)
        return False


def generate_response(
    prompt: str,
    model: str = None,
    system_prompt: str = None,
    stream: bool = False,
    **kwargs: Any,
) -> str:
    """
    Generate a text response from the Ollama model.

    Args:
        prompt: The user's input prompt.
        model: The Ollama model name. Defaults to settings.default_model.
        system_prompt: Optional system prompt to set context/behavior.
        stream: Whether to stream the response (not supported in this wrapper).
        **kwargs: Additional parameters to pass to Ollama (e.g., temperature, top_p).

    Returns:
        The generated text response.

    Raises:
        OllamaError: If the model cannot be reached or fails to generate.
        ModelNotAvailableError: If the configured model is not available.
    """
    if model is None:
        model = settings.default_model

    if not model_available(model):
        raise ModelNotAvailableError(
            f"Model '{model}' is not available on Ollama server at {settings.ollama_base_url}. "
            f"Available models: {_get_available_models()}"
        )

    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        **kwargs,
    }

    if system_prompt:
        payload["system"] = system_prompt

    try:
        resp = requests.post(
            OLLAMA_API,
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )
        resp.raise_for_status()

        result = resp.json()
        generated_text = result.get("response", "").strip()

        if not generated_text:
            raise OllamaError("Ollama returned an empty response.")

        logger.info("Ollama response generated (%d chars)", len(generated_text))
        return generated_text

    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out after %s seconds", OLLAMA_TIMEOUT)
        raise OllamaError(f"Ollama request timed out after {OLLAMA_TIMEOUT}s")
    except requests.exceptions.ConnectionError:
        logger.error("Ollama server not reachable at %s", settings.ollama_base_url)
        raise OllamaError(
            f"Cannot connect to Ollama at {settings.ollama_base_url}. "
            "Ensure Ollama is running (`ollama serve`)."
        )
    except requests.exceptions.HTTPError as e:
        logger.error("Ollama HTTP error: %s", e)
        raise OllamaError(f"Ollama HTTP error: {e}")
    except json.JSONDecodeError as e:
        logger.error("Ollama returned invalid JSON: %s", e)
        raise OllamaError(f"Ollama returned invalid response: {e}")


def _get_available_models() -> list:
    """Helper to list available Ollama models."""
    try:
        resp = requests.get(
            f"{settings.ollama_base_url}/api/tags",
            timeout=5.0,
        )
        resp.raise_for_status()
        return [m.get("name", "") for m in resp.json().get("models", [])]
    except Exception:
        return []


def generate_with_context(
    conversation_history: list,
    user_input: str,
    model: str = None,
) -> str:
    """
    Generate a response using conversation context.

    Formats the conversation history and user input into a prompt suitable
    for the Llama model.

    Args:
        conversation_history: List of dicts with 'role' and 'content' keys.
        user_input: The current user message.
        model: Override model name.

    Returns:
        Generated response text.
    """
    # Build a simple chat prompt for Llama
    prompt_parts = []

    # Add system prompt if we have conversation context
    if conversation_history:
        # Format: role/content pairs
        for turn in conversation_history[-10:]:  # Last 10 turns for context
            role = turn.get("role", "user")
            content = turn.get("content", "")
            prompt_parts.append(f"{role}: {content}")
    else:
        # Default system prompt for ECHOME
        prompt_parts.append(
            "You are ECHOME, a personal AI clone. "
            "Be helpful, conversational, and remember user preferences "
            "when relevant. Keep responses concise but intelligent."
        )

    # Add the current user input
    prompt_parts.append(f"user: {user_input}")
    prompt_parts.append("assistant:")

    full_prompt = "\n".join(prompt_parts)
    return generate_response(full_prompt, model=model)