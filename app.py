from flask_cors import CORS
import os, datetime, uuid, random, json
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from groq import Groq

# ---------- Setup ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # just the backend folder
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "frontend", "static")
)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "database", "mindease.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ---------- Sentiment Analyzer ----------
sia = None
groq_client = None

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

CRISIS_MESSAGE = (
    "I'm really glad you told me. If you might hurt yourself or feel unsafe, "
    "please contact emergency services right now or reach out to someone near you. "
    "India: AASRA 24x7 +91 9820466726, iCALL +91 9152987821. "
    "If you can, move away from anything you could use to hurt yourself and call "
    "a trusted person to stay with you. You do not have to handle this alone."
)

SYSTEM_PROMPT = """
You are MindEase, a warm mental health support chatbot for a student project.
You are not a therapist, doctor, or emergency service.

Style:
- Be empathetic, specific, and conversational.
- Keep replies concise: usually 3 to 6 sentences.
- Ask one gentle follow-up question when useful.
- Offer practical coping steps such as breathing, grounding, journaling, reframing, or breaking a problem into small next actions.
- Do not sound generic or repetitive.

Safety:
- Never diagnose.
- Never claim to provide professional treatment.
- If the user may be in immediate danger or mentions self-harm intent, urge immediate help from local emergency services, a trusted person, or a crisis helpline.
""".strip()

# ---------- Models ----------
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), index=True)
    role = db.Column(db.String(10))  # 'user' or 'bot'
    content = db.Column(db.Text)
    sentiment = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# ---------- Utils ----------
def get_sentiment_analyzer():
    global sia
    if sia is None:
        try:
            nltk.data.find("sentiment/vader_lexicon.zip")
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)
        sia = SentimentIntensityAnalyzer()
    return sia

def classify_sentiment(text: str):
    scores = get_sentiment_analyzer().polarity_scores(text)
    c = scores["compound"]
    if c >= 0.3:
        return "positive", c
    elif c <= -0.6:
        return "strongly_negative", c
    elif c <= -0.2:
        return "negative", c
    else:
        return "neutral", c

def get_groq_client():
    global groq_client
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    if groq_client is None:
        groq_client = Groq(api_key=api_key)
    return groq_client

def has_crisis_language(text: str):
    lowered = text.lower()
    crisis_phrases = [
        "kill myself",
        "end my life",
        "suicide",
        "suicidal",
        "hurt myself",
        "harm myself",
        "self harm",
        "self-harm",
        "i want to die",
        "don't want to live",
        "dont want to live",
    ]
    return any(phrase in lowered for phrase in crisis_phrases)

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

def conversation_history(session_id, limit=8):
    messages = (
        Message.query.filter_by(session_id=session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()
    history = []
    for message in messages:
        role = "assistant" if message.role == "bot" else "user"
        content = (message.content or "").strip()
        if content:
            history.append({"role": role, "content": content[:1200]})
    return history

def groq_reply(session_id, label):
    client = get_groq_client()
    if client is None:
        return None

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": f"The latest sentiment label is {label}. Use it only as a hint, not a diagnosis.",
        },
    ]
    messages.extend(conversation_history(session_id))

    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.75,
        max_tokens=220,
    )
    return completion.choices[0].message.content.strip()

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

    if has_crisis_language(text):
        bot_text = CRISIS_MESSAGE
    else:
        try:
            bot_text = groq_reply(session_id, label) or local_reply(label, session_id=session_id)
        except Exception as e:
            app.logger.warning("Groq reply failed: %s", e)
            bot_text = local_reply(label, session_id=session_id)

        # Extra warning for strongly negative messages.
        if label == "strongly_negative":
            bot_text += "\n\nIf you're thinking about harming yourself, please seek immediate help. India: AASRA 24x7 +91 9820466726, iCALL +91 9152987821, or local emergency services."

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
