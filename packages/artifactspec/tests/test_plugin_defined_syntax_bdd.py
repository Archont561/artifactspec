"""Plugin templates describe the entire user-facing statement syntax."""

from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

from artifactspec.core.validation import validate
from artifactspec.plugins import ManifestCatalog

scenarios(
    str(
        Path(__file__).resolve().parents[1]
        / "features"
        / "plugin_defined_syntax.feature"
    )
)


@pytest.fixture
def state():
    return {}


@given("static metadata for a plugin with its own statement templates")
@given("a plugin that declares a different output and content syntax")
def plugin_catalog(state):
    state["catalog"] = ManifestCatalog(
        [
            {
                "schema_version": 3,
                "id": "example",
                "version": "1",
                "outputs": ["image"],
                "output_syntax": {"image": "Produce image."},
                "phrases": [
                    {
                        "name": "label",
                        "outputs": [],
                        "object_type": "label",
                        "syntax": "Draw label {name}.",
                    }
                ],
                "properties": [
                    {
                        "name": "content",
                        "outputs": [],
                        "target_types": ["label"],
                        "syntax": "Write {value} on {reference}.",
                    }
                ],
                "representations": [],
                "renderers": [],
            }
        ]
    )


@when("I validate a document written using those templates")
def validate_custom(state):
    state["result"] = validate(
        'Produce image.\nDraw label title.\nWrite "Hello" on title.',
        state["catalog"],
        source="example.art",
    )


@when("I validate a document using undeclared generic forms")
def validate_generic(state):
    state["result"] = validate(
        "Output image.\nCreate label named title.", state["catalog"]
    )


@then("the document is valid and its statement locations are retained")
def valid_result(state):
    result = state["result"]
    assert result.valid, result.diagnostics
    assert result.document.output == "image"
    assert result.document.statements[0].name == "title"
    assert result.document.statements[1].value.value == "Hello"
    assert result.document.statements[1].reference.span.start.column == 18
    assert result.document.statements[1].span.start.line == 3


@then("validation reports an unknown output declaration")
def invalid_result(state):
    assert not state["result"].valid
    assert state["result"].diagnostics[0].code == "unknown_output"
