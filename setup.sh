#!/bin/bash

echo "📦 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete! Run the script with: source venv/bin/activate && python sample.py"