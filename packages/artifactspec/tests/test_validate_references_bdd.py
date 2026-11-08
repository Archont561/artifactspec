from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

from artifactspec.plugins import Plugin, Registry

scenarios(
    str(
        Path(__file__).resolve().parents[1] / "features" / "validate_references.feature"
    )
)


@pytest.fixture
def state():
    return {"executed": []}


@given("typed circle and color capabilities")
def typed_capabilities(state):
    plugin = Plugin("shapes", "1", outputs=("image",), schema_version=2)
    plugin.phrase("circle", object_type="circle")(
        lambda ctx: state["executed"].append(ctx)
    )
    plugin.phrase("text", object_type="text")(lambda ctx: state["executed"].append(ctx))
    plugin.property("color", target_types=("circle",))(
        lambda ctx: state["executed"].append(ctx)
    )
    state["registry"] = Registry()
    state["registry"].register(plugin)


@given("a legacy plugin without type metadata")
def legacy_plugin(state):
    plugin = Plugin("old", "1", outputs=("image",))
    plugin.phrase("circle")(lambda ctx: None)
    plugin.property("color")(lambda ctx: None)
    state["registry"] = Registry()
    state["registry"].register(plugin)


def check(state, text):
    from artifactspec.validation import validate

    state["result"] = validate(text, state["registry"], source="scene.art")


@when("I validate a specification with forward and latest references")
def valid_input(state):
    check(
        state,
        'Output image.\nSet color of later to "red".\nCreate circle named later.\nSet color of it to "blue".',
    )


@when("I validate a color property on a text object")
def wrong_type(state):
    check(
        state, 'Output image.\nCreate text named title.\nSet color of title to "red".'
    )


@when("I validate a legacy specification")
def legacy_input(state):
    check(state, 'Output image.\nCreate circle named c.\nSet color of c to "red".')


@then("both references resolve to their intended objects")
def resolved(state):
    result = state["result"]
    assert result.diagnostics == ()
    assert [item.target.name for item in result.resolutions] == ["later", "later"]


@then("validation has not run a plugin handler")
def no_execution(state):
    assert state["executed"] == []


@then("validation reports a wrong type at the reference")
def wrong_type_error(state):
    diagnostic = state["result"].diagnostics[0]
    assert diagnostic.code == "wrong_type"
    assert diagnostic.severity == "error"
    assert diagnostic.span.start.line == 3
    assert diagnostic.span.source == "scene.art"


@then("validation warns that the property type is unverified")
def legacy_warning(state):
    diagnostic = state["result"].diagnostics[0]
    assert diagnostic.code == "unverified_type"
    assert diagnostic.severity == "warning"
