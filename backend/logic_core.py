import json
import os 
import difflib
# Import the OpenAI client, but we will initialize it later
from openai import OpenAI

# 🔑 DELETED: Removed the global 'client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))'
# The client will now be created inside the function.

# Get the directory where the current script (logic_core.py) is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAQ_PATH = os.path.join(BASE_DIR, 'faq.json')

# 📂 Load FAQ data from faq.json
def load_faqs():
    try:
        with open(FAQ_PATH, "r") as f: 
            data = json.load(f)
            return data["faqs"]
    except FileNotFoundError:
        print(f"⚠️ faq.json not found at {FAQ_PATH}")
        return []
    except json.JSONDecodeError:
        print("⚠️ Error reading faq.json (check your JSON format).")
        return []

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
# 🔑 ADDED: api_key is now required as an argument
def ask_openai(user_input, api_key):
    try:
        # 🔑 INITIALIZE client *inside* the function using the passed key
        client = OpenAI(api_key=api_key)

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
        # This is the error the front end is seeing!
        return "Sorry, I couldn't generate a response."

# 🧠 Reset stored memory (if using sessions)
def reset_memory():
    # If you implement memory later, you will need to pass the session ID here
    return "Chat memory cleared."