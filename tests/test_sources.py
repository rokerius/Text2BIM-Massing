import ast
import hashlib
import json
from importlib import resources
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def function_ast(source, name):
    return ast.dump(
        next(
            node
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.FunctionDef) and node.name == name
        )
    )


def test_original_sources_match_pinned_blob_hashes():
    for project in ("text2bim", "maslov"):
        root = ROOT / "upstream" / project
        manifest = json.loads((root / "manifest.json").read_text())
        for path, hashes in manifest["files"].items():
            data = (root / path).read_bytes()
            assert hashlib.sha256(data).hexdigest() == hashes["sha256"]
            assert (
                hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                == hashes["git_blob"]
            )


def test_interpreter_diff_is_only_the_documented_syntax_fix():
    original = (ROOT / "upstream/text2bim/tool_agent/python_interpreter.py").read_text()
    expected = original.replace(
        '        print(f"Syntax error in generated code: {e}")\n        return None, state',
        '        raise InterpretorError(f"Syntax error in generated code: {e}") from e',
    )
    adapted = resources.files("text2bim_massing._vendor.text2bim").joinpath("python_interpreter.py")
    assert adapted.read_text() == expected


def test_reused_utils_and_conversion_methods_have_identical_ast():
    original = (ROOT / "upstream/text2bim/tool_agent/utils.py").read_text()
    adapted = resources.files("text2bim_massing._vendor.text2bim").joinpath("utils.py").read_text()
    for name in (
        "safe_encode",
        "remove_last_human_message_with_regex",
        "clean_code_for_chat_extend",
    ):
        assert function_ast(original, name) == function_ast(adapted, name)
    for name in ("polygons_to_shapely_converter.py", "shapely_to_polygons_converter.py"):
        original = (ROOT / "upstream/maslov/src" / name).read_text()
        adapted = resources.files("text2bim_massing._vendor.maslov").joinpath(name).read_text()
        assert function_ast(original, "__call__") == function_ast(adapted, "__call__")


def test_four_original_prompts_are_available_as_package_resources():
    root = resources.files("text2bim_massing._vendor.text2bim")
    sources = list((ROOT / "upstream/text2bim/tool_agent/muti_agent_prompt").glob("*.txt"))
    assert len(sources) == 4
    for source in sources:
        assert root.joinpath("prompts", source.name).read_bytes() == source.read_bytes()
    assert root.joinpath("LICENSE").is_file()
    assert root.joinpath("LICENSE-APACHE-2.0").is_file()
