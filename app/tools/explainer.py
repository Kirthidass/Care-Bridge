import requests
from app.core.config import settings
from google.adk.tools import BaseTool

# Implementation of MiroThinker using Hugging Face Inference API
# This avoids loading the massive 235B model locally.

class ExplanationTool(BaseTool):
    name = "explanation_tool"
    description = "Generates medical explanations using MiroThinker via Hugging Face API."

    def __init__(self):
        super().__init__(name="explanation_tool", description="Generates medical explanations using MiroThinker via Hugging Face API.")
        self.api_url = f"https://api-inference.huggingface.co/models/{settings.THINKER_MODEL_ID}"
        self.headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}

    def run(self, data_context: str, user_role: str):
        """
        Calls the HF API for reasoning.
        """
        prompt = f"As a assistant for a {user_role}, explain these medical findings carefully: {data_context}"
        
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 1000, "return_full_text": False}
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            return f"Error from HF API: {response.text}"
            
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "No response.")
        return str(result)
