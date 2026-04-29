import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def render_template(template_path: str, context: dict) -> str:
    template_dir = os.path.dirname(template_path) or '.'
    template_name = os.path.basename(template_path)
    env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
    tmpl = env.get_template(template_name)
    return tmpl.render(**context)


def main():
    # simple CLI for manual testing
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--template', default=str(Path(__file__).resolve().parents[1] / 'templates' / 'archived' / 'gitlab_ci_gradle.jinja.yml'))
    parser.add_argument('--out', default=None)
    args = parser.parse_args()
    rendered = render_template(args.template, {})
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(rendered)
    else:
        print(rendered)


if __name__ == '__main__':
    main()
