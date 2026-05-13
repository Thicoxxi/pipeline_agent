import {
  showWelcome,
  clearWelcome,
  addUserMessage
} from "./ui.js";

import {
  createPipelineBlock
} from "./pipelineBlock.js";

import {
  sendPrompt
} from "./api.js";

import {
  registerEvents
} from "./events.js";

document.addEventListener("DOMContentLoaded", () => {

  console.log("🔥 DOM carregado");

  const input = document.getElementById("chatInput");
  const messages = document.getElementById("messages");
  const sendBtn = document.getElementById("sendBtn");
  const providerSelect = document.getElementById("provider");

  if (!input || !messages || !sendBtn || !providerSelect) {
    console.error("❌ DOM inválido", {
      input,
      messages,
      sendBtn,
      providerSelect
    });
    return;
  }

  async function sendPipeline() {

    const prompt = input.value.trim();
    if (!prompt) return;

    clearWelcome();

    const provider = providerSelect.value;

    addUserMessage(messages, prompt);

    input.value = "";

    sendBtn.disabled = true;
    sendBtn.innerHTML = "⏳ Gerando Pipeline...";

    // 🔥 CRIA BLOCO
    const block = createPipelineBlock({
      messages,
      provider
    });

    if (!block) {
      console.error("❌ createPipelineBlock retornou vazio");
      sendBtn.disabled = false;
      sendBtn.innerHTML = "🚀 Gerar Pipeline";
      return;
    }

    try {

      await sendPrompt({
        prompt,
        provider,

        onProvider: (p) => {
          console.log("🤖 provider:", p);
          block.setProvider?.(p);
        },

        onGitlab: (yaml) => {
          console.log("🦊 gitlab recebido");
          block.setGitlab?.(yaml);
        },

        onGithub: (yaml) => {
          console.log("🐙 github recebido");
          block.setGithub?.(yaml);
        },

        onError: (err) => {
          console.error("❌ Erro pipeline:", err);
        }

      });

    } catch (err) {
      console.error("❌ Erro geral:", err);

    } finally {
      sendBtn.disabled = false;
      sendBtn.innerHTML = "🚀 Gerar Pipeline";
    }
  }

  // =========================
  // EVENTS
  // =========================
  sendBtn?.addEventListener("click", sendPipeline);

  registerEvents({ input, sendBtn });

  // =========================
  // WELCOME
  // =========================
  showWelcome({
    messages,
    input,
    onSelect: sendPipeline
  });

  console.log("✅ app.js OK");
});