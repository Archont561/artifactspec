---
id: doc-2
title: Proposed composable plugin and statement contract
type: specification
created_date: '2026-11-08 22:35'
updated_date: '2026-11-08 22:46'
---
## Status and scope

**Proposal for user review; not an implemented API.** ART-46 studies a possible replacement for the existing decorator-based plugin API. The examples below illustrate a contract, not importable code. ART-47 and ART-48 remain blocked on review. No user authorization to implement or merge follows from this draft alone.

The objective is to let plugins define complete statements, reusable typed properties, output declarations, representations, and renderers as composable Python objects. Core discovers and validates these contributions and dispatches handlers. Core does not own specific sentence wording or require every statement to be a creation or assignment statement.

## Existing behavior to preserve or explicitly migrate

The current parser accepts plugin-declared output, phrase, and property templates, but its source nodes and execution pipeline still distinguish `CreateStatement` and `SetStatement`. Templates currently have fixed name, reference, and JSON-string fields. Static validation resolves named and `it` references and checks declared types without invoking handlers. The pipeline creates all semantic nodes before applying property assignments in source order. The installed-plugin loader imports selected `Plugin` objects, and the owning distribution supplies the version.

Content, representation, composition, and rendering remain separate. Today a composition contains ordered core `Element` wrappers with plugin-owned values and provenance. SVG and events are separately installable and can contribute to the same image. This proposal does not add animation playback, a report renderer, operator overloading, or a core-owned basic plugin.

## Illustrative authoring API

This sketch proposes class-level declarations and no decorators. `Define` and `Reference` are generic typed syntax components; `Color` is a reusable plugin property class, not a generic core color concept.

```python
from artifactspec.plugin import (
    Define, Plugin, Property, Reference, Renderer, Representation, Statement,
)
from artifactspec_svg.elements import Rectangle
from artifactspec_svg.syntax import serialize_svg

class Color(Property):
    key = "color"
    target_types = (Rectangle,)
    # The base handler stores the captured string at key on the selected target.

class DrawRectangle(Statement):
    syntax = ("Draw rectangle ", Define("shape", Rectangle), " in ", Color, ".")

class PaintRectangle(Statement):
    syntax = ("Paint ", Reference("shape", (Rectangle,)), " in ", Color, ".")

class Diagram(Representation):
    name = "diagram"
    target_types = (Rectangle,)
    outputs = ("image",)

    def handle(self):
        node = self.context.node
        color = dict(node.properties).get("color", "black")
        self.context.add(node.name, Rectangle(20, 40 + 70 * self.context.index, 120, 40, color))

class Svg(Renderer):
    name = "svg"
    outputs = ("image",)

    def handle(self):
        # serialize_svg validates the format and emits trusted SVG fragments.
        data = serialize_svg(self.context.composition)
        self.context.emit(data, media_type="image/svg+xml", editable=True)

plugin = Plugin(
    id="shapes",
    outputs={"image": "Output image."},
    statements=(DrawRectangle, PaintRectangle),
    representations=(Diagram,),
    renderers=(Svg,),
)
```

This is an illustrative plugin, not the existing SVG package. A corresponding document could contain `Output image.`, `Draw rectangle box in "blue".`, and `Paint box in "red".` The statements and output wording belong to the plugin.

The statement base handler applies each captured property to its single unambiguous target. A property without a custom method stores its captured value at `key`. For custom behavior, a subclass overrides `handle(self)` and uses `self.context`, for example:

```python
class Color(Property):
    key = "color"
    target_types = (Rectangle,)

    def handle(self):
        if self.context.value not in {"red", "blue"}:
            raise ValueError("unsupported color")
        self.context.set(self.key, self.context.value)
```

Such handler checks run during materialization, **not** during static linting. A statement can also override `handle(self)` and call `self.context.apply_properties()` explicitly when it wants the default property behavior, or perform other permitted operations on its declared fields. An override does not implicitly call its base implementation.

A property class used in a pattern is a structured component that captures one value; its default value syntax is a JSON string. Its identity, value syntax, target types, and handler come from that class, not a second declaration or a decorator. A property class may be reused across statements. A direct property occurrence is allowed only once in a statement and only when there is one unambiguous definition or reference target. An explicit binding component, provisionally `Use(Color, slot="fill", target="shape")`, handles multiple targets or repeated properties. Duplicate slots, missing targets, and incompatible target types are errors. The exact spelling of this component is subject to review.

## Typed representation elements

**Proposed refinement:** a representation produces a typed element object, not a plain string. A core `Element` base would be format-neutral and open to plugin-owned subclasses; for example, the SVG package could define `Rectangle(Element)` with coordinates, dimensions, and color. The events package could define its own element classes without importing the SVG package. The classes and their instances remain owned by their plugins.

In the sketch, `Rectangle` is also the type token in `Define`, `Reference`, and `target_types`: authors pass the class itself, not the string `"rectangle"`. This identifies a semantic node type without constructing a visual rectangle during parsing. A representation constructs the `Rectangle` instance later, so semantic content and visual composition remain separate. A semantic type that does not directly represent a visual element need not inherit from `Element`.

Registration resolves type classes to stable, serializable qualified identities, such as `module:qualified_name`, and verifies that distinct classes do not claim the same identity. An optional explicit stable identity can protect a published type from module or class renames; the exact override spelling is subject to review. `Plugin.to_dict()` stores identities rather than Python class objects. Metadata-only consumers compare those identities without importing the classes. Reusing another plugin's type class in Python requires an intentional dependency on the package that exports it; independently installed SVG and event plugins do not need to import each other.

The current `Rectangle` is already a typed data class, but it is not a subclass of core `Element`: core `Element` is currently a provenance wrapper, and the SVG renderer converts plugin values to fragments via `str(value)`. This proposal changes that contract rather than describing current behavior. To avoid overloading the new base with provenance and layout bookkeeping, core would store each plugin element in a separate composition entry carrying its source spans. Reusing the public name `Element` for the base and renaming the existing wrapper is a breaking change that migration must address.

Renderers receive typed elements and are responsible for producing artifact bytes. Raw strings are not elements. An SVG renderer still needs an explicit way to serialize element types from independently installed plugins; options include a structural SVG serialization protocol or separately supplied adapters. The choice, type coverage, validation, and diagnostics need review before implementation. Neither option makes the events plugin depend on the SVG distribution, and plugin-supplied serialization remains trusted code. A typed base alone does not allow every renderer to handle every element.

## Syntax and semantic contract

A syntax declaration is an ordered tuple of literal text and typed components; it is not a Python f-string, executable parser, regular-expression fragment, or handler. `Define(slot, semantic_type)` captures a new named semantic object; `Reference(slot, accepted_types)` captures a reference; a property captures a typed value. Plugins may also define statements with no definitions or properties. More complex value types and multiline syntax are separate design work, not implied by this slice.

For the first version, keep the current single-line, bounded matching rules, JSON string escaping, ASCII identifier constraints, first output declaration, and ambiguity diagnostics. Each capture has a source span. Registration validates component names, duplicate slots, target bindings, accepted type classes and their identities, output compatibility, and malformed patterns. Identical output declarations may be shared; conflicting declarations and ambiguous input fail explicitly. Statement identity is scoped to its plugin and defaults to the class name; a stable explicit ID may be supplied when needed. No plugin must register a matching handler separately by name.

Static validation derives definitions, references, and types **only** from declarations. A generic parsed statement stores the matched contribution identity, typed captures, and spans rather than encoding a create/set category. Duplicate names, unresolved references, wrong types, and ambiguous matches remain source-linked diagnostics. `it` resolves to the most recent definition in a preceding statement; if that statement defines several names, the last definition in syntax order wins. Definitions in the same statement are not considered preceding. Named forward references remain allowed. Static validation cannot prove facts, execute custom value checks, or infer undeclared handler effects.

To make forward references usable, after validation the core allocates all explicitly declared semantic nodes with their declared names and types before invoking statement handlers. It then invokes statements in source order. Property applications and custom mutations happen at the statement's position. Thus a forward reference sees an allocated node, but may see properties not yet assigned; a later statement may overwrite an earlier assignment. Handler code cannot assume later handlers have already run. The default statement handler applies each captured property once in syntax order; a custom override controls whether and when to apply them. Core preserves declaration and mutation spans on the resulting content and links representation elements to their source nodes. A handler may use only declared definition/reference targets for core-managed node mutations; an attempt to use an undeclared or incompatible target fails at runtime. These generic facilities are not hard-coded sentence forms. More general document-level effects require a separate contract.

## Context lifetime and execution

A plugin exports contribution classes and declarative class attributes. Core validates and snapshots metadata at registration. It creates a **fresh instance of the contribution class per invocation**, binds a read-only `context` property before calling `handle()`, and never mutates the shared class or declaration to store the context. This applies independently to statements, properties, representations, and renderers. Nested calls and concurrent runs therefore get distinct handler instances and contexts. Instance state belongs to that invocation; any shared mutable state deliberately created by plugin code remains the plugin author's responsibility. A bound context expires when its handler returns and cannot be used to mutate a completed invocation.

For the initial API, contribution classes must be constructible without required arguments. Runtime constructors must not need a bound context; access before binding raises a clear error. This avoids unsafe shallow-copy assumptions about arbitrary plugin state. Parameterized contribution factories, if desired later, need an explicit contract. Existing test fakes should support binding a fresh instance to a fake context without importing private builders.

`StatementContext` exposes captured values, spans, declared targets, warnings, and explicit application of captured property handlers. `PropertyContext` exposes the captured value, target, span, and `set` operation. Representation and renderer contexts keep their current phase-specific responsibilities. No handler receives context as a method parameter. A failed validation prevents handlers from running; a failed handler stops the pipeline, reports a source-linked phase error, and does not replace the destination file. Trusted code can still perform its own side effects.

## Discovery, metadata, and migration

An installed distribution continues to expose a `Plugin` object through the existing `artifactspec.plugins` entry-point group. Discovery imports selected plugin code; it is not a sandbox. Explicit selection and autoload opt-out remain available for capabilities, validation, LSP, and rendering. Distribution metadata provides the installed plugin version; an uninstalled manually registered object reports no version.

`Plugin.to_dict()` returns an independent, versioned JSON-safe declaration of outputs, statement identities, structured syntax components, types and targets, representations, and renderers. It does not serialize handlers or contexts. A metadata catalog may consume an already supplied snapshot without imports, but such a snapshot cannot render or run handlers. The present schema and CLI capability envelope cannot express these declarations unchanged; the migration must version them and document compatibility. Metadata-only matching means handlers do not run during validation; it does **not** mean installed plugins are imported safely or not imported.

The old `Phrase` and `Property` declaration plus decorator API is a breaking migration. Migrate SVG, events, plugin tests, documentation, and wheel checks together; do not silently fall back to legacy core statement forms. Keep mixed event and SVG documents and isolated installs working. Representation dispatch remains output-filtered and deterministic: disjoint target types may share a representation name, while competing contributions for the same output, representation, and target type fail registration rather than relying on load order. Specific error-code changes, metadata version numbers, and any compatibility bridge require review before implementation.

## Inspiration and boundaries

- [Manim Scene](https://github.com/ManimCommunity/manim/blob/e80274a2586c3c2f8d72600fe873e5f7971c0c9c/manim/scene/scene.py) encourages extending classes with an overridable `construct(self)` and composing objects through a scene. Borrow the discoverable object-oriented authoring style, not its animation engine or a Manim dependency.
- [Rude custom rules](https://github.com/rude-dev/rude/blob/7182614d8780d7f90b82ac0419621baf034226ba/docs/guide/custom-rules.md) combines rule metadata and methods on subclasses, and its [plugin guide](https://github.com/rude-dev/rude/blob/7182614d8780d7f90b82ac0419621baf034226ba/docs/guide/plugin-development.md) exports rule classes for entry-point discovery. Borrow class-based contributions and explicit discovery. Unlike the Rude `check(self, node)` method, this proposal binds `self.context` per call. Do not add Rude as a runtime dependency or copy its Python AST grammar into ArtifactSpec.

## Review cases and decisions

Before implementation, review the example and these consequences:

1. A reusable property appears inside two differently worded statements without a second registration. A third statement with multiple targets must name the binding explicitly.
2. Two statements can have arbitrary plugin-defined wording, and a statement need not create or assign anything. The supported core semantic operations are still bounded by declared targets.
3. A forward named reference is valid; a later declaration's property assignments happen later in source order. `it` cannot refer to a future definition.
4. Two simultaneous invocations and a nested invocation receive different handler instances and contexts. No constructor may require context or other arguments.
5. An ambiguous pattern or wrong target type produces diagnostics without executing handlers. A plugin value check in `handle` instead fails during materialization.
6. An event-only install works without SVG; SVG plus events produces one mixed image with preserved provenance. `to_dict()` stays JSON-safe and distribution metadata supplies version.

**Review requested:** approve or revise the class-based syntax, typed element base and renderer interoperability, automatic single-target property behavior, forward-reference ordering, and no-argument constructor restriction. The syntax and names are proposals, not promises of the current package.
