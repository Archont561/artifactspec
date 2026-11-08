"""LSP diagnostics backed by the same validator as the CLI."""

from collections.abc import Sequence
from urllib.parse import unquote

from lsprotocol import types
from pygls.lsp.server import LanguageServer
from pygls.workspace import ServerTextPosition, TextDocument

from artifactspec._lines import source_lines
from artifactspec.discovery import installed_plugins
from artifactspec.plugins import CapabilityCatalog, ManifestCatalog
from artifactspec.validation import validate


class _LanguageDocument(TextDocument):
    """Use the same line boundaries as the parser, including for incremental edits."""

    @property
    def lines(self) -> Sequence[str]:
        return source_lines(self.source)


def _position(document: TextDocument, line: int, column: int) -> types.Position:
    return document.position_to_client_units(ServerTextPosition(line - 1, column - 1))


def create_server(catalog: CapabilityCatalog) -> LanguageServer:
    """Create an LSP server which validates against static capability metadata."""
    server = LanguageServer("artifactspec", "0.1.0")

    def publish(uri: str) -> None:
        document = server.workspace.get_text_document(uri)
        result = validate(document.source, catalog, source=uri)
        diagnostics = []
        for item in result.diagnostics:
            span = item.span
            diagnostics.append(
                types.Diagnostic(
                    range=types.Range(
                        start=_position(document, span.start.line, span.start.column),
                        end=_position(document, span.end.line, span.end.column),
                    ),
                    message=item.message,
                    severity=types.DiagnosticSeverity.Error
                    if item.severity == "error"
                    else types.DiagnosticSeverity.Warning,
                    code=item.code,
                    source="artifactspec",
                )
            )
        server.text_document_publish_diagnostics(
            types.PublishDiagnosticsParams(
                uri=uri, diagnostics=diagnostics, version=document.version
            )
        )

    @server.feature(types.TEXT_DOCUMENT_DID_OPEN)
    def did_open(params: types.DidOpenTextDocumentParams) -> None:
        item = params.text_document
        workspace = server.workspace
        original = workspace.get_text_document(item.uri)
        # pygls uses str.splitlines(), which treats JSON string characters such
        # as U+0085 as line breaks. Replace the workspace document before edits.
        workspace.text_documents[unquote(item.uri)] = _LanguageDocument(
            item.uri,
            source=item.text,
            version=item.version,
            language_id=item.language_id,
            position_codec=original.position_codec,
        )
        publish(item.uri)

    @server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
    def did_change(params: types.DidChangeTextDocumentParams) -> None:
        publish(params.text_document.uri)

    @server.feature(types.TEXT_DOCUMENT_DID_CLOSE)
    def did_close(params: types.DidCloseTextDocumentParams) -> None:
        server.text_document_publish_diagnostics(
            types.PublishDiagnosticsParams(uri=params.text_document.uri, diagnostics=[])
        )

    return server


def start(*, builtin_basic: bool = False) -> None:
    """Start the server over standard input and output."""
    manifests = [item[1] for item in installed_plugins().values()]
    if builtin_basic:
        from artifactspec._basic_metadata import basic_manifest

        manifests.append(basic_manifest())
    catalog = ManifestCatalog(manifests)
    create_server(catalog).start_io()
