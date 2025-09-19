from flask_cors import CORS
import os, datetime, uuid, random, json
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# ---------- Setup ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # just the backend folder

blenderbot_tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
blenderbot_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")
blenderbot_model.to("cpu")  # your CPU-only setup

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database", "mindease.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ---------- Ensure NLTK Data ----------
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

# ---------- Sentiment Analyzer ----------
sia = SentimentIntensityAnalyzer()

# ---------- Load Predefined Responses ----------
RESPONSES_FILE = os.path.join(BASE_DIR, "responses.json")
if os.path.exists(RESPONSES_FILE):
    with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
        responses = json.load(f)
else:
    # fallback minimal responses
    responses = {
        "positive": ["That's great! 🌟"],
        "neutral": ["I hear you."],
        "negative": ["I'm sorry you're feeling this way."],
        "strongly_negative": ["You're not alone. Reach out if you need help."]
    }

# Track last bot message per session to avoid repetition
last_bot_messages = {}

# ---------- Models ----------
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), index=True)
    role = db.Column(db.String(10))  # 'user' or 'bot'
    content = db.Column(db.Text)
    sentiment = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

def get_blenderbot_reply(user_text):
    inputs = blenderbot_tokenizer(user_text, return_tensors="pt").to("cpu")
    reply_ids = blenderbot_model.generate(**inputs, use_cache=False, max_new_tokens=50)
    bot_reply = blenderbot_tokenizer.decode(reply_ids[0], skip_special_tokens=True)
    return bot_reply

# ---------- Utils ----------
def classify_sentiment(text: str):
    scores = sia.polarity_scores(text)
    c = scores["compound"]
    if c >= 0.3:
        return "positive", c
    elif c <= -0.6:
        return "strongly_negative", c
    elif c <= -0.2:
        return "negative", c
    else:
        return "neutral", c

def local_reply(label, session_id=None):
    """Return a random reply based on sentiment, avoiding repetition."""
    options = responses.get(label, ["I hear you."])
    last_msg = last_bot_messages.get(session_id)
    if last_msg in options:
        options = [r for r in options if r != last_msg]
    reply = random.choice(options)
    if session_id:
        last_bot_messages[session_id] = reply
    return reply

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/resources")
def resources():
    return render_template("resources.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/api/message", methods=["POST"])
def api_message():
    data = request.get_json(force=True)
    text = (data.get("message") or "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())

    if not text:
        return jsonify({"error": "Empty message", "session_id": session_id}), 400

    # Sentiment analysis
    label, _ = classify_sentiment(text)

    # Save user message
    db.session.add(Message(session_id=session_id, role="user", content=text, sentiment=label))
    db.session.commit()

    # Generate bot reply using large predefined responses
    try:
        bot_text = get_blenderbot_reply(text)
    except Exception as e:
        print("BlenderBot error:", e)
        bot_text = local_reply(label, session_id=session_id)  # fallback


    # Extra warning for strongly negative
    if label == "strongly_negative":
        bot_text += "\n\nIf you’re thinking about harming yourself, please seek immediate help. India: AASRA 24x7 +91 9820466726 • iCALL +91 9152987821 • Local emergency services."

    # Save bot message
    db.session.add(Message(session_id=session_id, role="bot", content=bot_text, sentiment=label))
    db.session.commit()

    return jsonify({"reply": bot_text, "sentiment": label, "session_id": session_id})

@app.route("/api/mood-data", methods=["GET"])
def mood_data():
    session_id = request.args.get("session_id")
    q = Message.query
    if session_id:
        q = q.filter_by(session_id=session_id)
    q = q.filter(Message.role=="user").order_by(Message.created_at.asc())
    points = [{"t": m.created_at.isoformat(), "label": m.sentiment, "content": m.content} for m in q]
    return jsonify(points)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
