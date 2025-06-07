# HIVE Framework Environment Setup Guide

## Overview
This guide provides instructions for setting up your development environment for the HIVE framework. Follow the steps relevant to your operating system and preferred setup.

## Prerequisites

- Python 3.10 or higher
- pyenv (recommended for Python version management)
- API key from one or more supported LLM providers:
  - OpenAI
  - Anthropic
  - Azure OpenAI
  - Ollama
  - Gemini

## Python Installation

### Windows Native Installation

1. Download Python installer from the [official Python downloads page](https://www.python.org/downloads/)
   - Recommended version: [Python 3.10](https://www.python.org/downloads/release/python-31011/)
   - Select the Windows installer (64-bit) from the downloads section

2. Run the installer:
   - Ensure "Add Python to PATH" is selected
   - Follow the installation wizard with default settings
   - Click 'Install' to complete the process

3. Verify the installation:
   ```bash
   python --version
   # Expected output: Python 3.10.x
   ```

### Windows Subsystem for Linux (WSL) Installation

1. Install pyenv:
   ```bash
   curl -fsSL https://pyenv.run | bash
   ```

2. Configure shell environment:
   ```bash
   # Add pyenv configuration to shell
   echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
   echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
   echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
   echo 'eval "$(virtualenv-init - bash)"' >> ~/.bashrc

   # Reload shell configuration
   exec "$SHELL"
   ```

3. Install Python build dependencies:
    ```bash
    # Download and install build dependencies for Python
    sudo apt update; sudo apt install make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev curl git \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
    ```

4. Install Python:
   ```bash
   pyenv install 3.10.17
   ```

## Virtual Environment Setup

### Windows Native Environment

```bash
# Create virtual environment
python -m venv venv

# Activate the environment
# For Command Prompt:
venv\Scripts\activate.bat
# For PowerShell:
venv\Scripts\Activate.ps1
```

### WSL Environment

```bash
# Create virtual environment
pyenv virtualenv 3.10.17 hive

# Activate and set as local environment
pyenv local hive
```

## HIVE Installation

Install HIVE in development mode:
```bash
pip install -e hive
```

Note: The `-e` flag creates an editable installation, enabling live updates to the package during development.

## API Configuration

Create a `.env` file in your project root directory with the following structure:

```ini
# Required
OPENAI_API_KEY=your_openai_key_here

# Optional - Add as needed
ANTHROPIC_API_KEY=your_anthropic_key_here
AZURE_OPENAI_KEY=your_azure_key_here
```

## Next Steps

After completing the environment setup:
1. Verify your installation
2. Review the framework documentation
3. Start developing with HIVE

For troubleshooting and additional configuration options, please refer to our [documentation repository](link-to-docs).