document.addEventListener("DOMContentLoaded", () => {

  const input = document.getElementById("chatInput");
  const messages = document.getElementById("messages");
  const sendBtn = document.getElementById("sendBtn");

  function showWelcome(){
    const div = document.createElement("div");
    div.className = "welcome-box";

    div.innerHTML = `
      <h2>👋 Olá</h2>
      <p>Crie pipelines automaticamente</p>

      <div class="chips">
        <span class="chip">pipeline python pytest</span>
        <span class="chip">pipeline node docker deploy</span>
        <span class="chip">pipeline java maven</span>
        <span class="chip">pipeline github actions node</span>
        <span class="chip">pipeline terraform aws</span>
      </div>
    `;

    messages.appendChild(div);

    div.querySelectorAll(".chip").forEach(c=>{
      c.onclick = ()=>{
        input.value = c.textContent;
        sendBtn.click();
      }
    });
  }

  function addUserMessage(text){
    const msg = document.createElement("div");
    msg.className = "message user";
    msg.innerHTML = text;
    messages.appendChild(msg);
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
      return "# erro";
    }
  }

  function createBlock(){

    const wrap = document.createElement("div");
    wrap.className = "message";

    const container = document.createElement("div");
    container.className = "split-view";

    const left = document.createElement("textarea");
    const right = document.createElement("textarea");

    left.className = "editor";
    right.className = "editor";

    container.append(left, right);

    wrap.append(container);
    messages.appendChild(wrap);

    return {
      setData:(yaml)=>{
        left.value = yaml;
        right.value = convertToGitHub(yaml);
      }
    };
  }

  sendBtn.onclick = async () => {

    const prompt = input.value;
    if(!prompt) return;

    const provider = document.getElementById("provider").value;

    addUserMessage(prompt);

    sendBtn.innerHTML = "⏳";
    sendBtn.disabled = true;

    const block = createBlock();

    const res = await fetch("/api/stream", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
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
          block.setData(json.yaml);
        }
      }
    }

    sendBtn.innerHTML = "🚀";
    sendBtn.disabled = false;
  };

  showWelcome();

});