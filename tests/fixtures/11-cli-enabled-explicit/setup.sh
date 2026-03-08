#!/bin/sh
# Create a mock uvx command on PATH (sdd-cli not available, fallback to uvx)
bin_dir="${PROJECT_ROOT}/.mock-bin"
mkdir -p "$bin_dir"
printf '#!/bin/sh\necho "mock uvx"\n' > "${bin_dir}/uvx"
chmod +x "${bin_dir}/uvx"

# Export PATH addition for test runner
echo "PATH_PREPEND=${bin_dir}" > "${PROJECT_ROOT}/.test-env"
