"""Compile bounded declarative statement templates without executing plugins."""

import re
from string import Formatter


class TemplateError(ValueError):
    """A plugin's statement template is invalid."""


_FIELDS = {
    "name": r"[A-Za-z][A-Za-z0-9_-]*",
    "reference": r"[A-Za-z][A-Za-z0-9_-]*",
    "value": r'"(?:[^"\\\r\n]|\\.)*"',
}


def compile_template(template: str, fields: set[str]) -> re.Pattern[str]:
    """Compile literal text and named typed placeholders to a full-match pattern."""
    if not isinstance(template, str) or not template or len(template) > 1024:
        raise TemplateError("template must be nonempty and at most 1024 characters")
    if template != template.strip() or "\n" in template or "\r" in template:
        raise TemplateError("template must be a single trimmed line")
    parts: list[str] = []
    seen: set[str] = set()
    previous_field = False
    try:
        fragments = list(Formatter().parse(template))
    except ValueError as error:
        raise TemplateError(f"invalid template: {error}") from error
    for literal, field, spec, conversion in fragments:
        parts.append(re.escape(literal))
        if field is None:
            previous_field = False
            continue
        if field not in fields or field in seen or spec or conversion:
            raise TemplateError(f"invalid or repeated placeholder {field!r}")
        if previous_field and not literal:
            raise TemplateError("placeholders must be separated by literal text")
        parts.append(f"(?P<{field}>{_FIELDS[field]})")
        seen.add(field)
        previous_field = True
    if seen != fields:
        raise TemplateError(f"template requires placeholders {sorted(fields)!r}")
    return re.compile("".join(parts))
