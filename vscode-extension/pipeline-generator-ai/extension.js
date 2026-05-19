const vscode = require("vscode");
const axios = require("axios");
const fs = require("fs");
const path = require("path");

const API_URL = "http://localhost:5000";

// Send logs from the extension to backend so they appear in app.log and error.log
async function sendLog(level, message, meta) {
    try {
        await axios.post(`${API_URL}/api/log`, {
            level,
            message,
            name: "vscode-extension",
            meta: meta || {}
        }, { timeout: 5000 });
    } catch (e) {
        // avoid throwing in logging path
        console.warn("Failed to send log to backend:", e.message || e);
    }
}

// Monkey-patch console methods to also forward to backend
['log', 'info', 'warn', 'error', 'debug'].forEach(fn => {
    const orig = console[fn] || console.log;
    console[fn] = function (...args) {
        try {
            const msg = args.map(a => {
                try { return typeof a === 'string' ? a : JSON.stringify(a); } catch { return String(a); }
            }).join(' ');
            const level = fn === 'warn' ? 'warning' : (fn === 'error' ? 'error' : (fn === 'debug' ? 'debug' : 'info'));
            sendLog(level, msg);
        } catch (e) {
            // ignore
        }
        return orig.apply(console, args);
    };
});


// =====================================================
// GET PROJECT FILES
// =====================================================
function scanWorkspace(workspacePath) {

    const files = [];

    const allowedExtensions = [
        ".py",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".json",
        ".yml",
        ".yaml",
        ".tf",
        ".java",
        ".cs"
    ];

    const ignoreDirs = [
        "node_modules",
        ".git",
        "__pycache__",
        ".venv",
        "dist",
        "build"
    ];

    function walk(dir) {

        const entries = fs.readdirSync(
            dir,
            {
                withFileTypes: true
            }
        );

        for (const entry of entries) {

            const fullPath = path.join(
                dir,
                entry.name
            );

            // =============================================
            // IGNORE
            // =============================================
            if (
                entry.isDirectory() &&
                ignoreDirs.includes(entry.name)
            ) {
                continue;
            }

            // =============================================
            // DIRECTORY
            // =============================================
            if (entry.isDirectory()) {
                walk(fullPath);
                continue;
            }

            // =============================================
            // EXTENSION
            // =============================================
            const ext = path.extname(
                entry.name
            );

            if (
                !allowedExtensions.includes(ext)
            ) {
                continue;
            }

            try {

                const content = fs.readFileSync(
                    fullPath,
                    "utf-8"
                );

                files.push({

                    name: path.relative(
                        workspacePath,
                        fullPath
                    ),

                    content: content.slice(
                        0,
                        4000
                    )
                });

            } catch (err) {

                console.error(err);
            }
        }
    }

    walk(workspacePath);

    return files;
}


// =====================================================
// ACTIVATE
// =====================================================
function activate(context) {

    console.log(
        "Pipeline Generator AI loaded"
    );

    // =================================================
    // ANALYZE PROJECT
    // =================================================
    const analyzeCommand =
        vscode.commands.registerCommand(
            "pipeline-generator-ai.analyzeProject",

            async function () {

                try {

                    const workspaceFolders =
                        vscode.workspace.workspaceFolders;

                    if (!workspaceFolders) {

                        vscode.window.showErrorMessage(
                            "Open a project first"
                        );

                        return;
                    }

                    const workspacePath =
                        workspaceFolders[0].uri.fsPath;

                    vscode.window.showInformationMessage(
                        "Scanning project..."
                    );

                    // =====================================
                    // SCAN FILES
                    // =====================================
                    const files =
                        scanWorkspace(
                            workspacePath
                        );

                    // =====================================
                    // PLATFORM
                    // =====================================
                    const platform =
                        await vscode.window.showQuickPick(
                            [
                                "gitlab",
                                "github"
                            ],
                            {
                                placeHolder:
                                    "Select platform"
                            }
                        );

                    if (!platform) {
                        return;
                    }

                    vscode.window.showInformationMessage(
                        "Generating pipeline..."
                    );

                    // =====================================
                    // API CALL
                    // =====================================
                    const response =
                        await axios.post(

                            `${API_URL}/api/analyze-project`,

                            {
                                files,
                                provider: "auto",
                                platform
                            },

                            {
                                responseType: "text"
                            }
                        );

                    const pipeline =
                        response.data;

                    // =====================================
                    // OPEN YAML
                    // =====================================
                    const document =
                        await vscode.workspace.openTextDocument({
                            content: pipeline,
                            language: "yaml"
                        });

                    await vscode.window.showTextDocument(
                        document
                    );

                    vscode.window.showInformationMessage(
                        "Pipeline generated successfully"
                    );

                } catch (err) {

                    console.error(err);

                    vscode.window.showErrorMessage(
                        `Pipeline Generator Error: ${err.message}`
                    );
                }
            }
        );

    context.subscriptions.push(
        analyzeCommand
    );

    // =================================================
    // GENERATE PIPELINE
    // =================================================
    const generateCommand =
        vscode.commands.registerCommand(
            "pipeline-generator-ai.generatePipeline",

            async function () {

                try {

                    const prompt = await vscode.window.showInputBox({
                        prompt: "Describe the pipeline you want to generate",
                        placeHolder: "e.g. CI for Python project with tests and build"
                    });

                    if (!prompt) {
                        return;
                    }

                    vscode.window.showInformationMessage(
                        "Generating pipeline..."
                    );

                    const response = await axios.post(

                        `${API_URL}/api/stream`,

                        {
                            prompt,
                            provider: "auto"
                        },

                        {
                            responseType: "text"
                        }
                    );

                    const text = response.data || "";

                    // Parse SSE "data: {...}" lines
                    const lines = text.split(/\n/).map(l => l.trim()).filter(Boolean);

                    let gitlabYaml = "";
                    let githubYaml = "";

                    for (const line of lines) {

                        if (!line.startsWith("data:")) continue;

                        const payloadStr = line.replace("data:", "").trim();

                        try {
                            const payload = JSON.parse(payloadStr);

                            if (payload.gitlab) {
                                gitlabYaml += payload.gitlab;
                            }

                            if (payload.github) {
                                githubYaml += payload.github;
                            }

                            if (payload.content) {
                                // append generic content
                                gitlabYaml += payload.content;
                                githubYaml += payload.content;
                            }

                        } catch (e) {
                            // ignore non-json lines
                        }
                    }

                    if (gitlabYaml) {

                        const doc = await vscode.workspace.openTextDocument({
                            content: gitlabYaml,
                            language: "yaml"
                        });

                        await vscode.window.showTextDocument(doc);
                    }

                    if (githubYaml) {

                        const doc2 = await vscode.workspace.openTextDocument({
                            content: githubYaml,
                            language: "yaml"
                        });

                        await vscode.window.showTextDocument(doc2);
                    }

                    if (!gitlabYaml && !githubYaml) {

                        vscode.window.showErrorMessage(
                            "No pipeline generated"
                        );
                    } else {

                        vscode.window.showInformationMessage(
                            "Pipeline generated successfully"
                        );
                    }

                } catch (err) {

                    console.error(err);

                    vscode.window.showErrorMessage(
                        `Pipeline Generator Error: ${err.message}`
                    );
                }
            }
        );

    context.subscriptions.push(
        generateCommand
    );

        // =================================================
        // CHAT WEBVIEW
        // =================================================
        const chatCommand = vscode.commands.registerCommand(
                "pipeline-generator-ai.openChat",
                async function () {

                        const panel = vscode.window.createWebviewPanel(
                                "pipelineGeneratorChat",
                                "Pipeline Chat",
                                vscode.ViewColumn.One,
                                {
                                        enableScripts: true,
                                        retainContextWhenHidden: true
                                }
                        );

                        panel.webview.html = getWebviewContent();

                        // Handle messages from the webview
                        panel.webview.onDidReceiveMessage(async message => {

                            if (message.command === "send") {

                                        const prompt = message.text || "";

                                        try {
                                                panel.webview.postMessage({ type: "status", text: "Sending..." });

                                                const response = await axios.post(
                                                        `${API_URL}/api/stream`,
                                                        { prompt, provider: "auto" },
                                                        { responseType: "stream", timeout: 0 }
                                                );

                                                const stream = response.data;

                                                stream.on("data", chunk => {
                                                        const str = chunk.toString();

                                                        // split by newlines and look for data: payload
                                                        const lines = str.split(/\r?\n/).map(l => l.trim()).filter(Boolean);

                                                        for (const line of lines) {
                                                                if (!line.startsWith("data:")) continue;

                                                                const payloadStr = line.replace("data:", "").trim();

                                                                try {
                                                                        const payload = JSON.parse(payloadStr);

                                                                        if (payload.content) {
                                                                            panel.webview.postMessage({ type: "message", text: payload.content });
                                                                        }

                                                                        if (payload.gitlab) {
                                                                            panel.webview.postMessage({ type: "message", text: payload.gitlab });

                                                                            // Open generated GitLab YAML in an editor tab
                                                                            vscode.workspace.openTextDocument({
                                                                                content: payload.gitlab,
                                                                                language: "yaml"
                                                                            }).then(doc => {
                                                                                vscode.window.showTextDocument(doc);
                                                                            }).catch(err => console.error("Open doc error:", err));
                                                                        }

                                                                        if (payload.github) {
                                                                            panel.webview.postMessage({ type: "message", text: payload.github });

                                                                            // Open generated GitHub Actions workflow in an editor tab
                                                                            vscode.workspace.openTextDocument({
                                                                                content: payload.github,
                                                                                language: "yaml"
                                                                            }).then(doc => {
                                                                                vscode.window.showTextDocument(doc);
                                                                            }).catch(err => console.error("Open doc error:", err));
                                                                        }

                                                                } catch (e) {
                                                                        // non-json chunk
                                                                        panel.webview.postMessage({ type: "message", text: payloadStr });
                                                                }
                                                        }
                                                });

                                                stream.on("end", () => {
                                                        panel.webview.postMessage({ type: "status", text: "Done" });
                                                });

                                                stream.on("error", err => {
                                                        panel.webview.postMessage({ type: "status", text: `Error: ${err.message}` });
                                                });

                                        } catch (err) {
                                                console.error(err);
                                                panel.webview.postMessage({ type: "status", text: `Error: ${err.message}` });
                                        }
                                }

                        // =================================================
                        // ANALYZE PROJECT from Webview
                        // =================================================
                        else if (message.command === "analyze") {

                            try {
                                const workspaceFolders = vscode.workspace.workspaceFolders;

                                if (!workspaceFolders) {
                                    panel.webview.postMessage({ type: "status", text: "Open a project first" });
                                    return;
                                }

                                const workspacePath = workspaceFolders[0].uri.fsPath;

                                const platform = await vscode.window.showQuickPick([
                                    "gitlab",
                                    "github"
                                ], { placeHolder: "Select platform for pipeline" });

                                if (!platform) {
                                    panel.webview.postMessage({ type: "status", text: "Platform not selected" });
                                    return;
                                }

                                panel.webview.postMessage({ type: "status", text: "Scanning project..." });

                                const files = scanWorkspace(workspacePath);

                                // Try to infer entry file automatically from workspace files.
                                function inferEntryFromFiles(files) {
                                    // python preference
                                    const preferPy = ['hello.py', 'main.py', 'app.py', 'src/main.py'];
                                    for (const p of preferPy) {
                                        const found = files.find(f => f.name.toLowerCase().endsWith(p));
                                        if (found) return found.name;
                                    }

                                    const anyPy = files.find(f => f.name.toLowerCase().endsWith('.py'));
                                    if (anyPy) return anyPy.name;

                                    // dotnet solution
                                    const sln = files.find(f => f.name.toLowerCase().endsWith('.sln'));
                                    if (sln) return sln.name;

                                    // java build files
                                    const pom = files.find(f => f.name.toLowerCase().endsWith('pom.xml'));
                                    if (pom) return pom.name;
                                    const gradle = files.find(f => f.name.toLowerCase().endsWith('build.gradle'));
                                    if (gradle) return gradle.name;

                                    // node: package.json
                                    const pkg = files.find(f => f.name.toLowerCase().endsWith('package.json'));
                                    if (pkg) return pkg.name;

                                    // go: main.go
                                    const mainGo = files.find(f => f.name.toLowerCase().endsWith('main.go'));
                                    if (mainGo) return mainGo.name;

                                    return null;
                                }

                                function inferEntryFromInstruction(files, instr) {
                                    if (!instr) return null;

                                    const lower = instr.toLowerCase();

                                    // try to find an explicit filename mentioned
                                    const filenameRegex = /([\w\-\.]+\.(py|js|ts|java|jar|cs|sln|go|tf))/gi;
                                    const m = [...(instr.matchAll(filenameRegex) || [])];
                                    if (m.length) {
                                        for (const item of m) {
                                            const name = item[1];
                                            const found = files.find(f => f.name.toLowerCase().endsWith(name.toLowerCase()));
                                            if (found) return found.name;
                                        }
                                    }

                                    // heuristics for tool mentions
                                    if (lower.includes('pyinstaller') || lower.includes('py ')) {
                                        const prefer = ['hello.py', 'main.py', 'app.py', 'src/main.py'];
                                        for (const p of prefer) {
                                            const found = files.find(f => f.name.toLowerCase().endsWith(p));
                                            if (found) return found.name;
                                        }
                                        const anyPy = files.find(f => f.name.toLowerCase().endsWith('.py'));
                                        if (anyPy) return anyPy.name;
                                    }

                                    if (lower.includes('solution') || lower.includes('.sln') || lower.includes('dotnet')) {
                                        const sln = files.find(f => f.name.toLowerCase().endsWith('.sln'));
                                        if (sln) return sln.name;
                                    }

                                    if (lower.includes('maven') || lower.includes('pom') || lower.includes('gradle')) {
                                        const pom = files.find(f => f.name.toLowerCase().endsWith('pom.xml'));
                                        if (pom) return pom.name;
                                        const gradle = files.find(f => f.name.toLowerCase().endsWith('build.gradle'));
                                        if (gradle) return gradle.name;
                                        const anyJava = files.find(f => f.name.toLowerCase().endsWith('.java'));
                                        if (anyJava) return anyJava.name;
                                    }

                                    return null;
                                }

                                // first try automatic inference from files
                                let entryFile = inferEntryFromFiles(files);

                                // if not found, optionally ask the user for an instruction and try to infer
                                if (!entryFile) {
                                    const instruction = await vscode.window.showInputBox({
                                        prompt: "Optional instruction (e.g. 'utiliza hello.py com pyinstaller')",
                                        placeHolder: "Leave empty to skip custom entry detection",
                                    });

                                    if (instruction) {
                                        const inferred = inferEntryFromInstruction(files, instruction);
                                        if (inferred) entryFile = inferred;
                                    }
                                }

                                panel.webview.postMessage({ type: "status", text: "Generating pipeline..." });

                                const resp = await axios.post(`${API_URL}/api/analyze-project`, {
                                    files,
                                    provider: "auto",
                                    platform,
                                    entry: entryFile
                                }, { responseType: "text" });

                                const pipeline = resp.data || "";

                                // open pipeline in editor
                                const doc = await vscode.workspace.openTextDocument({ content: pipeline, language: "yaml" });
                                await vscode.window.showTextDocument(doc);

                                panel.webview.postMessage({ type: "status", text: "Pipeline generated and opened" });

                            } catch (err) {
                                console.error(err);
                                panel.webview.postMessage({ type: "status", text: `Error: ${err.message}` });
                            }
                        }
                        });
                }
        );

        context.subscriptions.push(chatCommand);


        function getWebviewContent() {
                return `<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <style>
        body { font-family: sans-serif; padding: 10px; }
        #messages { border: 1px solid #ccc; padding: 8px; height: 300px; overflow: auto; white-space: pre-wrap; }
        #input { width: 100%; box-sizing: border-box; }
        #controls { margin-top: 8px; }
        button { margin-left: 8px; }
        .status { color: #888; font-size: 12px; }
    </style>
</head>
<body>
    <h3>Pipeline Chat</h3>
    <div id="messages"></div>
    <div id="controls">
        <textarea id="input" rows="3" placeholder="Describe the pipeline or ask a question..."></textarea>
        <div>
            <button id="send">Send</button>
            <button id="analyze">Analyze Project</button>
            <span class="status" id="status"></span>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();

        const messages = document.getElementById('messages');
        const input = document.getElementById('input');
        const send = document.getElementById('send');
        const status = document.getElementById('status');

        send.addEventListener('click', () => {
            const text = input.value.trim();
            if (!text) return;
            appendMessage('You: ' + text);
            vscode.postMessage({ command: 'send', text });
            input.value = '';
        });

        const analyzeBtn = document.getElementById('analyze');
        analyzeBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'analyze' });
        });

        window.addEventListener('message', event => {
            const msg = event.data;
            if (msg.type === 'message') {
                appendMessage('AI: ' + msg.text);
            } else if (msg.type === 'status') {
                status.textContent = msg.text;
            }
        });

        function appendMessage(text) {
            const div = document.createElement('div');
            div.textContent = text;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>`;
        }
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};