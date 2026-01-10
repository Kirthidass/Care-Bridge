from google.adk.tools import BaseTool

# This tool acts as the "Safety Net".
# It quickly scans for values that are "Critical" (life-threatening)
# and adds a warning flag.

class SafetyCheckerTool(BaseTool):
    name = "safety_checker"
    description = "Checks extracted values for critical/panic levels."

    def __init__(self):
        super().__init__(name="safety_checker", description="Checks extracted values for critical/panic levels.")

    def run(self, extracted_data: dict):
        warnings = []
        
        # In a real system, this would be a comprehensive rules engine.
        # Here we demonstrate the LOGIC with some examples.
        
        if "results" in extracted_data:
            for item in extracted_data["results"]:
                test_name = item.get("test", "").lower()
                try:
                    val = float(item.get("value", 0))
                except:
                    continue
                
                # Example Rule: Hemoglobin < 7 is critical
                if "hemoglobin" in test_name and val < 7.0:
                    warnings.append(f"CRITICAL: Hemoglobin is {val} g/dL (Severe Anemia Risk)")
                    
                # Example Rule: Potassium > 6.0 is critical
                if "potassium" in test_name and val > 6.0:
                    warnings.append(f"CRITICAL: Potassium is {val} mmol/L (Hyperkalemia Risk)")

        if warnings:
            return "SAFETY ALERT: " + " | ".join(warnings)
        return "No immediate critical values detected."
