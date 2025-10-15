#!/bin/bash

# SecureEye Backend Setup Script

echo "Setting up SecureEye AI Backend..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p models
mkdir -p logs
mkdir -p data

# Copy environment template
cp env_template.txt .env

echo "Backend setup complete!"
echo "Please configure your .env file with Firebase credentials"
echo "Then run: python app.py"

