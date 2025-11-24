from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
import os, uuid
from logic_core import load_faqs, match_faq, ask_openai, reset_memory

app = Flask(__name__)

# --- SESSION CONFIGURATION (CLEANED FOR VERCEL) ---
# 1. Use a secure secret key from environment variables
app.secret_key = os.environ.get("SECRET_KEY", "a_very_secure_default_secret_key_if_none_is_set")

# 2. Configure session to use secure settings (switches to cookie-based storage)
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)
app.config["SESSION_USE_SIGNER"] = True
# Set session cookie security flags appropriate for production
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True if you deploy over HTTPS
# NOTE: Removed file-system specific configs (SESSION_TYPE, SESSION_FILE_DIR)

# Load FAQ data
faqs = load_faqs()

# Generate unique session ID
@app.before_request
def ensure_session_id():
    # Only checks if session ID exists. Session object is handled by app.secret_key.
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
        print(f"New session: {session['session_id']}")

@app.route("/")
def home():
    # Since Vercel is only hosting your API, this route might return nothing or a placeholder.
    # It's generally fine to leave as is if you don't intend to render HTML here.
    return "MRUKs AI Assistant Backend is running.", 200

@app.route("/api/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Please type something."})

    faq_match = match_faq(user_input, faqs)
    if faq_match:
        return jsonify({"reply": faq_match})

    ai_reply = ask_openai(user_input)
    return jsonify({"reply": ai_reply})

@app.route("/api/reset", methods=["POST"])
def reset():
    reset_memory()
    session.clear()
    return jsonify({"reply": "Chat memory cleared!"})

# --- CLEANED RUNTIME BLOCK ---
# Vercel ignores these blocks, but we keep a single, clean one for local testing.
if __name__ == "__main__":
    print("🚀 Running chatbot on http://127.0.0.1:5000")
    # Set debug=True for local development only
    app.run(debug=True, host="0.0.0.0", port=5000)