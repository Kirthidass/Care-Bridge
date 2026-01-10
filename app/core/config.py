from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "CARE-BRIDGE AI"
    API_V1_STR: str = "/api/v1"
    
    # AI Model Settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    HF_API_KEY: str = os.getenv("HF_API_KEY", "")
    AGENT_MODEL: str = "gemini-2.5-flash"
    PARSER_MODEL_ID: str = "Qwen/Qwen3-VL-30B-A3B-Instruct"
    THINKER_MODEL_ID: str = "miromind-ai/MiroThinker-v1.5-235B"
    
    # Storage Settings
    UPLOAD_DIR: str = "data/uploads"
    VECTOR_DB_DIR: str = "data/vector_db"
    MEDICAL_KNOWLEDGE_DIR: str = "data/raw_knowledge" # Where the PDF guidelines live

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
os.makedirs(settings.MEDICAL_KNOWLEDGE_DIR, exist_ok=True)
