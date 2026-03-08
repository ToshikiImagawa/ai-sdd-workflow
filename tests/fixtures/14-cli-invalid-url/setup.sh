#!/bin/sh
# Fixture 14: CLI enabled with invalid/malicious repository URL
# Expected: CLI should be rejected due to URL validation failure

# Create mock uvx in temporary directory
mkdir -p "${PROJECT_ROOT}/.test-bin"
cat > "${PROJECT_ROOT}/.test-bin/uvx" <<'EOF'
#!/bin/sh
echo "mock uvx"
EOF
chmod +x "${PROJECT_ROOT}/.test-bin/uvx"

# Add mock bin to PATH for this test
echo "PATH_PREPEND=${PROJECT_ROOT}/.test-bin" > "${PROJECT_ROOT}/.test-env"
