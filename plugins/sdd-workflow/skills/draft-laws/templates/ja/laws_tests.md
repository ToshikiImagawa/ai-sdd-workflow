"""{{SPEC_ID}} の差分テスト: 点命題を実装に対して検証する（/draft-laws が生成）。

各テストは spec が述べる固定入力の命題（判定表 1 行）に対応する。`impl-of:` の実装を直接呼び、
実装の実際の戻り値で assert する（Bend の符号化は使わない）。
`# source:` が各テストを抽出元の spec の節に結ぶ（`draft_laws.py check --tests` が検査する）。
"""
# spec: {{SPEC_ID}}
# impl-of: {{IMPL_PATH}}

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[{{REPO_DEPTH}}]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


impl = _load("{{IMPL_MODULE}}", REPO / "{{IMPL_PATH}}")


# source: {{SPEC_ID}} §{{SECTION}} sha256:{{SECTION_HASH}}
def test_{{CANDIDATE_NAME}}():
    # {{PROPOSITION}}
    assert impl.{{FUNCTION}}({{ARGUMENTS}}) == {{EXPECTED}}
