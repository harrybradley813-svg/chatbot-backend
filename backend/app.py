from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
import os, uuid
# Assuming you have a 'CORS' object for configuration
# If this causes an error, you may need to import flask_cors and use CORS(app)
import CORS
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
    return "MRUKs AI Assistant Backend is running.", 200

# *** FIX HERE: Changed from "/api/chat" to "/chat" ***
@app.route("/chat", methods=["POST"])
def chat():
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if not openai_api_key:
        return jsonify({"reply": "Error: OpenAI API Key is missing on the server."}), 500
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Please type something."})

    faq_match = match_faq(user_input, faqs)
    if faq_match:
        return jsonify({"reply": faq_match})

    # The failure is happening inside ask_openai due to the API key.
    # The Vercel routing fix will get us here, but we still need the key to work.
    ai_reply = ask_openai(user_input, openai_api_key)
    return jsonify({"reply": ai_reply})

# *** FIX HERE: Changed from "/api/reset" to "/reset" ***
@app.route("/reset", methods=["POST"])
def reset():
    reset_memory()
    session.clear()
    return jsonify({"reply": "Chat memory cleared!"})

# --- CLEANED RUNTIME BLOCK ---
if __name__ == "__main__":
    print("🚀 Running chatbot on http://127.0.0.1:5000")
    # Set debug=True for local development only
    app.run(debug=True, host="0.0.0.0", port=5000)