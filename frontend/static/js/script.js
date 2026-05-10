// script.js
document.addEventListener("DOMContentLoaded", () => {
  const chatbox = document.getElementById("chatbox");
  const userInput = document.getElementById("userInput");
  const sendBtn = document.getElementById("sendBtn");
  const loginBtn = document.getElementById("loginBtn");
  const loginModal = document.getElementById("loginModal");
  const closeBtn = document.querySelector("#loginModal .close");
  const faqQuestions = document.querySelectorAll(".faq-question");

  let session_id = null; // Track session for chat

  // FAQ toggle
  faqQuestions.forEach((question) => {
    question.addEventListener("click", () => {
      const answer = question.nextElementSibling;
      const arrow = question.querySelector(".arrow");
      if (answer.style.maxHeight) {
        answer.style.maxHeight = null;
        arrow.textContent = "+";
      } else {
        answer.style.maxHeight = answer.scrollHeight + "px";
        arrow.textContent = "−";
      }
    });
  });

  // Login modal
  if (loginBtn && loginModal) {
    loginBtn.addEventListener("click", (e) => {
      e.preventDefault();
      loginModal.classList.add("show");
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", () => loginModal.classList.remove("show"));
  }

  window.addEventListener("click", (e) => {
    if (loginModal && e.target === loginModal) loginModal.classList.remove("show");
  });

  if (!chatbox || !userInput || !sendBtn) return;

  // Typing indicator
  function showTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message bot typing";
    typingDiv.id = "bot-thinking";
    typingDiv.innerHTML = `<p class="typing-indicator"><span></span><span></span><span></span></p>`;
    chatbox.appendChild(typingDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  function hideTypingIndicator() {
    const typingDiv = document.getElementById("bot-thinking");
    if (typingDiv) typingDiv.remove();
  }

  // Add message to chatbox
  function addMessage(sender, message) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    const textNode = document.createElement("p");
    textNode.textContent = message;
    messageDiv.appendChild(textNode);
    chatbox.appendChild(messageDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  // Send message to backend
  async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    addMessage("user", message);
    userInput.value = "";
    showTypingIndicator();

    try {
      const response = await fetch("/api/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message, session_id: session_id }),
      });

      if (!response.ok) throw new Error("Server error: " + response.statusText);

      const data = await response.json();
      session_id = data.session_id || session_id;

      hideTypingIndicator();
      addMessage("bot", data.reply);
    } catch (error) {
      console.error("Error:", error);
      hideTypingIndicator();
      addMessage("bot", "⚠️ Sorry, something went wrong. Please try again later.");
    }
  }

  // Send on button click
  sendBtn.addEventListener("click", sendMessage);

  // Send on Enter key
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Optional: focus input on load
  userInput.focus();
});
