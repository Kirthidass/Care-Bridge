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

# Avoid pulling TensorFlow/Keras via transformers on environments where Keras 3 is installed.
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")

import json
import socket
import base64
from datetime import datetime
from dotenv import load_dotenv

from typing import Optional, List, Tuple

from pypdf import PdfReader

from huggingface_hub import AsyncInferenceClient

import numpy as np

import faiss
from sentence_transformers import SentenceTransformer

_here = os.path.dirname(os.path.abspath(__file__))
# Load env from common locations; override=True so key changes take effect.
load_dotenv(dotenv_path=os.path.join(_here, ".env"), override=True)
load_dotenv(dotenv_path=os.path.join(_here, "app", ".env"), override=True)

# ==================== CONFIGURATION ====================
HF_API_KEY = os.getenv("HF_API_KEY", "")
UPLOAD_DIR = "data/uploads"
DB_FILE = "data/db.json"

VECTOR_DB_DIR = "data/vector_db"
RAG_COLLECTION_NAME = "care_bridge_reports"

HF_LLM_MODEL_ID = os.getenv("HF_LLM_MODEL_ID", "meta-llama/Llama-3.3-70B-Instruct")
HF_LLM_FALLBACK_MODEL_ID = os.getenv(
    "HF_LLM_FALLBACK_MODEL_ID", "Qwen/Qwen2.5-7B-Instruct"
)
HF_OCR_MODE = os.getenv("HF_OCR_MODE", "vlm").strip().lower()  # trocr | qwen_vl | vlm
HF_OCR_MODEL_ID = os.getenv("HF_OCR_MODEL_ID", "microsoft/trocr-base-printed")
HF_OCR_VLM_MODEL_ID = os.getenv("HF_OCR_VLM_MODEL_ID", "meta-llama/Llama-3.2-11B-Vision-Instruct")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

AI_READY = bool(HF_API_KEY)
print(f"{'✓ Hugging Face API Ready' if AI_READY else '⚠ No HF_API_KEY - using fallback'}")
if AI_READY:
    print(f"LLM model: {HF_LLM_MODEL_ID}")
    if HF_LLM_FALLBACK_MODEL_ID and HF_LLM_FALLBACK_MODEL_ID != HF_LLM_MODEL_ID:
        print(f"LLM fallback: {HF_LLM_FALLBACK_MODEL_ID}")

HF_ROUTER_CHAT_URL = os.getenv(
    "HF_ROUTER_CHAT_URL", "https://router.huggingface.co/v1/chat/completions"
)
HF_HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}

HF_CLIENT: Optional[AsyncInferenceClient] = (
    # Still used for non-chat tasks (e.g., image_to_text) when enabled.
    AsyncInferenceClient(api_key=HF_API_KEY, timeout=60) if HF_API_KEY else None
)

# ==================== RAG (FAISS) ====================

FAISS_INDEX_PATH = os.path.join(VECTOR_DB_DIR, "faiss.index")
FAISS_STORE_PATH = os.path.join(VECTOR_DB_DIR, "faiss_store.json")

_EMBEDDER: Optional[SentenceTransformer] = None
_FAISS_INDEX: Optional[faiss.IndexIDMap2] = None
_FAISS_STORE: Optional[dict] = None


def _get_embedder() -> SentenceTransformer:
    global _EMBEDDER
    if _EMBEDDER is None:
        model_name = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        _EMBEDDER = SentenceTransformer(model_name)
    return _EMBEDDER


def _load_store() -> dict:
    if os.path.exists(FAISS_STORE_PATH):
        try:
            with open(FAISS_STORE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "vectors" in data and "next_id" in data:
                    return data
        except Exception:
            pass
    return {"next_id": 1, "vectors": {}}


def _save_store(store: dict) -> None:
    with open(FAISS_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)


def _ensure_faiss_loaded() -> Tuple[faiss.IndexIDMap2, dict]:
    global _FAISS_INDEX, _FAISS_STORE
    if _FAISS_INDEX is not None and _FAISS_STORE is not None:
        return _FAISS_INDEX, _FAISS_STORE

    store = _load_store()

    if os.path.exists(FAISS_INDEX_PATH):
        try:
            idx = faiss.read_index(FAISS_INDEX_PATH)
            if not isinstance(idx, faiss.IndexIDMap2):
                idx = faiss.IndexIDMap2(idx)
        except Exception:
            idx = None
    else:
        idx = None

    if idx is None:
        # Create a new index using embedder dimension.
        dim = int(_get_embedder().get_sentence_embedding_dimension())
        base = faiss.IndexFlatIP(dim)
        idx = faiss.IndexIDMap2(base)

    _FAISS_INDEX, _FAISS_STORE = idx, store
    return _FAISS_INDEX, _FAISS_STORE


def _save_faiss_index(index: faiss.IndexIDMap2) -> None:
    faiss.write_index(index, FAISS_INDEX_PATH)


def _embed_texts(texts: List[str]) -> np.ndarray:
    emb = _get_embedder().encode(texts, normalize_embeddings=True)
    arr = np.asarray(emb, dtype="float32")
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    return arr

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

async def call_huggingface_chat(messages: list, max_tokens: int = 500) -> Optional[str]:
    """Call Hugging Face Inference Providers via router using OpenAI-compatible chat completions."""
    if not HF_API_KEY:
        return None

    async with httpx.AsyncClient(timeout=60.0) as client:
        for model_id in [HF_LLM_MODEL_ID, HF_LLM_FALLBACK_MODEL_ID]:
            if not model_id:
                continue
            try:
                resp = await client.post(
                    HF_ROUTER_CHAT_URL,
                    headers=HF_HEADERS,
                    json={
                        "model": model_id,
                        "messages": messages,
                        "max_tokens": max_tokens,
                    },
                )
                if resp.status_code != 200:
                    print(f"HF Chat Error ({model_id}): {resp.status_code} - {resp.text}")
                    continue
                data = resp.json()
                choices = (data or {}).get("choices") or []
                if not choices:
                    continue
                content = ((choices[0] or {}).get("message") or {}).get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()
            except Exception as e:
                print(f"HF Chat Exception ({model_id}): {e}")
                continue

    return None


def _image_bytes_to_data_url(image_bytes: bytes, mime: str = "image/png") -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"


async def call_hf_vlm_ocr(image_bytes: bytes) -> Optional[str]:
    """OCR via a vision-language model over the HF router (OpenAI-compatible chat).

    This is intended for *remote inference* (no local transformers load).
    """
    if not HF_API_KEY:
        return None
    try:
        data_url = _image_bytes_to_data_url(image_bytes, mime="image/png")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {
                        "type": "text",
                        "text": (
                            "Extract all readable text from this document image. "
                            "Preserve line breaks as best as possible. "
                            "Output ONLY the extracted text, with no commentary."
                        ),
                    },
                ],
            }
        ]
        # Use the same router chat-completions endpoint for VLM OCR
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                HF_ROUTER_CHAT_URL,
                headers=HF_HEADERS,
                json={
                    "model": HF_OCR_VLM_MODEL_ID,
                    "messages": messages,
                    "max_tokens": 800,
                },
            )
            if resp.status_code != 200:
                print(f"HF VLM OCR Error: {resp.status_code} - {resp.text}")
                return None
            data = resp.json()
            choices = (data or {}).get("choices") or []
            if not choices:
                return None
            content = ((choices[0] or {}).get("message") or {}).get("content")
            return content.strip() if isinstance(content, str) and content.strip() else None
    except Exception as e:
        print(f"HF VLM OCR Exception: {e}")
        return None


async def call_hf_ocr(image_bytes: bytes) -> Optional[str]:
    """OCR an image using Hugging Face Inference Providers image-to-text."""
    if not HF_CLIENT:
        return None
    try:
        if HF_OCR_MODE in {"qwen_vl", "vlm", "qwen"}:
            text = await call_hf_vlm_ocr(image_bytes)
            if text:
                return text
            # fall back to TrOCR if VLM OCR fails (permissions/model gating, etc.)

        result = await HF_CLIENT.image_to_text(image_bytes, model=HF_OCR_MODEL_ID)
        # image_to_text returns a list of dicts like [{'generated_text': '...'}]
        if isinstance(result, list) and result:
            text = result[0].get("generated_text")
            return text.strip() if isinstance(text, str) and text.strip() else None
        if isinstance(result, dict):
            text = result.get("generated_text")
            return text.strip() if isinstance(text, str) and text.strip() else None
        return None
    except Exception as e:
        print(f"HF OCR Exception: {e}")
        return None

def _normalize_role(role: str) -> str:
    role = (role or "patient").strip().lower()
    if role not in {"patient", "caregiver", "provider", "doctor", "nurse"}:
        return "patient"
    if role in {"doctor", "nurse"}:
        return "provider"
    return role


def _role_instructions(role: str) -> str:
    role = _normalize_role(role)
    if role == "provider":
        return (
            "Audience: a healthcare provider. Use clinical terminology, but stay concise. "
            "Do not provide a diagnosis or treatment plan. Provide possible considerations as educational info only."
        )
    if role == "caregiver":
        return (
            "Audience: a caregiver/family member. Use plain language and focus on practical explanations "
            "and what to ask a clinician. Do not diagnose or prescribe."
        )
    return (
        "Audience: a patient. Use very simple language. Do not diagnose or prescribe. "
        "Explain what the report says and what questions to ask a clinician."
    )


def _safety_instructions() -> str:
    return (
        "Safety rules (must follow): "
        "1) Do NOT diagnose (no statements like 'you have X' or 'this means you have Y'). "
        "2) Do NOT prescribe or recommend medication changes. "
        "3) If asked for diagnosis/treatment, redirect: explain what the report shows and suggest consulting a licensed clinician. "
        "4) If content is unclear or missing, say so."
    )


def _chunk_text(text: str, max_chars: int = 900, overlap: int = 150) -> List[str]:
    cleaned = (text or "").replace("\r\n", "\n").strip()
    if not cleaned:
        return []
    parts: List[str] = []
    idx = 0
    while idx < len(cleaned):
        end = min(len(cleaned), idx + max_chars)
        chunk = cleaned[idx:end].strip()
        if chunk:
            parts.append(chunk)
        if end >= len(cleaned):
            break
        idx = max(0, end - overlap)
    return parts


def _extract_text_from_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        pages_text: List[str] = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                pages_text.append(t)
        return "\n\n".join(pages_text).strip()
    except Exception as e:
        print(f"PDF text extract failed: {e}")
        return ""


async def _extract_text_via_pdf_ocr(file_path: str, max_pages: int = 5) -> str:
    """Render PDF pages to images and OCR them. Requires PyMuPDF (fitz)."""
    try:
        import fitz  # type: ignore
    except Exception:
        return ""

    if not HF_API_KEY:
        return ""

    text_parts: List[str] = []
    try:
        doc = fitz.open(file_path)
        pages_to_process = min(len(doc), max_pages)
        for i in range(pages_to_process):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=200)
            image_bytes = pix.tobytes("png")
            ocr_text = await call_hf_ocr(image_bytes)
            if ocr_text:
                text_parts.append(f"[Page {i+1}]\n{ocr_text}")
        doc.close()
    except Exception as e:
        print(f"PDF OCR failed: {e}")

    return "\n\n".join(text_parts).strip()


async def extract_report_text(file_path: str) -> Tuple[str, str]:
    """Extract text from PDF/images using OCR when possible. Returns (text, method)."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        # First try native PDF text extraction.
        text = _extract_text_from_pdf(file_path)
        if len(text) >= 200:
            return text, "pdf_text"
        # If it looks scanned, try OCR if PyMuPDF is installed.
        ocr_text = await _extract_text_via_pdf_ocr(file_path)
        if ocr_text:
            return ocr_text, "pdf_ocr"
        return text, "pdf_text_low"

    # Images: OCR via HF
    if ext in {".png", ".jpg", ".jpeg"}:
        try:
            with open(file_path, "rb") as f:
                image_bytes = f.read()
            text = await call_hf_ocr(image_bytes)
            return (text or ""), "image_ocr"
        except Exception as e:
            print(f"Image OCR failed: {e}")
            return "", "image_ocr_failed"

    return "", "unsupported"


def _rag_upsert_report(report_id: str, filename: str, chunks: List[str], method: str) -> int:
    if not chunks:
        return 0
    index, store = _ensure_faiss_loaded()

    # Remove existing vectors for this report (FAISS supports delete via IDMap2)
    existing_ids: List[int] = []
    vectors = store.get("vectors", {})
    for vid_str, rec in list(vectors.items()):
        meta = (rec or {}).get("metadata", {})
        if meta.get("report_id") == report_id:
            try:
                existing_ids.append(int(vid_str))
            except Exception:
                continue
    if existing_ids:
        try:
            index.remove_ids(np.asarray(existing_ids, dtype="int64"))
        except Exception:
            pass
        for vid in existing_ids:
            vectors.pop(str(vid), None)

    # Add new vectors
    embeddings = _embed_texts(chunks)
    new_ids: List[int] = []
    for i, chunk in enumerate(chunks):
        vid = int(store.get("next_id", 1))
        store["next_id"] = vid + 1
        new_ids.append(vid)
        vectors[str(vid)] = {
            "text": chunk,
            "metadata": {
                "report_id": report_id,
                "filename": filename,
                "source": "upload",
                "method": method,
                "chunk_index": i,
            },
        }
    store["vectors"] = vectors

    index.add_with_ids(embeddings, np.asarray(new_ids, dtype="int64"))
    _save_faiss_index(index)
    _save_store(store)
    return len(chunks)


def _rag_retrieve_report(report_id: str, query: str, k: int = 5) -> List[str]:
    index, store = _ensure_faiss_loaded()
    if index.ntotal == 0:
        return []

    q_vec = _embed_texts([query])
    # Overfetch then filter by report_id
    top_n = max(k * 10, 25)
    scores, ids = index.search(q_vec, top_n)
    out: List[str] = []
    vectors = store.get("vectors", {})
    for vid in ids[0].tolist():
        if vid == -1:
            continue
        rec = vectors.get(str(int(vid)))
        if not rec:
            continue
        meta = (rec.get("metadata") or {})
        if meta.get("report_id") != report_id:
            continue
        text = rec.get("text")
        if isinstance(text, str) and text.strip():
            out.append(text)
        if len(out) >= k:
            break
    return out


def _rag_delete_report(report_id: str) -> int:
    index, store = _ensure_faiss_loaded()
    vectors = store.get("vectors", {})
    delete_ids: List[int] = []
    for vid_str, rec in list(vectors.items()):
        meta = (rec or {}).get("metadata", {})
        if meta.get("report_id") == report_id:
            try:
                delete_ids.append(int(vid_str))
            except Exception:
                continue

    if not delete_ids:
        return 0

    try:
        index.remove_ids(np.asarray(delete_ids, dtype="int64"))
    except Exception:
        pass
    for vid in delete_ids:
        vectors.pop(str(vid), None)
    store["vectors"] = vectors
    _save_faiss_index(index)
    _save_store(store)
    return len(delete_ids)


async def miro_thinker_explain(report_id: str, role: str) -> tuple[str, bool]:
    role = _normalize_role(role)
    context_chunks = _rag_retrieve_report(
        report_id,
        query="Summarize the medical report and highlight key values, interpretations, and follow-up questions.",
        k=6,
    )
    context = "\n\n".join(context_chunks)
    if not context.strip():
        return (
            "<h3>Report Summary</h3>"
            "<p>I couldn't extract enough readable text from this report to summarize it.</p>"
            "<p>If this is a scanned PDF/image, install <code>PyMuPDF</code> so OCR can run, then re-upload.</p>"
        ), False

    # Keep prompt bounded
    max_context = 6000
    context = context[:max_context]
    system_msg = (
        "You are Care-Bridge Assistant, a medical report explainer. "
        + _role_instructions(role)
        + "\n\n"
        + _safety_instructions()
    )
    user_msg = f"""Task: Produce an HTML explanation of this report.
Must include:
- Short overview (2-4 sentences)
- Key findings (bullet list)
- What each key measurement likely refers to (brief)
- Questions to ask a clinician (bullet list)
- A clear disclaimer that this is educational and not medical advice

STRICT RULES:
- Do NOT diagnose.
- Do NOT provide treatment plans or medication changes.
- If the report is unclear or missing details, say so.
- Ground your answer only in the report text provided.

Report text (grounding):
{context}
""".strip()

    result = await call_huggingface_chat(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=650,
    )
    if result:
        return result, True
    return "<h3>Report Summary</h3><p>AI is unavailable right now. Please try again later.</p>", False


async def miro_thinker_chat(report_id: str, question: str, role: str) -> tuple[str, bool]:
    role = _normalize_role(role)
    q = (question or "").strip()
    if not q:
        return "Please ask a question about the report.", False

    context_chunks = _rag_retrieve_report(report_id, query=q, k=5)
    context = "\n\n".join(context_chunks)
    if not context.strip():
        return (
            "I couldn't retrieve enough text from the uploaded report to answer that. "
            "If this is a scanned PDF/image, enable OCR (install PyMuPDF) and re-upload."
        ), False

    # Keep context bounded
    context = context[:5000]
    system_msg = (
        "You are Care-Bridge Assistant, a medical report assistant. "
        + _role_instructions(role)
        + "\n\n"
        + _safety_instructions()
    )
    user_msg = f"""Answer efficiently: 3-8 sentences max.
Ground your answer ONLY in the provided report excerpts. If the excerpts don't contain the answer, say so.
If asked to diagnose or prescribe, refuse and instead explain what the report text says.

REPORT EXCERPTS:
{context}

USER QUESTION:
{q}
""".strip()

    result = await call_huggingface_chat(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=320,
    )
    if result:
        return result, True
    return "AI is unavailable right now. Please try again later.", False

# ==================== TOOLS ====================

def parse_medical_report(file_path: str) -> dict:
    """Legacy parser placeholder (kept for backward compatibility).

    This app now primarily uses OCR + RAG for analysis, so structured tests may be empty.
    """
    return {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "report_type": "Uploaded Report",
        "tests": [],
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
    
    # OCR/Text extraction + RAG ingestion
    extracted_text, method = await extract_report_text(file_path)
    chunks = _chunk_text(extracted_text)
    chunk_count = 0
    try:
        chunk_count = _rag_upsert_report(report_id, file.filename, chunks, method)
    except Exception as e:
        print(f"RAG upsert failed: {e}")

    parsed = parse_medical_report(file_path)
    parsed["extraction_method"] = method
    parsed["text_preview"] = (extracted_text[:800] + "...") if len(extracted_text) > 800 else extracted_text
    parsed["rag_chunks"] = chunk_count
    
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

    # Remove RAG vectors for this report (best effort)
    try:
        _rag_delete_report(doc_id)
    except Exception as e:
        print(f"RAG delete failed: {e}")
    
    return {"message": "Deleted", "id": doc_id}

@app.get("/api/explain/{report_id}")
async def get_explanation(report_id: str, role: str = "patient"):
    """Get AI explanation for a report"""
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(404, "Report not found")

    role = _normalize_role(role)
    tests = report.get("parsed_data", {}).get("tests", [])
    warnings = check_safety(tests) if tests else []

    # Generate explanation grounded in RAG (OCR'd report)
    explanation, ai_powered = await miro_thinker_explain(report_id, role)
    
    return {
        "report_id": report_id,
        "role": role,
        "explanation": explanation,
        "safety_warnings": warnings,
        "critical": False,
        "contextual_message": f"Report from {report.get('parsed_data', {}).get('report_date', 'recent')}",
        "disclaimer": "⚠️ This information is for educational purposes only and is not medical advice. Please consult your healthcare provider.",
        "citations": ["CDC Laboratory Guidelines", "American Diabetes Association"],
        "ai_powered": ai_powered
    }

@app.post("/api/chat/{report_id}")
async def chat_with_report(report_id: str, question: str, role: str = "patient"):
    """Chat about a report"""
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(404, "Report not found")

    role = _normalize_role(role)

    # Generate response grounded in RAG (OCR'd report)
    answer, ai_powered = await miro_thinker_chat(report_id, question, role)
    
    return {"answer": answer, "report_id": report_id, "ai_powered": ai_powered}

@app.post("/api/rag/feed")
async def feed_knowledge(text: str, source: str = "manual"):
    text = (text or "").strip()
    if not text:
        raise HTTPException(400, "text is required")
    chunks = _chunk_text(text)
    if not chunks:
        raise HTTPException(400, "text too short")
    index, store = _ensure_faiss_loaded()
    embeddings = _embed_texts(chunks)

    vectors = store.get("vectors", {})
    new_ids: List[int] = []
    for i, chunk in enumerate(chunks):
        vid = int(store.get("next_id", 1))
        store["next_id"] = vid + 1
        new_ids.append(vid)
        vectors[str(vid)] = {
            "text": chunk,
            "metadata": {"source": source, "type": "knowledge"},
        }
    store["vectors"] = vectors

    index.add_with_ids(embeddings, np.asarray(new_ids, dtype="int64"))
    _save_faiss_index(index)
    _save_store(store)

    return {"message": "Knowledge saved", "source": source, "chunks": len(chunks)}

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("CARE-BRIDGE AI v3.0 - Hugging Face API")
    print("="*50)
    print(f"AI: {'✓ HF API Ready' if AI_READY else '⚠ Fallback mode'}")
    print("="*50 + "\n")
    def _find_free_port(start_port: int, max_tries: int = 20) -> int:
        # Probe bind to 0.0.0.0 (same as uvicorn) so the check matches actual server binding.
        for port in range(start_port, start_port + max_tries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    s.bind(("0.0.0.0", port))
                    return port
                except OSError:
                    continue
        return start_port

    port_env = os.getenv("PORT")
    try:
        requested_port = int(port_env) if port_env else 8000
    except ValueError:
        requested_port = 8000

    port = _find_free_port(requested_port)
    if port != requested_port:
        print(f"Port {requested_port} is in use; starting on {port} instead.")
    uvicorn.run(app, host="0.0.0.0", port=port)
