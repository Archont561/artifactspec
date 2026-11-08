from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from artifactspec.plugins import Plugin, Registry

scenarios(
    str(
        Path(__file__).resolve().parents[1] / "features" / "parse_specification.feature"
    )
)


@pytest.fixture
def state():
    return {"executions": []}


@given("image phrases and properties are registered")
@given("an image color property is registered")
@given("an image circle phrase is registered")
@given("an image color property can be parsed")
@given("image and animation outputs are registered")
@given("a circle phrase is registered only for image output")
def registered_capabilities(state):
    plugin = Plugin("draw", "1", outputs=("image", "animation"))

    @plugin.phrase("circle", outputs=("image",))
    def circle(context):
        state["executions"].append(context)

    @plugin.property("color")
    def color(context):
        state["executions"].append(context)

    @plugin.property("label", outputs=("image",))
    def label(context):
        state["executions"].append(context)

    state["registry"] = Registry()
    state["registry"].register(plugin)


def parse_input(state, text):
    from artifactspec.core.parser import ParseError, parse

    try:
        state["document"] = parse(text, state["registry"], source="scene.image")
    except ParseError as exc:
        state["error"] = exc


@when("I parse an image specification with a named object and properties")
def valid_specification(state):
    parse_input(
        state,
        'Output image.\nCreate circle named sun.\nSet color of it to "yellow".\nSet label of sun to "Bright sun".\n',
    )


@when("I parse a property referring to it before any object is created")
def unresolved_reference(state):
    parse_input(state, 'Output image.\nSet color of it to "yellow".\n')


@when("I parse a specification with an unregistered phrase")
def unknown_phrase(state):
    parse_input(state, "Output image.\nCreate square named sun.\n")


@when("I parse a specification with a non-string property value")
def invalid_value(state):
    parse_input(state, "Output image.\nSet color of it to 42.\n")


@when("I parse a specification with two output headers")
def ambiguous_outputs(state):
    parse_input(state, "Output image.\nOutput animation.\n")


@when("I parse an animation specification using an image-only phrase")
def incompatible_phrase(state):
    parse_input(state, "Output animation.\nCreate circle named sun.\n")


@then("the document has typed statements and source locations")
def typed_document(state):
    from artifactspec.core.syntax import CreateStatement, SetStatement

    document = state["document"]
    assert document.output == "image"
    assert document.span.source == "scene.image"
    assert len(document.statements) == 3
    created, first, second = document.statements
    assert isinstance(created, CreateStatement)
    assert (
        created.phrase,
        created.name,
        created.span.start.line,
        created.span.start.column,
    ) == ("circle", "sun", 2, 1)
    assert isinstance(first, SetStatement)
    assert (first.property, first.reference.name, first.value.value) == (
        "color",
        "it",
        "yellow",
    )
    assert (first.reference.span.start.line, first.reference.span.start.column) == (
        3,
        14,
    )
    assert (second.reference.name, second.value.value) == ("sun", "Bright sun")


@then("parsing has not executed plugin handlers")
def no_handlers_called(state):
    assert state["executions"] == []


@then("the reference is preserved without being resolved")
def reference_preserved(state):
    assert state["document"].statements[0].reference.name == "it"
    assert state["executions"] == []


@then(
    parsers.re(
        r"parsing fails with (?:a|an) (?P<kind>.+) diagnostic at line (?P<line>\d+)"
    )
)
def diagnostic_at_line(state, kind, line):
    error = state["error"]
    assert error.code == kind.replace(" ", "_")
    assert error.span.source == "scene.image"
    assert error.span.start.line == int(line)
    assert "scene.image:" in str(error)
    assert "document" not in state
