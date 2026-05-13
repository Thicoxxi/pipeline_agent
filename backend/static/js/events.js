export function registerEvents({ input, sendBtn }) {

  if (!input || !sendBtn) {
    console.warn("registerEvents: input ou sendBtn não encontrados");
    return;
  }

  // =========================================================
  // ENTER PARA ENVIAR
  // =========================================================
  input.addEventListener("keydown", (e) => {

    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();

      // simula clique no botão (mantém lógica única no app.js)
      sendBtn.click();
    }
  });

}