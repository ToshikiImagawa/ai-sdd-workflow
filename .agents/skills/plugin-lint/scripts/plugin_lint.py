#!/usr/bin/env python3
"""AI-SDD プラグインの構造品質 lint チェック。

プロンプト Markdown 内のコードブロック検出と、スキルのサポートファイル構造検証を行い、
結果を JSON で stdout に出力する。検出とレポートのみを行い、自動修正は行わない。

終了コード: 0 = 問題なし, 1 = 問題あり, 2 = 実行エラー
"""

import json
import re
import subprocess
import sys
from pathlib import Path

PLUGIN_DIR = "plugins/sdd-workflow"
SUPPORT_DIRS = ("templates", "examples", "references")
ALLOWED_SKILL_ENTRIES = {"SKILL.md", "README.md", "templates", "examples", "references", "scripts"}
SNAKE_CASE_RE = re.compile(r"^[a-z0-9_]+\.[a-z]+$")

# Claude Code の組み込みツール名（allowed-tools フロントマターで指定可能な名称）。
# 新しいツールが追加された場合はここに追記する。
KNOWN_TOOLS = {
    "Agent",
    "Artifact",
    "AskUserQuestion",
    "Bash",
    "BashOutput",
    "Edit",
    "ExitPlanMode",
    "Glob",
    "Grep",
    "KillBash",
    "MultiEdit",
    "NotebookEdit",
    "Read",
    "ScheduleWakeup",
    "SendMessage",
    "ShareOnboardingGuide",
    "Skill",
    "SlashCommand",
    "Task",
    "TaskCreate",
    "TaskGet",
    "TaskList",
    "TaskUpdate",
    "TodoWrite",
    "ToolSearch",
    "WebFetch",
    "WebSearch",
    "Workflow",
    "Write",
}


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
    )
    return Path(out.stdout.strip())


def is_excluded(path: Path) -> bool:
    return any(part in SUPPORT_DIRS for part in path.parts)


def check_code_blocks(root: Path, findings: list) -> None:
    """Check 1: プロンプト Markdown 内のコードブロック検出。"""
    targets = sorted(root.glob(f"{PLUGIN_DIR}/agents/*.md")) + sorted(
        root.glob(f"{PLUGIN_DIR}/skills/*/SKILL.md")
    )
    for file in targets:
        rel = file.relative_to(root)
        if is_excluded(rel):
            continue
        in_block = False
        for lineno, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            if not line.startswith("```"):
                continue
            if in_block:
                in_block = False
                continue
            in_block = True
            block_type = line[3:].strip() or "plain"
            findings.append(
                {
                    "check_id": "1",
                    "file": str(rel),
                    "line": lineno,
                    "message": f"コードブロック検出 (type: {block_type})",
                    "block_type": block_type,
                }
            )


def check_support_structure(root: Path, findings: list) -> None:
    """Check 2: サポートファイル構造検証（2.1〜2.5）。"""
    skills_dir = root / PLUGIN_DIR / "skills"
    skill_dirs = sorted(d for d in skills_dir.iterdir() if d.is_dir())

    for skill in skill_dirs:
        # 2.1 ディレクトリ名の正確性
        for entry in sorted(skill.iterdir()):
            if entry.name not in ALLOWED_SKILL_ENTRIES:
                findings.append(
                    {
                        "check_id": "2.1",
                        "file": str(entry.relative_to(root)),
                        "line": None,
                        "message": f"想定外のエントリ: {entry.name}"
                        f"（許可: {', '.join(sorted(ALLOWED_SKILL_ENTRIES))}）",
                        "skill": skill.name,
                    }
                )

        # 2.3 言語ディレクトリの完全性
        templates = skill / "templates"
        if templates.is_dir():
            for lang in ("en", "ja"):
                if not (templates / lang).is_dir():
                    findings.append(
                        {
                            "check_id": "2.3",
                            "file": str(templates.relative_to(root)),
                            "line": None,
                            "message": f"言語ディレクトリ {lang}/ が不足",
                            "skill": skill.name,
                        }
                    )
            # 2.4 言語間ファイルセットの一致
            en_dir, ja_dir = templates / "en", templates / "ja"
            if en_dir.is_dir() and ja_dir.is_dir():
                en_files = {p.name for p in en_dir.iterdir() if p.is_file()}
                ja_files = {p.name for p in ja_dir.iterdir() if p.is_file()}
                for name in sorted(en_files - ja_files):
                    findings.append(
                        {
                            "check_id": "2.4",
                            "file": str((ja_dir / name).relative_to(root)),
                            "line": None,
                            "message": f"{name} は en/ にのみ存在（ja/ に不足）",
                            "skill": skill.name,
                        }
                    )
                for name in sorted(ja_files - en_files):
                    findings.append(
                        {
                            "check_id": "2.4",
                            "file": str((en_dir / name).relative_to(root)),
                            "line": None,
                            "message": f"{name} は ja/ にのみ存在（en/ に不足）",
                            "skill": skill.name,
                        }
                    )

    # 2.2 / 2.5: スキル配下 + shared/references のサポートファイル
    support_files = []
    for skill in skill_dirs:
        for dirname in SUPPORT_DIRS:
            base = skill / dirname
            if base.is_dir():
                support_files += [p for p in base.rglob("*") if p.is_file()]
    shared_refs = root / PLUGIN_DIR / "shared" / "references"
    if shared_refs.is_dir():
        support_files += [p for p in shared_refs.rglob("*") if p.is_file()]

    for file in sorted(support_files):
        rel = file.relative_to(root)
        if not SNAKE_CASE_RE.match(file.name):
            findings.append(
                {
                    "check_id": "2.2",
                    "file": str(rel),
                    "line": None,
                    "message": f"ファイル名が snake_case ではありません: {file.name}",
                }
            )
        if file.suffix != ".md":
            findings.append(
                {
                    "check_id": "2.5",
                    "file": str(rel),
                    "line": None,
                    "message": f"サポートファイルの拡張子が .md ではありません: {file.suffix}",
                }
            )


def check_allowed_tools(root: Path, findings: list) -> None:
    """Check 3: スキル SKILL.md の allowed-tools フィールド検証（3.1〜3.2）。"""
    for file in sorted(root.glob(f"{PLUGIN_DIR}/skills/*/SKILL.md")):
        rel = file.relative_to(root)
        for line in file.read_text(encoding="utf-8").splitlines():
            if not line.startswith("allowed-tools:"):
                continue
            tools = [t.strip() for t in line[len("allowed-tools:") :].split(",")]
            tools = [t for t in tools if t]
            seen = set()
            for tool in tools:
                if tool not in KNOWN_TOOLS:
                    findings.append(
                        {
                            "check_id": "3.1",
                            "file": str(rel),
                            "line": None,
                            "message": f"未知のツール名です: {tool}",
                        }
                    )
                if tool in seen:
                    findings.append(
                        {
                            "check_id": "3.2",
                            "file": str(rel),
                            "line": None,
                            "message": f"ツール名が重複しています: {tool}",
                        }
                    )
                seen.add(tool)
            break


def main() -> int:
    try:
        root = repo_root()
    except subprocess.CalledProcessError as e:
        print(json.dumps({"error": f"git リポジトリを検出できません: {e.stderr}"}), file=sys.stderr)
        return 2

    findings: list = []
    check_code_blocks(root, findings)
    check_support_structure(root, findings)
    check_allowed_tools(root, findings)

    summary = {}
    for f in findings:
        summary[f["check_id"]] = summary.get(f["check_id"], 0) + 1

    print(
        json.dumps(
            {
                "total": len(findings),
                "summary_by_check": summary,
                "findings": findings,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
