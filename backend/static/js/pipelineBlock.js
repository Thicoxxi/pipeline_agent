import {
  validateYAML,
  highlightError,
  convertToGitHub
} from "./yaml.js";

export function createPipelineBlock({ messages, provider }) {
  if (!messages?.appendChild) {
    console.error("❌ messages inválido");
    return;
  }

  const wrap = document.createElement("div");
  wrap.className = "message assistant";

  // =====================================================
  // HEADER
  // =====================================================
  const header = document.createElement("div");
  header.className = "assistant-header";

  const providerBadge = document.createElement("div");
  providerBadge.className = "provider-badge";
  providerBadge.innerHTML = `🤖 ${provider || "auto"}`;

  const updateBtn = document.createElement("button");
  updateBtn.className = "update-btn";
  updateBtn.innerHTML = "♻️ Atualizar Pipeline";

  header.append(providerBadge, updateBtn);

  // =====================================================
  // SPLIT VIEW
  // =====================================================
  const split = document.createElement("div");
  split.className = "split-view";

  // =====================================================
  // GITLAB PANEL
  // =====================================================
  const gitlabPanel = document.createElement("div");
  gitlabPanel.className = "panel gitlab-panel";

  const gitlabTop = document.createElement("div");
  gitlabTop.className = "panel-top";
  gitlabTop.innerHTML = `<div class="panel-title">🦊 GitLab CI</div>`;

  const gitlabButtons = document.createElement("div");
  gitlabButtons.className = "panel-buttons";

  const saveGitlab = document.createElement("button");
  saveGitlab.className = "save-btn";
  saveGitlab.innerHTML = "💾 salvar .gitlab-ci.yml";

  const applyGitlab = document.createElement("button");
  applyGitlab.className = "save-btn";
  applyGitlab.innerHTML = "🦊 Aplicar no GitLab";

  gitlabButtons.append(saveGitlab, applyGitlab);
  gitlabTop.appendChild(gitlabButtons);

  const gitlabEditor = document.createElement("textarea");
  gitlabEditor.className = "editor";
  gitlabEditor.placeholder = "Pipeline GitLab aparecerá aqui...";

  const gitlabForm = document.createElement("div");
  gitlabForm.className = "gitlab-form";
  gitlabForm.innerHTML = `
    <div class="gitlab-form-grid">
      <input type="text" class="gitlab-input" placeholder="🆔 GitLab Project ID">
      <input type="text" class="gitlab-input" placeholder="🌿 Branch" value="main">
    </div>
  `;
  const projectIdInput = gitlabForm.querySelectorAll(".gitlab-input")[0];
  const branchInput = gitlabForm.querySelectorAll(".gitlab-input")[1];

  gitlabPanel.append(gitlabTop, gitlabEditor, gitlabForm);

  // =====================================================
  // GITHUB PANEL
  // =====================================================
  const githubPanel = document.createElement("div");
  githubPanel.className = "panel github-panel";

  const githubTop = document.createElement("div");
  githubTop.className = "panel-top";
  githubTop.innerHTML = `<div class="panel-title">🐙 GitHub Actions</div>`;

  const githubButtons = document.createElement("div");
  githubButtons.className = "panel-buttons";

  const saveGithub = document.createElement("button");
  saveGithub.className = "save-btn";
  saveGithub.innerHTML = "💾 salvar github-actions.yml";

  const applyGithub = document.createElement("button");
  applyGithub.className = "save-btn";
  applyGithub.innerHTML = "🐙 Aplicar no GitHub";

  githubButtons.append(saveGithub, applyGithub);
  githubTop.appendChild(githubButtons);

  const githubEditor = document.createElement("textarea");
  githubEditor.className = "editor";
  githubEditor.placeholder = "GitHub Actions aparecerá aqui...";

  const githubForm = document.createElement("div");
  githubForm.className = "gitlab-form";
  githubForm.innerHTML = `
    <div class="gitlab-form-grid">
      <input type="text" class="gitlab-input" placeholder="🐙 GitHub Owner">
      <input type="text" class="gitlab-input" placeholder="📦 GitHub Repo">
      <input type="text" class="gitlab-input" placeholder="🌿 Branch" value="main">
    </div>
  `;
  const githubOwnerInput = githubForm.querySelectorAll(".gitlab-input")[0];
  const githubRepoInput = githubForm.querySelectorAll(".gitlab-input")[1];
  const githubBranchInput = githubForm.querySelectorAll(".gitlab-input")[2];

  githubPanel.append(githubTop, githubEditor, githubForm);

  // =====================================================
  // VALIDATION
  // =====================================================
  const validation = document.createElement("div");
  validation.className = "validation";

  split.append(gitlabPanel, githubPanel);
  wrap.append(header, split, validation);
  messages.appendChild(wrap);

  // =====================================================
  // UPDATE BUTTON (manual conversão)
  // =====================================================
  updateBtn.onclick = () => {
    const result = validateYAML(gitlabEditor.value);
    if (!result.valid) {
      validation.innerHTML = result.message;
      validation.className = "validation error";
      highlightError(gitlabEditor, result.line);
      return;
    }
    githubEditor.value = convertToGitHub(gitlabEditor.value);
    githubEditor.classList.remove("placeholder");
    validation.innerHTML = "✅ Pipeline atualizada";
    validation.className = "validation success";
  };

  // =====================================================
  // SAVE GITLAB
  // =====================================================
  saveGitlab.onclick = () => {
    const blob = new Blob([gitlabEditor.value]);
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = ".gitlab-ci.yml";
    a.click();
  };

  // =====================================================
  // SAVE GITHUB
  // =====================================================
  saveGithub.onclick = () => {
    const blob = new Blob([githubEditor.value]);
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "github-actions.yml";
    a.click();
  };

  // =====================================================
  // APPLY GITLAB
  // =====================================================
  applyGitlab.onclick = async () => {
    const res = await fetch("/api/gitlab/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_id: projectIdInput.value,
        branch: branchInput.value,
        yaml: gitlabEditor.value
      })
    });
    const data = await res.json();
    validation.innerHTML = data.message || data.error;
    validation.className = res.ok ? "validation success" : "validation error";
  };

  // =====================================================
  // APPLY GITHUB
  // =====================================================
  applyGithub.onclick = async () => {
    const res = await fetch("/api/github/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        owner: githubOwnerInput.value,
        repo: githubRepoInput.value,
        branch: githubBranchInput.value,
        yaml: githubEditor.value
      })
    });
    const data = await res.json();
    validation.innerHTML = data.message || data.error;
    validation.className = res.ok ? "validation success" : "validation error";
  };

  // =====================================================
  // API (corrigido para pedidos específicos + placeholders visuais)
  // =====================================================
  return {
    setProvider(provider) {
      providerBadge.innerHTML = `🤖 ${provider}`;
    },
    setGitlab(yaml) {
      if (!yaml || yaml.startsWith("# Nenhum")) {
        gitlabEditor.value = "# Nenhum pipeline GitLab gerado para este pedido";
        gitlabEditor.classList.add("placeholder");
      } else {
        gitlabEditor.value = yaml;
        gitlabEditor.classList.remove("placeholder");
      }
    },
    setGithub(yaml) {
      if (!yaml || yaml.startsWith("# Nenhum")) {
        githubEditor.value = "# Nenhum pipeline GitHub gerado para este pedido";
        githubEditor.classList.add("placeholder");
      } else {
        githubEditor.value = yaml;
        githubEditor.classList.remove("placeholder");
      }
    }
  };
}
