#!/usr/bin/env python3
"""Seed curated editorial YAML from the pinned legacy-site inventory.

This is an explicit migration command, not part of CI. Running it overwrites the
curated file, so future source refreshes should be reviewed before reseeding.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


PRINCIPLES = [
    {
        "title": "Open Source",
        "body": [
            "Open source is not only an efficient paradigm for scalability and collaboration; it facilitates verification and reproducibility.",
            "We advocate open-source principles and consult scientific developers on licensing and sustainable development practices.",
        ],
    },
    {
        "title": "Re-Use & Integration",
        "body": [
            "Scientific communities already share powerful software and data. We develop products that harness, improve, and integrate existing solutions rather than reinventing them.",
        ],
    },
    {
        "title": "Dissemination",
        "body": [
            "Scientific software often lacks the facilities and funding needed for reliable promotion and distribution.",
            "We help distribute software, data, and documentation while giving careful attention to intellectual property and due acknowledgment.",
        ],
    },
    {
        "title": "Quality Assurance",
        "body": [
            "Research developers are not always programmers by training. We establish unit, regression, integration, and validity testing so scientific tools produce robust, correct results.",
        ],
    },
    {
        "title": "Convenience",
        "body": [
            "Reliability and accessibility only matter at scale when software and data are convenient to use. We reduce the complexity that prevents communities from using shared resources.",
        ],
    },
    {
        "title": "Community",
        "body": [
            "Neuroscience projects are often pursued in isolation. We participate in cross-disciplinary initiatives and build bridges between previously disconnected research groups.",
        ],
    },
]

REFERENCES = [
    {
        "label": "Open and reproducible neuroimaging: from study inception to publication",
        "url": "https://doi.org/10.1016/j.neuroimage.2022.119623",
    },
    {
        "label": "Four aspects to make science open by design and not as an after-thought",
        "url": "https://doi.org/10.1186/s13742-015-0072-7",
    },
    {
        "label": "Open is not enough. Let's take the next step",
        "url": "https://doi.org/10.3389/fninf.2012.00022",
    },
]


def clean_links(links: list[dict[str, Any]]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for link in links:
        url = str(link.get("url", "")).strip()
        if not url or url in seen or url.startswith("javascript:"):
            continue
        seen.add(url)
        result.append(
            {
                "label": str(link.get("label", "")).strip() or url,
                "url": url,
            }
        )
    return result


def engagement_sections(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    order: list[str] = []
    for topic in inventory["engagement_topics"]:
        category = topic.get("category") or "Ways to engage"
        if category not in grouped:
            order.append(category)
        grouped[category].append(
            {
                "title": topic["title"],
                "body": topic.get("text_blocks", []),
                "links": clean_links(topic.get("links", [])),
            }
        )
    return [
        {"title": category, "layout": "entries", "items": grouped[category]}
        for category in order
    ]


def supporter_items(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "title": supporter["name"],
            "links": clean_links(supporter.get("links", [])),
        }
        for supporter in inventory["supporters"]
    ]


def seed(inventory: dict[str, Any]) -> dict[str, Any]:
    source = inventory["source"]
    support_page = inventory["pages"]["content/pages/support.html"]
    support_body = support_page.get("text_blocks", [])
    if not support_body:
        support_body = [
            "Support helps the Center for Open Neuroscience sustain open software, data, infrastructure, training, and community work."
        ]

    return {
        "format_version": 1,
        "provenance": {
            "migration_source": source["url"],
            "migration_commit": source["commit"],
            "note": "Seeded from the legacy site and curated in this repository thereafter.",
        },
        "navigation": [
            {"label": "About", "slug": "about"},
            {"label": "Engage", "slug": "engage"},
            {"label": "Support", "slug": "support"},
            {"label": "Contact", "slug": "contact"},
        ],
        "pages": {
            "about": {
                "title": "Center for Open Neuroscience",
                "eyebrow": "Open tools. Reusable knowledge. Better science.",
                "lead": "We provide open software frameworks, platforms, data, and methodologies for neuroscience and beyond.",
                "sections": [
                    {"title": "Our principles", "layout": "cards", "items": PRINCIPLES},
                    {
                        "title": "References",
                        "layout": "links",
                        "body": [
                            "These publications frame the center's approach to open and reproducible neuroscience."
                        ],
                        "links": REFERENCES,
                    },
                    {
                        "title": "A long view",
                        "layout": "quote",
                        "body": [
                            "Together we can make neuroscience a better science."
                        ],
                    },
                ],
            },
            "engage": {
                "title": "Engage with CON",
                "eyebrow": "Contribute, connect, and promote",
                "lead": "Join the communities that develop, test, document, teach, and sustain open neuroscience.",
                "sections": engagement_sections(inventory),
            },
            "support": {
                "title": "Support open neuroscience",
                "eyebrow": "Sustain shared infrastructure",
                "lead": "Support enables long-term maintenance, distribution, testing, and community work.",
                "sections": [
                    {"title": "How support helps", "layout": "prose", "body": support_body},
                    {
                        "title": "Supporters",
                        "layout": "supporters",
                        "items": supporter_items(inventory),
                    },
                ],
            },
            "contact": {
                "title": "Contact the center",
                "eyebrow": "Center for Open Neuroscience",
                "lead": "Questions, collaboration proposals, and contributions are welcome.",
                "sections": [
                    {
                        "title": "Stay in touch",
                        "layout": "contact",
                        "items": [
                            {"title": "Email", "value": "team@centerforopenneuroscience.org", "url": "mailto:team@centerforopenneuroscience.org"},
                            {"title": "GitHub", "value": "github.com/con", "url": "https://github.com/con"},
                            {"title": "ROR", "value": "ror.org/04tfhh831", "url": "https://ror.org/04tfhh831"},
                            {"title": "Address", "value": "Psychological and Brain Sciences, 3 Maynard Street, Hanover, NH 03755, USA"},
                        ],
                    },
                    {
                        "title": "Licensing and identity",
                        "layout": "prose",
                        "body": [
                            "Website content is copyright of its respective authors and is released under the Creative Commons Attribution 3.0 license.",
                            "The Center for Open Neuroscience is not directly affiliated with COS, the Center for Open Science.",
                        ],
                        "links": [
                            {"label": "Creative Commons Attribution 3.0", "url": "https://creativecommons.org/licenses/by/3.0/"},
                            {"label": "Center for Open Science", "url": "https://centerforopenscience.org/"},
                        ],
                    },
                ],
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("inputs/con_site/inventory.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("site/content/editorial.yaml"),
    )
    args = parser.parse_args()
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    payload = seed(inventory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(
            payload,
            allow_unicode=False,
            sort_keys=False,
            width=100,
        ),
        encoding="utf-8",
    )
    print(
        f"Seeded {len(payload['pages'])} editorial pages at {args.output} "
        f"from {payload['provenance']['migration_commit']}."
    )


if __name__ == "__main__":
    main()
