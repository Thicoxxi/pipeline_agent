from src.generate_pipeline import render_template
from pathlib import Path

tpl = Path(__file__).resolve().parents[1] / 'templates' / 'archived' / 'gitlab_ci_gradle.jinja.yml'
out = render_template(str(tpl), {'language': 'java', 'version': '1.2.3', 'gradle_task': 'build', 'nexus_url': 'https://nexus.example.com', 'nexus_repo': 'my-repo', 'group': 'com.example', 'artifact': 'my-app', 'deploy_command': 'echo deploy'})
print(out[:400])
