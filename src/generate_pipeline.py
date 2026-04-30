import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def render_template(template_path: str, context: dict) -> str:
    template_path = Path(template_path)

    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        trim_blocks=True,
        lstrip_blocks=True
    )

    template = env.get_template(template_path.name)
    return template.render(**context)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--template',
        default=str(
            Path(__file__).resolve().parents[1]
            / 'templates'
            / 'archived'
            / 'gitlab_ci_gradle.jinja.yml'
        )
    )
    parser.add_argument('--out')

    args = parser.parse_args()

    rendered = render_template(args.template, {})

    if args.out:
        Path(args.out).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == '__main__':
    main()