document.addEventListener("DOMContentLoaded", () => {

  const messages = document.getElementById("messages");
  const input = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const providerSel = document.getElementById("provider");

  let welcomeVisible = true;

  // Auto expand
  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 360) + "px";
  });

  // Enter to send
  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendBtn.click();
    }
  });

  // Autocomplete
  new Awesomplete(input, {
    list: [
      "stages", "build", "test", "deploy",
      "image", "services", "before_script",
      "script", "after_script", "rules",
      "tags", "variables", "cache"
    ],
    minChars: 1
  });

  function scrollBottom() {
    messages.scrollTop = messages.scrollHeight;
  }

  function showWelcome() {
    const div = document.createElement("div");
    div.className = "welcome-box";
    div.innerHTML = `
      <h2>👋 Olá!</h2>
      <p>Gere pipelines GitLab automaticamente</p>
      <div class="chips">
        <div class="chip">pipeline java com build e test</div>
        <div class="chip">pipeline docker build e push</div>
        <div class="chip">pipeline python com pytest</div>
      </div>
    `;
    div.querySelectorAll(".chip").forEach(c => {
      c.onclick = () => { input.value = c.innerText; input.focus(); };
    });
    messages.appendChild(div);
  }

  function addUser(text) {
    const d = document.createElement("div");
    d.className = "msg user";
    d.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
    messages.appendChild(d);
    scrollBottom();
  }

  function createAICodeBlock() {
    const wrapper = document.createElement("div");
    wrapper.className = "msg ai";

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    const actions = document.createElement("div");
    actions.className = "actions";

    const copyBtn = document.createElement("button");
    copyBtn.className = "action-btn";
    copyBtn.textContent = "📋 copiar";

    const downloadBtn = document.createElement("button");
    downloadBtn.className = "action-btn";
    downloadBtn.textContent = "⬇️ baixar";

    const spinner = document.createElement("div");
    spinner.className = "spinner";

    const pre = document.createElement("pre");
    const code = document.createElement("code");
    code.classList.add("language-yaml", "typing");

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

    copyBtn.onclick = () => navigator.clipboard.writeText(code.textContent || "");
    downloadBtn.onclick = () => {
      const blob = new Blob([code.textContent || ""], { type: "text/yaml" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = ".gitlab-ci.yml";
      a.click();
      URL.revokeObjectURL(a.href);
    };

    return { wrapper, code, spinner, validationDiv };
  }

  function validateYAML(yamlText) {
    try {
      jsyaml.load(yamlText);
      return { valid: true };
    } catch (e) {
      return { valid: false, error: e.message };
    }
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  async function sendMessage() {
    const prompt = input.value.trim();
    const provider = providerSel.value;
    if (!prompt) return;

    if (welcomeVisible) {
      messages.innerHTML = "";
      welcomeVisible = false;
    }

    addUser(prompt);
    input.value = "";
    input.style.height = "auto";

    const { code, spinner, validationDiv } = createAICodeBlock();
    scrollBottom();

    const res = await fetch("/api/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, provider })
    });

    if (!res.ok || !res.body) {
      spinner.remove();
      validationDiv.textContent = "❌ erro ao conectar";
      validationDiv.classList.add("invalid");
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    let fullText = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const parts = chunk.split("\n\n");

      for (let p of parts) {
        if (!p.startsWith("data:")) continue;
        const payload = p.replace(/^data:\s*/, "");

        try {
          const json = JSON.parse(payload);

          if (json.chunk !== undefined) {
            fullText += json.chunk;
            code.textContent = fullText;
            scrollBottom();
          }

          if (json.validation) {
            // optional server signal
          }
        } catch (e) {
          // ignore partial frames
        }
      }
    }

    // finalize
    spinner.remove();
    code.classList.remove("typing");
    Prism.highlightElement(code);

    const result = validateYAML(fullText);
    if (result.valid) {
      validationDiv.textContent = "✅ YAML válido";
      validationDiv.classList.add("valid");
    } else {
      validationDiv.textContent = "❌ " + result.error;
      validationDiv.classList.add("invalid");
    }
  }

  sendBtn.onclick = sendMessage;
  showWelcome();

});
