document.addEventListener("DOMContentLoaded", () => {

  const messages = document.getElementById("messages");
  const input = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");

  let welcomeVisible = true;

  // ===== YAML VALIDATOR =====
  function validateYAML(yamlText) {
    try {
      jsyaml.load(yamlText);
      return { valid: true };
    } catch (e) {
      return { valid: false, error: e.message };
    }
  }

  // ===== FILA DE DIGITAÇÃO =====
  class TypeQueue {
    constructor(element) {
      this.el = element;
      this.queue = [];
      this.running = false;
    }

    push(text) {
      this.queue.push(...text.split(""));
      if (!this.running) this.run();
    }

    async run() {
      this.running = true;

      while (this.queue.length > 0) {
        this.el.textContent += this.queue.shift();
        Prism.highlightElement(this.el);
        await new Promise(r => setTimeout(r, 5));
      }

      this.running = false;
    }
  }

  function removeWelcome() {
    if (welcomeVisible) {
      messages.innerHTML = "";
      welcomeVisible = false;
    }
  }

  function addMessage(text, type="user") {
    const div = document.createElement("div");
    div.className = `msg ${type}`;
    div.innerHTML = `<div class="bubble">${text}</div>`;
    messages.appendChild(div);
  }

  function showWelcome() {
    const div = document.createElement("div");
    div.className = "welcome-box";

    div.innerHTML = `
      <h2>👋 Olá!</h2>
      <p>Sou seu <strong>Agent de Pipelines 🤖</strong></p>
      <p>Transformo ideias em <strong>.gitlab-ci.yml</strong></p>

      <div class="chips">
        <div class="chip">pipeline java com test e build</div>
        <div class="chip">pipeline docker build e push</div>
        <div class="chip">pipeline python 3.12</div>
      </div>
    `;

    div.querySelectorAll(".chip").forEach(c => {
      c.onclick = () => input.value = c.innerText;
    });

    messages.appendChild(div);
  }

  function createCodeBlock() {
    const wrapper = document.createElement("div");
    wrapper.className = "msg ai";

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    const actions = document.createElement("div");
    actions.className = "actions";

    const copyBtn = document.createElement("button");
    copyBtn.className = "action-btn";
    copyBtn.innerText = "📋 copiar";

    const downloadBtn = document.createElement("button");
    downloadBtn.className = "action-btn";
    downloadBtn.innerText = "⬇️ baixar";

    const spinner = document.createElement("div");
    spinner.className = "spinner";

    const pre = document.createElement("pre");
    const code = document.createElement("code");

    const validationDiv = document.createElement("div");
    validationDiv.className = "validation";

    pre.appendChild(code);
    actions.appendChild(copyBtn);
    actions.appendChild(downloadBtn);

    bubble.appendChild(actions);
    bubble.appendChild(spinner);
    bubble.appendChild(pre);
    bubble.appendChild(validationDiv);

    wrapper.appendChild(bubble);
    messages.appendChild(wrapper);

    const typer = new TypeQueue(code);

    copyBtn.onclick = () => navigator.clipboard.writeText(code.textContent);

    downloadBtn.onclick = () => {
      const blob = new Blob([code.textContent], {type: "text/yaml"});
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = ".gitlab-ci.yml";
      a.click();
    };

    return { typer, spinner, validationDiv, code };
  }

  async function sendMessage() {
    const provider = document.getElementById("provider").value;
    const prompt = input.value.trim();
    if (!prompt) return;

    removeWelcome();
    addMessage(prompt, "user");

    input.value = "";

    const { typer, spinner, validationDiv, code } = createCodeBlock();

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
      const parts = chunk.split("\n\n");

      for (let p of parts) {
        if (!p.startsWith("data:")) continue;

        const json = JSON.parse(p.replace("data: ", ""));

        if (json.chunk) {
          typer.push(json.chunk);
        }

        if (json.validation) {
          spinner.remove();

          const result = validateYAML(code.textContent);

          if (result.valid) {
            validationDiv.innerHTML = "✅ YAML válido";
            validationDiv.classList.add("valid");
          } else {
            validationDiv.innerHTML = "❌ YAML inválido:<br>" + result.error;
            validationDiv.classList.add("invalid");
          }
        }
      }
    }
  }

  sendBtn.onclick = sendMessage;

  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  showWelcome();
});