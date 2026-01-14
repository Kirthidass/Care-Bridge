import os
import httpx
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from app.core.config import settings

# Hugging Face API Configuration (Primary)
HF_API_KEY = settings.HF_API_KEY or os.getenv("HF_API_KEY", "")
HF_LLM_MODEL_ID = os.getenv("HF_LLM_MODEL_ID", "meta-llama/Llama-3.3-70B-Instruct")
HF_ROUTER_CHAT_URL = os.getenv("HF_ROUTER_CHAT_URL", "https://router.huggingface.co/v1/chat/completions")
HF_HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}
HF_AVAILABLE = bool(HF_API_KEY)

# Try to import Google GenAI (fallback)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
    if settings.GOOGLE_API_KEY:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
except ImportError:
    GENAI_AVAILABLE = False
    print("Warning: google.genai not available.")
    client = None

if HF_AVAILABLE:
    print(f"✓ Agent HF API Ready (Model: {HF_LLM_MODEL_ID})")
elif GENAI_AVAILABLE:
    print("✓ Agent Gemini API Ready (fallback)")
else:
    print("⚠ No AI API available for agents - using fallback responses")

from app.tools.parser import ReportParserTool
from app.tools.explainer import ExplanationTool
from app.tools.rag import MedicalRAGTool
from app.tools.safety import SafetyCheckerTool


def call_huggingface_chat_sync(messages: list, max_tokens: int = 500) -> Optional[str]:
    """Synchronous call to Hugging Face Inference API for chat completions."""
    if not HF_API_KEY:
        return None
    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                HF_ROUTER_CHAT_URL,
                headers=HF_HEADERS,
                json={
                    "model": HF_LLM_MODEL_ID,
                    "messages": messages,
                    "max_tokens": max_tokens,
                },
            )
            if resp.status_code != 200:
                print(f"HF Chat Error: {resp.status_code}")
                return None
            data = resp.json()
            choices = (data or {}).get("choices") or []
            if not choices:
                return None
            content = ((choices[0] or {}).get("message") or {}).get("content")
            return content.strip() if isinstance(content, str) and content.strip() else None
    except Exception as e:
        print(f"HF Chat Exception: {e}")
        return None


# ==================== BASE AGENT CLASS ====================
class BaseCareBridgeAgent(ABC):
    """
    Base Agent class following multi-agent orchestration architecture
    """
    
    def __init__(self, role: str):
        self.role = role
        self.agent_name = f"{role.upper()}_AGENT"
        self.conversation_history: List[Dict[str, str]] = []
        
        # Prioritize Hugging Face API (more reliable, working quota)
        if HF_AVAILABLE:
            self.use_hf = True
            self.ai_enabled = True
            self.client = None  # Not needed for HF
        elif GENAI_AVAILABLE and settings.GOOGLE_API_KEY and client:
            try:
                self.use_hf = False
                self.client = client
                self.model_id = "gemini-2.0-flash-exp"
                self.ai_enabled = True
            except Exception as e:
                print(f"Could not initialize Gemini for {self.agent_name}: {e}")
                self.ai_enabled = False
                self.use_hf = False
        else:
            self.ai_enabled = False
            self.use_hf = False
            self.client = None
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Returns role-specific system prompt"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[str]:
        """Returns list of available tools for this agent"""
        pass
    
    @abstractmethod
    def process_request(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Process a request with role-specific logic"""
        pass
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})
    
    def get_history_context(self, max_messages: int = 5) -> str:
        """Get recent conversation history as context"""
        recent = self.conversation_history[-max_messages:]
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent])


# ==================== PATIENT AGENT ====================
class PatientAgent(BaseCareBridgeAgent):
    """
    Specialized Agent for Patient interactions
    - Simplifies medical terminology
    - Focuses on patient education
    - Emphasizes safety and redirection to healthcare providers
    - Uses empathetic, reassuring communication
    """
    
    def __init__(self):
        super().__init__(role="patient")
        self.parser_tool = ReportParserTool()
        self.explainer_tool = ExplanationTool()
        self.rag_tool = MedicalRAGTool()
        self.safety_tool = SafetyCheckerTool()
        
        # Patient-specific configuration
        self.max_complexity = "simple"
        self.enable_guardrails = True
        self.explanation_style = "layperson"
    
    def get_system_prompt(self) -> str:
        return """
        You are a compassionate medical report assistant helping a PATIENT understand their health reports.
        
        YOUR AUDIENCE: A patient with NO medical training who needs simple, clear explanations.
        
        COMMUNICATION STYLE:
        - Use simple, everyday language - NO medical jargon
        - Explain terms like you're talking to a friend or family member
        - Use analogies (e.g., "Think of hemoglobin like delivery trucks carrying oxygen")
        - Be warm, empathetic, and reassuring
        - Use emojis to make content friendly: 📋 ✅ ⚠️ 💡 ❓
        
        REQUIRED OUTPUT SECTIONS (use these exact headings):
        <h3>📋 What This Report Is About</h3>
        - 2-3 sentence overview of what tests were done
        
        <h3>✅ Good News First</h3>
        - List all NORMAL values with simple explanations
        - Reassure the patient about healthy results
        
        <h3>⚠️ Things to Discuss with Your Doctor</h3>
        - List any abnormal values in simple terms
        - Explain what each test measures (no medical jargon)
        - Do NOT diagnose - just explain what the numbers mean
        
        <h3>❓ Questions to Ask Your Doctor</h3>
        - 3-5 helpful questions based on the results
        
        <h3>💡 Helpful Tips</h3>
        - General wellness suggestions (stay hydrated, follow-up timing, etc.)
        
        SAFETY RULES (CRITICAL):
        - NEVER say "You have [disease]" or make diagnoses
        - NEVER recommend medications or treatments
        - Always encourage discussing results with their doctor
        
        FORMAT: Use HTML with <h3>, <ul>, <li>, <b>, <br> tags
        """
    
    def get_tools(self) -> List[str]:
        return [
            "report_parser",      # Parse medical reports
            "simple_explainer",   # Simplified explanations
            "medical_rag",        # General medical knowledge lookup
            "safety_checker"      # Safety and guardrails
        ]
    
    def process_request(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Process patient request with safety checks and simplification"""
        if not self.ai_enabled:
            return self._get_patient_fallback_response(prompt, context)
        
        # Clear history for fresh context per request
        self.conversation_history = []
        
        try:
            # Build messages for HuggingFace API
            system_prompt = self.get_system_prompt()
            
            # Add report context to system prompt
            if context and context.get('report_data'):
                system_prompt += f"\n\nREPORT DATA TO ANALYZE:\n{context.get('report_data', '')}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Use HuggingFace API (primary) or Gemini (fallback)
            if self.use_hf:
                result = call_huggingface_chat_sync(messages, max_tokens=600)
            else:
                # Gemini fallback
                full_prompt = system_prompt + f"\n\nPATIENT QUESTION:\n{prompt}"
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=full_prompt
                )
                result = response.text
            
            if not result:
                return self._get_patient_fallback_response(prompt, context)
            
            # Apply safety check
            if self.enable_guardrails:
                result = self._apply_safety_guardrails(result)
            
            return result
            
        except Exception as e:
            print(f"Patient Agent Error: {e}")
            return self._get_patient_fallback_response(prompt, context)
    
    def _get_patient_fallback_response(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Patient-specific fallback response when AI is unavailable"""
        return (
            "<h3>📋 Understanding Your Report</h3>"
            "<p>I'm here to help you understand your medical report in simple terms.</p><br>"
            "<p>While I'm having some technical difficulties right now, here are some helpful tips:</p>"
            "<ul>"
            "<li>📝 <b>Write down questions</b> to ask your doctor about any values marked as 'high' or 'low'</li>"
            "<li>🔍 <b>Normal ranges</b> are usually shown next to your test values</li>"
            "<li>👨‍⚕️ <b>Always consult</b> your healthcare provider for proper interpretation</li>"
            "</ul><br>"
            "<p><em>Please try again in a moment, or speak with your healthcare team directly.</em></p>"
        )
    
    def _apply_safety_guardrails(self, response: str) -> str:
        """Apply additional safety checks to patient responses"""
        # More specific phrases that indicate actual diagnosis/prescription
        # Avoid common phrases like "you have" which can appear in educational context
        dangerous_phrases = [
            "you have diabetes",
            "you have cancer",
            "you have been diagnosed",
            "i diagnose you",
            "my diagnosis is",
            "you are diagnosed with",
            "you need to take this medication",
            "start taking medication",
            "stop taking your medication",
            "increase your dosage",
            "decrease your dosage",
            "you should take",
            "i prescribe",
            "prescription for you"
        ]
        
        response_lower = response.lower()
        for phrase in dangerous_phrases:
            if phrase in response_lower:
                # Instead of replacing, append a safety disclaimer
                return response + (
                    "<br><br><b>⚠️ Important Reminder:</b> "
                    "This information is for educational purposes only. "
                    "Please consult your healthcare provider for diagnosis and treatment."
                )
        
        return response


# ==================== CLINICIAN AGENT ====================
class ClinicianAgent(BaseCareBridgeAgent):
    """
    Specialized Agent for Healthcare Provider (Clinician) interactions
    - Provides technical, clinical insights
    - Uses medical terminology appropriately
    - Offers differential considerations
    - Supports clinical decision-making with evidence-based information
    - Provides advanced analysis capabilities
    """
    
    def __init__(self):
        super().__init__(role="clinician")
        self.parser_tool = ReportParserTool()
        self.explainer_tool = ExplanationTool()
        self.rag_tool = MedicalRAGTool()
        self.safety_tool = SafetyCheckerTool()
        
        # Clinician-specific configuration
        self.max_complexity = "advanced"
        self.enable_guardrails = False  # Less restrictive for professionals
        self.explanation_style = "clinical"
    
    def get_system_prompt(self) -> str:
        return """
        You are an advanced clinical decision support assistant for HEALTHCARE PROVIDERS.
        
        YOUR AUDIENCE: Licensed physicians, nurses, and clinical staff with medical training.
        
        COMMUNICATION STYLE:
        - Use standard medical terminology (no simplification needed)
        - Be concise, clinical, and data-driven
        - Reference clinical guidelines (ADA, AHA, etc.) when applicable
        - Include reference ranges and deviation percentages
        - Use clinical abbreviations appropriately (WBC, RBC, HbA1c, etc.)
        
        REQUIRED OUTPUT SECTIONS (use these exact headings):
        <h3>🔬 Clinical Synopsis</h3>
        - 2-3 sentence clinical summary
        - Key abnormal findings with values
        
        <h3>📊 Laboratory Analysis</h3>
        - Table or list of all values with reference ranges
        - Flag abnormals with ↑ (high) or ↓ (low)
        - Include % deviation from normal when significant
        
        <h3>🩺 Differential Considerations</h3>
        - List possible differential diagnoses to CONSIDER (educational only)
        - Correlate abnormal values with potential etiologies
        - Note: Label as "considerations" not diagnoses
        
        <h3>📋 Recommended Workup</h3>
        - Suggested additional tests if indicated
        - Follow-up timing recommendations
        - Monitoring parameters
        
        <h3>⚕️ Clinical Notes</h3>
        - Relevant guideline references (ADA, WHO, etc.)
        - Risk stratification if applicable
        - Critical values requiring immediate attention
        
        IMPORTANT:
        - This is clinical decision SUPPORT, not replacement
        - All suggestions are for EDUCATIONAL purposes
        - Final clinical decisions rest with the treating provider
        
        FORMAT: Use HTML with <h3>, <table>, <ul>, <li>, <b> tags. Use clinical formatting.
        """
    
    def get_tools(self) -> List[str]:
        return [
            "report_parser",           # Parse medical reports
            "clinical_explainer",      # Technical explanations
            "advanced_medical_rag",    # Advanced medical knowledge
            "pattern_analyzer",        # Identify clinical patterns
            "differential_generator",  # Suggest differentials (educational)
            "guideline_reference"      # Clinical guidelines lookup
        ]
    
    def process_request(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Process clinician request with advanced analysis"""
        if not self.ai_enabled:
            return self._get_clinician_fallback_response(prompt, context)
        
        # Clear history for fresh context per request
        self.conversation_history = []
        
        try:
            # Build messages for HuggingFace API
            system_prompt = self.get_system_prompt()
            
            # Add report context and patient history to system prompt
            if context:
                if context.get('report_data'):
                    system_prompt += f"\n\nCLINICAL DATA:\n{context.get('report_data', '')}"
                if context.get('patient_history'):
                    system_prompt += f"\n\nPATIENT HISTORY:\n{context.get('patient_history')}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            # Use HuggingFace API (primary) or Gemini (fallback)
            if self.use_hf:
                result = call_huggingface_chat_sync(messages, max_tokens=700)
            else:
                # Gemini fallback
                full_prompt = system_prompt + f"\n\nCLINICAL QUERY:\n{prompt}"
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=full_prompt
                )
                result = response.text
            
            if not result:
                return self._get_clinician_fallback_response(prompt, context)
            
            # Add professional disclaimer
            result = self._add_clinical_disclaimer(result)
            
            return result
            
        except Exception as e:
            print(f"Clinician Agent Error: {e}")
            return self._get_clinician_fallback_response(prompt, context)
    
    def _get_clinician_fallback_response(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Clinician-specific fallback response when AI is unavailable"""
        return (
            "<h3>Clinical Analysis Temporarily Unavailable</h3>"
            "<p>The AI clinical assistant is experiencing technical difficulties.</p><br>"
            "<h4>Standard Review Approach:</h4>"
            "<ul>"
            "<li><b>Critical Values:</b> Verify any values outside reference ranges</li>"
            "<li><b>Trending:</b> Compare with prior results if available</li>"
            "<li><b>Clinical Correlation:</b> Consider findings in context of presenting symptoms</li>"
            "<li><b>Follow-up:</b> Determine if additional workup is indicated</li>"
            "</ul><br>"
            "<p><em>Please retry the analysis or consult relevant clinical guidelines directly.</em></p>"
        )
    
    def _add_clinical_disclaimer(self, response: str) -> str:
        """Add professional disclaimer to clinical responses"""
        if len(response) > 100:  # Only add for substantive responses
            disclaimer = (
                "<br><br><i><small>"
                "Note: This analysis is for educational and clinical decision support purposes only. "
                "Final clinical decisions should be based on complete patient assessment, "
                "clinical judgment, and applicable standards of care."
                "</small></i>"
            )
            return response + disclaimer
        return response
    
    def analyze_trends(self, historical_data: List[Dict]) -> str:
        """Analyze trends in lab results over time (clinician-specific feature)"""
        if not historical_data:
            return "No historical data available for trend analysis."
        
        # This would implement trend analysis logic
        return "Trend analysis feature - to be implemented with historical data"


# ==================== SUPERVISORY AGENT ====================
class SupervisoryAgent:
    """
    Supervisory Agent that orchestrates collaboration between specialized agents
    - Routes requests to appropriate agent based on role
    - Manages multi-agent workflows
    - Coordinates information flow between agents
    - Handles escalation and cross-consultation
    """
    
    def __init__(self):
        self.patient_agent = PatientAgent()
        self.clinician_agent = ClinicianAgent()
        self.agent_registry = {
            "patient": self.patient_agent,
            "clinician": self.clinician_agent,
            "provider": self.clinician_agent,  # Alias
            "doctor": self.clinician_agent,    # Alias
            "nurse": self.clinician_agent      # Alias
        }
    
    def route_request(self, role: str, prompt: str, context: Optional[Dict] = None) -> str:
        """Route request to appropriate specialized agent"""
        normalized_role = role.lower().strip()
        
        # Get appropriate agent
        agent = self.agent_registry.get(normalized_role, self.patient_agent)
        
        print(f"[SUPERVISORY] Routing to {agent.agent_name}")
        
        # Process through specialized agent
        return agent.process_request(prompt, context)
    
    def get_agent_capabilities(self, role: str) -> Dict[str, Any]:
        """Get capabilities of specific agent"""
        normalized_role = role.lower().strip()
        agent = self.agent_registry.get(normalized_role, self.patient_agent)
        
        return {
            "agent_name": agent.agent_name,
            "role": agent.role,
            "tools": agent.get_tools(),
            "explanation_style": getattr(agent, 'explanation_style', 'standard')
        }
    
    def multi_agent_consultation(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, str]:
        """
        Run consultation through multiple agents for comparison
        (useful for training or quality assurance)
        """
        return {
            "patient_perspective": self.patient_agent.process_request(prompt, context),
            "clinician_perspective": self.clinician_agent.process_request(prompt, context)
        }


# ==================== FACTORY FUNCTIONS ====================
def create_care_bridge_agent(role: str) -> BaseCareBridgeAgent:
    """
    Creates a specialized CARE-BRIDGE AI agent for the specified role
    """
    normalized_role = role.lower().strip()
    
    if normalized_role in ["clinician", "provider", "doctor", "nurse"]:
        return ClinicianAgent()
    else:
        return PatientAgent()


def create_supervisory_agent() -> SupervisoryAgent:
    """
    Creates the supervisory orchestration agent
    """
    return SupervisoryAgent()


# ==================== SINGLETON INSTANCES ====================
# Default patient agent for backward compatibility
root_agent = PatientAgent()

# Supervisory agent for orchestration
supervisory_agent = SupervisoryAgent()