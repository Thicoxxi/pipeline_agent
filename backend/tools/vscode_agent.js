const fs = require("fs");
const path = require("path");
const readline = require("readline");

const API_URL = "http://localhost:5000";

// =========================================================
// LOGS
// =========================================================
const BASE_DIR = path.resolve(
    __dirname,
    ".."
);

const LOG_DIR = path.join(
    BASE_DIR,
    "logs"
);

if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR);
}

const LOG_FILE = path.join(
    LOG_DIR,
    "vscode_agent_js.log"
);

// =========================================================
// LOGGER
// =========================================================
function log(message) {

    const line =
        `[${new Date().toISOString()}] ${message}\n`;

    fs.appendFileSync(
        LOG_FILE,
        line
    );

    console.log(line.trim());
}

// =========================================================
// READLINE
// =========================================================
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function ask(prompt) {

    return new Promise(resolve => {
        rl.question(prompt, resolve);
    });
}

// =========================================================
// HELPERS
// =========================================================
function separator() {

    console.log(
        "\n=================================================\n"
    );
}

// =========================================================
// CHAT
// =========================================================
async function sendChat(prompt) {

    log(`CHAT START | ${prompt}`);

    const res = await fetch(
        `${API_URL}/api/stream`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                prompt,
                provider: "auto"
            })
        }
    );

    const text = await res.text();

    separator();

    console.log(
        "🤖 RESPONSE:\n"
    );

    console.log(text);

    separator();

    log("CHAT END");
}

// =========================================================
// ANALYZE
// =========================================================
async function analyzeProject(platform) {

    log(
        `ANALYZE START | ${platform}`
    );

    const { spawn } = require("child_process");

    const process = spawn(
        "python",
        [
            "tools/analyze_project.py"
        ],
        {
            cwd: BASE_DIR,
            stdio: [
                "pipe",
                "inherit",
                "inherit"
            ]
        }
    );

    process.stdin.write(
        `${platform}\n`
    );

    process.stdin.end();

    process.on(
        "close",
        code => {

            log(
                `ANALYZE END | code=${code}`
            );
        }
    );
}

// =========================================================
// GITHUB APPLY
// =========================================================
async function sendToGitHub() {

    const owner = await ask(
        "\nOwner: "
    );

    const repo = await ask(
        "Repo: "
    );

    const filePath = await ask(
        "Pipeline file path: "
    );

    if (!fs.existsSync(filePath)) {

        console.log(
            "\n❌ file not found\n"
        );

        return;
    }

    const yaml =
        fs.readFileSync(
            filePath,
            "utf-8"
        );

    log(
        `GITHUB APPLY | ${owner}/${repo}`
    );

    const res = await fetch(
        `${API_URL}/api/github/apply`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                owner,
                repo,
                branch: "main",
                yaml
            })
        }
    );

    const result = await res.json();

    separator();

    console.log(
        "🚀 RESULT:\n"
    );

    console.log(result);

    separator();

    log(
        `GITHUB RESPONSE | ${JSON.stringify(result)}`
    );
}

// =========================================================
// MAIN
// =========================================================
async function main() {

    separator();

    console.log(
        "🤖 VSCode Agent (Node.js)"
    );

    console.log(
        `📝 log file: ${LOG_FILE}`
    );

    separator();

    while (true) {

        console.log(
            "Available commands:\n"
        );

        console.log(" - chat");
        console.log(" - analyze");
        console.log(" - github");
        console.log(" - exit");

        const command = (
            await ask("\nCommand: ")
        )
        .trim()
        .toLowerCase();

        log(
            `COMMAND | ${command}`
        );

        // =================================================
        // CHAT
        // =================================================
        if (command === "chat") {

            const prompt = await ask(
                "\n💬 Prompt: "
            );

            await sendChat(prompt);
        }

        // =================================================
        // ANALYZE
        // =================================================
        else if (command === "analyze") {

            const platform = (
                await ask(
                    "\n🛠 Platform (gitlab/github): "
                )
            )
            .trim()
            .toLowerCase();

            await analyzeProject(
                platform
            );
        }

        // =================================================
        // GITHUB
        // =================================================
        else if (command === "github") {

            await sendToGitHub();
        }

        // =================================================
        // EXIT
        // =================================================
        else if (command === "exit") {

            log(
                "APPLICATION CLOSED"
            );

            console.log(
                "\n👋 bye\n"
            );

            rl.close();

            process.exit(0);
        }

        else {

            console.log(
                "\n❌ invalid command\n"
            );
        }
    }
}

// =========================================================
// START
// =========================================================
log(
    "VSCODE AGENT JS STARTED"
);

main();