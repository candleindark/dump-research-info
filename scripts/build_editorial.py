#!/usr/bin/env python3
"""Render curated editorial YAML and expose it across the generated site."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


def normalize_base_path(value: str) -> str:
    value = "/" + value.strip("/") if value.strip("/") else ""
    return f"{value}/"


def site_url(base_path: str, suffix: str = "") -> str:
    return f"{base_path}{suffix.lstrip('/')}"


def navigation_html(content: dict[str, Any], base_path: str) -> str:
    links = [
        '<a class="con-editorial-nav__brand" href="{}">CON</a>'.format(
            html.escape(site_url(base_path), quote=True)
        )
    ]
    for item in content["navigation"]:
        href = site_url(base_path, f"{item['slug']}/")
        links.append(
            '<a href="{}">{}</a>'.format(
                html.escape(href, quote=True),
                html.escape(str(item["label"])),
            )
        )
    links.append(
        '<a href="{}">Research index</a>'.format(
            html.escape(site_url(base_path, "projects/"), quote=True)
        )
    )
    return (
        '<nav id="con-editorial-nav" class="con-editorial-nav" '
        'aria-label="Center information">' + "".join(links) + "</nav>"
    )


def inject_navigation(path: Path, content: dict[str, Any], base_path: str) -> bool:
    document = path.read_text(encoding="utf-8")
    changed = False
    css_href = html.escape(site_url(base_path, "assets/editorial.css"), quote=True)
    if "assets/editorial.css" not in document:
        link = f'<link rel="stylesheet" href="{css_href}">'
        document = re.sub(r"</head>", f"  {link}\n</head>", document, count=1, flags=re.I)
        changed = True
    if 'id="con-editorial-nav"' not in document:
        nav = navigation_html(content, base_path)
        match = re.search(r"<body(?:\s[^>]*)?>", document, flags=re.I)
        if match:
            document = document[: match.end()] + nav + document[match.end() :]
            changed = True
    if changed:
        path.write_text(document, encoding="utf-8")
    return changed


def build(args: argparse.Namespace) -> dict[str, int]:
    content = yaml.safe_load(args.content.read_text(encoding="utf-8"))
    if content.get("format_version") != 1:
        raise ValueError("Unsupported editorial content format_version")
    pages = content.get("pages")
    if not isinstance(pages, dict) or not pages:
        raise ValueError("Editorial content requires at least one page")

    base_path = normalize_base_path(args.base_path)
    environment = Environment(
        loader=FileSystemLoader(args.template.parent),
        autoescape=select_autoescape(("html", "xml")),
        undefined=StrictUndefined,
    )
    environment.globals["site_url"] = lambda suffix="": site_url(base_path, suffix)
    template = environment.get_template(args.template.name)
    args.output.mkdir(parents=True, exist_ok=True)

    for slug, page in pages.items():
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise ValueError(f"Unsafe editorial slug: {slug}")
        target = args.output / slug / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            template.render(
                content=content,
                current_slug=slug,
                page=page,
                base_path=base_path,
            ),
            encoding="utf-8",
        )

    data_target = args.output / "data" / "editorial.json"
    data_target.parent.mkdir(parents=True, exist_ok=True)
    data_target.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")

    injected = sum(
        inject_navigation(path, content, base_path)
        for path in args.output.glob("**/*.html")
    )
    return {"editorial_pages": len(pages), "navigation_injected": injected}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-path", default="/")
    result = build(parser.parse_args())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
