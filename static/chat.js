document.addEventListener("DOMContentLoaded", () => {

  const input = document.getElementById("chatInput");
  const messages = document.getElementById("messages");
  const sendBtn = document.getElementById("sendBtn");

  /**
   * Exibe uma mensagem de boas-vindas com chips de sugestões de pipelines.
   * Cada chip, ao ser clicado, insere o texto no input e dispara o envio.
   */
  function showWelcome(){
    const div = document.createElement("div");
    div.className = "welcome-box";

    div.innerHTML = `
      <h2>👋 Olá!</h2>
      <p>Sou seu assistente para criar pipelines 🚀</p>
      <div class="chips">
        <span class="chip">pipeline python pytest</span>
        <span class="chip">pipeline docker build push</span>
        <span class="chip">pipeline java maven</span>
        <span class="chip">pipeline java spring</span>
        <span class="chip">pipeline java gradle</span>
        <span class="chip">pipeline nodejs npm</span>
        <span class="chip">pipeline nodejs express</span>
        <span class="chip">pipeline nodejs jest</span>
        <span class="chip">pipeline java python 3.13 com pyinstaller</span>
        <span class="chip">pipeline .NET Core 9 para Linux com variavel de ambiente para solution.sln</span>
        <span class="chip">pipeline .NET Core 9 para Windows com variavel de ambiente para solution.sln</span>
        <span class="chip">pipeline nodejs 20</span>
        <span class="chip">pipeline .NET Framework 4.8 com variavel de ambiente para solution.sln</span>
        <span class="chip">pipeline golang 1.20</span>
        <span class="chip">pipeline rust</span>
        <span class="chip">pipeline android</span>
        <span class="chip">pipeline ios</span>
        <span class="chip">pipeline terraform para AWS</span>
        <span class="chip">pipeline terraform para Azure</span>
        <span class="chip">pipeline terraform para GCP</span>      
      </div>
    `;

    messages.appendChild(div);

    const chips = div.querySelectorAll(".chip");
    chips.forEach(chip => {
      chip.addEventListener("click", () => {
        input.value = chip.textContent;
        sendBtn.click();
      });
    });
  }

  /**
   * Remove a caixa de boas-vindas, se existir.
   */
  function clearWelcome(){
    const w=document.querySelector(".welcome-box");
    if(w) w.remove();
  }

  /**
   * Retorna o ícone correspondente ao provider.
   * @param {string} p - Nome do provider ("openai", "groq", "local", "auto").
   * @returns {string} Ícone e nome do provider.
   */
  function getProviderIcon(p){
    if(p==="openai") return "🧠 OpenAI";
    if(p==="groq") return "⚡ Groq";
    if(p==="local") return "💻 Local";
    return "🤖 Auto";
  }

  /**
   * Valida se o conteúdo fornecido é um YAML válido.
   * @param {string} y - Texto YAML.
   * @returns {boolean} True se válido, False caso contrário.
   */
  function validateYAML(y){
    try{jsyaml.load(y);return true}catch{return false}
  }

  /**
   * Converte um YAML de GitLab CI para GitHub Actions.
   * @param {string} yaml - Conteúdo YAML do GitLab CI.
   * @returns {string} YAML convertido para GitHub Actions ou mensagem de erro.
   */
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
      - name: Run ${key}
        run: |
${parsed[key].script.map(s=>"          "+s).join("\n")}
`;
        }
      }

      return `name: CI

on:
  push:
    branches: [ main ]

jobs:
${jobs}`;
    }catch{
      return "# erro ao converter";
    }
  }

  /**
   * Cria um bloco visual para exibir o resultado do provider.
   * Inclui botões de copiar, baixar para GitLab e converter para GitHub.
   * @param {string} provider - Nome do provider.
   * @returns {{code: HTMLElement, val: HTMLElement}} Elementos para manipulação do código e validação.
   */
  function createBlock(provider){
    const wrap=document.createElement("div");

    const providerTag=document.createElement("div");
    providerTag.className="provider-tag";
    providerTag.textContent=getProviderIcon(provider);

    const actions=document.createElement("div");

    const copy=document.createElement("button");
    copy.textContent="📋 copiar";

    const gitlab=document.createElement("button");
    gitlab.textContent="⬇️ gitlab";

    const github=document.createElement("button");
    github.textContent="⬇️ github";

    const pre=document.createElement("pre");
    const code=document.createElement("code");

    const val=document.createElement("div");

    actions.append(copy,gitlab,github);
    wrap.append(providerTag,actions,pre,val);
    pre.appendChild(code);
    messages.appendChild(wrap);

    copy.onclick=()=>navigator.clipboard.writeText(code.textContent);

    gitlab.onclick=()=>{
      const blob=new Blob([code.textContent]);
      const a=document.createElement("a");
      a.href=URL.createObjectURL(blob);
      a.download=".gitlab-ci.yml";
      a.click();
    };

    github.onclick=()=>{
      const converted=convertToGitHub(code.textContent);
      const blob=new Blob([converted]);
      const a=document.createElement("a");
      a.href=URL.createObjectURL(blob);
      a.download="github-actions.yml";
      a.click();
    };

    return {code,val};
  }

  /**
   * Evento de clique no botão "Enviar".
   * - Remove a mensagem de boas-vindas.
   * - Cria bloco para exibir resultado.
   * - Faz requisição POST para `/api/stream`.
   * - Lê resposta em streaming (SSE).
   * - Atualiza código e valida YAML.
   */
  sendBtn.onclick=async()=>{
    clearWelcome();
    const prompt=input.value;
    const provider=document.getElementById("provider").value;

    const {code,val}=createBlock(provider);

    const res=await fetch("/api/stream",{method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({prompt,provider})
    });

    const reader=res.body.getReader();
    const decoder=new TextDecoder();

    let full="";

    while(true){
      const {done,value}=await reader.read();
      if(done) break;
      const chunk=decoder.decode(value);
      const parts=chunk.split("\n\n");
      for(let p of parts){
        if(!p.startsWith("data:")) continue;
        const json=JSON.parse(p.replace("data: ",""));
        if(json.chunk){
          full+=json.chunk;
          code.textContent=full;
        }
      }
    }

    val.textContent = validateYAML(full) ? "✅ YAML válido" : "❌ YAML inválido";
  };

  showWelcome();

});
