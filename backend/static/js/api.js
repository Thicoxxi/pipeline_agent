export async function sendPrompt({
  prompt,
  provider,
  onProvider,
  onGitlab,
  onGithub,
  onError
}) {

  try {

    const res = await fetch("/api/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        prompt,
        provider
      })
    });

    if (!res.ok) {
      throw new Error("Erro ao conectar API");
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    let buffer = "";

    while (true) {

      const {
        done,
        value
      } = await reader.read();

      if (done) break;

      buffer += decoder.decode(
        value,
        { stream: true }
      );

      const events =
        buffer.split("\n\n");

      buffer =
        events.pop() || "";

      for (const event of events) {

        if (!event.startsWith("data:"))
          continue;

        const raw =
          event.replace("data:", "").trim();

        if (!raw) continue;

        try {

          const json =
            JSON.parse(raw);

          console.log("📦 SSE:", json);

          // =========================
          // PROVIDER
          // =========================
          if (json.provider) {
            onProvider?.(json.provider);
          }

          // =========================
          // GITLAB
          // =========================
          if (json.gitlab) {
            onGitlab?.(json.gitlab);
          }

          // =========================
          // GITHUB
          // =========================
          if (json.github) {
            onGithub?.(json.github);
          }

          // =========================
          // ERROR
          // =========================
          if (json.error) {
            console.error(json.error);
            onError?.(json.error);
          }

        } catch (err) {

          console.error(
            "Erro parse SSE:",
            err
          );

          onError?.(err);
        }
      }
    }

  } catch (err) {

    console.error(
      "sendPrompt error:",
      err
    );

    onError?.(err);
  }
}