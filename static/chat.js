document.addEventListener("DOMContentLoaded", () => {

  const messages = document.getElementById("messages");
  const input = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");

  let welcomeVisible = true;

  function showWelcome() {
    const div = document.createElement("div");
    div.className = "welcome-box";

    div.innerHTML = `
      <h2>👋 Olá!</h2>
      <p>Sou seu <strong>Agent de Pipelines 🤖</strong></p>
      <p>Transformo ideias em <strong>.gitlab-ci.yml</strong></p>

      <div class="chips">
        <div class="chip">pipeline java com build e test</div>
        <div class="chip">pipeline docker build e push</div>
        <div class="chip">pipeline python com pytest</div>
        <div class="chip">pipeline node com npm install e build</div>
      </div>
    `;

    div.querySelectorAll(".chip").forEach(c => {
      c.onclick = () => {
        input.value = c.innerText;
        input.focus();
      };
    });

    messages.appendChild(div);
  }

  function scrollToBottom() {
    messages.scrollTop = messages.scrollHeight;
  }

  function addMessage(text, type="user") {
    const div = document.createElement("div");
    div.className = `msg ${type}`;
    div.innerHTML = `<div class="bubble">${text}</div>`;
    messages.appendChild(div);
    scrollToBottom();
  }

  async function sendMessage() {
    const prompt = input.value.trim();
    const provider = document.getElementById("provider").value;
    if (!prompt) return;

    if (welcomeVisible) {
      messages.innerHTML = "";
      welcomeVisible = false;
    }

    addMessage(prompt, "user");

    input.value = "";
    input.style.height = "auto";

    const res = await fetch("/api/stream", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({prompt, provider})
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      addMessage(chunk, "ai");
    }
  }

  sendBtn.onclick = sendMessage;

  showWelcome();

});
