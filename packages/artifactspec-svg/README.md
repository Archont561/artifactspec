# artifactspec-svg

An optional static SVG rendering plugin for ArtifactSpec. Install this package
alongside `artifactspec` to make image text and rectangle statements, the `diagram` layout, and the
`svg` renderer available. The separately installed `artifactspec-events` plugin
can add events to the same image diagram. SVG serialization
is separate from the renderer adapter and from reusable semantic content.

Installed plugin code is automatically loaded at render time unless autoload is
disabled. Discovery and validation inspect static metadata without importing
plugin code. See the repository's rendering and plugin documentation for the
trust boundary and supported SVG features.
