#!/bin/bash
echo "📦 Installing system dependencies..."
if [ -f packages.txt ]; then
    xargs -a packages.txt sudo apt install -y
fi

echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Installation complete! Ready to deploy."
