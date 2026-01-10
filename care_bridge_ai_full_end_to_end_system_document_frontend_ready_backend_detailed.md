# CARE-BRIDGE AI
## End-to-End System Design Document (Frontend Ready, Backend Fully Explained)

---

## 1. Executive Summary

CARE-BRIDGE AI is a persistent, role-aware healthcare report explainer designed to help patients and clinicians understand medical lab and radiology reports safely and effectively. The frontend is implemented using React and provides a professional dashboard experience. The backend is powered by a Google ADK–based agent that orchestrates multimodal report parsing, retrieval-augmented medical reasoning, safety checks, and role-specific explanation generation.

This document explains the complete system **from user interaction to backend intelligence**, intended for technical leadership review.

---

## 2. Problem Context

Medical reports are complex, technical, and often misunderstood. Key challenges include:
- Patients struggling to interpret values, terminology, and implications.
- Clinicians needing fast, focused summaries under time constraints.
- Existing AI tools lacking persistence, role-awareness, and safety.
- Clinical relevance depending on the **actual report date**, not upload time.

CARE-BRIDGE AI addresses these challenges with a persistent, agent-driven architecture.

---

## 3. High-Level System Architecture

```
React Frontend
   ↓ (REST API)
Backend API Layer
   ↓
Google ADK Agent (Orchestrator)
   ├── Qwen3-VL Parser Tool
   ├── RAG Retrieval Tool
   ├── Safety Checker Tool
   ├── MiroThinker Explanation Tool
   └── Formatter
   ↓
Structured, Role-Specific Output
```

---

## 4. Frontend Status (React – Already Implemented)

The frontend is implemented using React and provides:
- Login and session handling
- Role selection (Patient / Clinician)
- Persistent dashboard
- Sidebar-based document management
- Main content area for AI explanations

The frontend communicates with the backend only through APIs and does not contain AI logic.

---

## 5. Backend Overview

The backend is responsible for:
- Secure document storage
- Multimodal report parsing
- Medical knowledge grounding
- Role-aware explanation generation
- Safety enforcement

It is built as a modular service where intelligence is centralized in a Google ADK agent.

---

## 6. Document Lifecycle (Backend)

### 6.1 Upload Phase

When a user uploads a report:
1. File is received by backend API.
2. File is stored securely (filesystem or object storage).
3. The report is passed to the **Report Parser Tool**.
4. Extracted metadata and content are stored in the database.
5. The uploaded report is marked as the **active document**.

### 6.2 Stored Document Metadata

Each document record contains:
- Document ID
- User ID
- Extracted report text
- Extracted report date (from document)
- Upload timestamp (UI only)
- Report type (lab / radiology)
- Status (active / inactive)

Only the active document is used for explanations.

---

## 7. Multimodal Report Parsing (Qwen3-VL)

### 7.1 Purpose

Qwen/Qwen3-VL-30B-A3B-Instruct is used strictly for **perception and extraction**, not reasoning.

### 7.2 Responsibilities

- Read PDFs, scanned pages, and images.
- Extract:
  - Report date
  - Test names
  - Values and units
  - Reference ranges
  - Impression text
- Detect presence of graphs or images.
- Output structured JSON only.

### 7.3 Constraints

- No medical interpretation.
- No advice or explanation.
- Deterministic, schema-bound output.

---

## 8. Google ADK Agent (Core Intelligence)

A single Google ADK agent orchestrates all backend intelligence.

### 8.1 Agent Context (Memory)

The agent maintains:
- User role (patient / clinician)
- Active document ID
- Extracted report date

This enables consistent behavior across sessions.

---

## 9. Agent Tools

### 9.1 Report Parser Tool
- Calls Qwen3-VL
- Returns structured report JSON

### 9.2 Medical Knowledge Retrieval Tool (RAG)
- Queries a vector database built from public medical guidelines (CDC, RSNA).
- Retrieves relevant medical context.

### 9.3 Safety Checker Tool
- Evaluates extracted values.
- Flags abnormal or critical values.
- Triggers cautionary messaging (non-diagnostic).

### 9.4 Explanation Generator Tool
- Calls miromind-ai/MiroThinker-v1.5-235B.
- Generates role-specific explanations.

### 9.5 Formatter Tool
- Assembles final response structure.
- Ensures consistent sections and disclaimers.

---

## 10. Retrieval-Augmented Generation (RAG)

- Vector store contains only public medical guidelines.
- User reports are never added to the vector database.
- Retrieved context grounds explanations and prevents hallucination.
- Citations are attached to outputs.

---

## 11. Agent Reasoning Pipeline

For every explanation request:

1. Load user context (role, active document).
2. Fetch active report.
3. Parse report content (if not already parsed).
4. Extract report date.
5. Compute report age.
6. Retrieve relevant medical knowledge via RAG.
7. Perform safety checks.
8. Generate **Report Explanation**.
9. Generate **Contextual Message** based on timing and severity.
10. Append disclaimer and citations.

This pipeline is deterministic, explainable, and auditable.

---

## 12. Explanation vs Contextual Message

### Report Explanation
- Explains what the report findings mean.
- Uses RAG-grounded knowledge.
- Role-specific language and depth.

### Contextual Message
- Provides guidance based on:
  - Report age
  - Severity
- Non-diagnostic and advisory only.

These sections are always clearly separated.

---

## 13. Handling Non-Text Report Elements

- Graphs and images are acknowledged but not interpreted clinically.
- Explanations rely on written findings only.
- Users are informed when visuals are present.

This ensures regulatory safety.

---

## 14. API Design (Backend → Frontend)

Key APIs:
- POST /upload-report
- GET /documents
- DELETE /document/{id}
- GET /explain

All AI logic remains server-side.

---

## 15. Security, Privacy, and Ethics

- No real patient data required (synthetic/de-identified only).
- Role-based access enforced.
- Clear disclaimers always shown.
- No diagnosis or treatment advice.
- No medical image interpretation.

---

## 16. Alignment with Original Problem Statement

The system fully satisfies:
- Dual patient/clinician views
- Faithful report extraction
- Simple patient explanations
- Concise clinician summaries
- Safety and disclaimers
- Public source citations
- Agentic reasoning

---

## 17. Scalability and Future Extensions

- Multilingual explanations
- Offline report viewing
- Integration with EHR systems
- Advanced analytics (trend comparison)

---

## 18. Conclusion

CARE-BRIDGE AI is a complete, end-to-end healthcare AI system that combines a production-ready React frontend with a robust, agent-driven backend. By separating perception, reasoning, and orchestration across specialized models and a Google ADK agent, the system delivers safe, accurate, and role-aware medical report explanations suitable for academic, hackathon, and future real-world applications.

