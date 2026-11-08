# Backlog

This directory is the Backlog.md workspace for ArtifactSpec's planned product
capabilities and engineering work. Its records describe intentions and progress;
they are not a claim that the language, CLI, renderer, or plugin API already exist.

- [`docs/`](docs/) contains the product and architecture specification.
- [`decisions/`](decisions/) records architectural decisions.
- [`milestones/`](milestones/) groups work by intended product outcome.
- [`tasks/`](tasks/) tracks the work and its acceptance criteria.

With the Pixi environment available, survey the backlog with:

```sh
pixi run backlog instructions overview
pixi run backlog milestone list --plain
pixi run backlog task list --status "In Progress" --plain
pixi run backlog task list --status "To Do" --plain
```

Use `pixi run backlog` to create or update records, and read its task instructions
before changing task state. See [CONTRIBUTING.md](../CONTRIBUTING.md) for the
repository workflow.
