from dataclasses import FrozenInstanceError

import pytest

from artifactspec.parser import ParseError, parse
from artifactspec.plugins import Plugin, RegistrationError, Registry
from artifactspec.syntax import CreateStatement, Position, SetStatement, SourceSpan


@pytest.fixture
def registry():
    plugin = Plugin("test", "1", outputs=("image", "animation"))
    plugin.phrase("rounded circle", outputs=("image",))(lambda ctx: None)
    plugin.property("fill color", outputs=("image",))(lambda ctx: None)
    plugin.property("label")(lambda ctx: None)
    registry = Registry()
    registry.register(plugin)
    return registry


def test_spans_escapes_whitespace_and_immutability(registry):
    document = parse(
        "\n  Output image.  \r\n\tCreate rounded circle named sun-1.\r\n"
        '  Set fill color of sun-1 to "café. \\"yes\\"".\r\n',
        registry,
        source="example.image",
    )
    assert document.output_span == SourceSpan(
        "example.image", Position(2, 3), Position(2, 16)
    )
    assert document.span == SourceSpan("example.image", Position(2, 3), Position(4, 46))
    assert isinstance(document.statements[0], CreateStatement)
    statement = document.statements[1]
    assert isinstance(statement, SetStatement)
    assert statement.value.value == 'café. "yes"'
    assert statement.reference.name == "sun-1"
    assert statement.reference.span == SourceSpan(
        "example.image", Position(4, 21), Position(4, 26)
    )
    assert statement.value.span == SourceSpan(
        "example.image", Position(4, 30), Position(4, 45)
    )
    with pytest.raises(FrozenInstanceError):
        document.output = "animation"


@pytest.mark.parametrize(
    ("text", "code", "line"),
    [
        ("", "missing_output", 1),
        ("  \n", "missing_output", 1),
        ("Create rounded circle named c.", "missing_output", 1),
        ("Output image", "missing_output", 1),
        ("Output svg.", "unknown_output", 1),
        ("Output image.\nOutput image.", "ambiguous_output", 2),
        ("Output image.\nCreate rounded circle named it.", "malformed_statement", 2),
        ("Output image.\nCreate rounded circle named 1bad.", "malformed_statement", 2),
        ("Output image.\nCreate rounded circle named sun", "malformed_statement", 2),
        ("Output image.\nCreate round square named sun.", "unknown_phrase", 2),
        ('Output image.\nSet label of it to "hello"', "malformed_statement", 2),
        ("Output image.\nSet label of it to [1].", "malformed_statement", 2),
        ('Output image.\nSet label of it to "bad\\q".', "malformed_statement", 2),
        ('Output image.\nSet missing of it to "x".', "unknown_property", 2),
        ('Output animation.\nSet fill color of it to "red".', "unknown_property", 2),
        ("Output image.\nRun arbitrary code.", "unknown_statement", 2),
        (
            'Output image.\nCreate rounded circle named x. Set label of x to "a".',
            "malformed_statement",
            2,
        ),
    ],
)
def test_invalid_inputs_are_source_linked(registry, text, code, line):
    with pytest.raises(ParseError) as captured:
        parse(text, registry, source="test.image")
    error = captured.value
    assert error.code == code
    assert error.span.start.line == line
    assert error.span.source == "test.image"
    assert str(error).startswith(f"test.image:{line}:")


def test_empty_output_has_an_empty_immutable_statement_sequence(registry):
    document = parse("Output image.\n\n", registry)
    assert document.statements == ()
    assert document.span == document.output_span


def test_unknown_capabilities_never_invoke_handlers(registry):
    with pytest.raises(ParseError, match="not registered"):
        parse("Output animation.\nCreate rounded circle named x.", registry)


def test_duplicate_phrase_registrations_are_rejected_before_parsing(registry):
    other = Plugin("other", "1", outputs=("image",))
    other.phrase("rounded circle")(lambda ctx: None)
    with pytest.raises(RegistrationError, match="conflicting"):
        registry.register(other)


def test_named_and_it_references_remain_unresolved(registry):
    document = parse(
        'Output image.\nSet label of future to "before".\n'
        'Create rounded circle named future.\nSet label of it to "after".',
        registry,
    )
    assert document.statements[0].reference.name == "future"
    assert document.statements[2].reference.name == "it"


def test_json_literal_may_contain_statement_delimiters(registry):
    document = parse(
        'Output image.\nSet label of it to "x of thing to y. Z".', registry
    )
    assert document.statements[0].value.value == "x of thing to y. Z"


def test_registered_names_cannot_smuggle_a_second_statement():
    plugin = Plugin("test", "1", outputs=("image",))
    plugin.phrase("circle named first. Create circle")(lambda ctx: None)
    plugin.property("label of first to x. Set label")(lambda ctx: None)
    registry = Registry()
    registry.register(plugin)
    with pytest.raises(ParseError):
        parse(
            "Output image.\nCreate circle named first. Create circle named second.",
            registry,
        )
    with pytest.raises(ParseError):
        parse(
            'Output image.\nSet label of first to x. Set label of first to "y".',
            registry,
        )


def test_registered_names_can_include_grammar_words():
    plugin = Plugin("test", "1", outputs=("image",))
    plugin.phrase("a circle named circle")(lambda ctx: None)
    plugin.property("label of apple to orange")(lambda ctx: None)
    registry = Registry()
    registry.register(plugin)
    document = parse(
        'Output image.\nCreate a circle named circle named apple.\nSet label of apple to orange of apple to "ok".',
        registry,
    )
    assert document.statements[0].phrase == "a circle named circle"
    assert document.statements[1].property == "label of apple to orange"


def test_lark_parses_each_kind_of_statement(registry, monkeypatch):
    from lark import Lark

    original = Lark.parse
    parsed_starts = []

    def record_parse(self, text, *args, **kwargs):
        parsed_starts.append(kwargs.get("start"))
        return original(self, text, *args, **kwargs)

    monkeypatch.setattr(Lark, "parse", record_parse)
    parse(
        'Output image.\nCreate rounded circle named sun.\nSet label of sun to "x".',
        registry,
    )
    assert parsed_starts == ["header", "create", "set"]


@pytest.mark.parametrize(
    "line",
    [
        'Set label of it to "bad\\q".',
        'Set label of it to "bad\tcontrol".',
        'Set label of it to "good" "bad".',
        'Set  label of it to "x".',
        'Set label  of it to "x".',
        'Set label of it to "x". Set label of it to "y".',
        "Create rounded  circle named sun.",
        "Create rounded circle named sun. Create rounded circle named other.",
    ],
)
def test_invalid_single_line_grammar_is_rejected(registry, line):
    with pytest.raises(ParseError) as captured:
        parse("Output image.\n" + line, registry)
    assert captured.value.code == "malformed_statement"


def test_literal_and_reference_spans_with_unicode_and_tabs(registry):
    line = '\tSet label of sun to "☀ café".'
    document = parse("\tOutput image.\n" + line, registry, source="unicode")
    statement = document.statements[0]
    assert statement.reference.span == SourceSpan(
        "unicode",
        Position(2, line.index("sun") + 1),
        Position(2, line.index("sun") + 4),
    )
    assert statement.value.span == SourceSpan(
        "unicode", Position(2, line.index('"') + 1), Position(2, len(line))
    )
    assert statement.value.value == "☀ café"


def test_ambiguous_lark_parse_is_rejected(registry, monkeypatch):
    from lark import Tree

    from artifactspec import parser

    monkeypatch.setattr(
        parser._PARSER, "parse", lambda *args, **kwargs: Tree("_ambig", [])
    )
    with pytest.raises(ParseError) as captured:
        parse("Output image.", registry)
    assert captured.value.code == "ambiguous_statement"
    assert captured.value.span.start == Position(1, 1)
