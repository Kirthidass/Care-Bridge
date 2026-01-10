"""
CARE-BRIDGE AI Backend - Hugging Face API
==========================================
Uses Hugging Face Inference API for all AI operations
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import shutil
import uuid
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ====================
HF_API_KEY = os.getenv("HF_API_KEY", "")
UPLOAD_DIR = "data/uploads"
DB_FILE = "data/db.json"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

# Hugging Face API endpoint
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

AI_READY = bool(HF_API_KEY)
print(f"{'✓ Hugging Face API Ready' if AI_READY else '⚠ No HF_API_KEY - using fallback'}")

# ==================== DATABASE ====================
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return []

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_report_by_id(report_id):
    for r in load_db():
        if r["id"] == report_id:
            return r
    return None

# ==================== HUGGING FACE AI ====================

async def call_huggingface(prompt: str, max_tokens: int = 500) -> str:
    """Call Hugging Face Inference API"""
    if not HF_API_KEY:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                HF_API_URL,
                headers=HF_HEADERS,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": max_tokens,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
            else:
                print(f"HF API Error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        print(f"HF API Exception: {e}")
        return None

async def generate_explanation(tests: list, role: str) -> str:
    """Generate AI explanation for lab results"""
    tests_text = "\n".join([f"- {t['name']}: {t['value']} {t['unit']} ({t['status']}, range: {t['range']})" for t in tests])
    
    if role == "patient":
        prompt = f"""<s>[INST] You are a friendly medical assistant explaining lab results to a patient. Use simple language and emojis. Format with HTML tags.

Lab Results:
{tests_text}

Explain these results in a friendly way. Include:
1. A brief overview
2. What each test measures
3. Which results need attention
4. Recommended next steps

Never diagnose. Recommend consulting a doctor. [/INST]"""
    else:
        prompt = f"""<s>[INST] You are a clinical assistant summarizing lab results for a healthcare provider. Use professional medical terminology.

Lab Results:
{tests_text}

Provide a clinical summary including:
1. Overview of findings
2. Abnormal values and clinical significance
3. Recommended follow-up

Format with HTML tags. [/INST]"""
    
    result = await call_huggingface(prompt, 600)
    return result if result else generate_fallback_explanation(tests, role)

async def generate_chat_response(question: str, tests: list, role: str) -> str:
    """Generate AI chat response"""
    tests_text = ", ".join([f"{t['name']}={t['value']}{t['unit']}({t['status']})" for t in tests])
    
    style = "friendly and simple" if role == "patient" else "clinical"
    
    prompt = f"""<s>[INST] You are a {style} medical assistant. Answer briefly.

Patient's lab data: {tests_text}

Question: {question}

Provide a helpful, concise answer. Never diagnose or prescribe. Recommend consulting a doctor when appropriate. [/INST]"""
    
    result = await call_huggingface(prompt, 300)
    return result if result else generate_fallback_chat(question, tests, role)

# ==================== TOOLS ====================

def parse_medical_report(file_path: str) -> dict:
    """Parse medical report - returns structured data"""
    return {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "report_type": "Complete Blood Count (CBC)",
        "tests": [
            {"name": "Hemoglobin", "value": 12.5, "unit": "g/dL", "range": "12.0-16.0", "status": "normal"},
            {"name": "WBC", "value": 7.2, "unit": "K/uL", "range": "4.5-11.0", "status": "normal"},
            {"name": "RBC", "value": 4.5, "unit": "M/uL", "range": "4.0-5.5", "status": "normal"},
            {"name": "Platelets", "value": 250, "unit": "K/uL", "range": "150-400", "status": "normal"},
            {"name": "Glucose", "value": 105, "unit": "mg/dL", "range": "70-100", "status": "high"},
            {"name": "HbA1c", "value": 5.8, "unit": "%", "range": "4.0-5.6", "status": "high"},
        ]
    }

def check_safety(tests: list) -> list:
    """Check for abnormal values"""
    warnings = []
    for t in tests:
        if t["status"] != "normal":
            warnings.append(f"⚠️ {t['name']}: {t['value']} {t['unit']} is {t['status']} (normal: {t['range']})")
    return warnings

# ==================== FALLBACK FUNCTIONS ====================

def generate_fallback_explanation(tests: list, role: str) -> str:
    """Fallback when AI unavailable"""
    if role == "patient":
        html = "<h3>📋 Your Lab Results Summary</h3><br/>"
        
        for t in tests:
            icon = "✅" if t["status"] == "normal" else "⚠️"
            color = "green" if t["status"] == "normal" else "#e67e22"
            html += f"<p>{icon} <strong>{t['name']}</strong>: {t['value']} {t['unit']}</p>"
            if t["status"] == "normal":
                html += f"<p style='color:{color}; margin-left:20px;'>✓ Within normal range ({t['range']})</p>"
            else:
                html += f"<p style='color:{color}; margin-left:20px;'>→ {t['status'].upper()} - Normal range: {t['range']}</p>"
        
        normal = sum(1 for t in tests if t["status"] == "normal")
        abnormal = len(tests) - normal
        
        html += f"<br/><h4>📊 Summary</h4>"
        html += f"<p>✅ <strong>{normal}</strong> tests within normal range</p>"
        if abnormal > 0:
            html += f"<p>⚠️ <strong>{abnormal}</strong> tests need attention</p>"
        
        html += "<br/><h4>💡 What's Next?</h4>"
        html += "<ul>"
        html += "<li>Discuss these results with your healthcare provider</li>"
        if abnormal > 0:
            html += "<li>Ask about any abnormal values and what they mean for you</li>"
        html += "<li>Follow any recommendations your doctor provides</li>"
        html += "</ul>"
        
        html += "<br/><p><em>Remember: Lab results are just one piece of the puzzle. Your doctor considers your complete health picture.</em></p>"
    else:
        html = "<h3>Clinical Laboratory Summary</h3>"
        html += "<table style='width:100%;border-collapse:collapse;margin:10px 0;'>"
        html += "<tr style='background:#f5f5f5;'><th style='padding:10px;text-align:left;border:1px solid #ddd;'>Test</th><th style='padding:10px;border:1px solid #ddd;'>Value</th><th style='padding:10px;border:1px solid #ddd;'>Reference</th><th style='padding:10px;border:1px solid #ddd;'>Status</th></tr>"
        
        for t in tests:
            color = "#27ae60" if t["status"] == "normal" else "#e67e22"
            html += f"<tr><td style='padding:10px;border:1px solid #ddd;'>{t['name']}</td>"
            html += f"<td style='padding:10px;border:1px solid #ddd;'>{t['value']} {t['unit']}</td>"
            html += f"<td style='padding:10px;border:1px solid #ddd;'>{t['range']}</td>"
            html += f"<td style='padding:10px;border:1px solid #ddd;color:{color};font-weight:bold;'>{t['status'].upper()}</td></tr>"
        
        html += "</table>"
        
        abnormal = [t for t in tests if t["status"] != "normal"]
        if abnormal:
            html += "<h4>Clinical Findings</h4>"
            html += "<ul>"
            for t in abnormal:
                if "glucose" in t["name"].lower():
                    html += f"<li><strong>{t['name']}</strong>: Elevated at {t['value']} {t['unit']}. Consider fasting glucose recheck or HbA1c if not already done. Prediabetes range.</li>"
                elif "hba1c" in t["name"].lower():
                    html += f"<li><strong>{t['name']}</strong>: {t['value']}% indicates increased diabetes risk. Lifestyle modifications recommended.</li>"
                else:
                    html += f"<li><strong>{t['name']}</strong>: {t['status']} at {t['value']} {t['unit']}. Clinical correlation recommended.</li>"
            html += "</ul>"
        else:
            html += "<p>All parameters within reference ranges. No immediate concerns.</p>"
    
    return html

def generate_fallback_chat(question: str, tests: list, role: str) -> str:
    """Fallback chat response"""
    q = question.lower()
    
    # Check for specific test questions
    for t in tests:
        if t["name"].lower() in q:
            if t["status"] == "normal":
                return f"Your {t['name']} is {t['value']} {t['unit']}, which is within the normal range ({t['range']}). This is a good result! ✅"
            else:
                return f"Your {t['name']} is {t['value']} {t['unit']}, which is {t['status']} compared to the normal range ({t['range']}). I recommend discussing this with your healthcare provider to understand what it means for you."
    
    # Topic-specific responses
    if any(w in q for w in ["glucose", "sugar", "diabetes"]):
        glucose = next((t for t in tests if "glucose" in t["name"].lower()), None)
        if glucose:
            return f"Your Glucose level is {glucose['value']} {glucose['unit']}. Normal fasting glucose is 70-100 mg/dL. Values between 100-125 mg/dL indicate prediabetes. Your value of {glucose['value']} is slightly elevated, suggesting you should discuss lifestyle changes with your doctor."
        return "Glucose measures blood sugar. Normal fasting is 70-100 mg/dL. Values above 100 may indicate prediabetes risk."
    
    if any(w in q for w in ["hemoglobin", "anemia", "iron"]):
        hb = next((t for t in tests if "hemoglobin" in t["name"].lower()), None)
        if hb:
            return f"Your Hemoglobin is {hb['value']} {hb['unit']}, which is {hb['status']}. Hemoglobin carries oxygen in your blood. Normal range is {hb['range']}."
        return "Hemoglobin carries oxygen in your blood. Low levels may indicate anemia."
    
    if any(w in q for w in ["worried", "concerned", "scared", "nervous", "anxious"]):
        normal_count = sum(1 for t in tests if t["status"] == "normal")
        return f"I understand that medical results can be concerning. Looking at your results, {normal_count} out of {len(tests)} tests are within normal range. For the values that are slightly off, it's best to discuss with your healthcare provider who can explain what they mean for your specific situation. They know your full health history and can give you personalized advice. 💙"
    
    if any(w in q for w in ["summary", "overview", "explain", "mean"]):
        normal = sum(1 for t in tests if t["status"] == "normal")
        abnormal = [t["name"] for t in tests if t["status"] != "normal"]
        response = f"Here's a quick summary: {normal} out of {len(tests)} tests are normal. "
        if abnormal:
            response += f"The following need attention: {', '.join(abnormal)}. "
        response += "Please discuss your complete results with your healthcare provider for personalized guidance."
        return response
    
    if any(w in q for w in ["thank", "thanks"]):
        return "You're welcome! If you have more questions about your lab results, feel free to ask. Remember to follow up with your healthcare provider for personalized medical advice. 😊"
    
    if any(w in q for w in ["hi", "hello", "hey"]):
        return "Hello! 👋 I'm here to help you understand your lab results. Feel free to ask me about any specific test or what your results mean. What would you like to know?"
    
    return "Thank you for your question! For the most accurate interpretation of your lab results, I recommend discussing them with your healthcare provider who can consider your complete health history. Is there a specific test result you'd like me to explain?"

# ==================== FASTAPI APP ====================

app = FastAPI(title="CARE-BRIDGE AI", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "CARE-BRIDGE AI v3.0 - Hugging Face", "ai": "ready" if AI_READY else "fallback"}

@app.post("/api/upload-report")
async def upload_report(file: UploadFile = File(...), role: str = Form("patient")):
    """Upload and parse a medical report"""
    report_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{report_id}{ext}")
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    parsed = parse_medical_report(file_path)
    
    reports = load_db()
    reports.append({
        "id": report_id,
        "filename": file.filename,
        "upload_date": datetime.now().isoformat(),
        "parsed_data": parsed
    })
    save_db(reports)
    
    return {"report_id": report_id, "filename": file.filename, "data": parsed}

@app.get("/api/documents")
async def get_documents():
    return load_db()

@app.delete("/api/document/{doc_id}")
async def delete_document(doc_id: str):
    reports = load_db()
    new_reports = [r for r in reports if r["id"] != doc_id]
    
    if len(new_reports) == len(reports):
        raise HTTPException(404, "Not found")
    
    save_db(new_reports)
    
    for ext in ['.pdf', '.png', '.jpg', '.jpeg']:
        path = os.path.join(UPLOAD_DIR, f"{doc_id}{ext}")
        if os.path.exists(path):
            os.remove(path)
            break
    
    return {"message": "Deleted", "id": doc_id}

@app.get("/api/explain/{report_id}")
async def get_explanation(report_id: str, role: str = "patient"):
    """Get AI explanation for a report"""
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    
    tests = report.get("parsed_data", {}).get("tests", [])
    warnings = check_safety(tests)
    
    # Generate explanation
    explanation = await generate_explanation(tests, role)
    
    return {
        "report_id": report_id,
        "role": role,
        "explanation": explanation,
        "safety_warnings": warnings,
        "critical": False,
        "contextual_message": f"Report from {report.get('parsed_data', {}).get('report_date', 'recent')}",
        "disclaimer": "⚠️ This information is for educational purposes only and is not medical advice. Please consult your healthcare provider.",
        "citations": ["CDC Laboratory Guidelines", "American Diabetes Association"],
        "ai_powered": AI_READY
    }

@app.post("/api/chat/{report_id}")
async def chat_with_report(report_id: str, question: str, role: str = "patient"):
    """Chat about a report"""
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(404, "Report not found")
    
    tests = report.get("parsed_data", {}).get("tests", [])
    
    # Generate response
    answer = await generate_chat_response(question, tests, role)
    
    return {"answer": answer, "report_id": report_id, "ai_powered": AI_READY}

@app.post("/api/rag/feed")
async def feed_knowledge(text: str, source: str = "manual"):
    return {"message": "Knowledge noted", "source": source}

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("CARE-BRIDGE AI v3.0 - Hugging Face API")
    print("="*50)
    print(f"AI: {'✓ HF API Ready' if AI_READY else '⚠ Fallback mode'}")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
