document.addEventListener("DOMContentLoaded", () => {

  const input = document.getElementById("chatInput");
  const messages = document.getElementById("messages");
  const sendBtn = document.getElementById("sendBtn");

  function showWelcome(){
    const div = document.createElement("div");
    div.className = "welcome-box";

    div.innerHTML = `
      <h2>👋 Olá!</h2>
      <p>Sou seu assistente para criar pipelines 🚀</p>

      <h3>💡 Exemplos rápidos</h3>
      <div class="chips">
        <span class="chip">pipeline gitlab python pytest</span>
        <span class="chip">pipeline gitlab nodejs build test deploy</span>
        <span class="chip">pipeline gitlab docker build push registry</span>

        <span class="chip">pipeline github actions node 20 com jest</span>
        <span class="chip">pipeline github actions java maven build</span>
        <span class="chip">pipeline github actions deploy aws</span>

        <span class="chip">pipeline terraform aws com validação e apply</span>
        <span class="chip">pipeline azure devops build .net 9</span>
        <span class="chip">pipeline ci cd com sonar e docker</span>
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

  function getProviderIcon(p){
    if(p==="openai") return "🧠 OpenAI";
    if(p==="groq") return "⚡ Groq";
    if(p==="local") return "💻 Local";
    return "🤖 Auto";
  }

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

  function convertToGitLab(yaml){
    try{
      const parsed = jsyaml.load(yaml);
      let stages = [];
      let jobs = "";

      for(const jobName in parsed.jobs){
        const job = parsed.jobs[jobName];
        stages.push(jobName);

        const steps = job.steps
          ?.filter(s => s.run)
          .map(s => "    - " + s.run)
          .join("\n");

        jobs += `
${jobName}:
  stage: ${jobName}
  script:
${steps || "    - echo no steps"}
`;
      }

      return `stages:
${stages.map(s=>"  - "+s).join("\n")}

${jobs}`;
    }catch{
      return "# erro ao converter";
    }
  }

  function createBlock(provider){
    const wrap = document.createElement("div");

    let pipelineType = "unknown";
    let gitlabYaml = "";
    let githubYaml = "";

    const providerTag = document.createElement("div");
    providerTag.className = "provider-tag";
    providerTag.textContent = getProviderIcon(provider);

    const actions = document.createElement("div");
    actions.className = "actions";

    const copyAll = document.createElement("button");
    copyAll.textContent = "📋 copiar ambos";

    actions.append(copyAll);

    const container = document.createElement("div");
    container.className = "split-view";

    // GITLAB
    const left = document.createElement("div");
    const leftHeader = document.createElement("div");
    leftHeader.innerHTML = `
      <span>GitLab CI</span>
      <button class="save-btn">💾 salvar .gitlab-ci.yml</button>
    `;
    const leftBtn = leftHeader.querySelector("button");

    const preLeft = document.createElement("pre");
    const codeLeft = document.createElement("code");
    preLeft.appendChild(codeLeft);
    left.append(leftHeader, preLeft);

    // GITHUB
    const right = document.createElement("div");
    const rightHeader = document.createElement("div");
    rightHeader.innerHTML = `
      <span>GitHub Actions</span>
      <button class="save-btn">💾 salvar github-actions.yml</button>
    `;
    const rightBtn = rightHeader.querySelector("button");

    const preRight = document.createElement("pre");
    const codeRight = document.createElement("code");
    preRight.appendChild(codeRight);
    right.append(rightHeader, preRight);

    container.append(left, right);

    const val = document.createElement("div");
    val.className = "validation";

    wrap.append(providerTag, actions, container, val);
    messages.appendChild(wrap);

    // ações
    copyAll.onclick = () => {
      const combined = `# GitLab\n${gitlabYaml}\n\n# GitHub\n${githubYaml}`;
      navigator.clipboard.writeText(combined);
    };

    leftBtn.onclick = () => {
      const blob = new Blob([gitlabYaml]);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = ".gitlab-ci.yml";
      a.click();
    };

    rightBtn.onclick = () => {
      const blob = new Blob([githubYaml]);
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "github-actions.yml";
      a.click();
    };

    return {
      setData: (yaml, type, validation) => {
        pipelineType = type;

        if(type === "gitlab"){
          gitlabYaml = yaml;
          githubYaml = convertToGitHub(yaml);
        } else if(type === "github"){
          githubYaml = yaml;
          gitlabYaml = convertToGitLab(yaml);
        }

        codeLeft.textContent = gitlabYaml;
        codeRight.textContent = githubYaml;

        val.textContent = validation;
        providerTag.textContent = `${getProviderIcon(provider)} • ${type.toUpperCase()}`;
      }
    };
  }

  sendBtn.onclick = async () => {
    clearWelcome();

    const prompt = input.value;
    const provider = document.getElementById("provider").value;

    const block = createBlock(provider);

    const res = await fetch("/api/stream", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({prompt, provider})
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    let full = "";

    while(true){
      const {done,value} = await reader.read();
      if(done) break;

      const chunk = decoder.decode(value);
      const parts = chunk.split("\n\n");

      for(let p of parts){
        if(!p.startsWith("data:")) continue;

        const json = JSON.parse(p.replace("data: ",""));

        if(json.chunk){
          full += json.chunk;
        }

        if(json.yaml){
          block.setData(json.yaml, json.type, json.validation);
        }
      }
    }
  };

  showWelcome();
});