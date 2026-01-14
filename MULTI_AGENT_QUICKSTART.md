# Multi-Agent System - Quick Start Guide

## Overview
CARE-BRIDGE AI now has separate specialized agents for patients and clinicians that work differently based on the user's role.

## How It Works

### For Patients
When a patient asks a question, the **Patient Agent** provides:
- ✓ Simple, easy-to-understand explanations
- ✓ No medical jargon
- ✓ Safety guardrails (never diagnoses or prescribes)
- ✓ Empathetic, supportive tone
- ✓ Questions to ask their doctor

### For Clinicians  
When a clinician/doctor asks a question, the **Clinician Agent** provides:
- ✓ Technical medical terminology
- ✓ Advanced clinical analysis
- ✓ Differential diagnoses (for educational purposes)
- ✓ Follow-up test recommendations
- ✓ Evidence-based insights

## Usage Examples

### Example 1: Same Question, Different Responses

**Question:** "What does an elevated white blood cell count mean?"

**Patient Agent Response:**
```
Your white blood cell count is slightly higher than normal. White blood cells 
help fight infections in your body. When the count is high, it usually means 
your body is fighting off something like an infection or inflammation.

What you should do:
• Talk to your doctor about these results
• Ask if you need any treatment
• Mention any symptoms you're having (fever, pain, etc.)

⚠️ Remember: This is just information. Only your doctor can tell you exactly 
what this means for your health.
```

**Clinician Agent Response:**
```
Leukocytosis with WBC 11.2 x10^9/L (reference: 4.0-10.0)

Clinical Considerations:
• Mild elevation (~12% above upper limit)
• Differential: infection (bacterial > viral), inflammation, stress, 
  medication effect, early myeloproliferative process

Recommended Workup:
• CBC with differential to characterize predominant cell type
• Review clinical presentation and vital signs
• Consider inflammatory markers if clinically indicated
• Rule out medication-induced leukocytosis

Follow-up: Repeat CBC in 1-2 weeks if asymptomatic with isolated finding.
```

### Example 2: Safety Guardrails in Action

**Dangerous Question:** "Should I stop taking my medication?"

**Patient Agent Response:**
```
⚠️ Safety Notice:

I cannot provide medical advice about starting, stopping, or changing 
medications. This is a decision that only your doctor can make based on 
your complete medical history.

What I can help with:
• Explaining what your test results show
• Helping you understand medical terms
• Suggesting questions to ask your doctor

Please contact your healthcare provider before making any changes to 
your medications.
```

**Clinician Agent Response:**
```
As a clinical assistant, I cannot make medication management decisions. 
Treatment modifications should be based on:

• Complete patient assessment
• Clinical presentation and trends
• Risk-benefit analysis
• Patient-specific factors
• Current evidence-based guidelines

Recommend reviewing patient's medication profile in context of current 
findings and clinical status during consultation.
```

## Using the API

### Chat with a Report (Basic)
```bash
curl -X POST "http://localhost:8000/api/chat/report123" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What do my glucose levels mean?",
    "role": "patient"
  }'
```

### Get Agent Capabilities
```bash
curl "http://localhost:8000/api/agent/capabilities/patient"
curl "http://localhost:8000/api/agent/capabilities/clinician"
```

### Compare Both Agents
```bash
curl -X POST "http://localhost:8000/api/agent/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Interpret these cholesterol results",
    "report_id": "report123"
  }'
```

## Testing Locally

### Run the Test Suite
```bash
# Make sure you're in the AiIgnite directory
cd C:\Users\lenovo\Desktop\AiIgnite

# Activate your virtual environment if needed
.\venv\Scripts\Activate.ps1

# Run the multi-agent test
python test_multi_agent.py
```

### Start the Backend
```bash
# Terminal 1: Start backend
python main.py
```

### Test with Frontend
```bash
# Terminal 2: Start frontend
cd frontend
npm run dev
```

Then:
1. Login as a patient or clinician
2. Upload a medical report
3. Ask questions about the report
4. Notice how responses differ based on your role!

## Architecture Benefits

### 1. Personalized Experience
- Patients get understandable, safe information
- Clinicians get professional, detailed analysis

### 2. Safety First
- Patient agent has strict guardrails
- Prevents inappropriate medical advice
- Redirects to healthcare providers when needed

### 3. Professional Support
- Clinicians get advanced analysis tools
- Access to differential considerations
- Evidence-based information

### 4. Scalable Design
- Easy to add new agent types (caregiver, researcher, etc.)
- Independent agent updates
- Modular tool configuration

## Key Components

### Agent.py Structure
```
BaseCareBridgeAgent (Abstract)
├── PatientAgent
│   ├── Simple language
│   ├── Safety guardrails
│   └── Basic tools
└── ClinicianAgent
    ├── Medical terminology
    ├── Advanced analysis
    └── Clinical tools

SupervisoryAgent
├── Routes to PatientAgent
├── Routes to ClinicianAgent
└── Manages multi-agent workflows
```

### Main.py Integration
- Supervisory agent initialized on startup
- Chat endpoint routes through supervisory agent
- Role-based agent selection automatic
- Fallback to traditional method if needed

## Troubleshooting

### "Agent not found" error
- Check that role is one of: patient, clinician, doctor, nurse, provider
- Role is normalized automatically (case-insensitive)

### Agent not using context
- Verify report_id is valid
- Check that RAG system has indexed the report
- Ensure report text was extracted successfully

### Responses seem generic
- Make sure GOOGLE_API_KEY is set in .env
- Check that Gemini API is accessible
- Review console logs for API errors

## Next Steps

1. **Test both agents** - See how they respond differently
2. **Review documentation** - Read MULTI_AGENT_ARCHITECTURE.md
3. **Customize agents** - Modify prompts and tools as needed
4. **Add new agents** - Extend for caregivers, researchers, etc.

## Support

For issues or questions:
1. Check the logs in the console
2. Review MULTI_AGENT_ARCHITECTURE.md
3. Run test_multi_agent.py for diagnostics
4. Verify environment variables are set correctly

---

**Remember:** The multi-agent system is designed to provide role-appropriate, safe, and effective healthcare communication. Always encourage users to consult with licensed healthcare providers for medical decisions.
