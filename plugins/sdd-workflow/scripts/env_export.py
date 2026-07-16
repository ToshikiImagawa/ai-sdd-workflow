"""env_export.py - Shared CLAUDE_ENV_FILE export helper.

Hooks and skill scripts publish metadata to the shell env file named by
CLAUDE_ENV_FILE. They all follow the same rule: drop the existing
``export {PREFIX}...`` lines (so re-runs don't accumulate stale vars) and then
append the current values. This centralizes that rule and writes atomically
(tmp + replace) so a source-ing shell never sees a half-written file.
"""

import os
from pathlib import Path
from typing import List


def rewrite_exports(prefix: str, entries: List[str]) -> bool:
    """Rewrite CLAUDE_ENV_FILE, replacing existing ``export {prefix}...`` lines.

    ``entries`` are full ``export NAME="value"`` strings without trailing
    newlines. Lines not matching ``prefix`` are preserved. Returns ``False``
    when CLAUDE_ENV_FILE is unset (nothing written), ``True`` otherwise.
    """
    env_file = os.environ.get("CLAUDE_ENV_FILE")
    if not env_file:
        return False

    path = Path(env_file)
    kept = ""
    if path.exists():
        kept = "".join(
            line
            for line in path.read_text(encoding="utf-8").splitlines(keepends=True)
            if not line.startswith(f"export {prefix}")
        )
    appended = "".join(entry + "\n" for entry in entries)

    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(kept + appended, encoding="utf-8")
    tmp.replace(path)
    return True
