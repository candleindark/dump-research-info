#!/usr/bin/env python3
"""Build deterministic, project-centered relationship reports from Things data."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

import yaml


NodeKey = tuple[str, str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def canonical(value: str) -> str:
    return value.casefold()


def nested_strings(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from nested_strings(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from nested_strings(child, path + (str(index),))
    elif isinstance(value, str):
        yield ".".join(path), value


def load_graph(data_root: Path) -> tuple[
    dict[NodeKey, dict[str, Any]],
    dict[str, list[NodeKey]],
    list[dict[str, Any]],
]:
    contributions: dict[NodeKey, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    pid_index: dict[str, list[NodeKey]] = defaultdict(list)

    for path in sorted(data_root.rglob("*.json")):
        relative = path.relative_to(data_root)
        source = relative.parts[0]
        class_name = path.stem
        records = json.loads(path.read_text(encoding="utf-8"))
        for record in records:
            pid = record["pid"]
            key = class_name, canonical(pid)
            contributions[key].append((source, record))
            if key not in pid_index[canonical(pid)]:
                pid_index[canonical(pid)].append(key)

    nodes: dict[NodeKey, dict[str, Any]] = {}
    for key, records in contributions.items():
        first = records[0][1]
        label = next(
            (
                record.get(field)
                for _, record in records
                for field in ("display_label", "title", "short_name")
                if record.get(field)
            ),
            first["pid"],
        )
        nodes[key] = {
            "class": key[0],
            "pid": first["pid"],
            "label": label,
            "sources": sorted({source for source, _ in records}),
        }

    edge_keys: set[tuple[NodeKey, NodeKey, str, str]] = set()
    edges: list[dict[str, Any]] = []
    for subject, records in contributions.items():
        for source, record in records:
            attribute_relations = {
                f"attributes.{index}.value": item.get("predicate", "attributes")
                for index, item in enumerate(record.get("attributes", []))
                if isinstance(item, dict)
            }
            for path, value in nested_strings(record):
                if path == "pid":
                    continue
                targets = pid_index.get(canonical(value), [])
                if not targets:
                    continue
                relation = attribute_relations.get(path, path.split(".", 1)[0])
                for target in targets:
                    if target == subject:
                        continue
                    edge_key = subject, target, relation, path
                    if edge_key in edge_keys:
                        continue
                    edge_keys.add(edge_key)
                    edges.append(
                        {
                            "subject_key": subject,
                            "target_key": target,
                            "relation": relation,
                            "path": path,
                            "source": source,
                        }
                    )
    return nodes, pid_index, edges


def build_slice(
    definition: dict[str, Any],
    nodes: dict[NodeKey, dict[str, Any]],
    pid_index: dict[str, list[NodeKey]],
    edges: list[dict[str, Any]],
) -> dict[str, Any]:
    root_matches = pid_index.get(canonical(definition["root"]), [])
    if len(root_matches) != 1:
        raise ValueError(f"Slice root must resolve to exactly one entity: {definition['root']}")
    root = root_matches[0]
    outgoing: dict[NodeKey, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        outgoing[edge["subject_key"]].append(edge)

    depths = {root: 0}
    selected_edges: list[dict[str, Any]] = []
    queue: deque[NodeKey] = deque([root])
    max_depth = int(definition.get("max_depth", 1))
    while queue:
        subject = queue.popleft()
        depth = depths[subject]
        if depth >= max_depth:
            continue
        for edge in sorted(
            outgoing.get(subject, []),
            key=lambda item: (nodes[item["target_key"]]["pid"].casefold(), item["relation"], item["path"]),
        ):
            selected_edges.append(edge)
            target = edge["target_key"]
            if target not in depths:
                depths[target] = depth + 1
                queue.append(target)

    included_pids = {canonical(nodes[key]["pid"]) for key in depths}
    rendered_edges = [
        {
            "subject": nodes[edge["subject_key"]]["pid"],
            "subject_class": nodes[edge["subject_key"]]["class"],
            "relation": edge["relation"],
            "target": nodes[edge["target_key"]]["pid"],
            "target_class": nodes[edge["target_key"]]["class"],
            "source": edge["source"],
            "path": edge["path"],
        }
        for edge in selected_edges
    ]

    for expected in definition.get("expected_targets", []):
        target = canonical(expected["pid"])
        if target not in included_pids:
            raise ValueError(f"Expected target is not reachable in {definition['slug']}: {expected['pid']}")
        relation = expected.get("relation")
        if relation and not any(
            canonical(edge["target"]) == target and edge["relation"] == relation
            for edge in rendered_edges
        ):
            raise ValueError(
                f"Expected relation is absent in {definition['slug']}: {relation} -> {expected['pid']}"
            )

    external_candidates = []
    for candidate in definition.get("external_candidates", []):
        external_candidates.append(
            {
                **candidate,
                "status": "modeled" if canonical(candidate["pid"]) in pid_index else "missing_entity",
            }
        )

    rendered_nodes = [
        {**nodes[key], "depth": depth}
        for key, depth in sorted(depths.items(), key=lambda item: (item[1], nodes[item[0]]["class"], nodes[item[0]]["pid"].casefold()))
    ]
    class_counts = Counter(node["class"] for node in rendered_nodes)
    return {
        "format_version": 1,
        "slug": definition["slug"],
        "label": definition["label"],
        "root": definition["root"],
        "summary": {
            "node_count": len(rendered_nodes),
            "edge_count": len(rendered_edges),
            "class_counts": dict(sorted(class_counts.items())),
            "missing_external_candidates": sum(
                item["status"] == "missing_entity" for item in external_candidates
            ),
        },
        "nodes": rendered_nodes,
        "edges": rendered_edges,
        "expected_targets": definition.get("expected_targets", []),
        "external_candidates": external_candidates,
        "evidence": definition.get("evidence", []),
        "follow_up": definition.get("follow_up", []),
    }


def render_reports(data_root: Path, config_path: Path) -> dict[str, dict[str, Any]]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if config.get("format_version") != 1:
        raise ValueError("Research slice config must use format_version: 1")
    nodes, pid_index, edges = load_graph(data_root)
    reports = {
        f"{definition['slug']}.json": build_slice(definition, nodes, pid_index, edges)
        for definition in config["slices"]
    }
    reports["index.json"] = {
        "format_version": 1,
        "description": config.get("description"),
        "slices": [
            {
                "slug": report["slug"],
                "label": report["label"],
                **report["summary"],
            }
            for name, report in sorted(reports.items())
            if name != "index.json"
        ],
    }
    return reports


def main() -> int:
    args = parse_args()
    reports = render_reports(args.data_root, args.config)
    expected_names = set(reports)
    existing_names = {path.name for path in args.output.glob("*.json")} if args.output.exists() else set()

    if args.check:
        problems = []
        for name, report in reports.items():
            path = args.output / name
            if not path.exists() or json.loads(path.read_text(encoding="utf-8")) != report:
                problems.append(name)
        problems.extend(sorted(existing_names - expected_names))
        if problems:
            raise ValueError(f"Research slice reports are stale: {sorted(set(problems))}")
        print(json.dumps({"checked_reports": len(reports), "status": "current"}, sort_keys=True))
        return 0

    args.output.mkdir(parents=True, exist_ok=True)
    for name in existing_names - expected_names:
        (args.output / name).unlink()
    for name, report in reports.items():
        (args.output / name).write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    print(json.dumps({"written_reports": len(reports), "output": str(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
