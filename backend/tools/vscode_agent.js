const readline = require("readline");

const API_URL = "http://localhost:5000";

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function ask(prompt) {
    return new Promise(resolve => rl.question(prompt, resolve));
}

async function sendToLLM(prompt) {
    const res = await fetch(`${API_URL}/api/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            prompt,
            provider: "auto"
        })
    });

    return res.text();
}

async function sendToGitHub(owner, repo, yaml) {
    const res = await fetch(`${API_URL}/api/github/apply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            owner,
            repo,
            branch: "main",
            yaml
        })
    });

    return res.json();
}

async function main() {
    console.log("🤖 Simple VSCode Agent (phase 1)\n");

    const mode = await ask(
        "Mode (chat / github): "
    );

    if (mode === "chat") {
        const prompt = await ask("Prompt: ");
        const response = await sendToLLM(prompt);
        console.log("\n🤖 Response:\n", response);
    }

    if (mode === "github") {
        const owner = await ask("Owner: ");
        const repo = await ask("Repo: ");
        const yaml = await ask("YAML (paste): ");

        const result = await sendToGitHub(owner, repo, yaml);
        console.log("\n🚀 Result:\n", result);
    }

    rl.close();
}

main();