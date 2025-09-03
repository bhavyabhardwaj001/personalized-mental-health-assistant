# MindEase - Personal Mental Health Assistant

MindEase is a **web-based mental health companion** designed to provide emotional support, sentiment tracking, and basic mental health guidance. It leverages **NLP-based sentiment analysis** and optionally integrates with **OpenAI GPT API** for complex conversations.

---

## 🌟 Features

- **Chatbot Interface**: Friendly, supportive responses for users.
- **Sentiment Analysis**: Classifies user messages as `positive`, `neutral`, `negative`, or `strongly_negative`.
- **Hybrid Reply System**:
  - Local, pre-defined responses for quick replies.
  - GPT-based responses (if API key is provided) for emotional or complex cases.
- **Session Management**: Tracks conversation per session.
- **Mood Tracking**: Collects user sentiment over time and can generate mood data.
- **Safety Guidance**: Provides emergency helplines for strongly negative responses.

---

## 🛠️ Technology Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy
- **Database**: SQLite
- **NLP**: NLTK SentimentIntensityAnalyzer
- **Frontend**: HTML, CSS, JavaScript
- **Optional AI Integration**: OpenAI GPT API (`gpt-4o-mini`)

---

## 📂 Project Structure

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