"""Execute a trusted, user-supplied evaluator in a fresh interpreter."""

import json
import sys
from pathlib import Path

import cloudpickle


def main():
    input_path, output_path, paths_path = map(Path, sys.argv[1:])
    sys.path[:] = json.loads(paths_path.read_text())
    try:
        with input_path.open("rb") as stream:
            evaluator, massing, context = cloudpickle.load(stream)
        report = evaluator(massing, context)
        if not isinstance(report, dict):
            raise TypeError("Evaluator must return a JSON-compatible dictionary")
        data = json.dumps({"ok": True, "report": report}, allow_nan=False)
    except BaseException as error:
        data = json.dumps({"ok": False, "error": f"{type(error).__name__}: {error}"})
    output_path.write_text(data)


if __name__ == "__main__":
    main()
