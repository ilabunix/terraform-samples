#!/bin/bash

set -e

echo "🚀 Installing build dependencies..."
sudo yum update -y
sudo yum groupinstall -y "Development Tools"
sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel wget make zlib-devel xz-devel

echo "⬇️ Downloading Python 3.12 source..."
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tgz
sudo tar xzf Python-3.12.1.tgz
cd Python-3.12.1

echo "⚙️ Building and installing Python 3.12..."
sudo ./configure --enable-optimizations
sudo make altinstall

echo "🧪 Verifying installation..."
/usr/local/bin/python3.12 --version
/usr/local/bin/pip3.12 --version

echo "📌 Creating symlinks..."
sudo ln -sf /usr/local/bin/python3.12 /usr/bin/python3
sudo ln -sf /usr/local/bin/pip3.12 /usr/bin/pip3

echo "✅ Python 3.12 and pip installed successfully."