// =========================================
// YAML -> GITHUB ACTIONS (CORRIGIDO)
// =========================================
function convertToGitHub(yaml) {

  try {

    if (!yaml) return "# yaml vazio";

    const parsed = window.jsyaml
      ? window.jsyaml.load(yaml)
      : jsyaml.load(yaml);

    if (!parsed || typeof parsed !== "object") {
      return "# YAML inválido";
    }

    let jobs = "";

    for (const key in parsed) {

      const job = parsed[key];

      if (!job) continue;

      const script = Array.isArray(job.script)
        ? job.script
        : typeof job.script === "string"
          ? [job.script]
          : [];

      if (script.length === 0) continue;

      jobs += `
  ${key}:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run ${key}
        run: |
${script.map(s => `          ${s}`).join("\n")}
`;
    }

    return `name: CI

on:
  push:

jobs:
${jobs || "  build:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo 'no jobs found'"}
`;

  } catch (err) {
    console.error("convertToGitHub error:", err);
    return "# erro ao converter YAML";
  }
}

// =========================================
// WELCOME (CORRIGIDO)
// =========================================
export function showWelcome({ messages, input, onSelect }) {

  if (!messages || typeof messages.appendChild !== "function") {
    console.error("messages inválido:", messages);
    return;
  }

  const div = document.createElement("div");
  div.className = "welcome-box";

  div.innerHTML = `
    <h1>🚀 Pipeline Generator AI</h1>
    <p>Gere pipelines GitLab CI e GitHub Actions automaticamente</p>

    <div class="chips">
      <span class="chip">pipeline gitlab python pytest docker</span>
      <span class="chip">pipeline node build deploy aws ecs</span>
      <span class="chip">pipeline github actions java maven sonar</span>
      <span class="chip">pipeline terraform aws validate plan apply</span>
      <span class="chip">pipeline dotnet core 8 build test publish</span>
    </div>
  `;

  messages.appendChild(div);

  div.querySelectorAll(".chip").forEach(chip => {

    chip.addEventListener("click", () => {

      const text = chip.textContent.trim();

      if (input) {
        input.value = text;
        input.focus();
      }

      if (onSelect) {
        onSelect(text);
      }
    });
  });
}

// =========================================
// CLEAR WELCOME
// =========================================
export function clearWelcome() {
  document.querySelector(".welcome-box")?.remove();
}

// =========================================
// USER MESSAGE
// =========================================
export function addUserMessage(messages, text) {

  if (!messages || typeof messages.appendChild !== "function") {
    console.error("addUserMessage: messages inválido", messages);
    return;
  }

  const msg = document.createElement("div");
  msg.className = "message user";

  msg.innerHTML = `
    <div class="msg-header">👤 Você</div>
    <div class="msg-body">${text}</div>
  `;

  messages.appendChild(msg);

  messages.scrollTop = messages.scrollHeight;
}