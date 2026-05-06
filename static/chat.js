document.addEventListener("DOMContentLoaded", () => {

  const input = document.getElementById("chatInput");
  const messages = document.getElementById("messages");
  const sendBtn = document.getElementById("sendBtn");

  // ================= YAML VALIDATION =================
  function validateYAML(text){
    try {
      if (typeof YAML !== "undefined") YAML.parse(text);
      else jsyaml.load(text);

      return { valid: true, message: "✔️ YAML válido" };
    } catch (e) {
      const match = e.message.match(/line (\d+)/i);
      return {
        valid: false,
        message: `❌ ${e.message}`,
        line: match ? parseInt(match[1]) : null
      };
    }
  }

  function highlight(textarea, line){
    if(!line) return;

    const lines = textarea.value.split("\n");
    let pos = 0;

    for(let i=0;i<line-1;i++){
      pos += lines[i].length + 1;
    }

    textarea.focus();
    textarea.setSelectionRange(pos, pos + lines[line-1].length);
  }

  // ================= WELCOME =================
  function showWelcome(){
    const div = document.createElement("div");
    div.className = "welcome-box";

    div.innerHTML = `
      <h2>👋 Olá!</h2>
      <p>Sou seu assistente para criar pipelines CI/CD 🚀</p>

      <div class="chips">
        <span class="chip">pipeline gitlab python pytest</span>
        <span class="chip">pipeline gitlab docker build push</span>
        <span class="chip">pipeline gitlab nodejs build deploy</span>
        <span class="chip">pipeline github actions node 20</span>
        <span class="chip">pipeline github actions java maven</span>
      </div>
    `;

    messages.appendChild(div);

    div.querySelectorAll(".chip").forEach(chip => {
      chip.onclick = () => {
        input.value = chip.textContent;
        sendBtn.click();
      };
    });
  }

  function clearWelcome(){
    document.querySelector(".welcome-box")?.remove();
  }

  // ================= CONVERT =================
  function convertToGitHub(yaml){
    try{
      const parsed = jsyaml.load(yaml);
      let jobs = "";

      for(const key in parsed){
        if(parsed[key].script){
          jobs += `
  ${key}:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
${parsed[key].script.map(s=>"          "+s).join("\n")}
`;
        }
      }

      return `name: CI
on: [push]

jobs:
${jobs}`;
    }catch{
      return "# erro ao converter";
    }
  }

  // ================= BLOCK =================
  function createBlock(provider){

    const wrap = document.createElement("div");

    const header = document.createElement("div");
    header.className = "provider-tag";
    header.textContent = provider.toUpperCase();

    const actions = document.createElement("div");
    actions.className = "actions";

    const updateBtn = document.createElement("button");
    updateBtn.textContent = "♻️ Atualizar";

    actions.append(updateBtn);

    const container = document.createElement("div");
    container.className = "split-view";

    // LEFT (GitLab)
    const left = document.createElement("div");

    const leftHeader = document.createElement("div");
    leftHeader.className = "block-header";

    const saveGitlab = document.createElement("button");
    saveGitlab.textContent = "💾 GitLab";

    leftHeader.appendChild(saveGitlab);

    const codeLeft = document.createElement("textarea");
    codeLeft.className = "editor";

    left.append(leftHeader, codeLeft);

    // RIGHT (GitHub)
    const right = document.createElement("div");

    const rightHeader = document.createElement("div");
    rightHeader.className = "block-header";

    const saveGithub = document.createElement("button");
    saveGithub.textContent = "💾 GitHub";

    rightHeader.appendChild(saveGithub);

    const codeRight = document.createElement("textarea");
    codeRight.className = "editor";

    right.append(rightHeader, codeRight);

    container.append(left, right);

    const val = document.createElement("div");
    val.className = "validation";

    wrap.append(header, actions, container, val);
    messages.appendChild(wrap);

    // EVENTS
    codeLeft.addEventListener("input", () => {
      const res = validateYAML(codeLeft.value);

      val.textContent = res.message;
      val.style.color = res.valid ? "#22c55e" : "#ef4444";

      if(!res.valid) highlight(codeLeft, res.line);
    });

    updateBtn.onclick = () => {
      const res = validateYAML(codeLeft.value);

      if(!res.valid){
        val.textContent = res.message;
        val.style.color = "#ef4444";
        highlight(codeLeft, res.line);
        return;
      }

      codeRight.value = convertToGitHub(codeLeft.value);
      val.textContent = "✔️ convertido";
    };

    saveGitlab.onclick = () => {
      const blob = new Blob([codeLeft.value]);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = ".gitlab-ci.yml";
      a.click();
    };

    saveGithub.onclick = () => {
      const blob = new Blob([codeRight.value]);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "github-actions.yml";
      a.click();
    };

    return {
      setData: (yaml) => {
        codeLeft.value = yaml;
        codeRight.value = convertToGitHub(yaml);
      }
    };
  }

  // ================= SEND =================
  sendBtn.onclick = async () => {

    clearWelcome();

    const prompt = input.value;
    const provider = document.getElementById("provider").value;

    const block = createBlock(provider);

    const res = await fetch("/api/stream", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ prompt, provider })
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    while(true){
      const {done,value} = await reader.read();
      if(done) break;

      const chunk = decoder.decode(value);
      const parts = chunk.split("\n\n");

      for(let p of parts){
        if(!p.startsWith("data:")) continue;

        const json = JSON.parse(p.replace("data: ",""));

        if(json.yaml){
          block.setData(json.yaml);
        }
      }
    }
  };

  showWelcome();

});