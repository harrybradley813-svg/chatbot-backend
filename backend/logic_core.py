import json
import os
import difflib
from openai import OpenAI

# 🔑 Set your OpenAI API key here
client = OpenAI(api_key=("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"))

# 📂 Load FAQ data from faq.json
def load_faqs():
    try:
        with open("faq.json", "r") as f:
            data = json.load(f)
            return data["faqs"]
    except FileNotFoundError:
        print("⚠️ faq.json not found.")
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
