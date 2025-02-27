document.addEventListener("DOMContentLoaded", function () {
    let chatBox = document.querySelector(".chat-box");
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to latest message
});