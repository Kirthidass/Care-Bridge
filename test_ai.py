import os
import sys

# Set UTF-8 encoding for console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.agent import create_care_bridge_agent
from app.core.config import settings

def test_ai():
    print("\n" + "="*50)
    print("CARE-BRIDGE AI - Testing AI Integration")
    print("="*50 + "\n")
    
    # Check API Key
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "":
        print("[X] GOOGLE_API_KEY not found in .env file!")
        return
    else:
        print(f"[OK] GOOGLE_API_KEY found: {settings.GOOGLE_API_KEY[:10]}...")
    
    # Test Agent Creation
    try:
        print("\n[*] Creating Patient Agent...")
        agent = create_care_bridge_agent(role="patient")
        print("[OK] Agent created successfully!")
        print(f"    AI Enabled: {agent.ai_enabled}")
    except Exception as e:
        print(f"[X] Failed to create agent: {e}")
        return
    
    # Test AI Response
    if agent.ai_enabled:
        print("\n[*] Testing AI Response...")
        test_prompt = """
        Explain this lab test result to a patient:
        - Hemoglobin: 12.5 g/dL (Range: 12.0-16.0, Status: normal)
        
        Keep it brief and friendly.
        """
        
        try:
            response = agent.run(test_prompt)
            print("\n[OK] AI Response Received:")
            print("-" * 50)
            print(response[:300] + "..." if len(response) > 300 else response)
            print("-" * 50)
        except Exception as e:
            print(f"[X] AI Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n[!] AI is not enabled. Check if google-genai is installed.")
    
    print("\n" + "="*50)
    print("Test Complete!")
    print("="*50 + "\n")

if __name__ == "__main__":
    test_ai()
