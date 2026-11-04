import json
import sys

from test_workflow import BUILD, ScriptedLLM, decision

from text2bim_massing import cli
from text2bim_massing.codex_client import CodexCLIClient, CodexConfig


def test_cli_writes_real_workflow_artifacts_with_a_configured_test_transport(
    tmp_path, monkeypatch, capsys
):
    config = tmp_path / "run.json"
    config.write_text(
        json.dumps(
            {
                "llm": {"provider": "test"},
                "evaluator": {"factory": "test_workflow:report", "kind": "callable"},
            }
        )
    )
    monkeypatch.setattr(cli, "load_llm", lambda spec: ScriptedLLM(["Build", BUILD, decision()]))
    monkeypatch.setattr(ScriptedLLM, "close", lambda self: None, raising=False)
    exit_code = cli.main(
        ["generate", "--config", str(config), "--task", "Build", "--output", str(tmp_path / "out")]
    )
    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)["status"] == "completed"
    assert (tmp_path / "out" / "selected_massing.json").exists()


def test_codex_transport_uses_saved_chatgpt_login_and_structured_output(tmp_path, monkeypatch):
    metadata = tmp_path / "metadata.json"
    executable = tmp_path / "codex-test"
    executable.write_text(f"""#!{sys.executable}
import json, os, sys
from pathlib import Path
if sys.argv[1:]==['login','status']:
    print('Logged in using ChatGPT')
    raise SystemExit(0)
prompt=sys.stdin.read()
Path({str(metadata)!r}).write_text(json.dumps({{'args':sys.argv[1:],'prompt':prompt,'api_key_present':'OPENAI_API_KEY' in os.environ}}))
path=Path(sys.argv[sys.argv.index('--output-last-message')+1])
path.write_text(json.dumps({{'text':'generated text','tool_calls':[]}}))
print(json.dumps({{'type':'turn.completed','usage':{{'input_tokens':12,'output_tokens':3}}}}))
""")
    executable.chmod(0o755)
    monkeypatch.setenv("OPENAI_API_KEY", "test-value-that-must-not-be-forwarded")
    client = CodexCLIClient(CodexConfig(executable=str(executable)))
    response = client.complete([{"role": "user", "content": "test task"}])
    assert response.text == "generated text" and response.total_tokens == 15
    data = json.loads(metadata.read_text())
    assert data["api_key_present"] is False
    assert data["args"][data["args"].index("--sandbox") + 1] == "read-only"
    assert "--ignore-user-config" in data["args"]
    assert "--output-schema" in data["args"]
    assert "test task" in data["prompt"]
