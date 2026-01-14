# CARE-BRIDGE AI - Multi-Agent System Architecture

## Overview

CARE-BRIDGE AI now implements a sophisticated **Multi-Agent Orchestration System** that provides role-specific healthcare report analysis. The system features specialized agents for different user types (patients and clinicians) with a supervisory agent coordinating interactions.

## Architecture Components

### 1. Base Agent Class (`BaseCareBridgeAgent`)
Abstract base class defining the core agent interface:
- **Conversation History**: Maintains context across interactions
- **System Prompt**: Role-specific instructions
- **Tool Access**: Configurable tool availability
- **Request Processing**: Abstract method for specialized handling

### 2. Patient Agent (`PatientAgent`)
Specialized agent for patient interactions:

#### Communication Style
- **Simple Language**: Avoids medical jargon, uses everyday terms
- **Empathetic Tone**: Supportive and reassuring
- **Educational Focus**: Explains concepts, suggests questions for doctors
- **Safety-First**: Strong guardrails against medical advice

#### Capabilities
- Report parsing and interpretation
- Simplified medical explanations
- Medical knowledge lookup (general)
- Safety checking and validation

#### Safety Guardrails
- **Never diagnoses**: Refuses statements like "You have X"
- **Never prescribes**: Won't recommend medications
- **Redirects appropriately**: Guides users to healthcare providers
- **Pattern detection**: Identifies dangerous phrases and blocks them

#### Example Response Style
```
Q: "What does my elevated white blood cell count mean?"

Patient Agent Response:
"Your white blood cell count is 11.2, which is slightly higher than the 
normal range of 4.0-10.0. White blood cells are part of your immune system 
that fights infections. When they're elevated, it often means your body might 
be fighting something like an infection or inflammation.

❓ Questions to ask your doctor:
- Do I have an infection that needs treatment?
- Should we do follow-up testing?
- Are there any symptoms I should watch for?

⚠️ Remember: Only your doctor can diagnose what's causing this. Please 
schedule an appointment to discuss these results."
```

### 3. Clinician Agent (`ClinicianAgent`)
Specialized agent for healthcare provider interactions:

#### Communication Style
- **Technical Language**: Uses appropriate medical terminology
- **Clinical Depth**: Provides detailed analysis and context
- **Evidence-Based**: References guidelines when applicable
- **Concise**: Focused on clinical relevance

#### Advanced Capabilities
- Report parsing with clinical context
- Technical medical explanations
- Advanced medical knowledge lookup
- Pattern analysis across results
- Differential considerations (educational)
- Clinical guideline references

#### Analysis Approach
1. Identify abnormal values and significance
2. Consider clinical context
3. Suggest differential diagnoses (educational only)
4. Highlight urgent findings
5. Recommend additional workup

#### Example Response Style
```
Q: "Analyze this elevated WBC."

Clinician Agent Response:
"WBC 11.2 x10^9/L (ref: 4.0-10.0) - mild leukocytosis.

Clinical Significance:
- 12% above upper limit of normal
- Consider: acute infection, inflammation, stress response, 
  medication effect, early leukemoid reaction

Differential Considerations (educational):
• Infectious: bacterial infection (most common), viral syndrome
• Inflammatory: autoimmune process, tissue injury
• Hematologic: CML (unlikely with mild elevation), leukemoid reaction
• Physiologic: stress, exercise, pregnancy

Recommended Follow-up:
- CBC with differential to characterize cell types
- Review clinical history and symptoms
- Consider inflammatory markers (CRP, ESR) if indicated
- Monitor trend with repeat CBC in 1-2 weeks if isolated finding

Critical values requiring immediate attention: None currently.

Note: This analysis is for educational purposes. Final clinical decisions 
should be based on complete patient assessment and clinical judgment."
```

### 4. Supervisory Agent (`SupervisoryAgent`)
Orchestrates the multi-agent system:

#### Responsibilities
- **Request Routing**: Directs queries to appropriate specialized agent
- **Agent Registry**: Manages available agents and their roles
- **Capability Management**: Provides information about agent capabilities
- **Multi-Agent Consultation**: Runs queries through multiple agents for comparison

#### Routing Logic
```
User Role → Normalized Role → Appropriate Agent
─────────────────────────────────────────────
patient     → patient        → PatientAgent
clinician   → clinician      → ClinicianAgent
doctor      → clinician      → ClinicianAgent
nurse       → clinician      → ClinicianAgent
provider    → clinician      → ClinicianAgent
```

## Key Differences Between Agents

| Feature | Patient Agent | Clinician Agent |
|---------|--------------|-----------------|
| **Language** | Simple, layperson terms | Medical terminology |
| **Tone** | Empathetic, reassuring | Professional, clinical |
| **Analysis Depth** | Basic interpretation | Advanced clinical analysis |
| **Safety Guardrails** | Strict (always active) | Flexible (professional) |
| **Diagnosis** | Never provides | Educational considerations only |
| **Treatment** | Never recommends | Suggests follow-up only |
| **Tools** | Basic explainer, safety checker | Advanced analysis, differentials |
| **Target Audience** | Patients, caregivers | Doctors, nurses, providers |

## API Integration

### Chat Endpoint (Updated)
```python
POST /api/chat/{report_id}
{
    "question": "What do these results mean?",
    "role": "patient"  # or "clinician"
}

Response:
{
    "answer": "...",
    "report_id": "123",
    "ai_powered": true,
    "agent_used": "PATIENT_AGENT"
}
```

### Agent Capabilities Endpoint
```python
GET /api/agent/capabilities/{role}

Response:
{
    "role": "patient",
    "capabilities": {
        "agent_name": "PATIENT_AGENT",
        "role": "patient",
        "tools": ["report_parser", "simple_explainer", ...],
        "explanation_style": "layperson"
    }
}
```

### Agent Comparison Endpoint
```python
POST /api/agent/compare
{
    "question": "What do these cholesterol numbers mean?",
    "report_id": "123"
}

Response:
{
    "question": "...",
    "patient_response": "...",
    "clinician_response": "...",
    "comparison": {
        "patient_style": "Simple, empathetic, safety-focused",
        "clinician_style": "Technical, clinical, advanced analysis"
    }
}
```

## Implementation Details

### Conversation History
Each agent maintains conversation history to provide context-aware responses:
```python
agent.conversation_history = [
    {"role": "patient", "content": "What is TSH?"},
    {"role": "assistant", "content": "TSH is..."},
    {"role": "patient", "content": "Why is mine high?"},
    # ...
]
```

### Context Management
Agents receive rich context for informed responses:
```python
context = {
    "report_data": "...",        # Report text from RAG
    "report_id": "123",           # Report identifier
    "report_type": "lab",         # Type of report
    "report_date": "2026-01-12",  # Report date
    "patient_history": "..."      # Optional patient history
}
```

### Safety Pattern Detection (Patient Agent)
```python
dangerous_phrases = [
    "you have", "diagnosed with", "you need to take",
    "start medication", "stop taking", "increase dosage"
]
# If detected → Override response with safety notice
```

## Testing

Run the comprehensive test suite:
```bash
python test_multi_agent.py
```

Tests include:
- Patient Agent behavior with various questions
- Clinician Agent advanced analysis
- Supervisory Agent routing
- Agent capabilities retrieval
- Safety guardrail validation
- Conversation history tracking
- Multi-turn dialogue simulation

## Benefits of Multi-Agent Architecture

1. **Role-Appropriate Communication**
   - Patients get understandable explanations
   - Clinicians get professional analysis

2. **Safety & Compliance**
   - Patient agent has strict guardrails
   - Prevents inappropriate medical advice

3. **Scalability**
   - Easy to add new specialized agents (e.g., Caregiver Agent)
   - Modular design allows independent updates

4. **Quality Assurance**
   - Compare responses across agents
   - Validate appropriateness of content

5. **User Experience**
   - Tailored to user expertise level
   - Context-aware across conversation

## Future Enhancements

### Planned Agents
- **Caregiver Agent**: For family members caring for patients
- **Researcher Agent**: For clinical research and data analysis
- **Educator Agent**: For medical students and training

### Advanced Features
- **Multi-Agent Collaboration**: Agents consulting each other
- **Workflow Automation**: Automated report triage and routing
- **Memory & Learning**: Long-term patient history tracking
- **External Integration**: Connect to EHR systems, clinical databases

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   SUPERVISORY AGENT                         │
│  (Orchestration, Routing, Multi-Agent Coordination)         │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌────────▼────────┐
│  PATIENT AGENT  │    │ CLINICIAN AGENT │
│                 │    │                 │
│ • Simple Lang   │    │ • Medical Terms │
│ • Safety First  │    │ • Clinical      │
│ • Empathetic    │    │ • Advanced      │
│ • Educational   │    │ • Evidence-Based│
└────────┬────────┘    └────────┬────────┘
         │                      │
         └──────────┬───────────┘
                    │
         ┌──────────▼──────────┐
         │   SHARED TOOLS      │
         │                     │
         │ • Report Parser     │
         │ • RAG Tool          │
         │ • Safety Checker    │
         │ • Explainer         │
         └─────────────────────┘
```

## Conclusion

The Multi-Agent System provides a sophisticated, role-aware approach to medical report analysis. By specializing agents for different user types, CARE-BRIDGE AI delivers appropriate, safe, and effective healthcare communication tailored to each user's needs and expertise level.
