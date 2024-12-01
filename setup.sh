#/bin/bash
set -ex

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install the requirements
pip install -r requirements.txt
pip install -r requirements_dev.txt
