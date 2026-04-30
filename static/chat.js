const messages = document.getElementById("messages");
const input = document.getElementById("chatInput");

// -----------------------------
// SUGESTÕES
// -----------------------------
const SUGGESTIONS = [
  "criar pipeline dotnet core 10",
  "pipeline java com test e build",
  "pipeline terraform aws",
  "pipeline python 3.12",
  "pipeline .net framework 4.8 com nuget",
  "pipeline docker build e push",
  "pipeline node com npm install e test"
];

// -----------------------------
// ADD MESSAGE
// -----------------------------
function addMessage(html, type="ai") {
  const div = document.createElement("div");
  div.className = `msg ${type}`;
  div.innerHTML = `<div class="bubble">${html}</div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

// -----------------------------
// TYPE HTML (EFEITO REAL)
// -----------------------------
function typeHTML(element, html, speed = 12) {
  const temp = document.createElement("div");
  temp.innerHTML = html;

  let queue = [];

  function walk(node) {
    if (node.nodeType === 3) {
      queue.push({type: "text", content: node.textContent});
    } else if (node.nodeType === 1) {
      queue.push({type: "startTag", tag: node.cloneNode(false)});
      node.childNodes.forEach(walk);
      queue.push({type: "endTag"});
    }
  }

  temp.childNodes.forEach(walk);

  let currentNode = element;
  let stack = [];
  let i = 0;

  function process() {
    if (i >= queue.length) return;

    const item = queue[i];

    if (item.type === "startTag") {
      const el = item.tag;
      currentNode.appendChild(el);
      stack.push(currentNode);
      currentNode = el;
      i++;
      process();
    }
    else if (item.type === "endTag") {
      currentNode = stack.pop();
      i++;
      process();
    }
    else if (item.type === "text") {
      let text = item.content;
      let j = 0;

      function typeChar() {
        if (j < text.length) {
          currentNode.append(text[j]);
          j++;
          setTimeout(typeChar, speed);
        } else {
          i++;
          process();
        }
      }

      typeChar();
    }
  }

  process();
}

// -----------------------------
// CURSOR
// -----------------------------
function addCursor(element) {
  const cursor = document.createElement("span");
  cursor.className = "typing-cursor";
  cursor.innerText = "|";
  element.appendChild(cursor);
  return cursor;
}

// -----------------------------
// WELCOME
// -----------------------------
function typeMessage(html) {
  const div = document.createElement("div");
  div.className = "msg ai";

  const bubble = document.createElement("div");
  bubble.className = "bubble welcome";

  div.appendChild(bubble);
  messages.appendChild(div);

  const cursor = addCursor(bubble);

  typeHTML(bubble, html, 10);

  setTimeout(() => {
    cursor.remove();
  }, 4000);
}

function showWelcome() {
  typeMessage(`
    <h2>👋 Olá!</h2>
    <p>Sou seu <strong>Agent de Pipelines 🤖</strong></p>
    <p>Transformo ideias em <strong>.gitlab-ci.yml</strong> ⚡</p>
    <p style="opacity:0.7">Clique em um exemplo abaixo:</p>
  `);

  renderChips(SUGGESTIONS);
}

// -----------------------------
// CHIPS
// -----------------------------
function renderChips(list) {
  const container = document.createElement("div");
  container.className = "chips";

  list.forEach(text => {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.innerText = text;

    chip.onclick = () => {
      input.value = text;
      input.focus();
    };

    container.appendChild(chip);
  });

  messages.appendChild(container);
}

// -----------------------------
// CODE BLOCK
// -----------------------------
function createCodeBlock() {
  const wrapper = document.createElement("div");
  wrapper.className = "msg ai";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  const header = document.createElement("div");
  header.style.display = "flex";
  header.style.justifyContent = "space-between";

  const providerLabel = document.createElement("span");
  const validationLabel = document.createElement("span");

  const spinner = document.createElement("div");
  spinner.className = "spinner";

  const copyBtn = document.createElement("button");
  copyBtn.textContent = "📋";

  const downloadBtn = document.createElement("button");
  downloadBtn.textContent = "⬇️";

  const pre = document.createElement("pre");
  const code = document.createElement("code");
  code.className = "language-yaml";

  copyBtn.onclick = () => {
    navigator.clipboard.writeText(code.textContent);
  };

  downloadBtn.onclick = () => {
    const blob = new Blob([code.textContent], {type: "text/yaml"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = ".gitlab-ci.yml";
    a.click();
  };

  header.appendChild(providerLabel);
  header.appendChild(validationLabel);

  bubble.appendChild(header);
  bubble.appendChild(spinner);
  bubble.appendChild(copyBtn);
  bubble.appendChild(downloadBtn);

  pre.appendChild(code);
  bubble.appendChild(pre);

  wrapper.appendChild(bubble);
  messages.appendChild(wrapper);

  return {code, spinner, providerLabel, validationLabel};
}

// -----------------------------
// SEND
// -----------------------------
async function sendMessage() {
  const provider = document.getElementById("provider").value;
  const prompt = input.value.trim();

  if (!prompt) return;

  addMessage(prompt, "user");
  input.value = "";

  const {code, spinner, providerLabel, validationLabel} = createCodeBlock();

  const res = await fetch("/api/stream", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({prompt, provider})
  });

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  let full = "";

  while (true) {
    const {done, value} = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const parts = chunk.split("\n\n");

    for (let p of parts) {
      if (!p.startsWith("data:")) continue;

      const json = JSON.parse(p.replace("data: ", ""));

      if (json.error) {
        spinner.remove();
        code.textContent = "❌ Erro: " + json.error;
        return;
      }

      if (json.chunk) {
        full += json.chunk;
        code.textContent = full;
        Prism.highlightElement(code);
      }

      if (json.provider) {
        if (json.provider === "openai") {
          providerLabel.textContent = "🤖 OpenAI";
        } else if (json.provider === "groq") {
          providerLabel.textContent = "⚡ Groq";
        } else {
          providerLabel.textContent = "🧠 Local";
        }
      }

      if (json.validation) {
        validationLabel.textContent = json.validation;
        spinner.remove();
      }
    }
  }
}

// -----------------------------
document.getElementById("sendBtn").onclick = sendMessage;

input.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

document.addEventListener("DOMContentLoaded", showWelcome);