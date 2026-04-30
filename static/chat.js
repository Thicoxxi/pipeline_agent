document.addEventListener("DOMContentLoaded", () => {

  const messages = document.getElementById("messages");
  const input = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");

  let welcomeVisible = true;

  // ================= AUTO EXPAND MELHORADO =================
  input.addEventListener("input", () => {
    input.style.height = "auto";

    const maxHeight = 400; // 🔥 aumentado para combinar com CSS
    input.style.height = Math.min(input.scrollHeight, maxHeight) + "px";
  });

  // ENTER ENVIA
  input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendBtn.click();
    }
  });

  // ================= AUTOCOMPLETE =================
  new Awesomplete(input, {
    list: [
      "stages", "build", "test", "deploy",
      "image", "services", "before_script",
      "script", "after_script", "rules",
      "tags", "variables", "cache"
    ],
    minChars: 1
  });

  // ================= YAML VALIDATOR =================
  function validateYAMLWithLine(yamlText) {
    try {
      jsyaml.load(yamlText);
      return { valid: true };
    } catch (e) {
      const match = e.message.match(/at line (\d+)/);
      return {
        valid: false,
        error: e.message,
        line: match ? parseInt(match[1]) : null
      };
    }
  }

  function highlightErrorLine(codeEl, lineNumber) {
    const lines = codeEl.textContent.split("\n");

    const html = lines.map((line, i) => {
      if (i + 1 === lineNumber) {
        return `<span class="error-line">${line}</span>`;
      }
      return line;
    }).join("\n");

    codeEl.innerHTML = html;
    Prism.highlightElement(codeEl);
  }

  // ================= TEMPLATES =================
  const TEMPLATES = {
    java: `stages:
  - build
  - test

build:
  stage: build
  script:
    - mvn clean package

test:
  stage: test
  script:
    - mvn test
`,
    python: `stages:
  - test

test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest
`,
    docker: `stages:
  - build

build:
  stage: build
  script:
    - docker build -t app .
    - docker push app
`
  };

  function detectTemplate(prompt) {
    prompt = prompt.toLowerCase();
    if (prompt.includes("java")) return TEMPLATES.java;
    if (prompt.includes("python")) return TEMPLATES.python;
    if (prompt.includes("docker")) return TEMPLATES.docker;
    return null;
  }

  // ================= DIGITAÇÃO OTIMIZADA =================
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

        if (this.queue.length % 5 === 0) {
          Prism.highlightElement(this.el);
        }

        await new Promise(r => setTimeout(r, 10));
      }

      Prism.highlightElement(this.el);
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
    input.style.height = "100px"; // 🔥 alinhado com CSS

    const { typer, spinner, validationDiv, code } = createCodeBlock();

    const template = detectTemplate(prompt);
    if (provider === "local" && template) {
      typer.push(template);
      spinner.remove();

      const result = validateYAMLWithLine(template);

      if (!result.valid && result.line) {
        highlightErrorLine(code, result.line);
      }

      validationDiv.innerHTML = result.valid
        ? "✅ YAML válido"
        : "❌ " + result.error;

      return;
    }

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

          const result = validateYAMLWithLine(code.textContent);

          if (result.valid) {
            validationDiv.innerHTML = "✅ YAML válido";
            validationDiv.className = "validation valid";
          } else {
            validationDiv.innerHTML = "❌ " + result.error;
            validationDiv.className = "validation invalid";

            if (result.line) {
              highlightErrorLine(code, result.line);
            }
          }
        }
      }
    }
  }

  sendBtn.onclick = sendMessage;

  showWelcome();
});
