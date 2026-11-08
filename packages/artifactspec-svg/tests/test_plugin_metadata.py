"""The installed entry point loads the actual SVG plugin object."""


def test_installed_plugin_object_is_registered():
    from artifactspec_svg.plugin import plugin

    from artifactspec.plugins.discovery import installed_plugins

    loaded = installed_plugins(only={"svg"})["svg"]
    assert loaded is plugin
    assert loaded.to_dict()["version"] == "0.1.0"
