import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

scenarios(
    str(Path(__file__).resolve().parents[1] / "features" / "language_server.feature")
)


class Client:
    def __init__(self, env):
        self.process = subprocess.Popen(
            [sys.executable, "-m", "artifactspec", "lsp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        self.messages = queue.Queue()
        self.thread = threading.Thread(target=self._read, daemon=True)
        self.thread.start()

    def _read(self):
        while True:
            headers = {}
            while True:
                line = self.process.stdout.readline()
                if not line:
                    return
                if line == b"\r\n":
                    break
                key, value = line.decode("ascii").split(":", 1)
                headers[key.lower()] = value.strip()
            payload = self.process.stdout.read(int(headers["content-length"]))
            self.messages.put(json.loads(payload))

    def send(self, method, params, id=None):
        message = {"jsonrpc": "2.0", "method": method, "params": params}
        if id is not None:
            message["id"] = id
        payload = json.dumps(message).encode("utf-8")
        self.process.stdin.write(
            f"Content-Length: {len(payload)}\r\n\r\n".encode() + payload
        )
        self.process.stdin.flush()

    def receive(self):
        return self.messages.get(timeout=10)

    def stop(self):
        if self.process.poll() is None:
            self.process.terminate()
        self.process.communicate(timeout=10)


@pytest.fixture
def state():
    state = {}
    yield state
    if "client" in state:
        state["client"].stop()


@given("an editor connected to the language server with typed static capabilities")
def connected(state, installed_plugin_factory):
    fixture = installed_plugin_factory(
        manifest={
            "schema_version": 2,
            "id": "example",
            "version": "1",
            "outputs": ["image"],
            "phrases": [{"name": "circle", "outputs": [], "object_type": "circle"}],
            "properties": [
                {"name": "color", "outputs": [], "target_types": ["circle"]}
            ],
            "representations": [],
            "renderers": [],
        }
    )
    state.update(fixture)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(fixture["path"]), env.get("PYTHONPATH", "")]
    )
    client = state["client"] = Client(env)
    client.send(
        "initialize", {"processId": None, "rootUri": None, "capabilities": {}}, id=1
    )
    assert client.receive()["id"] == 1
    client.send("initialized", {})
    state["uri"] = "file:///scene.art"


@when("the editor opens a specification with an unresolved reference")
def open_document(state):
    state["text"] = 'Output image.\nSet color of missing to "red".'
    state["client"].send(
        "textDocument/didOpen",
        {
            "textDocument": {
                "uri": state["uri"],
                "languageId": "artifactspec",
                "version": 1,
                "text": state["text"],
            }
        },
    )


@then("the language server publishes the shared validation diagnostic")
def invalid_diagnostic(state):
    result = state["client"].receive()
    assert result["method"] == "textDocument/publishDiagnostics"
    diagnostic = result["params"]["diagnostics"][0]
    assert diagnostic["code"] == "unresolved_reference"
    assert diagnostic["range"] == {
        "start": {"line": 1, "character": 13},
        "end": {"line": 1, "character": 20},
    }
    assert not state["marker"].exists()


@when("the editor fixes the specification")
def fix_document(state):
    state["client"].send(
        "textDocument/didChange",
        {
            "textDocument": {"uri": state["uri"], "version": 2},
            "contentChanges": [
                {
                    "text": 'Output image.\nCreate circle named c.\nSet color of c to "red".'
                }
            ],
        },
    )


@then("the language server clears the diagnostic")
def cleared(state):
    result = state["client"].receive()
    assert result["params"]["uri"] == state["uri"]
    assert result["params"]["diagnostics"] == []


def test_utf16_incremental_edits_close_and_cli_consistency(
    state, installed_plugin_factory
):
    connected(state, installed_plugin_factory)
    client = state["client"]
    uri = state["uri"]
    text = "Output image.\nCreate 😀."
    client.send(
        "textDocument/didOpen",
        {
            "textDocument": {
                "uri": uri,
                "languageId": "artifactspec",
                "version": 1,
                "text": text,
            }
        },
    )
    diagnostic = client.receive()["params"]["diagnostics"][0]
    assert diagnostic["code"] == "malformed_statement"
    assert diagnostic["range"] == {
        "start": {"line": 1, "character": 0},
        "end": {"line": 1, "character": 10},
    }
    client.send(
        "textDocument/didChange",
        {
            "textDocument": {"uri": uri, "version": 2},
            "contentChanges": [
                {
                    "range": {
                        "start": {"line": 1, "character": 7},
                        "end": {"line": 1, "character": 9},
                    },
                    "text": "circle named sun",
                }
            ],
        },
    )
    assert client.receive()["params"]["diagnostics"] == []
    client.send(
        "textDocument/didChange",
        {
            "textDocument": {"uri": uri, "version": 3},
            "contentChanges": [
                {"text": 'Output image.\nSet color of missing to "red".'}
            ],
        },
    )
    server_diagnostic = client.receive()["params"]["diagnostics"][0]
    from artifactspec.plugins import ManifestCatalog
    from artifactspec.validation import validate

    result = validate(
        'Output image.\nSet color of missing to "red".',
        ManifestCatalog([state["manifest"]]),
        source=uri,
    )
    assert server_diagnostic["code"] == result.diagnostics[0].code
    assert server_diagnostic["message"] == result.diagnostics[0].message
    client.send("textDocument/didClose", {"textDocument": {"uri": uri}})
    assert client.receive()["params"]["diagnostics"] == []
    assert not state["marker"].exists()


def test_empty_document_publishes_missing_output(state, installed_plugin_factory):
    connected(state, installed_plugin_factory)
    state["client"].send(
        "textDocument/didOpen",
        {
            "textDocument": {
                "uri": state["uri"],
                "languageId": "artifactspec",
                "version": 1,
                "text": "",
            }
        },
    )
    diagnostic = state["client"].receive()["params"]["diagnostics"][0]
    assert diagnostic["code"] == "missing_output"
    assert diagnostic["range"] == {
        "start": {"line": 0, "character": 0},
        "end": {"line": 0, "character": 0},
    }


def test_server_shutdown_and_rejects_invalid_metadata(state, installed_plugin_factory):
    connected(state, installed_plugin_factory)
    state["client"].send("shutdown", None, id=2)
    reply = state["client"].receive()
    assert reply["id"] == 2 and reply["result"] is None
    state["client"].send("exit", None)
    assert state["client"].process.wait(timeout=10) == 0


def test_cli_lsp_reports_invalid_static_metadata(installed_plugin_factory, monkeypatch):
    from typer.testing import CliRunner

    from artifactspec.cli import app

    fixture = installed_plugin_factory()
    fixture["manifest_path"].write_text("invalid json", encoding="utf-8")
    monkeypatch.syspath_prepend(str(fixture["path"]))
    result = CliRunner().invoke(app, ["lsp"])
    assert result.exit_code == 2
    assert "cannot read manifest" in result.stderr
    assert not fixture["marker"].exists()
