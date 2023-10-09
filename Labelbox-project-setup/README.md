# Project Setup and Guidelines for Team Leaders

## Project Setup:

1. Sign up on Labelbox using your university email address.
2. Create your workspace API key:
    - Navigate to your workspace settings or use this link [Workspace Settings](https://app.labelbox.com/workspace-settings/workspace)
    - Click on API and then create a New API Key. (Caution: DO NOT SHARE YOUR API KEY ANYWHERE)

### Local Setup:

```bash
# Create a python virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# Unix/MacOS:
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Copy and paste your workspace API key in the .env file
LB_API_KEY=<workspace api key>

# Now run the project.py script and follow the command-line prompts
python project.py
