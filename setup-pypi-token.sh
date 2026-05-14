#!/bin/bash
# setup-pypi-token.sh
# Setup PyPI token for publishing squad-config-validator

set -euo pipefail

if [ -z "$1" ]; then
    echo "Usage: $0 <your-pypi-token>"
    echo ""
    echo "Get a token from: https://pypi.org/manage/account/token/"
    echo "Choose 'Entire account' scope for simplicity"
    exit 1
fi

TOKEN="$1"

# Create .pypirc file
cat > "$HOME/.pypirc" <<EOF
[pypi]
  username = __token__
  password = $TOKEN
EOF

# Secure the file
chmod 600 "$HOME/.pypirc"

echo "✅ PyPI token configured in ~/.pypirc"
echo "You can now run ./deploy.sh to publish to PyPI"
