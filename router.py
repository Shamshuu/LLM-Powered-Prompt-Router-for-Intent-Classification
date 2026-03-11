import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq Client
# Note: Ensure GROQ_API_KEY is set in your .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load Prompts
with open("prompts.json", "r", encoding="utf-8") as f:
    PROMPTS = json.load(f)

# Supported intents
SUPPORTED_INTENTS = {"code", "data", "writing", "career", "unclear"}

def log_request(intent: str, confidence: float, user_message: str, final_response: str):
    """Logs the routing cycle to a JSON Lines file."""
    log_entry = {
        "intent": intent,
        "confidence": confidence,
        "user_message": user_message,
        "final_response": final_response
    }
    with open("route_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def classify_intent(message: str) -> dict:
    """Classifies user intent dynamically, checking for manual override first."""
    # 1. Manual Override check
    if message.startswith("@"):
        parts = message.split(" ", 1)
        intent_candidate = parts[0][1:].lower()
        if intent_candidate in SUPPORTED_INTENTS and intent_candidate != "unclear":
            return {"intent": intent_candidate, "confidence": 1.0}

    # 2. LLM Classification with Groq
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": PROMPTS["classifier"]},
                {"role": "user", "content": message}
            ],
            model="llama-3.1-8b-instant", # fast and cheap
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        result_text = response.choices[0].message.content
        result_json = json.loads(result_text)
        
        intent = result_json.get("intent", "unclear").lower()
        
        try:
            confidence = float(result_json.get("confidence", 0.0))
        except (ValueError, TypeError):
            confidence = 0.0
        
        if intent not in SUPPORTED_INTENTS:
            intent = "unclear"
            
        return {"intent": intent, "confidence": confidence}

    except Exception as e:
        # Fallback for parsing errors or API issues
        print(f"Classification error: {e}")
        return {"intent": "unclear", "confidence": 0.0}

def route_and_respond(message: str, intent_dict: dict) -> str:
    """Routes the message to the appropriate expert persona and generates a response."""
    intent = intent_dict.get("intent", "unclear")
    confidence = intent_dict.get("confidence", 0.0)

    # Apply Confidence Threshold
    if confidence < 0.7:
        intent = "unclear"

    if intent == "unclear":
        return "Are you asking for help with coding, data analysis, writing, or career advice?"

    # Route to Expert
    system_prompt = PROMPTS.get(intent)
    
    if not system_prompt: # Safety net
        return "Are you asking for help with coding, data analysis, writing, or career advice?"

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            model="llama-3.3-70b-versatile", # more capable model for reasoning
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Generation error: {e}")
        return "An error occurred while generating the response."
