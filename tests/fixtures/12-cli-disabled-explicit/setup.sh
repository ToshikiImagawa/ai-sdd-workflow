#!/bin/sh
# Create a mock sdd-cli command on PATH (should be ignored because cli.enabled=false)
bin_dir="${PROJECT_ROOT}/.mock-bin"
mkdir -p "$bin_dir"
printf '#!/bin/sh\necho "mock sdd-cli"\n' > "${bin_dir}/sdd-cli"
chmod +x "${bin_dir}/sdd-cli"

# Export PATH addition for test runner
echo "PATH_PREPEND=${bin_dir}" > "${PROJECT_ROOT}/.test-env"
