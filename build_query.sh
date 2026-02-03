#!/bin/bash

set -e

# === CONFIG VARIABLES ===
LAMBDA_NAME="query_lambda"
BUNDLE_NAME="${LAMBDA_NAME}_bundle.zip"
REQUIREMENTS_FILE="requirements.txt"
MAIN_SCRIPT="lambda_function.py"
CONFIG_FILE="config.py"
VENV_DIR="venv"

echo "📦 Building $LAMBDA_NAME Lambda deployment package..."

# === SETUP DIRECTORIES ===
mkdir -p "$LAMBDA_NAME"
cd "$LAMBDA_NAME"

# === CREATE AND ACTIVATE VIRTUAL ENVIRONMENT ===
echo "🐍 Creating virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# === INSTALL DEPENDENCIES ===
echo "📥 Installing Python packages..."
pip install -r "../$REQUIREMENTS_FILE" -t .

# === COPY SOURCE FILES ===
echo "📄 Copying source files..."
cp "../$MAIN_SCRIPT" .
cp "../$CONFIG_FILE" .

# === CREATE ZIP BUNDLE ===
echo "🗜️  Creating zip bundle $BUNDLE_NAME..."
zip -r "$BUNDLE_NAME" .

echo "✅ Done! Bundle created at: $(pwd)/$BUNDLE_NAME"