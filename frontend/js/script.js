// Wait until page is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // 1. FAQ Expand/Collapse
    const faqQuestions = document.querySelectorAll(".faq-question");

    faqQuestions.forEach((question) => {
        question.addEventListener("click", () => {
            // Toggle the "active" state for styling
            question.classList.toggle("active");

            // Show/hide the answer
            const answer = question.nextElementSibling;
            if (answer.style.maxHeight) {
                answer.style.maxHeight = null;
            } else {
                answer.style.maxHeight = answer.scrollHeight + "px";
            }
        });
    });

    // 2. Chatbot Toggle
    const chatToggleBtn = document.getElementById("chat-toggle-btn");
    const chatBox = document.getElementById("chatbox");

    if (chatToggleBtn && chatBox) {
        chatToggleBtn.addEventListener("click", () => {
            chatBox.classList.toggle("open");
        });
    }
});
