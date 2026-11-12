# Offline sandbox (orphan branch)

Built 2026-11-12T19:49:01Z from commit `1840445` for platform `linux-64`.
`pixi.lock` sha256 `7d876a7dfbe1f403c04002050d6c2e4e6b8156b83974c3c161322519ffc2a5a4`.

The verified self-bootstrap binary is stored at `.pixi-sandbox/tools/linux-64/pixi-sandbox`. The branch root intentionally contains documentation only.

| env | platform | packed | unpacked | files |
| --- | --- | ---: | ---: | ---: |
| `default` | linux-64 | 143.4 MiB | 461.4 MiB | 121 |
| `gherkin` | linux-64 | 48.1 MiB | 167.8 MiB | 34 |


## Restore on the disconnected machine

```bash
./.pixi-sandbox/tools/linux-64/pixi-sandbox doctor --branch-location . --verify
./.pixi-sandbox/tools/linux-64/pixi-sandbox restore --branch-location . --output-path <project> --force
# then, from <project> with no network, use pixi as the sole entrypoint:
pixi install --frozen --offline
pixi run --frozen -- cargo build --offline
```

Every manifest blob is verified before it is written into the working tree.
