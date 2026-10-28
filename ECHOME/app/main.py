"""
ECHOME Main Application

FastAPI backend for the personal AI clone.
Connects to local Ollama model and serves Gradio frontend.
"""

import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from app.services.ollama_service import (
    check_ollama_health,
    generate_with_context,
    generate_response,
    model_available,
    OllamaError,
)
from app.config import settings

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("echome")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ECHOME",
    description="Personal AI clone - Your Voice. Your Mind. Your Digital Self.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ---------------------------------------------------------------------------
# Health check endpoint
# -------------------------------------------------------------------------
@app.get("/healthz")
async def health_check():
    """Return the application health status."""
    ollama_ok = check_ollama_health()
    return {
        "status": "ok" if ollama_ok else "degraded",
        "ollama": "available" if ollama_ok else "unavailable",
        "model": settings.default_model,
        "bind": settings.bind_address,
        "memory_db": str(settings.db_path),
    }

# ---------------------------------------------------------------------------
# Text generation endpoint
# -------------------------------------------------------------------------
@app.post("/api/generate")
async def api_generate(request: Request):
    """Generate a text response from the Ollama model."""
    body = await request.json()
    prompt = body.get("prompt", "").strip()
    model = body.get("model", settings.default_model)
    system_prompt = body.get("system_prompt", None)
    conversation_history = body.get("conversation_history", [])

    if not prompt:
        return {"error": "Prompt is required", "type": "validation_error"}

    try:
        # Use the context-aware generator if we have history, otherwise simple generate
        if conversation_history:
            response = generate_with_context(
                conversation_history=conversation_history,
                user_input=prompt,
                model=model,
            )
        else:
            response = generate_response(prompt, model=model, system_prompt=system_prompt)

        return {
            "response": response,
            "success": True,
            "model": model,
        }

    except ModelNotAvailableError as e:
        logger.warning("Model not available: %s", e)
        return {
            "error": str(e),
            "type": "model_not_available",
            "suggestion": f"Available models: {_get_available_models_llm()}",
        }
    except OllamaError as e:
        logger.error("Ollama error: %s", e)
        return {"error": str(e), "type": "ollama_error"}
    except Exception as e:
        logger.exception("Unexpected error during generation")
        return {"error": f"Internal error: {e}", "type": "internal_error"}


def _get_available_models_llm() -> list:
    """List available Ollama models via the service module."""
    from app.services.ollama_service import _get_available_models
    return _get_available_models()


# ---------------------------------------------------------------------------
# Serve the Gradio frontend (HTML page)
# -------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main ECHOME chat interface."""
    return HTMLResponse(content=_render_home(request))

def _render_home(request: Request) -> str:
    """Render the home page template."""
    # Simple inline HTML for Milestone 1
    return f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>ECHOME - Personal AI Clone</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ padding: 2rem; background: #f8f9fa; font-family: system-ui, sans-serif; }}
            .card {{ max-width: 800px; margin: 0 auto; border: none; border-radius: 8px; }}
            .chat-area {{ height: 500px; overflow-y: auto; padding: 1rem; background: white; border-radius: 8px; margin-bottom: 1rem; }}
            .message {{ margin-bottom: 1rem; padding: 0.75rem; border-radius: 8px; max-width: 85%; }}
            .user {{ background: #e3f2fd; margin-left: auto; }}
            .assistant {{ background: #f1f8e9; }}
            .input-area {{ padding-top: 1rem; display: flex; gap: 0.5rem; }}
            .btn-primary {{ flex: 1; }}
        </style>
    </head>
    <body>
    <div class="card">
        <div class="card-body">
            <h1 class="mb-3">ECHOME</h1>
            <p class="text-muted mb-3">Personal AI Clone</p>
            
            <div class="chat-area" id="chatWindow">
                <div class="message assistant">Hello! I'm ECHOME, your personal AI clone. How can I help you today?</div>
            </div>
            
            <div class="input-area">
                <input type="text" id="userInput" class="form-control" placeholder="Type your message..." style="flex: 1;">
                <button class="btn btn-primary" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        async function sendMessage() {{
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if (!text) return;
            
            input.value = '';
            const chatWindow = document.getElementById('chatWindow');
            
            // Show user message
            const userMsg = document.createElement('div');
            userMsg.className = 'message user';
            userMsg.textContent = text;
            chatWindow.appendChild(userMsg);
            
            // Show processing indicator
            const processing = document.createElement('div');
            processing.className = 'message assistant';
            processing.textContent = 'Thinking...';
            chatWindow.appendChild(processing);
            chatWindow.scrollTop = chatWindow.scrollHeight;
            
            try {{
                const response = await fetch('/api/generate', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ prompt: text }})
                }});
                
                const data = await response.json();
                
                // Remove processing indicator
                chatWindow.removeChild(processing);
                
                if (data.error) {{
                    const errMsg = document.createElement('div');
                    errMsg.className = 'message assistant';
                    errMsg.style.color = 'red';
                    errMsg.textContent = 'Error: ' + data.error;
                    chatWindow.appendChild(errMsg);
                }} else if (data.response) {{
                    const assistantMsg = document.createElement('div');
                    assistantMsg.className = 'message assistant';
                    assistantMsg.textContent = data.response;
                    chatWindow.appendChild(assistantMsg);
                }}
            }} catch (err) {{
                chatWindow.removeChild(processing);
                const errMsg = document.createElement('div');
                errMsg.className = 'message assistant';
                errMsg.style.color = 'red';
                errMsg.textContent = 'Connection error. Is Ollama running?';
                chatWindow.appendChild(errMsg);
            }}
            
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }}
        
        // Allow pressing Enter to send
        document.getElementById('userInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') sendMessage();
        }});
        
        // Initial health check
        fetch('/healthz')
            .then(r => r.json())
            .then(d => {{
                if (!d.ollama) {{
                    alert('Ollama is not available. Please start Ollama with `ollama serve`.');
                }}
            }});
    </script>
    </body>
    </html>
    """

# ---------------------------------------------------------------------------
# Startup event
# -------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("ECHOME starting up...")
    logger.info("Configuration: %s", {
        "ollama_base": settings.ollama_base_url,
        "default_model": settings.default_model,
        "bind": settings.bind_address,
        "memory_db": str(settings.db_path),
    })

    # Verify Ollama connection
    health = check_ollama_health()
    if not health:
        logger.warning(
            "Ollama health check failed. "
            "Start with: `ollama serve`"
        )
    else:
        logger.info("Ollama is running and healthy.")

    # List available models
    try:
        models = _get_available_models_llm()
        logger.info("Available Ollama models: %s", models)
    except Exception:
        logger.debug("Could not list models at startup")

    logger.info("ECHOME startup complete. Visit http://127.0.0.1:%s", settings.port)


# ---------------------------------------------------------------------------
# Helper: list available models (for API responses)
# -------------------------------------------------------------------------
def _get_available_models_llm() -> list:
    """List available Ollama models."""
    import requests
    try:
        resp = requests.get(
            f"{settings.ollama_base_url}/api/tags",
            timeout=5.0,
        )
        resp.raise_for_status()
        return [m.get("name", "") for m in resp.json().get("models", [])]
    except Exception:
        return []