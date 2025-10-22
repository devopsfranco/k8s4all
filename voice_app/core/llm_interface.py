"""
Local LLM Interface
Connects to Ollama for private, local learning conversations
"""

import requests
import json
from typing import Dict, Optional

class LocalLLM:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model

    def chat(self, prompt: str, conversation_history: list = None, stream: bool = False) -> str:
        """
        Send a prompt to the local LLM and get response
        """
        url = f"{self.base_url}/api/generate"

        # Build messages format
        full_prompt = prompt

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": stream,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()

            if stream:
                return self._handle_stream(response)
            else:
                result = response.json()
                return result.get("response", "")

        except requests.exceptions.ConnectionError:
            return "ERROR: Could not connect to Ollama. Please ensure Ollama is running (ollama serve)."
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _handle_stream(self, response):
        """Handle streaming responses"""
        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if "response" in chunk:
                    full_response += chunk["response"]
        return full_response

    def is_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m["name"].startswith(self.model) for m in models)
            return False
        except:
            return False

    def list_models(self) -> list:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return [m["name"] for m in response.json().get("models", [])]
            return []
        except:
            return []
