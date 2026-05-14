#!/bin/bash
# deploy.sh
# Builds and publishes squad-config-validator to PyPI

set -euo pipefail

echo "Building and publishing squad-config-validator to PyPI"

# Check if .pypirc exists and has token
if [ ! -f "$HOME/.pypirc" ]; then
    echo "ERROR: PyPI token not configured."
    echo "Run ./setup-pypi-token.sh <your-token> first"
    exit 1
fi

# Clean any existing builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info squad_config_validator.egg-info

# Install build dependencies
echo "Installing build dependencies..."
pip install --upgrade build twine

# Build the package
echo "Building package..."
python -m build

# Check what was built
echo "Built packages:"
ls -lh dist/

# Upload to PyPI
echo "Uploading to PyPI..."
twine upload dist/*

echo ""
echo "✅ Successfully published to PyPI!"
echo ""
echo "Users can now install with:"
echo "  pip install squad-config-validator"
