#!/bin/bash

set -e

# === Configuration ===
LAMBDA_DIR="confluence_indexer"
ZIP_FILE="confluence_indexer_bundle.zip"
REQUIREMENTS="boto3==1.34.18
requests==2.31.0
beautifulsoup4==4.12.3
atlassian-python-api==3.41.11"

# === Step 1: Prepare directory ===
rm -rf "$LAMBDA_DIR"
mkdir "$LAMBDA_DIR"
cd "$LAMBDA_DIR"

# === Step 2: Write requirements.txt ===
echo "$REQUIREMENTS" > requirements.txt

# === Step 3: Copy source files ===
cp ../lambda_function.py .
cp ../config.py .

# === Step 4: Create virtual environment ===
python3 -m venv venv
source venv/bin/activate

# === Step 5: Install dependencies ===
pip install -r requirements.txt -t .

# === Step 6: Zip everything ===
zip -r "$ZIP_FILE" . > /dev/null

# === Done ===
echo "✅ Bundle created: $LAMBDA_DIR/$ZIP_FILE"