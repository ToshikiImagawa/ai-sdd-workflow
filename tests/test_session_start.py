"""session-start.py のユニットテスト（pytest）。

ゴールデンファイル回帰テスト（scripts/test-session-start.sh）を補完し、
関数単位のエッジケース（不正JSON、未知のlang値、設定ファイル欠如等）を検証する。
"""

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "plugins" / "sdd-workflow" / "scripts" / "session-start.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("session_start", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ss = _load_module()


class TestLoadOrCreateConfig:
    def test_missing_file_creates_default(self, tmp_path, capsys):
        config_path = tmp_path / ".sdd-config.json"
        result = ss.load_or_create_config(str(config_path), "en")

        assert config_path.is_file()
        assert result["root"] == ".sdd"
        assert result["lang"] == "en"
        assert result["directories"] == {
            "requirement": "requirement",
            "specification": "specification",
            "task": "task",
        }
        # 生成されたファイル自体も同内容であること
        assert json.loads(config_path.read_text(encoding="utf-8")) == result
        assert "auto-generated" in capsys.readouterr().out

    def test_missing_file_respects_default_lang(self, tmp_path):
        config_path = tmp_path / ".sdd-config.json"
        result = ss.load_or_create_config(str(config_path), "ja")
        assert result["lang"] == "ja"

    def test_missing_parent_directory_is_created(self, tmp_path):
        config_path = tmp_path / "nested" / "dir" / ".sdd-config.json"
        result = ss.load_or_create_config(str(config_path), "en")
        assert config_path.is_file()
        assert result["lang"] == "en"

    def test_invalid_json_returns_empty_dict_with_warning(self, tmp_path, capsys):
        config_path = tmp_path / ".sdd-config.json"
        config_path.write_text("{ invalid json !!!", encoding="utf-8")

        result = ss.load_or_create_config(str(config_path), "en")

        assert result == {}
        assert "invalid JSON" in capsys.readouterr().err
        # 不正なファイルは上書きされないこと
        assert config_path.read_text(encoding="utf-8") == "{ invalid json !!!"

    def test_valid_json_is_returned_as_is(self, tmp_path):
        config_path = tmp_path / ".sdd-config.json"
        config = {"root": "docs/sdd", "lang": "ja"}
        config_path.write_text(json.dumps(config), encoding="utf-8")

        assert ss.load_or_create_config(str(config_path), "en") == config


class TestBuildSddConfig:
    def test_empty_raw_uses_defaults(self):
        cfg = ss.build_sdd_config({}, "en")
        assert cfg.root == ".sdd"
        assert cfg.lang == "en"
        assert cfg.requirement_dir == "requirement"
        assert cfg.specification_dir == "specification"
        assert cfg.task_dir == "task"

    def test_empty_raw_uses_default_lang(self):
        assert ss.build_sdd_config({}, "ja").lang == "ja"

    def test_raw_values_override_defaults(self):
        raw = {
            "root": "docs/sdd",
            "lang": "ja",
            "directories": {
                "requirement": "req",
                "specification": "spec",
                "task": "tasks",
            },
        }
        cfg = ss.build_sdd_config(raw, "en")
        assert cfg.root == "docs/sdd"
        assert cfg.lang == "ja"
        assert cfg.requirement_dir == "req"
        assert cfg.specification_dir == "spec"
        assert cfg.task_dir == "tasks"

    def test_unknown_lang_value_is_passed_through(self):
        # 未知の lang 値（例: "jp"、#53参照）は検証されずそのまま採用される
        # （現状仕様の回帰検知。バリデーション導入時はこのテストを更新すること）
        cfg = ss.build_sdd_config({"lang": "jp"}, "en")
        assert cfg.lang == "jp"

    def test_empty_string_values_fall_back_to_defaults(self):
        raw = {
            "root": "",
            "lang": "",
            "directories": {"requirement": "", "specification": "", "task": ""},
        }
        cfg = ss.build_sdd_config(raw, "en")
        assert cfg.root == ".sdd"
        assert cfg.lang == "en"
        assert cfg.requirement_dir == "requirement"
        assert cfg.specification_dir == "specification"
        assert cfg.task_dir == "task"


class TestEnsureSddDirectory:
    def test_creates_directory_when_missing(self, tmp_path, capsys):
        sdd_dir = tmp_path / ".sdd"
        ss.ensure_sdd_directory(str(sdd_dir), ".sdd")
        assert sdd_dir.is_dir()
        assert ".sdd/ directory created" in capsys.readouterr().out

    def test_no_message_when_directory_exists(self, tmp_path, capsys):
        sdd_dir = tmp_path / ".sdd"
        sdd_dir.mkdir()
        ss.ensure_sdd_directory(str(sdd_dir), ".sdd")
        assert capsys.readouterr().out == ""


class TestGetPluginVersion:
    def _make_plugin(self, tmp_path, content):
        plugin_dir = tmp_path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(content, encoding="utf-8")
        return str(tmp_path)

    def test_returns_version_field(self, tmp_path):
        root = self._make_plugin(tmp_path, json.dumps({"version": "1.2.3"}))
        assert ss.get_plugin_version(root) == "1.2.3"

    def test_missing_plugin_json_returns_empty(self, tmp_path):
        assert ss.get_plugin_version(str(tmp_path)) == ""

    def test_invalid_json_returns_empty(self, tmp_path):
        root = self._make_plugin(tmp_path, "not json")
        assert ss.get_plugin_version(root) == ""

    def test_missing_version_field_returns_empty(self, tmp_path):
        root = self._make_plugin(tmp_path, json.dumps({"name": "x"}))
        assert ss.get_plugin_version(root) == ""


class TestSyncPrinciplesFile:
    def _make_source(self, plugin_root, version_line='version: "0.0.0"'):
        source = plugin_root / "AI-SDD-PRINCIPLES.source.md"
        source.write_text(f"---\n{version_line}\n---\n# Test\n", encoding="utf-8")
        return source

    def test_version_is_rewritten(self, tmp_path, capsys):
        plugin_root = tmp_path / "plugin"
        sdd_dir = tmp_path / ".sdd"
        plugin_root.mkdir()
        sdd_dir.mkdir()
        self._make_source(plugin_root)

        ss.sync_principles_file(str(plugin_root), str(sdd_dir), "3.3.0")

        target = sdd_dir / "AI-SDD-PRINCIPLES.md"
        assert 'version: "3.3.0"' in target.read_text(encoding="utf-8")
        assert "updated to v3.3.0" in capsys.readouterr().out

    def test_missing_source_skips_with_warning(self, tmp_path, capsys):
        sdd_dir = tmp_path / ".sdd"
        sdd_dir.mkdir()
        ss.sync_principles_file(str(tmp_path), str(sdd_dir), "3.3.0")
        assert not (sdd_dir / "AI-SDD-PRINCIPLES.md").exists()
        assert "Source file not found" in capsys.readouterr().err

    def test_empty_version_copies_source_as_is(self, tmp_path, capsys):
        plugin_root = tmp_path / "plugin"
        sdd_dir = tmp_path / ".sdd"
        plugin_root.mkdir()
        sdd_dir.mkdir()
        self._make_source(plugin_root)

        ss.sync_principles_file(str(plugin_root), str(sdd_dir), "")

        target = sdd_dir / "AI-SDD-PRINCIPLES.md"
        assert 'version: "0.0.0"' in target.read_text(encoding="utf-8")
        assert "version unknown" in capsys.readouterr().out


class TestWriteEnvVars:
    def test_no_env_file_env_var_does_nothing(self, monkeypatch):
        monkeypatch.delenv("CLAUDE_ENV_FILE", raising=False)
        ss.write_env_vars(ss.SddConfig())  # 例外が出ないこと

    def test_writes_all_sdd_exports(self, tmp_path, monkeypatch):
        env_file = tmp_path / "env"
        monkeypatch.setenv("CLAUDE_ENV_FILE", str(env_file))

        ss.write_env_vars(ss.SddConfig(root="docs/sdd", lang="ja", task_dir="tasks"))

        content = env_file.read_text(encoding="utf-8")
        assert 'export SDD_ROOT="docs/sdd"' in content
        assert 'export SDD_LANG="ja"' in content
        assert 'export SDD_TASK_DIR="tasks"' in content
        assert 'export SDD_TASK_PATH="docs/sdd/tasks"' in content
        assert 'export SDD_REQUIREMENT_PATH="docs/sdd/requirement"' in content
        assert 'export SDD_SPECIFICATION_PATH="docs/sdd/specification"' in content

    def test_existing_sdd_lines_are_replaced(self, tmp_path, monkeypatch):
        env_file = tmp_path / "env"
        env_file.write_text(
            'export OTHER_VAR="keep"\nexport SDD_LANG="old"\n', encoding="utf-8"
        )
        monkeypatch.setenv("CLAUDE_ENV_FILE", str(env_file))

        ss.write_env_vars(ss.SddConfig(lang="ja"))

        content = env_file.read_text(encoding="utf-8")
        assert 'export OTHER_VAR="keep"' in content
        assert 'export SDD_LANG="ja"' in content
        assert 'export SDD_LANG="old"' not in content


class TestCompareMajorMinor:
    @pytest.mark.parametrize(
        ("plugin", "project", "expected"),
        [
            ("3.3.0", "3.3.0", True),
            ("3.3.0", "3.4.0", True),
            ("3.3.0", "4.0.0", True),
            ("3.3.0", "3.2.0", False),
            ("3.3.0", "2.9.9", False),
            # patch バージョンは比較対象外
            ("3.3.9", "3.3.0", True),
            # パース不能な値は True（警告を出さない）
            ("invalid", "3.3.0", True),
            ("3.3.0", "invalid", True),
        ],
    )
    def test_comparison(self, plugin, project, expected):
        assert ss.compare_major_minor(plugin, project) is expected


class TestCheckClaudeMd:
    def _setup(self, tmp_path):
        sdd_dir = tmp_path / ".sdd"
        sdd_dir.mkdir()
        return str(tmp_path), str(sdd_dir), sdd_dir / "UPDATE_REQUIRED.md"

    def test_no_sdd_dir_does_nothing(self, tmp_path):
        ss.check_claude_md(str(tmp_path), str(tmp_path / ".sdd"), "3.3.0")
        assert not (tmp_path / ".sdd").exists()

    def test_missing_claude_md_creates_warning(self, tmp_path, capsys):
        project_root, sdd_dir, warning_file = self._setup(tmp_path)
        ss.check_claude_md(project_root, sdd_dir, "3.3.0")
        assert "CLAUDE.md not found" in warning_file.read_text(encoding="utf-8")
        assert "update required" in capsys.readouterr().err

    def test_no_version_section_creates_warning(self, tmp_path):
        project_root, sdd_dir, warning_file = self._setup(tmp_path)
        (tmp_path / "CLAUDE.md").write_text("# No AI-SDD section\n", encoding="utf-8")
        ss.check_claude_md(project_root, sdd_dir, "3.3.0")
        assert "no AI-SDD section" in warning_file.read_text(encoding="utf-8")

    def test_outdated_version_creates_warning(self, tmp_path):
        project_root, sdd_dir, warning_file = self._setup(tmp_path)
        (tmp_path / "CLAUDE.md").write_text(
            "## AI-SDD Instructions (v1.0.0)\n", encoding="utf-8"
        )
        ss.check_claude_md(project_root, sdd_dir, "3.3.0")
        content = warning_file.read_text(encoding="utf-8")
        assert "outdated" in content
        assert "v3.3.0" in content

    def test_up_to_date_removes_existing_warning(self, tmp_path):
        project_root, sdd_dir, warning_file = self._setup(tmp_path)
        warning_file.write_text("old warning", encoding="utf-8")
        (tmp_path / "CLAUDE.md").write_text(
            "## AI-SDD Instructions (v3.3.0)\n", encoding="utf-8"
        )
        ss.check_claude_md(project_root, sdd_dir, "3.3.0")
        assert not warning_file.exists()


class TestGetRoots:
    def test_get_plugin_root_exits_when_unset(self, monkeypatch, capsys):
        monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)
        with pytest.raises(SystemExit) as exc_info:
            ss.get_plugin_root()
        assert exc_info.value.code == 1
        assert "CLAUDE_PLUGIN_ROOT is not set" in capsys.readouterr().err

    def test_get_plugin_root_returns_env_value(self, monkeypatch):
        monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", "/path/to/plugin")
        assert ss.get_plugin_root() == "/path/to/plugin"

    def test_get_project_root_prefers_env_value(self, monkeypatch):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/path/to/project")
        assert ss.get_project_root() == "/path/to/project"

    def test_get_project_root_falls_back_to_cwd_without_git(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
        monkeypatch.setenv("PATH", "")  # git を見つけられなくする
        monkeypatch.chdir(tmp_path)
        assert ss.get_project_root() == str(tmp_path)


class TestMainIntegration:
    """main() を経由したエンドツーエンドの動作確認。"""

    def _setup_env(self, tmp_path, monkeypatch):
        plugin_root = tmp_path / "plugin"
        project_root = tmp_path / "project"
        env_file = tmp_path / "env"
        (plugin_root / ".claude-plugin").mkdir(parents=True)
        (plugin_root / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"version": "3.3.0"}), encoding="utf-8"
        )
        (plugin_root / "AI-SDD-PRINCIPLES.source.md").write_text(
            '---\nversion: "0.0.0"\n---\n# Test\n', encoding="utf-8"
        )
        project_root.mkdir()
        (project_root / "CLAUDE.md").write_text(
            "## AI-SDD Instructions (v3.3.0)\n", encoding="utf-8"
        )
        env_file.touch()
        monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(plugin_root))
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project_root))
        monkeypatch.setenv("CLAUDE_ENV_FILE", str(env_file))
        return project_root, env_file

    def test_main_with_no_config_generates_defaults(self, tmp_path, monkeypatch):
        project_root, env_file = self._setup_env(tmp_path, monkeypatch)
        monkeypatch.setattr(sys, "argv", ["session-start.py"])

        ss.main()

        assert (project_root / ".sdd-config.json").is_file()
        assert (project_root / ".sdd").is_dir()
        assert (project_root / ".sdd" / "AI-SDD-PRINCIPLES.md").is_file()
        assert 'export SDD_LANG="en"' in env_file.read_text(encoding="utf-8")

    def test_main_with_invalid_config_uses_defaults(self, tmp_path, monkeypatch):
        project_root, env_file = self._setup_env(tmp_path, monkeypatch)
        (project_root / ".sdd-config.json").write_text("broken{", encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["session-start.py", "--default-lang", "ja"])

        ss.main()

        content = env_file.read_text(encoding="utf-8")
        assert 'export SDD_LANG="ja"' in content
        assert 'export SDD_ROOT=".sdd"' in content

    def test_main_with_unknown_lang_passes_through(self, tmp_path, monkeypatch):
        project_root, env_file = self._setup_env(tmp_path, monkeypatch)
        (project_root / ".sdd-config.json").write_text(
            json.dumps({"lang": "jp"}), encoding="utf-8"
        )
        monkeypatch.setattr(sys, "argv", ["session-start.py"])

        ss.main()

        assert 'export SDD_LANG="jp"' in env_file.read_text(encoding="utf-8")
