```markdown
# MindEase – Personal Mental Health Assistant

**MindEase** is a **web-based mental health companion** designed to provide emotional support, sentiment tracking, and basic mental health guidance. It leverages **NLP-based sentiment analysis** and optionally integrates with the **OpenAI GPT API** for more complex and empathetic conversations.

---

## 🌟 Features

- **Chatbot Interface** – Friendly and supportive responses for users.
- **Sentiment Analysis** – Classifies messages as `positive`, `neutral`, `negative`, or `strongly_negative`.
- **Hybrid Reply System**:
  - Local, pre-defined responses for quick, lightweight replies.
  - GPT-based responses (if API key is provided) for emotional or complex situations.
- **Session Management** – Tracks conversation per user session.
- **Mood Tracking** – Records user sentiment over time and generates mood data.
- **Safety Guidance** – Provides emergency helplines for strongly negative responses.

---

## 🛠️ Technology Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** SQLite
- **NLP:** NLTK SentimentIntensityAnalyzer
- **Frontend:** HTML, CSS, JavaScript
- **Optional AI Integration:** OpenAI GPT API (`gpt-4o-mini`)

---

## 📂 Project Structure
```

personalized-mental-health-assistant/
│
├─ backend/
│ ├─ app.py # Flask application
│ └─ .env # Environment variables (API key)
│
├─ frontend/
│ ├─ html/
│ │ ├─ index.html
│ │ ├─ chatbot.html
│ │ ├─ resources.html
│ │ └─ privacy.html
│ ├─ css/
│ │ └─ chatbot.css
│ └─ js/
│ └─ script.js
│
└─ database/
└─ mindease.db # SQLite database

````

---

## ⚡ Setup & Installation

1. **Clone the repository**
```bash
git clone <your-repo-link>
cd personalized-mental-health-assistant/backend
````

2. **Create a virtual environment**

```bash
python -m venv venv
# Activate the environment
# Linux / Mac
source venv/bin/activate
# Windows
venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up `.env` (optional, only if using GPT API)**
   Create a `.env` file in `backend/`:

```
OPENAI_API_KEY=your_openai_api_key
```

5. **Run the application**

```bash
python app.py
```

6. **Access the chatbot**
   Open your browser and go to:
   [http://127.0.0.1:5000/chatbot](http://127.0.0.1:5000/chatbot)

---

## 📈 Future Enhancements

- Add a **graphical mood tracking dashboard**.
- Integrate **voice-based chat input/output**.
- Enable **user account login** and conversation history tracking.
- Expand **local AI responses** for offline support.

```

```
