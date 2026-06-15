"""Validate TemplateDraft and exported .html.j2 content."""

from __future__ import annotations

import re

import yaml
from jinja2 import Environment

from .catalog_loader import load_keyword_index
from .models import TemplateDraft, ValidationResult

_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_FRONT_MATTER_RE = re.compile(
    r"\{#\s*---\s*\n(.*?)\n\s*---\s*#\}",
    re.DOTALL,
)


def validate_draft(draft: TemplateDraft) -> ValidationResult:
    """Validate a TemplateDraft.

    Returns a ValidationResult with errors and warnings lists.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not _ID_RE.match(draft.template_id):
        errors.append(
            "template_id must start with a lowercase letter and contain "
            "only lowercase letters, numbers, and underscores."
        )

    if not draft.sections:
        errors.append("At least one section is required.")

    seen_ids: set[str] = set()
    for section in draft.sections:
        if not _ID_RE.match(section.id):
            errors.append(
                f"Section id '{section.id}' must start with a lowercase "
                "letter and contain only lowercase letters, numbers, "
                "and underscores."
            )
        if section.id in seen_ids:
            errors.append(f"Duplicate section id: '{section.id}'.")
        seen_ids.add(section.id)

        if not section.title.strip():
            errors.append(f"Section '{section.id}' title cannot be empty.")

        if not section.data_hint:
            errors.append(
                f"Section '{section.id}' data_hint cannot be empty."
            )

    # Keyword checks
    known = load_keyword_index()
    for section in draft.sections:
        unknown = [
            kw for kw in section.data_hint if kw.lower() not in known
        ]
        if unknown:
            warnings.append(
                f"Section '{section.id}' has unknown keywords: "
                f"{', '.join(unknown)}."
            )
        matches = [
            kw for kw in section.data_hint if kw.lower() in known
        ]
        if not matches:
            errors.append(
                f"Section '{section.id}' data_hint contains no known "
                "keywords."
            )

    return ValidationResult(errors=errors, warnings=warnings)


def validate_html_j2(content: str) -> ValidationResult:
    """Validate exported .html.j2 content.

    Checks front-matter round-trip and Jinja parseability.
    """
    errors: list[str] = []
    warnings: list[str] = []

    match = _FRONT_MATTER_RE.search(content)
    if not match:
        errors.append("Front-matter block not found.")
        return ValidationResult(errors=errors, warnings=warnings)

    try:
        fm = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        errors.append(f"Front-matter YAML parse error: {exc}")
        return ValidationResult(errors=errors, warnings=warnings)

    if not isinstance(fm, dict):
        errors.append("Front-matter must be a YAML mapping.")
        return ValidationResult(errors=errors, warnings=warnings)

    if "template_id" not in fm:
        errors.append("Front-matter missing template_id.")
    if "sections" not in fm:
        errors.append("Front-matter missing sections.")

    # Jinja parse check
    try:
        Environment().parse(content)
    except Exception as exc:
        errors.append(f"Jinja parse error: {exc}")

    return ValidationResult(errors=errors, warnings=warnings)
