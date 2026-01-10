import requests
from app.core.config import settings
from google.adk.tools import BaseTool

# Implementation of Qwen3-VL using Hugging Face Inference API
# This avoids loading the massive 30B model locally.

class ReportParserTool(BaseTool):
    name = "report_parser"
    description = "Extracts data from medical reports using Qwen3-VL via Hugging Face API."

    def __init__(self):
        super().__init__(name="report_parser", description="Extracts data from medical reports using Qwen3-VL via Hugging Face API.")
        self.api_url = f"https://api-inference.huggingface.co/models/{settings.PARSER_MODEL_ID}"
        self.headers = {"Authorization": f"Bearer {settings.HF_API_KEY}"}

    def run(self, image_url: str):
        """
        Calls the HF API to extract data from an image.
        """
        payload = {
            "inputs": {
                "image": image_url,
                "question": "Identify and extract all medical test results, values, units, and ranges. Format as structured JSON."
            }
        }
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            return f"Error from HF API: {response.text}"
            
        return response.json()
