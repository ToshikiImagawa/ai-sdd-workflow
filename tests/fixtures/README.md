# Test Fixtures

Golden-file regression test fixtures for `session-start.py`.

## Fixture List

| #  | Name                | Description                                                |
|----|---------------------|------------------------------------------------------------|
| 01 | default-config      | Default settings (no .sdd-config.json)                     |
| 02 | custom-dirs         | Custom directory names                                     |
| 03 | custom-root         | Custom root directory                                      |
| 04 | *(gap)*             | Former `04-legacy-docs` — removed in v3.2.0                |
| 05 | *(gap)*             | Former `05-legacy-requirement-diagram` — removed in v3.2.0 |
| 06 | ja-lang             | lang: ja specified in .sdd-config.json                     |
| 07 | default-ja-lang     | --default-lang ja (no config)                              |
| 08 | invalid-json        | Invalid JSON → falls back to defaults                      |
| 09 | empty-string-values | All fields empty string → falls back to defaults           |

## Fixture Structure

```
{fixture-name}/
├── .sdd-config.json   # (optional) Test config file
├── default-lang       # (optional) --default-lang argument value (default: en)
├── setup.sh           # (optional) Pre-test environment setup script
└── expected_env.txt   # (required) Expected SDD_* environment variable output
```
