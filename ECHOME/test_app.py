"""Test script for ECHOME application."""
import json
import sys
sys.path.insert(0, "/home/amul/Desktop/Echome/ECHOME")

from app.config import settings
from app.services.ollama_service import check_ollama_health, model_available, generate_response, _get_available_models

print("=" * 60)
print("ECHOME Application Test - Milestone 1")
print("=" * 60)

# Test 1: Configuration
print("\n1. Configuration:")
print(f"   Default model: {settings.default_model}")
print(f"   Ollama base URL: {settings.ollama_base_url}")
print(f"   Bind address: {settings.bind_address}")

# Test 2: Ollama health
print("\n2. Ollama health check:")
health = check_ollama_health()
print(f"   Result: {'OK' if health else 'FAIL'}")

# Test 3: Model availability
print("\n3. Model availability:")
avail = model_available()
print(f"   llama3.2:3b available: {avail}")

# Test 4: Text generation
print("\n4. Text generation:")
try:
    result = generate_response("Hello, ECHOME!")
    print(f"   Generated: {result[:100]}{'...' if len(result) > 100 else ''}")
except Exception as e:
    print(f"   Error: {e}")

# Test 5: Available models list
print("\n5. Available models:")
models = _get_available_models()
print(f"   Models: {models}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)