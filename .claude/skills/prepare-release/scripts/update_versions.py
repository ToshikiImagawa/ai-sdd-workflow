#!/usr/bin/env python3
"""リリース準備: バージョンマニフェストの一括更新。

semver 形式を検証し、marketplace.json と plugin.json の version フィールドを
新バージョンに更新する。結果を JSON で stdout に出力する。

使い方: update_versions.py <version>   （例: 3.4.0, 4.0.0-alpha）

終了コード: 0 = 成功, 1 = 引数エラー, 2 = 実行エラー
"""

import json
import re
import subprocess
import sys
from pathlib import Path

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$")


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
    )
    return Path(out.stdout.strip())


def main() -> int:
    if len(sys.argv) != 2:
        print("使い方: update_versions.py <version>  （例: 3.4.0）", file=sys.stderr)
        return 1
    version = sys.argv[1]
    if not SEMVER_RE.match(version):
        print(
            f"エラー: '{version}' はセマンティックバージョニング形式"
            "（X.Y.Z または X.Y.Z-prerelease）ではありません",
            file=sys.stderr,
        )
        return 1

    try:
        root = repo_root()
    except subprocess.CalledProcessError as e:
        print(f"git リポジトリを検出できません: {e.stderr}", file=sys.stderr)
        return 2

    updated = []

    marketplace_path = root / ".claude-plugin" / "marketplace.json"
    marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    updated.append(
        {
            "file": ".claude-plugin/marketplace.json",
            "field": "metadata.version",
            "old": marketplace["metadata"]["version"],
            "new": version,
        }
    )
    marketplace["metadata"]["version"] = version
    for plugin in marketplace.get("plugins", []):
        updated.append(
            {
                "file": ".claude-plugin/marketplace.json",
                "field": f"plugins[{plugin['name']}].version",
                "old": plugin.get("version"),
                "new": version,
            }
        )
        plugin["version"] = version
    marketplace_path.write_text(
        json.dumps(marketplace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    for plugin_json in sorted(root.glob("plugins/*/.claude-plugin/plugin.json")):
        manifest = json.loads(plugin_json.read_text(encoding="utf-8"))
        updated.append(
            {
                "file": str(plugin_json.relative_to(root)),
                "field": "version",
                "old": manifest.get("version"),
                "new": version,
            }
        )
        manifest["version"] = version
        plugin_json.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    print(json.dumps({"version": version, "updated": updated}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
