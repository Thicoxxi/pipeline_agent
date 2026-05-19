const assert = require('assert');
const vscode = require('vscode');
const http = require('http');

suite('Analyze Command Integration Test', function () {
  let server;

  setup(function (done) {
    // Start a simple HTTP server that responds with a YAML pipeline
    server = http.createServer((req, res) => {
      if (req.method === 'POST' && req.url === '/api/analyze-project') {
        let body = '';
        req.on('data', (chunk) => { body += chunk; });
        req.on('end', () => {
          const yaml = 'stages:\n  - build\n' +
            'build:\n  script:\n    - echo "building"\n';
          res.writeHead(200, { 'Content-Type': 'text/plain' });
          res.end(yaml);
        });
      } else {
        res.writeHead(404);
        res.end();
      }
    });

    server.listen(5000, '127.0.0.1', done);
  });

  teardown(function (done) {
    server.close(done);
  });

  test('generates pipeline and opens YAML editor', async function () {
    this.timeout(20000);

    // Ensure we have a workspace open
    const folders = vscode.workspace.workspaceFolders;
    assert.ok(folders && folders.length > 0, 'Workspace must be open for the test');

    // Execute the command registered by the extension
    await vscode.commands.executeCommand('pipeline-generator-ai.analyzeProject');

    // Wait briefly for the editor to open
    await new Promise((r) => setTimeout(r, 1000));

    const editor = vscode.window.activeTextEditor;
    assert.ok(editor, 'An editor should be opened');
    const doc = editor.document;
    assert.strictEqual(doc.languageId, 'yaml', 'Document language should be yaml');
    const text = doc.getText();
    assert.ok(text.includes('stages:'), 'Generated YAML should contain pipeline stages');
  });
});
