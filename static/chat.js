document.addEventListener("DOMContentLoaded", () => {

  const input = document.getElementById("chatInput");
  const messages = document.getElementById("messages");
  const sendBtn = document.getElementById("sendBtn");
  const providerSelect = document.getElementById("provider");

  // =========================================
  // WELCOME
  // =========================================
  function showWelcome(){

    const div = document.createElement("div");
    div.className = "welcome-box";

    div.innerHTML = `
      <h1>🚀 Pipeline Generator AI</h1>
      <p>
        Gere pipelines GitLab CI e GitHub Actions automaticamente
      </p>

      <div class="chips">

        <span class="chip">
          pipeline gitlab python pytest docker
        </span>

        <span class="chip">
          pipeline node build deploy aws ecs
        </span>

        <span class="chip">
          pipeline github actions java maven sonar
        </span>

        <span class="chip">
          pipeline terraform aws validate plan apply
        </span>

        <span class="chip">
          pipeline .net 9 build test publish
        </span>

        <span class="chip">
          pipeline docker build push registry
        </span>

        <span class="chip">
          pipeline github actions nextjs vercel
        </span>

        <span class="chip">
          pipeline gitlab ci com stages build test deploy
        </span>

      </div>
    `;

    messages.appendChild(div);

    div.querySelectorAll(".chip").forEach(chip => {
      chip.onclick = () => {
        input.value = chip.textContent.trim();
        sendBtn.click();
      };
    });
  }

  function clearWelcome(){
    document.querySelector(".welcome-box")?.remove();
  }

  // =========================================
  // USER MESSAGE
  // =========================================
  function addUserMessage(text){

    const msg = document.createElement("div");
    msg.className = "message user";

    msg.innerHTML = `
      <div class="msg-header">
        👤 Você
      </div>

      <div class="msg-body">
        ${text}
      </div>
    `;

    messages.appendChild(msg);

    messages.scrollTop = messages.scrollHeight;
  }

  // =========================================
  // YAML VALIDATION
  // =========================================
  function validateYAML(yamlText){

    try{
      jsyaml.load(yamlText);

      return {
        valid: true,
        message: "✅ YAML válido"
      };

    }catch(err){

      let line = 0;

      if(err.mark){
        line = err.mark.line + 1;
      }

      return {
        valid: false,
        line,
        message: `❌ YAML inválido na linha ${line}`
      };
    }
  }

  // =========================================
  // HIGHLIGHT ERROR LINE
  // =========================================
  function highlightError(textarea, line){

    const lines = textarea.value.split("\n");

    let start = 0;

    for(let i=0;i<line-1;i++){
      start += lines[i].length + 1;
    }

    const end = start + (lines[line-1]?.length || 0);

    textarea.focus();
    textarea.setSelectionRange(start, end);
  }

  // =========================================
  // GITLAB -> GITHUB
  // =========================================
  function convertToGitHub(yaml){

    try{

      const parsed = jsyaml.load(yaml);

      let jobs = "";

      for(const key in parsed){

        if(parsed[key]?.script){

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

on:
  push:

jobs:
${jobs}`;

    }catch{
      return "# erro ao converter";
    }
  }

  // =========================================
  // CREATE BLOCK
  // =========================================
  function createBlock(){

    const wrap = document.createElement("div");
    wrap.className = "message assistant";

    // HEADER
    const header = document.createElement("div");
    header.className = "assistant-header";

    const providerBadge = document.createElement("div");
    providerBadge.className = "provider-badge";
    providerBadge.innerHTML = `🤖 ${providerSelect.value}`;

    const updateBtn = document.createElement("button");
    updateBtn.className = "update-btn";
    updateBtn.innerHTML = "♻️ Atualizar Pipeline";

    header.append(providerBadge, updateBtn);

    // SPLIT
    const split = document.createElement("div");
    split.className = "split-view";

    // LEFT
    const left = document.createElement("div");
    left.className = "panel";

    const leftTop = document.createElement("div");
    leftTop.className = "panel-top";

    leftTop.innerHTML = `
      <span>🦊 GitLab CI</span>
    `;

    const saveGitlab = document.createElement("button");
    saveGitlab.className = "save-btn";
    saveGitlab.innerHTML = "💾 salvar .gitlab-ci.yml";

    leftTop.appendChild(saveGitlab);

    const gitlabEditor = document.createElement("textarea");
    gitlabEditor.className = "editor";

    left.append(leftTop, gitlabEditor);

    // RIGHT
    const right = document.createElement("div");
    right.className = "panel";

    const rightTop = document.createElement("div");
    rightTop.className = "panel-top";

    rightTop.innerHTML = `
      <span>🐙 GitHub Actions</span>
    `;

    const saveGithub = document.createElement("button");
    saveGithub.className = "save-btn";
    saveGithub.innerHTML = "💾 salvar github-actions.yml";

    rightTop.appendChild(saveGithub);

    const githubEditor = document.createElement("textarea");
    githubEditor.className = "editor";

    right.append(rightTop, githubEditor);

    split.append(left, right);

    // VALIDATION
    const validation = document.createElement("div");
    validation.className = "validation";

    wrap.append(header, split, validation);

    messages.appendChild(wrap);

    // =========================================
    // UPDATE PIPELINE
    // =========================================
    updateBtn.onclick = () => {

      updateBtn.disabled = true;
      updateBtn.innerHTML = "⏳ validando...";

      const result = validateYAML(gitlabEditor.value);

      if(!result.valid){

        validation.innerHTML = result.message;
        validation.className = "validation error";

        highlightError(gitlabEditor, result.line);

        updateBtn.disabled = false;
        updateBtn.innerHTML = "♻️ Atualizar Pipeline";

        return;
      }

      githubEditor.value = convertToGitHub(gitlabEditor.value);

      validation.innerHTML = "✅ Pipeline atualizado com sucesso";
      validation.className = "validation success";

      updateBtn.disabled = false;
      updateBtn.innerHTML = "♻️ Atualizar Pipeline";
    };

    // =========================================
    // SAVE GITLAB
    // =========================================
    saveGitlab.onclick = () => {

      const blob = new Blob([gitlabEditor.value]);

      const a = document.createElement("a");

      a.href = URL.createObjectURL(blob);
      a.download = ".gitlab-ci.yml";

      a.click();
    };

    // =========================================
    // SAVE GITHUB
    // =========================================
    saveGithub.onclick = () => {

      const blob = new Blob([githubEditor.value]);

      const a = document.createElement("a");

      a.href = URL.createObjectURL(blob);
      a.download = "github-actions.yml";

      a.click();
    };

    return {

      setProvider:(provider)=>{
        providerBadge.innerHTML = `🤖 ${provider}`;
      },

      setData:(yaml)=>{

        gitlabEditor.value = yaml;

        githubEditor.value = convertToGitHub(yaml);

        const result = validateYAML(yaml);

        if(result.valid){

          validation.innerHTML = "✅ YAML válido";
          validation.className = "validation success";

        }else{

          validation.innerHTML = result.message;
          validation.className = "validation error";
        }
      }
    };
  }

  // =========================================
  // SEND
  // =========================================
  sendBtn.onclick = async () => {

    clearWelcome();

    const prompt = input.value.trim();

    if(!prompt) return;

    const provider = providerSelect.value;

    addUserMessage(prompt);

    input.value = "";

    sendBtn.disabled = true;
    sendBtn.innerHTML = "⏳ Gerando Pipeline...";

    const block = createBlock();

    block.setProvider(provider);

    try{

      const res = await fetch("/api/stream", {

        method: "POST",

        headers:{
          "Content-Type":"application/json"
        },

        body: JSON.stringify({
          prompt,
          provider
        })
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

          const json = JSON.parse(
            p.replace("data: ","")
          );

          if(json.provider){
            block.setProvider(json.provider);
          }

          if(json.yaml){
            block.setData(json.yaml);
          }
        }
      }

    }catch(err){

      console.error(err);

    }finally{

      sendBtn.disabled = false;
      sendBtn.innerHTML = "🚀 Gerar Pipeline";
    }
  };

  // =========================================
  // ENTER
  // =========================================
  input.addEventListener("keydown",(e)=>{

    if(e.key === "Enter" && !e.shiftKey){

      e.preventDefault();

      sendBtn.click();
    }
  });

  showWelcome();

});