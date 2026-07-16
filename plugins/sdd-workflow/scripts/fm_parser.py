"""fm_parser.py - Shared YAML-ish front matter parsing for AI-SDD documents.

Single source of truth for front matter detection and parsing, consumed by
sdd_index.py (indexing) and the recommend-front-matter skill (scan-documents.py).

Delimiter detection uses ``str.strip()`` so that a trailing CR (CRLF files) and
incidental surrounding whitespace on the ``---`` fence are both tolerated. The
50-line window bounds how far a closing fence is searched.
"""

import re
from typing import Any, Dict, List, Tuple

FM_MAX_LINES = 50
LIST_KEYS = {"depends-on", "tags"}


def find_front_matter_bounds(lines: List[str]) -> Tuple[bool, int]:
    """Locate the front matter block in a list of lines.

    Returns ``(has_fm, closing_index)`` where ``closing_index`` is the 0-based
    index of the closing ``---``. The first line must be ``---`` and a closing
    ``---`` must appear within the first ``FM_MAX_LINES`` lines.
    """
    if not lines or lines[0].strip() != "---":
        return (False, 0)
    for i in range(1, min(len(lines), FM_MAX_LINES)):
        if lines[i].strip() == "---":
            return (True, i)
    return (False, 0)


# Alias kept for readers that think in terms of "does this doc have FM".
has_front_matter = find_front_matter_bounds


def split_front_matter(text: str) -> Tuple[str, str]:
    """Split raw text into ``(front_matter, body)`` strings.

    Returns ``("", text)`` when no front matter block is present.
    """
    lines = text.splitlines()
    has_fm, closing = find_front_matter_bounds(lines)
    if not has_fm:
        return "", text
    fm = "\n".join(lines[1:closing])
    body = "\n".join(lines[closing + 1:])
    return fm, body


def _strip_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
        return value[1:-1]
    return value


def parse_front_matter(fm_text: str) -> Dict[str, Any]:
    """Parse the front matter text block into a dict.

    Supports scalar values and list values (inline ``[a, b]`` or block ``- item``
    forms) for the keys in :data:`LIST_KEYS`.
    """
    result: Dict[str, Any] = {}
    current_list_key = ""
    for raw in fm_text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        m_item = re.match(r"^\s+-\s+(.*)$", line)
        if m_item and current_list_key:
            result.setdefault(current_list_key, [])
            result[current_list_key].append(_strip_scalar(m_item.group(1)))
            continue
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        current_list_key = ""
        if key in LIST_KEYS:
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                items = [_strip_scalar(x) for x in inner.split(",") if x.strip()]
                result[key] = items
            elif value == "":
                current_list_key = key
                result[key] = []
            else:
                result[key] = [_strip_scalar(value)]
        else:
            result[key] = _strip_scalar(value)
    return result
