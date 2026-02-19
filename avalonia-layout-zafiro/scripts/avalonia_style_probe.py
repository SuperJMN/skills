#!/usr/bin/env python3
"""
Avalonia style probe.

Builds an approximate style/resource tree from *.axaml files and estimates
which properties would apply to a target control type + classes.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple


RESOURCE_EXPR_RE = re.compile(r"\{(?:DynamicResource|StaticResource)\s+([^\s\}]+)\s*\}")


def strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def get_attr(elem: ET.Element, name: str) -> Optional[str]:
    for key, value in elem.attrib.items():
        if key == name or key.endswith("}" + name) or key.endswith(":" + name):
            return value
    return None


def selector_terminal(selector: str) -> str:
    s = selector.strip()
    if "/template/" in s:
        return ""
    parts = re.split(r"\s+|>", s)
    if not parts:
        return ""
    return parts[-1].strip()


def parse_selector(selector: str) -> Tuple[Optional[str], Set[str], bool, int]:
    term = selector_terminal(selector)
    if not term:
        return None, set(), False, -1

    pseudos = re.findall(r":[A-Za-z0-9_-]+", term)
    term = re.sub(r":[A-Za-z0-9_-]+", "", term)
    term = re.sub(r"#[A-Za-z0-9_-]+", "", term)

    type_name = None
    is_wrapper = re.match(r"^:is\(([A-Za-z0-9_\.]+)\)", term)
    if is_wrapper:
        type_name = is_wrapper.group(1).split(".")[-1]
        term = term[is_wrapper.end() :]
    else:
        base = re.match(r"^[A-Za-z_][A-Za-z0-9_\.]*", term)
        if base:
            type_name = base.group(0).split(".")[-1]
            term = term[base.end() :]

    classes = set(re.findall(r"\.([A-Za-z0-9_-]+)", term))
    specificity = (100 if type_name else 0) + (10 * len(classes)) + len(pseudos)
    return type_name, classes, True, specificity


def parse_setters(style_elem: ET.Element) -> Dict[str, str]:
    setters: Dict[str, str] = {}
    for child in style_elem:
        if strip_ns(child.tag) != "Setter":
            continue
        prop = get_attr(child, "Property")
        if not prop:
            continue
        value = get_attr(child, "Value")
        if value is None:
            if len(child):
                value = ET.tostring(child[0], encoding="unicode").strip()
            else:
                value = (child.text or "").strip()
        setters[prop] = value
    return setters


def serialize_resource_value(elem: ET.Element) -> str:
    value = get_attr(elem, "Value")
    if value is not None:
        return value
    if len(elem):
        return ET.tostring(elem[0], encoding="unicode").strip()
    return (elem.text or "").strip()


@dataclass
class StyleRule:
    selector: str
    file: str
    order: int
    setters: Dict[str, str]
    type_name: Optional[str]
    classes: Set[str]
    specificity: int
    based_on_key: Optional[str] = None


@dataclass
class ControlTheme:
    key: str
    target_type: Optional[str]
    setters: Dict[str, str]
    file: str


@dataclass
class ProbeModel:
    styles: List[StyleRule] = field(default_factory=list)
    resources: Dict[str, Dict[str, str]] = field(default_factory=dict)
    control_themes: Dict[str, ControlTheme] = field(default_factory=dict)
    includes: List[Dict[str, str]] = field(default_factory=list)
    parse_errors: List[str] = field(default_factory=list)


def build_model(project_root: Path) -> ProbeModel:
    model = ProbeModel()
    axaml_files: List[Path] = []

    def on_walk_error(exc: OSError) -> None:
        model.parse_errors.append(f"walk: {exc.filename}: {exc.strerror}")

    for dirpath, _, filenames in os.walk(project_root, onerror=on_walk_error):
        for filename in filenames:
            if filename.endswith(".axaml"):
                axaml_files.append(Path(dirpath) / filename)
    axaml_files.sort()
    order = 0
    for path in axaml_files:
        rel = str(path.relative_to(project_root))
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            model.parse_errors.append(f"{rel}: {exc}")
            continue

        for elem in root.iter():
            tag = strip_ns(elem.tag)

            if tag in {"ResourceInclude", "MergeResourceInclude", "StyleInclude"}:
                source = get_attr(elem, "Source")
                if source:
                    model.includes.append({"from": rel, "kind": tag, "source": source})

            selector = get_attr(elem, "Selector")
            if tag == "Style" and selector:
                t_name, classes, active, spec = parse_selector(selector)
                if not active:
                    continue
                based_on = get_attr(elem, "BasedOn")
                based_on_key = None
                if based_on:
                    match = RESOURCE_EXPR_RE.search(based_on)
                    if match:
                        based_on_key = match.group(1)
                model.styles.append(
                    StyleRule(
                        selector=selector,
                        file=rel,
                        order=order,
                        setters=parse_setters(elem),
                        type_name=t_name,
                        classes=classes,
                        specificity=spec,
                        based_on_key=based_on_key,
                    )
                )
                order += 1

            if tag == "ControlTheme":
                key = get_attr(elem, "Key")
                if not key:
                    continue
                model.control_themes[key] = ControlTheme(
                    key=key,
                    target_type=(get_attr(elem, "TargetType") or "").split(".")[-1] or None,
                    setters=parse_setters(elem),
                    file=rel,
                )

            key = get_attr(elem, "Key")
            if key:
                model.resources[key] = {"value": serialize_resource_value(elem), "file": rel}

    return model


def matches_style(control_type: str, classes: Set[str], style: StyleRule) -> bool:
    if style.type_name and style.type_name.lower() != control_type.lower():
        return False
    if not style.classes.issubset(classes):
        return False
    return True


def resolve_resource(expr: str, resources: Dict[str, Dict[str, str]]) -> str:
    match = RESOURCE_EXPR_RE.search(expr)
    if not match:
        return expr
    key = match.group(1)
    found = resources.get(key)
    if not found:
        return f"{expr} (unresolved)"
    return f"{expr} -> {found['value']}"


def estimate_properties(
    model: ProbeModel,
    control_type: str,
    class_list: Sequence[str],
    local_overrides: Dict[str, str],
    theme_key: Optional[str],
) -> Dict[str, object]:
    classes = {c for c in class_list if c}
    matched = [s for s in model.styles if matches_style(control_type, classes, s)]
    matched.sort(key=lambda s: (s.specificity, s.order))

    applied: Dict[str, Dict[str, str]] = {}
    trace: Dict[str, List[Dict[str, str]]] = {}

    if theme_key:
        theme = model.control_themes.get(theme_key)
        if theme:
            for prop, raw in theme.setters.items():
                value = resolve_resource(raw, model.resources)
                source = f"ControlTheme:{theme.key} ({theme.file})"
                applied[prop] = {"value": value, "source": source}
                trace.setdefault(prop, []).append({"value": value, "source": source})

    for style in matched:
        if style.based_on_key and style.based_on_key in model.control_themes:
            base_theme = model.control_themes[style.based_on_key]
            for prop, raw in base_theme.setters.items():
                value = resolve_resource(raw, model.resources)
                source = f"Style.BasedOn->{base_theme.key} ({base_theme.file})"
                applied[prop] = {"value": value, "source": source}
                trace.setdefault(prop, []).append({"value": value, "source": source})

        for prop, raw in style.setters.items():
            value = resolve_resource(raw, model.resources)
            source = f"Style:{style.selector} ({style.file})"
            applied[prop] = {"value": value, "source": source}
            trace.setdefault(prop, []).append({"value": value, "source": source})

    for prop, value in local_overrides.items():
        source = "LocalOverride"
        applied[prop] = {"value": value, "source": source}
        trace.setdefault(prop, []).append({"value": value, "source": source})

    return {
        "control": control_type,
        "classes": sorted(classes),
        "theme_key": theme_key,
        "matched_styles": [
            {
                "selector": s.selector,
                "specificity": s.specificity,
                "file": s.file,
                "setters": s.setters,
                "based_on_key": s.based_on_key,
            }
            for s in matched
        ],
        "computed_properties": applied,
        "property_trace": trace,
    }


def parse_local_assignments(local: Sequence[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for item in local:
        if "=" not in item:
            raise ValueError(f"Invalid --local value '{item}', expected Property=Value")
        key, value = item.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def render_text(result: Dict[str, object], model: ProbeModel, show_tree: bool) -> str:
    lines: List[str] = []
    lines.append(f"Control: {result['control']}")
    classes = result.get("classes", [])
    lines.append(f"Classes: {', '.join(classes) if classes else '(none)'}")

    if result.get("theme_key"):
        lines.append(f"Theme key: {result['theme_key']}")

    lines.append("")
    lines.append("Matched styles (low->high priority):")
    matched_styles = result.get("matched_styles", [])
    if not matched_styles:
        lines.append("  - (none)")
    else:
        for style in matched_styles:
            lines.append(
                f"  - {style['selector']} [spec={style['specificity']}] ({style['file']})"
            )

    lines.append("")
    lines.append("Computed properties:")
    computed = result.get("computed_properties", {})
    if not computed:
        lines.append("  - (none)")
    else:
        for prop in sorted(computed.keys()):
            winner = computed[prop]
            lines.append(f"  - {prop} = {winner['value']}  <- {winner['source']}")

    if show_tree:
        lines.append("")
        lines.append("Resource/style tree summary:")
        lines.append(f"  - styles indexed: {len(model.styles)}")
        lines.append(f"  - resources indexed: {len(model.resources)}")
        lines.append(f"  - control themes indexed: {len(model.control_themes)}")
        lines.append(f"  - include edges: {len(model.includes)}")
        for edge in model.includes[:50]:
            lines.append(f"    - {edge['kind']}: {edge['from']} -> {edge['source']}")
        if len(model.includes) > 50:
            lines.append("    - ... (truncated)")
        if model.parse_errors:
            lines.append("  - parse warnings:")
            for err in model.parse_errors:
                lines.append(f"    - {err}")

    return "\n".join(lines)


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Estimate effective Avalonia style properties for a target control using "
            "project *.axaml files."
        )
    )
    parser.add_argument("--project-root", required=True, help="Root directory of the Avalonia project.")
    parser.add_argument("--control", required=True, help="Control type name, e.g., Button, TextBlock.")
    parser.add_argument(
        "--classes",
        default="",
        help="Comma-separated classes, e.g., Primary,Outline",
    )
    parser.add_argument(
        "--local",
        action="append",
        default=[],
        help="Optional local override, repeatable: --local Background=Red",
    )
    parser.add_argument(
        "--theme-key",
        default=None,
        help="Optional ControlTheme resource key applied to the control.",
    )
    parser.add_argument("--show-tree", action="store_true", help="Print style/resource tree summary.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    if not project_root.exists() or not project_root.is_dir():
        print(f"Project root not found: {project_root}", file=sys.stderr)
        return 2

    try:
        local_overrides = parse_local_assignments(args.local)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    classes = [c.strip() for c in args.classes.split(",") if c.strip()]
    model = build_model(project_root)
    result = estimate_properties(
        model=model,
        control_type=args.control.strip(),
        class_list=classes,
        local_overrides=local_overrides,
        theme_key=args.theme_key,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "summary": {
                        "styles_indexed": len(model.styles),
                        "resources_indexed": len(model.resources),
                        "control_themes_indexed": len(model.control_themes),
                        "include_edges": len(model.includes),
                        "parse_errors": model.parse_errors,
                    },
                    "result": result,
                    "includes": model.includes if args.show_tree else [],
                },
                indent=2,
                ensure_ascii=True,
            )
        )
    else:
        print(render_text(result, model, show_tree=args.show_tree))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
