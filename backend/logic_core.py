import json
import os # Make sure this is imported!
import difflib
from openai import OpenAI

# 🔑 Set your OpenAI API key here
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- START OF CHANGE ---
# Get the directory where the current script (logic_core.py) is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAQ_PATH = os.path.join(BASE_DIR, 'faq.json')

# 📂 Load FAQ data from faq.json
def load_faqs():
    try:
        # Use the constructed absolute path
        with open(FAQ_PATH, "r") as f: 
            data = json.load(f)
            return data["faqs"]
    except FileNotFoundError:
        print(f"⚠️ faq.json not found at {FAQ_PATH}") # Added f-string for better debugging
        return []
    except json.JSONDecodeError:
        print("⚠️ Error reading faq.json (check your JSON format).")
        return []

# --- END OF CHANGE ---

# 🔍 Match a user message to an FAQ
def match_faq(user_input, faqs):
    user_input = user_input.lower()
    best_match = None
    best_score = 0

    for item in faqs:
        question = item["question"].lower()
        score = difflib.SequenceMatcher(None, user_input, question).ratio()

        if score > best_score:
            best_score = score
            best_match = item["answer"]
    
    return best_match if best_score >= 0.45 else None

# 💬 Ask OpenAI if no FAQ match is found
def ask_openai(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Peonia Hairs AI Assistant. Be friendly and helpful."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ OpenAI error:", e)
        return "Sorry, I couldn't generate a response."

# 🧠 Reset stored memory (if using sessions)
def reset_memory():
    return "Chat memory cleared."