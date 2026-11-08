"""The installed plugin advertises its runtime contract without importing it."""


def test_installed_manifest_matches_plugin_declaration():
    from artifactspec_svg.plugin import plugin

    from artifactspec.plugins.discovery import installed_plugins

    entry, manifest = installed_plugins()["svg"]
    assert entry.value == "artifactspec_svg.plugin:plugin"
    assert manifest == plugin.manifest()
