"""Check complete file coverage, pinned sources, documented code hashes and exact diffs."""

from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path

SPEC = "docs/adaptation-spec.json"
LOCK = "docs/adaptation-lock.json"
REPORT = "docs/text2bim-diff.md"
GENERATED = {LOCK, REPORT}
IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    ".local",
    "runs",
    "outputs",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "htmlcov",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unified_diff(original, adapted, source, target):
    lines = difflib.unified_diff(
        original.splitlines(True), adapted.splitlines(True), fromfile=source, tofile=target
    )
    return "".join(
        line if line.endswith("\n") else line + "\n\\ No newline at end of file\n" for line in lines
    )


def inventory(root):
    try:
        top = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if Path(top).resolve() == root.resolve():
            paths = (
                subprocess.check_output(
                    [
                        "git",
                        "-C",
                        str(root),
                        "ls-files",
                        "--cached",
                        "--others",
                        "--exclude-standard",
                        "-z",
                    ]
                )
                .decode()
                .split("\0")
            )
            return {path for path in paths if path}
    except (OSError, subprocess.CalledProcessError):
        pass
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        # setuptools adds these two generated metadata files when creating an sdist.
        and path.relative_to(root).as_posix() not in {"PKG-INFO", "setup.cfg"}
        and not any(
            p in IGNORED_DIRS or p.endswith(".egg-info") for p in path.relative_to(root).parts
        )
        and not path.name.startswith((".env", ".coverage"))
        and path.name != ".DS_Store"
    }


def source_text(root, project, path, symbol=None):
    data = (root / "upstream" / project / path).read_text()
    return extract_symbol(data, symbol) if symbol else data


def extract_symbol(text, name):
    if name is None:
        return text
    nodes = ast.parse(text).body
    node = None
    for part in name.split("."):
        node = next(
            (n for n in nodes if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name == part),
            None,
        )
        if node is None:
            raise ValueError(f"Missing symbol: {name}")
        nodes = node.body
    return ast.get_source_segment(text, node) + "\n"


def fragment_text(root, fragment, side):
    if side == "source":
        text = source_text(
            root, fragment["project"], fragment["source"], fragment.get("source_symbol")
        )
    else:
        text = extract_symbol(
            (root / fragment["target"]).read_text(), fragment.get("target_symbol")
        )
    assignment = fragment.get(side + "_assignment")
    if assignment:
        node = next(
            n
            for n in ast.walk(ast.parse(text))
            if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == assignment for t in n.targets)
        )
        text = ast.get_source_segment(text, node) + "\n"
    return text


def symbols(text):
    result = []
    for node in ast.parse(text).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            result.append(node.name)
            if isinstance(node, ast.ClassDef):
                result.extend(
                    node.name + "." + child.name
                    for child in node.body
                    if isinstance(child, ast.FunctionDef)
                )
    return result


def validate(root, spec):
    entries = {}
    for group in spec["file_groups"]:
        for path in group["paths"]:
            if path in entries:
                raise ValueError(f"Duplicate file coverage: {path}")
            if (
                not group.get("reason")
                or not group.get("method_effect")
                or not group.get("verification")
            ):
                raise ValueError(f"Incomplete adaptation record: {path}")
            entries[path] = group
    actual = inventory(root) | GENERATED
    if actual != set(entries):
        raise ValueError(
            f"File coverage mismatch; undocumented={sorted(actual - set(entries))}; missing={sorted(set(entries) - actual)}"
        )
    for project in ("text2bim", "maslov"):
        manifest = json.loads((root / "upstream" / project / "manifest.json").read_text())
        for path, expected in manifest["files"].items():
            data = (root / "upstream" / project / path).read_bytes()
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if digest(data) != expected["sha256"] or blob != expected["git_blob"]:
                raise ValueError(f"Pinned source was modified: {project}/{path}")
    tree = json.loads((root / "upstream/text2bim/tree.json").read_text())
    if tree["commit"] != spec["source_commit"] or tree["tree"] != spec["source_tree"]:
        raise ValueError("Upstream tree does not match the pinned source")
    all_source = {entry["path"] for entry in tree["files"]}
    dispositions = spec["source_disposition"]
    if all_source != set(dispositions):
        raise ValueError("The complete upstream tree is not accounted for")
    for path, entry in dispositions.items():
        if not entry.get("status") or not entry.get("reason"):
            raise ValueError(f"Missing upstream file disposition: {path}")
    for path, records in spec["symbol_disposition"].items():
        if set(symbols(source_text(root, "text2bim", path))) != set(records):
            raise ValueError(f"Unaccounted upstream declarations: {path}")
        if any(not record.get("reason") or not record.get("status") for record in records.values()):
            raise ValueError(f"Incomplete symbol dispositions: {path}")
    for fragment in spec["fragments"]:
        original, adapted = (fragment_text(root, fragment, side) for side in ("source", "target"))
        if fragment["mode"] == "exact_ast" and ast.dump(ast.parse(original)) != ast.dump(
            ast.parse(adapted)
        ):
            raise ValueError(f"Preserved AST changed: {fragment['id']}")
        if (
            fragment["mode"] == "exact_bytes"
            and (root / "upstream" / fragment["project"] / fragment["source"]).read_bytes()
            != (root / fragment["target"]).read_bytes()
        ):
            raise ValueError(f"Preserved fragment changed: {fragment['id']}")
    return entries


def render_report(root, spec):
    sys.path.insert(0, str(root / "src"))
    from text2bim_massing.prompts import SOURCE_NAMES, load_prompts

    lines = [
        "# Проверяемые отличия от Text2BIM",
        "",
        "Сгенерировано `python tools/audit_adaptation.py --write`; проверка — `--check`.",
        "",
        "Граница аудита: полный Git tree исходного commit, все declarations пяти выбранных",
        "Python-файлов, все файлы standalone-проекта, перенесённые фрагменты и четыре промпта.",
        "Хеши фиксируют проверенное состояние; причины и влияние задаются вручную в adaptation-spec.json.",
        "",
        "Это проверка полноты заявленной карты и точных diff, а не доказательство эквивалентности методов.",
        "",
        "## Исходные файлы",
        "",
        "| Файл | Статус | Причина |",
        "| --- | --- | --- |",
    ]
    for path, record in sorted(spec["source_disposition"].items()):
        lines.append(f"| `{path}` | {record['status']} | {record['reason']} |")
    lines += ["", "## Отличия метода", ""]
    for record in spec["method_changes"]:
        lines += [
            f"### {record['id']}: {record['title']}",
            "",
            record["reason"],
            "",
            "Влияние: " + record["method_effect"],
            "",
            "Проверка: " + record["verification"],
            "",
        ]
    dependencies = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    original_requirements = (root / "upstream/text2bim/requirements.txt").read_text(
        encoding="utf-16"
    )
    lines += [
        "## Зависимости",
        "",
        "Исходные requirements.txt (UTF-16):",
        "",
        "```text",
        original_requirements.rstrip(),
        "```",
        "",
        "Текущие зависимости и extras (причины — LLM, EVALUATOR, PACKAGING выше):",
        "",
        "```json",
        json.dumps(
            {key: dependencies[key] for key in ("dependencies", "optional-dependencies")},
            indent=2,
        ),
        "```",
        "",
        "## Точные diff фрагментов",
        "",
    ]
    for fragment in spec["fragments"]:
        original, adapted = (fragment_text(root, fragment, side) for side in ("source", "target"))
        lines += ["### " + fragment["id"], "", fragment["reason"], ""]
        diff = unified_diff(
            original,
            adapted,
            fragment["source"] + ":" + str(fragment.get("source_symbol", "*")),
            fragment["target"] + ":" + str(fragment.get("target_symbol", "*")),
        )
        lines += ["```diff", diff.rstrip() or "# Без изменений", "```", ""]
    lines += ["## Точные diff рабочих промптов", ""]
    for units in ("mm", "m"):
        adapted = load_prompts(units)
        for role, filename in SOURCE_NAMES.items():
            original = source_text(root, "text2bim", "tool_agent/muti_agent_prompt/" + filename)
            diff = unified_diff(original, adapted[role], filename, role + ":" + units)
            lines += [
                f"### {role}, {units}",
                "",
                "```diff",
                diff.rstrip() or "# Без изменений",
                "```",
                "",
            ]
    return "\n".join(lines)


def run(root, write=False):
    spec = json.loads((root / SPEC).read_text())
    entries = validate(root, spec)
    report = render_report(root, spec)
    if write:
        (root / REPORT).write_text(report)
    elif not (root / REPORT).is_file() or (root / REPORT).read_text() != report:
        raise ValueError("Generated source/prompt diff is stale")
    state = {
        "source_commit": spec["source_commit"],
        "files": {
            path: digest((root / path).read_bytes()) for path in sorted(entries) if path != LOCK
        },
    }
    if write:
        (root / LOCK).write_text(json.dumps(state, indent=2) + "\n")
    elif json.loads((root / LOCK).read_text()) != state:
        raise ValueError(
            "Unreviewed changes: adaptation-lock.json differs; review reasons and regenerate the audit"
        )
    return len(entries), len(spec["source_disposition"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        files, upstream = run(args.root.resolve(), args.write)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"Adaptation audit failed: {error}\n")
    print(
        f"Adaptation audit passed: {files} project files; {upstream} upstream files accounted for."
    )


if __name__ == "__main__":
    main()
