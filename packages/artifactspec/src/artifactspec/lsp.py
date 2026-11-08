"""LSP diagnostics backed by the same validator as the CLI."""

from lsprotocol import types
from pygls.lsp.server import LanguageServer
from pygls.workspace import ServerTextPosition, TextDocument

from artifactspec.discovery import installed_plugins
from artifactspec.plugins import CapabilityCatalog, ManifestCatalog
from artifactspec.validation import validate


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
        publish(params.text_document.uri)

    @server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
    def did_change(params: types.DidChangeTextDocumentParams) -> None:
        publish(params.text_document.uri)

    @server.feature(types.TEXT_DOCUMENT_DID_CLOSE)
    def did_close(params: types.DidCloseTextDocumentParams) -> None:
        server.text_document_publish_diagnostics(
            types.PublishDiagnosticsParams(uri=params.text_document.uri, diagnostics=[])
        )

    return server


def start() -> None:
    """Start the server over standard input and output."""
    catalog = ManifestCatalog(item[1] for item in installed_plugins().values())
    create_server(catalog).start_io()
