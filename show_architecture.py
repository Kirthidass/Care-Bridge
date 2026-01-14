"""
Visual representation of Multi-Agent System Architecture
Run this file to see the agent workflow diagram in the console
"""

def print_architecture_diagram():
    """Print visual architecture diagram"""
    
    diagram = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CARE-BRIDGE AI MULTI-AGENT SYSTEM                        ║
║                        Orchestration Architecture                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

                                   USER
                                     │
                                     │ Query + Role
                                     ▼
                    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                    ┃    SUPERVISORY AGENT          ┃
                    ┃  (Orchestration & Routing)    ┃
                    ┃                               ┃
                    ┃  • Route to correct agent     ┃
                    ┃  • Manage workflows           ┃
                    ┃  • Coordinate multi-agent     ┃
                    ┗━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┛
                                 │
                    ┌────────────┴────────────┐
                    │                         │
         role='patient'              role='clinician'
                    │                         │
                    ▼                         ▼
    ┌───────────────────────────┐ ┌───────────────────────────┐
    │    PATIENT AGENT          │ │    CLINICIAN AGENT        │
    │                           │ │                           │
    │  Communication:           │ │  Communication:           │
    │  • Simple language        │ │  • Medical terminology    │
    │  • Empathetic tone        │ │  • Clinical depth         │
    │  • Safety-first           │ │  • Evidence-based         │
    │                           │ │                           │
    │  Tools:                   │ │  Tools:                   │
    │  • Report parser          │ │  • Report parser          │
    │  • Simple explainer       │ │  • Clinical explainer     │
    │  • Medical RAG            │ │  • Advanced medical RAG   │
    │  • Safety checker         │ │  • Pattern analyzer       │
    │                           │ │  • Differential generator │
    │  Guardrails:              │ │  • Guideline reference    │
    │  ✓ Never diagnose         │ │                           │
    │  ✓ Never prescribe        │ │  Guardrails:              │
    │  ✓ Redirect to doctor     │ │  ✓ Educational only       │
    │                           │ │  ✓ Support decisions      │
    └────────────┬──────────────┘ └────────────┬──────────────┘
                 │                             │
                 │                             │
                 └──────────┬──────────────────┘
                            │
                            ▼
                ┌──────────────────────────┐
                │   SHARED COMPONENTS      │
                │                          │
                │  • RAG System (FAISS)    │
                │  • Report Parser         │
                │  • Safety Checker        │
                │  • Medical Explainer     │
                │  • Gemini 2.0 Flash      │
                └──────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════

                           WORKFLOW EXAMPLES

─────────────────────────────────────────────────────────────────────────────

EXAMPLE 1: PATIENT WORKFLOW
───────────────────────────

User Input:
    Role: patient
    Question: "What does my high cholesterol mean?"

1. Request → SupervisoryAgent.route_request('patient', ...)
2. SupervisoryAgent routes → PatientAgent
3. PatientAgent:
   • Retrieves report context from RAG
   • Applies simple language prompt
   • Generates response with Gemini
   • Applies safety guardrails
4. Response:
   "Your cholesterol is 240, which is above the ideal range of 
   less than 200. Think of cholesterol like a waxy substance in 
   your blood...
   
   Questions to ask your doctor:
   • Do I need medication?
   • What diet changes would help?
   • Should I get retested?"

─────────────────────────────────────────────────────────────────────────────

EXAMPLE 2: CLINICIAN WORKFLOW
──────────────────────────────

User Input:
    Role: clinician
    Question: "Analyze this lipid panel"

1. Request → SupervisoryAgent.route_request('clinician', ...)
2. SupervisoryAgent routes → ClinicianAgent
3. ClinicianAgent:
   • Retrieves report context from RAG
   • Applies clinical analysis prompt
   • Generates technical response
   • Adds professional disclaimer
4. Response:
   "Lipid Panel Analysis:
   • Total Cholesterol: 240 mg/dL (elevated, >200)
   • LDL: 160 mg/dL (high, >130)
   • HDL: 45 mg/dL (borderline low, <50 for men)
   
   Clinical Significance:
   • Increased cardiovascular risk
   • Consider ASCVD risk calculator
   • Evaluate for secondary causes (hypothyroidism, DM, etc.)
   
   Recommended Follow-up:
   • Lifestyle modifications (diet, exercise)
   • Consider statin therapy per guidelines
   • Monitor LFTs if starting treatment"

═══════════════════════════════════════════════════════════════════════════════

                        KEY DIFFERENCES

┌─────────────────────┬────────────────────┬─────────────────────────┐
│ Feature             │ Patient Agent      │ Clinician Agent         │
├─────────────────────┼────────────────────┼─────────────────────────┤
│ Language            │ Simple, everyday   │ Medical, technical      │
│ Tone                │ Empathetic         │ Professional            │
│ Analysis Depth      │ Basic              │ Advanced                │
│ Safety Guardrails   │ Strict             │ Flexible                │
│ Diagnosis           │ Never              │ Educational only        │
│ Treatment           │ Never              │ Considerations only     │
│ Target Audience     │ Patients           │ Healthcare providers    │
│ Tool Complexity     │ Simplified         │ Advanced                │
└─────────────────────┴────────────────────┴─────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════

                    SAFETY MECHANISMS

PATIENT AGENT SAFETY:
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  Input Question: "Should I stop taking my medication?"         │
│                         │                                      │
│                         ▼                                      │
│              ┌──────────────────────┐                         │
│              │ Safety Pattern Check │                         │
│              └──────────┬───────────┘                         │
│                         │                                      │
│                    Dangerous phrase                            │
│                    detected: "stop taking"                     │
│                         │                                      │
│                         ▼                                      │
│              ┌──────────────────────┐                         │
│              │ Override Response    │                         │
│              └──────────┬───────────┘                         │
│                         │                                      │
│                         ▼                                      │
│  Output: "⚠️ I cannot provide medical advice about            │
│          medications. Please consult your doctor..."           │
│                                                                │
└────────────────────────────────────────────────────────────────┘

CLINICIAN AGENT SAFETY:
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  • Less restrictive guardrails (professional audience)         │
│  • Educational disclaimer added to responses                   │
│  • Emphasizes clinical judgment over AI suggestion             │
│  • No definitive diagnoses or treatment plans                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
"""
    print(diagram)


def print_api_endpoints():
    """Print API endpoint information"""
    
    endpoints = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                            API ENDPOINTS                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

1. CHAT WITH REPORT (Multi-Agent Enabled)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   POST /api/chat/{report_id}
   
   Request:
   {
       "question": "What do my test results mean?",
       "role": "patient"  // or "clinician", "doctor", "nurse"
   }
   
   Response:
   {
       "answer": "Your test results show...",
       "report_id": "report123",
       "ai_powered": true,
       "agent_used": "PATIENT_AGENT"
   }

2. GET AGENT CAPABILITIES
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GET /api/agent/capabilities/{role}
   
   Response:
   {
       "role": "patient",
       "capabilities": {
           "agent_name": "PATIENT_AGENT",
           "role": "patient",
           "tools": [
               "report_parser",
               "simple_explainer",
               "medical_rag",
               "safety_checker"
           ],
           "explanation_style": "layperson"
       },
       "available_roles": ["patient", "clinician", "provider", ...]
   }

3. COMPARE AGENTS (Testing/QA)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   POST /api/agent/compare
   
   Request:
   {
       "question": "Explain these cholesterol results",
       "report_id": "report123"  // optional
   }
   
   Response:
   {
       "question": "Explain these cholesterol results",
       "patient_response": "Your cholesterol is...",
       "clinician_response": "Lipid panel shows...",
       "comparison": {
           "patient_style": "Simple, empathetic, safety-focused",
           "clinician_style": "Technical, clinical, advanced analysis"
       }
   }

═══════════════════════════════════════════════════════════════════════════════
"""
    print(endpoints)


def print_testing_guide():
    """Print testing guide"""
    
    testing = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          TESTING GUIDE                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

COMPREHENSIVE TEST SUITE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run: python test_multi_agent.py

Tests included:
├── test_patient_agent()
│   └── Verifies simple language, safety guardrails, empathetic tone
│
├── test_clinician_agent()
│   └── Verifies technical language, advanced analysis, clinical depth
│
├── test_supervisory_agent()
│   └── Verifies correct routing based on role
│
├── test_agent_capabilities()
│   └── Verifies tool availability for each agent
│
├── test_safety_guardrails()
│   └── Verifies patient agent blocks dangerous questions
│
└── test_conversation_history()
    └── Verifies multi-turn conversation context

MANUAL TESTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Start Backend:
   python main.py

2. Test Patient Agent:
   curl -X POST "http://localhost:8000/api/chat/report123" \\
        -H "Content-Type: application/json" \\
        -d '{"question": "What is cholesterol?", "role": "patient"}'

3. Test Clinician Agent:
   curl -X POST "http://localhost:8000/api/chat/report123" \\
        -H "Content-Type: application/json" \\
        -d '{"question": "Analyze this lipid panel", "role": "clinician"}'

4. Compare Both:
   curl -X POST "http://localhost:8000/api/agent/compare" \\
        -H "Content-Type: application/json" \\
        -d '{"question": "What do elevated triglycerides mean?"}'

EXPECTED BEHAVIORS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Patient Agent Should:
✓ Use simple, everyday language
✓ Avoid medical jargon
✓ Show empathy and support
✓ Never diagnose or prescribe
✓ Redirect dangerous questions to doctors
✓ Suggest questions for healthcare providers

Clinician Agent Should:
✓ Use medical terminology appropriately
✓ Provide technical analysis
✓ Offer differential considerations
✓ Reference clinical guidelines
✓ Suggest follow-up testing
✓ Include professional disclaimers

═══════════════════════════════════════════════════════════════════════════════
"""
    print(testing)


if __name__ == "__main__":
    print("\n")
    print_architecture_diagram()
    print("\n")
    print_api_endpoints()
    print("\n")
    print_testing_guide()
    print("\n")
    print("="*80)
    print(" For detailed documentation, see MULTI_AGENT_ARCHITECTURE.md")
    print(" For quick start guide, see MULTI_AGENT_QUICKSTART.md")
    print("="*80)
    print("\n")
