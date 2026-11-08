# ArtifactSpec events plugin

An optional plugin providing dated event syntax and diagram representation.
Install alongside ArtifactSpec and a compatible renderer such as
`artifactspec-svg`. Installed plugin code is trusted executable Python and is
imported during capability discovery, validation, LSP startup, and rendering unless
autoload is disabled.

The event image representation provides its own SVG-compatible text value; the
report representation remains independent and requires a report renderer. The
events plugin does not import or depend on the SVG plugin.
