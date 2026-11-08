# Release preparation

There is no automatic publishing workflow. Publishing, tagging and creating a
release require explicit authorization; never use real credentials in PR jobs.

Before considering a release, review the milestone, changelog, license and
package metadata, resolve outstanding blockers, and verify CI on GitHub. The
Pixi environment currently targets Linux; support on other platforms requires
separate verification.

```sh
pixi run --locked lint
pixi run --locked format-check
pixi run --locked typecheck
pixi run --locked check-packages
pixi run --locked audit
pixi run --locked coverage-all
```

`check-packages` builds wheels and source distributions for both packages in a
temporary directory, checks metadata, checks wheel license inclusion, and
installs the wheels in a clean virtual environment. Both VERSION constants are
checked against their installed metadata in an isolated Python process. The Manim-named package is
currently a version-only placeholder. Builds and the clean install
need network access. Hatchling is capped below 1.30 because newer build metadata
was rejected by the currently locked Twine; revisit this pin when verified.

For a rehearsal, after authorization, build the desired artifacts to a known
output directory and use a dedicated TestPyPI project and trusted publishing or
a securely managed TestPyPI token. Use a unique test version, verify package
metadata and installation in a clean environment, and account for dependencies
that TestPyPI does not host. TestPyPI is not PyPI and does not reserve a name on
PyPI. Do not put credentials in repository files or PR logs.

For a real release, after explicit authorization, verify that the PyPI project
names are available or controlled by the project, confirm the version and
changelog, rebuild and check the artifacts, then publish through the approved
trusted-publishing or credential workflow. Verify the published distributions,
installation, and release notes. No publishing workflow or PyPI project has
been configured by this repository change.
