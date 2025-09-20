// script.js
document.addEventListener("DOMContentLoaded", () => {
  const chatbox = document.getElementById("chatbox");
  const userInput = document.getElementById("userInput");
  const sendBtn = document.getElementById("sendBtn");
  const loginBtn = document.getElementById("loginBtn");
  const loginModal = document.getElementById("loginModal");
  const closeBtn = document.querySelector("#loginModal .close");
  const faqQuestions = document.querySelectorAll(".faq-question");

  faqQuestions.forEach((question) => {
  question.addEventListener("click", () => {
    const answer = question.nextElementSibling; // get the <p> immediately after button
    const arrow = question.querySelector(".arrow");

    // Toggle the max-height
    if (answer.style.maxHeight) {
      answer.style.maxHeight = null; // collapse
      arrow.textContent = "+"; // change arrow back
    } else {
      answer.style.maxHeight = answer.scrollHeight + "px"; // expand
      arrow.textContent = "−"; // change arrow to minus
    }
  });
});
  loginBtn.addEventListener("click", (e) => {
    e.preventDefault();
    loginModal.classList.add("show");
  });

  // Close modal
  closeBtn.addEventListener("click", () => {
    loginModal.classList.remove("show");
  });

  // Close modal when clicking outside modal content
  window.addEventListener("click", (e) => {
    if (e.target === loginModal) {
      loginModal.classList.remove("show");
    }
  });

  // Typing indicator functions
  function showTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message bot typing";
    typingDiv.id = "bot-thinking";
    typingDiv.innerHTML = `
      <p class="typing-indicator">
        <span></span><span></span><span></span>
      </p>
    `;
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
    if (message === "") return;

    // Show user message
    addMessage("user", message);
    userInput.value = "";

    // Show typing indicator
    showTypingIndicator();

    try {
      const response = await fetch("/api/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message, session_id: session_id }),
      });

      if (!response.ok) throw new Error("Server error: " + response.statusText);

      const data = await response.json();
      session_id = data.session_id;

      // Hide typing dots
      hideTypingIndicator();

      // Add bot reply
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
  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  });
});