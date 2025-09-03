// script.js

document.addEventListener("DOMContentLoaded", () => {
  const chatbox = document.getElementById("chatbox");
  const userInput = document.getElementById("userInput");
  const sendBtn = document.getElementById("sendBtn");

  // Add message to chatbox
  function addMessage(sender, message) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);

    const textNode = document.createElement("p");
    textNode.textContent = message;

    messageDiv.appendChild(textNode);
    chatbox.appendChild(messageDiv);

    // Scroll to bottom
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  // Send message to backend
  async function sendMessage() {
    const message = userInput.value.trim();
    if (message === "") return;

    // Show user message
    addMessage("user", message);
    userInput.value = "";

    try {
      const response = await fetch("/api/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message, session_id: session_id })
      });

      if (!response.ok) {
        throw new Error("Server error: " + response.statusText);
      }

      const data = await response.json();

      // Save session ID for future messages
      session_id = data.session_id;

      // Show bot reply
      addMessage("bot", data.reply);
    } catch (error) {
      console.error("Error:", error);
      addMessage("bot", "⚠️ Sorry, something went wrong. Please try again later.");
    }
  }

  // Send on button click
  sendBtn.addEventListener("click", sendMessage);

  // Send on Enter key
  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  });
});

// FAQ Toggle with smooth height transition
document.addEventListener("DOMContentLoaded", () => {
  const faqQuestions = document.querySelectorAll(".faq-question");

  faqQuestions.forEach((question) => {
    question.addEventListener("click", () => {
      const answer = question.nextElementSibling;

      if (answer.style.maxHeight) {
        // Collapse
        answer.style.maxHeight = null;
      } else {
        // Expand to fit content
        answer.style.maxHeight = answer.scrollHeight + "px";
      }

      // Toggle the + / - symbol
      const arrow = question.querySelector(".arrow");
      arrow.textContent = answer.style.maxHeight ? "-" : "+";
    });
  });
});

