"""Guard the repository's pull-request lock repair workflow."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_relock_guard_precedes_repair_and_pins_pixi():
    workflow = (ROOT / ".github/workflows/relock.yml").read_text()
    assert workflow.count("pixi-version: v0.84.1") == 2
    assert "pixi lock --check" in workflow
    assert "needs: guard" in workflow
    assert "needs.guard.result == 'failure'" in workflow
    assert "github.event_name == 'pull_request'" in workflow


def test_relock_repairs_only_pixi_lock_without_publishing():
    workflow = (ROOT / ".github/workflows/relock.yml").read_text()
    assert (
        "github.event.pull_request.head.repo.full_name != github.repository" in workflow
    )
    assert "github.actor == 'dependabot[bot]'" in workflow
    assert "file_pattern: pixi.lock" in workflow
    assert "gh workflow run ci.yml" in workflow
    assert "gh workflow run pixi-sandbox.yml" not in workflow


def test_full_ci_requires_optional_manim_smoke_check():
    ci = (ROOT / ".github/workflows/ci.yml").read_text()
    assert "pixi run --locked -e manim -x python" in ci
    assert "pixi run --locked -e manim -x ffmpeg -version" in ci
    assert "needs.manim-environment.result" in ci
    assert '"$MANIM_RESULT" == success' in ci
