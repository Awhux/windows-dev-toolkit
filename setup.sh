#!/bin/bash

# Check if python3-venv is installed
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo "python3-venv is not installed. Installing now..."
    sudo apt update
    sudo apt install -y python3-venv
fi

# Create and activate virtual environment
python3 -m venv venv
source ./venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo "Setup complete. You can now run 'source ./venv/bin/activate' to activate the virtual environment."