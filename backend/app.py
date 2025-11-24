from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from datetime import timedelta
import os, uuid
from logic_core import load_faqs, match_faq, ask_openai, reset_memory

app = Flask(__name__)

# Secret key and session configuration
app.secret_key = os.environ.get("SECRET_KEY", "defaultsceretkey")
SESSION_DIR = os.path.join(os.getcwd(), "flask_session_data")
os.makedirs(SESSION_DIR, exist_ok=True)

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = SESSION_DIR
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
Session(app)

# Load FAQ data
faqs = load_faqs()

# Generate unique session ID
@app.before_request
def ensure_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
        print(f"New session: {session['session_id']}")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Please type something."})

    faq_match = match_faq(user_input, faqs)
    if faq_match:
        return jsonify({"reply": faq_match})

    ai_reply = ask_openai(user_input)
    return jsonify({"reply": ai_reply})

@app.route("/reset", methods=["POST"])
def reset():
    reset_memory()
    session.clear()
    return jsonify({"reply": "Chat memory cleared!"})

if __name__ == "__main__":
    print("🚀 Running chatbot on http://127.0.0.1:5000")
    app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)