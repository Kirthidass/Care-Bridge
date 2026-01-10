import os
from app.core.config import settings

# Try to import Google GenAI (new package)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
    if settings.GOOGLE_API_KEY:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google.genai not available. Using fallback responses.")
    client = None

from app.tools.parser import ReportParserTool
from app.tools.explainer import ExplanationTool
from app.tools.rag import MedicalRAGTool
from app.tools.safety import SafetyCheckerTool

class CareBridgeAgent:
    """
    CARE-BRIDGE AI Agent that orchestrates medical report analysis
    """
    
    def __init__(self, role: str = "patient"):
        self.role = role
        self.parser_tool = ReportParserTool()
        self.explainer_tool = ExplanationTool()
        self.rag_tool = MedicalRAGTool()
        self.safety_tool = SafetyCheckerTool()
        
        # Initialize Gemini client if available
        if GENAI_AVAILABLE and settings.GOOGLE_API_KEY and client:
            try:
                self.client = client
                self.model_id = "gemini-2.0-flash-exp"  # Latest model
                self.ai_enabled = True
            except Exception as e:
                print(f"Could not initialize Gemini: {e}")
                self.ai_enabled = False
        else:
            self.ai_enabled = False
            self.client = None
    
    def run(self, prompt: str) -> str:
        """
        Run the agent with a given prompt
        """
        if not self.ai_enabled or not self.client:
            return "AI is currently unavailable. Using fallback response."
        
        try:
            # Add role-specific instructions
            system_instruction = f"""
            You are a medical report assistant helping a {self.role}.
            
            Guidelines:
            - If patient: Use simple, clear language. Avoid medical jargon.
            - If clinician: Provide technical, clinical insights.
            - Always be empathetic and professional
            - Never diagnose or prescribe treatment
            - Always recommend consulting healthcare providers for medical decisions
            - Use HTML formatting for better readability (bold, line breaks, etc.)
            """
            
            full_prompt = system_instruction + "\n\n" + prompt
            
            # Generate response using Gemini 2.0
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=full_prompt
            )
            
            return response.text
            
        except Exception as e:
            print(f"AI Error: {e}")
            return f"I apologize, but I'm having trouble generating a response right now. Please try again later."

def create_care_bridge_agent(role: str):
    """
    Creates a CARE-BRIDGE AI agent for the specified role
    """
    return CareBridgeAgent(role=role)

# Initializing a default agent
root_agent = create_care_bridge_agent(role="patient")