#!/usr/bin/env python3
"""Security regression tests for session-start.py

Tests validate_repository_url() function to prevent command injection attacks.
These tests serve as security regression tests - any failure indicates a potential
security vulnerability has been introduced.

Run with: python3 -m pytest tests/test_security_session_start.py -v
"""

import sys
import os
from pathlib import Path
import importlib.util

# Load session-start.py as a module
script_path = Path(__file__).parent.parent / "plugins" / "sdd-workflow" / "scripts" / "session-start.py"

# Import the script as a module
spec = importlib.util.spec_from_file_location("session_start", script_path)
if spec is None or spec.loader is None:
    raise ImportError("SECURITY REGRESSION: Could not load session-start.py")

session_start = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_start)

# Import the function under test
# Note: This will fail if validate_repository_url is removed (regression detection)
try:
    validate_repository_url = session_start.validate_repository_url
except AttributeError as e:
    raise ImportError(
        "SECURITY REGRESSION: validate_repository_url function not found. "
        "This function is critical for preventing command injection attacks."
    ) from e


class TestValidRepositoryURLSecurity:
    """Security tests for repository URL validation.

    CRITICAL: These tests protect against command injection attacks.
    DO NOT modify or remove without security review.
    """

    def test_valid_default_url(self):
        """Test that the default repository URL is accepted."""
        url = "https://github.com/ToshikiImagawa/ai-sdd-workflow-cli.git"
        assert validate_repository_url(url) is True, "Default repository URL should be valid"

    def test_valid_github_urls(self):
        """Test that legitimate GitHub URLs are accepted."""
        valid_urls = [
            "https://github.com/user/repo.git",
            "https://github.com/user-name/repo-name.git",
            "https://github.com/user_name/repo_name.git",
            "https://github.com/user/repo.name.git",
            "https://github.com/user123/repo456.git",
            "https://github.com/user-123/repo_456.git",
        ]
        for url in valid_urls:
            assert validate_repository_url(url) is True, f"Valid URL should be accepted: {url}"

    def test_command_injection_semicolon(self):
        """SECURITY: Test rejection of semicolon command injection."""
        malicious_urls = [
            "https://example.com/fake.git; rm -rf ~",
            "https://github.com/user/repo.git; curl http://evil.com",
            "https://github.com/user/repo.git;echo pwned",
        ]
        for url in malicious_urls:
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: Command injection not blocked: {url}"

    def test_command_injection_ampersand(self):
        """SECURITY: Test rejection of ampersand command chaining."""
        malicious_urls = [
            "https://github.com/user/repo.git && rm -rf /",
            "https://github.com/user/repo.git & curl evil.com",
            "https://github.com/user/repo.git || echo fail",
        ]
        for url in malicious_urls:
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: Command chaining not blocked: {url}"

    def test_command_substitution_dollar_parens(self):
        """SECURITY: Test rejection of $(command) substitution."""
        malicious_urls = [
            "https://github.com/$(curl http://evil.com).git",
            "https://github.com/user/$(rm -rf ~).git",
            "https://github.com/$(whoami)/repo.git",
        ]
        for url in malicious_urls:
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: Command substitution not blocked: {url}"

    def test_command_substitution_backticks(self):
        """SECURITY: Test rejection of `command` substitution."""
        malicious_urls = [
            "https://github.com/`curl evil.com`.git",
            "https://github.com/user/`rm -rf ~`.git",
        ]
        for url in malicious_urls:
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: Backtick substitution not blocked: {url}"

    def test_pipeline_injection(self):
        """SECURITY: Test rejection of pipeline (|) injection."""
        malicious_urls = [
            "https://github.com/user/repo.git | bash",
            "https://github.com/user/repo.git|curl evil.com",
        ]
        for url in malicious_urls:
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: Pipeline injection not blocked: {url}"

    def test_redirect_injection(self):
        """SECURITY: Test rejection of redirect (<, >) injection."""
        malicious_urls = [
            "https://github.com/user/repo.git > /etc/passwd",
            "https://github.com/user/repo.git < /etc/shadow",
            "https://github.com/user/repo.git >> /var/log/evil.log",
        ]
        for url in malicious_urls:
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: Redirect injection not blocked: {url}"

    def test_newline_injection(self):
        """SECURITY: Test rejection of newline character injection."""
        malicious_urls = [
            "https://github.com/user/repo.git\nrm -rf ~",
            "https://github.com/user/repo.git\r\ncurl evil.com",
            "https://github.com/user/repo.git%0Aecho pwned",
        ]
        for url in malicious_urls:
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: Newline injection not blocked: {url}"

    def test_space_injection(self):
        """SECURITY: Test rejection of space characters."""
        malicious_urls = [
            "https://github.com/user /repo.git",
            "https://github.com/user/repo .git",
            "https://github.com/user repo/fake.git",
        ]
        for url in malicious_urls:
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: Space injection not blocked: {url}"

    def test_non_https_protocol(self):
        """SECURITY: Test rejection of non-HTTPS protocols."""
        malicious_urls = [
            "http://github.com/user/repo.git",
            "ftp://github.com/user/repo.git",
            "file:///etc/passwd",
            "git://github.com/user/repo.git",
        ]
        for url in malicious_urls:
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: Non-HTTPS protocol not blocked: {url}"

    def test_non_github_domain(self):
        """SECURITY: Test rejection of non-GitHub domains."""
        malicious_urls = [
            "https://evil.com/user/repo.git",
            "https://github.evil.com/user/repo.git",
            "https://githubcom.evil.com/user/repo.git",
            "https://github.com.evil.com/user/repo.git",
        ]
        for url in malicious_urls:
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: Non-GitHub domain not blocked: {url}"

    def test_missing_git_extension(self):
        """SECURITY: Test rejection of URLs without .git extension."""
        invalid_urls = [
            "https://github.com/user/repo",
            "https://github.com/user/repo.txt",
            "https://github.com/user/repo.git.evil",
        ]
        for url in invalid_urls:
            assert validate_repository_url(url) is False, \
                f"Invalid URL format should be rejected: {url}"

    def test_path_traversal(self):
        """SECURITY: Test rejection of path traversal attempts."""
        malicious_urls = [
            "https://github.com/../../../etc/passwd.git",
            "https://github.com/user/../../repo.git",
            "https://github.com/user/repo/../../../.git",
        ]
        for url in malicious_urls:
            # Note: Our regex pattern doesn't explicitly allow ../ so these should fail
            # This test documents the expected behavior
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: Path traversal not blocked: {url}"

    def test_url_encoded_attacks(self):
        """SECURITY: Test rejection of URL-encoded attack payloads."""
        malicious_urls = [
            "https://github.com/user%2Frepo.git",  # %2F = /
            "https://github.com/user/repo%00.git",  # %00 = null byte
            "https://github.com/user/repo%20.git",  # %20 = space
        ]
        for url in malicious_urls:
            assert validate_repository_url(url) is False, \
                f"SECURITY FAILURE: URL-encoded attack not blocked: {url}"

    def test_empty_and_malformed_urls(self):
        """Test rejection of empty or malformed URLs."""
        invalid_urls = [
            "",
            " ",
            "not-a-url",
            "https://",
            "github.com/user/repo.git",
            "//github.com/user/repo.git",
        ]
        for url in invalid_urls:
            assert validate_repository_url(url) is False, \
                f"Malformed URL should be rejected: {url}"


class TestSecurityRegressionDetection:
    """Tests to detect if security validation is bypassed or removed."""

    def test_function_exists(self):
        """Verify that validate_repository_url function exists."""
        assert callable(validate_repository_url), \
            "SECURITY REGRESSION: validate_repository_url function is missing or not callable"

    def test_function_is_called_in_detect_cli(self):
        """Verify that detect_cli uses validate_repository_url (static check)."""
        # Read session_start.py source code
        session_start_path = Path(__file__).parent.parent / "plugins" / "sdd-workflow" / "scripts" / "session-start.py"

        with open(session_start_path, 'r') as f:
            source_code = f.read()

        # Check that validate_repository_url is called within detect_cli function
        assert "validate_repository_url(cli_cfg.repository)" in source_code, \
            "SECURITY REGRESSION: validate_repository_url is not called in detect_cli function"

        # Check that there's error handling for invalid URLs
        assert "Invalid or potentially unsafe repository URL" in source_code, \
            "SECURITY REGRESSION: Error message for invalid URLs is missing"

    def test_validation_happens_before_command_construction(self):
        """Verify that URL validation happens before constructing the uvx command."""
        session_start_path = Path(__file__).parent.parent / "plugins" / "sdd-workflow" / "scripts" / "session-start.py"

        with open(session_start_path, 'r') as f:
            source_code = f.read()

        # Extract the detect_cli function
        detect_cli_start = source_code.find("def detect_cli(")
        detect_cli_end = source_code.find("\ndef ", detect_cli_start + 1)
        detect_cli_code = source_code[detect_cli_start:detect_cli_end]

        # Verify that validate_repository_url appears before the command construction
        validation_pos = detect_cli_code.find("validate_repository_url")
        command_construction_pos = detect_cli_code.find('f"uvx --from git+{cli_cfg.repository} sdd-cli"')

        assert validation_pos > 0, "SECURITY REGRESSION: URL validation not found in detect_cli"
        assert command_construction_pos > 0, "Command construction not found in detect_cli"
        assert validation_pos < command_construction_pos, \
            "SECURITY REGRESSION: URL validation must happen BEFORE command construction"


if __name__ == "__main__":
    # Allow running this test file directly
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
