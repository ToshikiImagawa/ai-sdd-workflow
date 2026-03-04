# Security Policy

## Supported Versions

We take security seriously and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < latest| :x:                |

**Recommendation**: Always use the latest version to ensure you have the latest security patches.

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

### How to Report

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Send an email to the repository maintainer with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

3. You can also use GitHub's private vulnerability reporting feature:
   - Go to the "Security" tab
   - Click "Report a vulnerability"
   - Fill in the details

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
- **Assessment**: We will assess the vulnerability and determine severity
- **Fix timeline**:
  - Critical vulnerabilities: Patched within 7 days
  - High severity: Patched within 14 days
  - Medium/Low severity: Patched in next release
- **Credit**: We will credit you in the release notes (unless you prefer to remain anonymous)

## Security Best Practices for Contributors

### 1. Input Validation

**Always validate external input before using it in commands or file operations.**

Example from `session-start.py`:

```python
def validate_repository_url(url: str) -> bool:
    """Validate that repository URL is a safe GitHub HTTPS URL."""
    pattern = r'^https://github\.com/[\w-]+/[\w\.-]+\.git$'
    if not re.match(pattern, url):
        return False

    # Reject URLs with shell metacharacters
    dangerous_chars = [';', '|', '&', '$', '`', '(', ')', '<', '>', '\n', '\r', ' ']
    if any(char in url for char in dangerous_chars):
        return False

    return True
```

**Key principles**:
- Use allowlists (known good values) rather than denylists (known bad values)
- Validate data type, format, and range
- Reject unexpected input rather than trying to sanitize it

### 2. Command Injection Prevention

**Never construct shell commands from user input without validation.**

❌ **Bad**:
```python
# VULNERABLE: User can inject arbitrary commands
repo = config.get("repository")  # User-controlled
command = f"uvx --from git+{repo} sdd-cli"
os.system(command)
```

✅ **Good**:
```python
# SAFE: Validate before using
repo = config.get("repository")
if not validate_repository_url(repo):
    raise ValueError("Invalid repository URL")
command = f"uvx --from git+{repo} sdd-cli"
subprocess.run(command, shell=True, check=True)
```

**Even better** (avoid shell=True):
```python
# BEST: Use argument list instead of shell string
subprocess.run(["uvx", "--from", f"git+{repo}", "sdd-cli"], check=True)
```

### 3. Path Traversal Prevention

**Validate file paths to prevent directory traversal attacks.**

❌ **Bad**:
```python
# VULNERABLE: User can access arbitrary files
file_path = user_input  # e.g., "../../../etc/passwd"
with open(file_path, 'r') as f:
    data = f.read()
```

✅ **Good**:
```python
# SAFE: Validate path is within allowed directory
import os
allowed_dir = "/path/to/sdd/docs"
file_path = os.path.join(allowed_dir, user_input)
real_path = os.path.realpath(file_path)

if not real_path.startswith(os.path.realpath(allowed_dir)):
    raise ValueError("Invalid path: directory traversal detected")

with open(real_path, 'r') as f:
    data = f.read()
```

### 4. Secure Configuration Loading

**Configuration files can be attack vectors. Validate thoroughly.**

```python
def load_config(config_path: str) -> dict:
    """Load and validate configuration file."""
    if not os.path.isfile(config_path):
        return {}

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError:
        # Invalid JSON - do not proceed
        return {}

    # Validate configuration schema
    if not isinstance(config, dict):
        return {}

    # Validate specific fields
    if "cli" in config:
        if not isinstance(config["cli"], dict):
            del config["cli"]
        elif "repository" in config["cli"]:
            if not validate_repository_url(config["cli"]["repository"]):
                # Remove invalid repository URL
                del config["cli"]["repository"]

    return config
```

### 5. Security Testing Requirements

**All security-critical code changes MUST include tests.**

When modifying security-sensitive code:

1. **Add unit tests** in `tests/test_security_session_start.py`
2. **Add integration tests** in `tests/fixtures/` if needed
3. **Run security test suite** before committing:
   ```bash
   bash scripts/test-security.sh
   ```
4. **Ensure CI passes** - security tests run automatically on PRs

### 6. Code Review Checklist

Before merging security-related PRs, verify:

- [ ] Input validation is present for all external data
- [ ] No shell metacharacters are allowed in user input
- [ ] File paths are validated against traversal attacks
- [ ] Secrets are not hardcoded or logged
- [ ] Error messages do not leak sensitive information
- [ ] Security tests are included and passing
- [ ] Dependencies are up to date and have no known vulnerabilities

## Security Testing

### Automated Security Tests

This repository includes comprehensive security regression tests:

1. **Python unit tests** (`tests/test_security_session_start.py`):
   - 19 security-focused test cases
   - Command injection attack detection
   - URL validation testing
   - Regression detection (ensures security functions exist)

2. **Integration tests** (`tests/fixtures/14-cli-invalid-url`, `tests/fixtures/15-cli-command-substitution`):
   - End-to-end security validation
   - Malicious configuration rejection

3. **CI/CD integration** (`.github/workflows/ci.yml`):
   - Runs on every PR and push to main
   - Blocks merge if security tests fail

### Running Security Tests Locally

```bash
# Run all security tests
bash scripts/test-security.sh

# Run quick security checks only (recommended for pre-commit)
bash scripts/test-security.sh --quick

# Run Python unit tests only
python3 -m pytest tests/test_security_session_start.py -v
```

### Adding New Security Tests

When adding new attack vectors or security controls:

1. Add test cases to `tests/test_security_session_start.py`
2. Follow naming convention: `test_<attack_type>_<specific_case>`
3. Include clear docstrings explaining the attack vector
4. Mark critical tests with `SECURITY:` prefix in docstring

Example:
```python
def test_command_injection_semicolon(self):
    """SECURITY: Test rejection of semicolon command injection."""
    malicious_urls = [
        "https://example.com/fake.git; rm -rf ~",
    ]
    for url in malicious_urls:
        assert validate_repository_url(url) is False, \
            f"SECURITY FAILURE: Command injection not blocked: {url}"
```

## Known Security Measures

This project implements the following security controls:

### 1. Repository URL Validation (`session-start.py`)

- **Purpose**: Prevent command injection via malicious repository URLs
- **Implementation**: Strict allowlist of GitHub HTTPS URLs only
- **Protected against**:
  - Command injection (`;`, `|`, `&&`)
  - Command substitution (`$()`, `` ` ``)
  - Path traversal (`../`)
  - Non-HTTPS protocols
  - Non-GitHub domains

### 2. Configuration File Validation

- **Purpose**: Prevent malicious configuration from compromising the system
- **Implementation**: JSON schema validation, type checking, field validation
- **Protected against**:
  - JSON injection attacks
  - Type confusion
  - Missing or malformed fields

### 3. Path Validation (Planned)

- **Purpose**: Prevent directory traversal attacks in document operations
- **Status**: To be implemented in future versions
- **Target**: All file read/write operations in skills

## Security Changelog

### [Unreleased]

- Added comprehensive security test suite (19 test cases)
- Added security regression detection tests
- Integrated security tests into CI/CD pipeline

### [2024-03-04] - Security Fix

- **Fixed**: Command injection vulnerability in `session-start.py` (CVE-pending)
- **Impact**: High - allowed arbitrary command execution via malicious `.sdd-config.json`
- **Mitigation**: Added `validate_repository_url()` with strict URL validation
- **Affected versions**: All versions prior to this fix
- **Credit**: Internal security review

## Dependencies and Supply Chain Security

- All dependencies are specified in `requirements.txt` (if applicable)
- Regular dependency updates via Dependabot (GitHub)
- No dependencies with known critical vulnerabilities

### Checking for Vulnerable Dependencies

```bash
# Python dependencies (if using pip)
pip install safety
safety check

# Shell scripts
shellcheck -S warning scripts/*.sh
```

## Incident Response

If a security incident occurs:

1. **Immediate action**: Create private security advisory on GitHub
2. **Assessment**: Evaluate scope and impact
3. **Patch development**: Develop and test fix in private fork
4. **Coordinated disclosure**: Notify affected users via GitHub Security Advisory
5. **Public disclosure**: Release patch and publish CVE details

## Contact

For security concerns, contact:
- GitHub Security Advisory: [Report a vulnerability](https://github.com/ToshikiImagawa/ai-sdd-workflow/security/advisories/new)
- Maintainer: See repository maintainer contact info

## Security Review Schedule

This security policy is reviewed quarterly to ensure it remains current and effective.

- **Last reviewed**: 2024-03-04
- **Next review**: 2024-06-04
- **Review frequency**: Quarterly (every 3 months)
- **Reviewer**: Project maintainers

**Review checklist**:
- [ ] Update supported versions if needed
- [ ] Review and update security best practices
- [ ] Check for new attack vectors or vulnerabilities
- [ ] Update security test coverage
- [ ] Review incident response procedures
- [ ] Update dependency security checks

---

**Last updated**: 2024-03-04
**Security policy version**: 1.0
