#!/usr/bin/env bash
# Fixture: row 16: document without front matter
set -euo pipefail
mkdir -p .sdd/specification
cat > .sdd-config.json <<'EOF'
{ "root": ".sdd", "lang": "en", "index": false }
EOF
cat > .sdd/specification/notes_spec.md <<'EOF'
# Notes spec

No front matter here.
EOF
