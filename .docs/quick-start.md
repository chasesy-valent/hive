# Quick Start Guide

This guide will help you get started with the HIVE framework for multi-agent AI development. Consult the [FAQ]() documentation if you have questions.

## Environment Setup

### Prerequisites
- Python 3.10 or higher
- pyenv (recommended for Python version management)
- A valid API key for one (or more) of the supported LLM providers:
  - OpenAI
  - Anthropic
  - Azure OpenAI
  - Ollama
  - Gemini

### Setting Up Python with pyenv

1. Install pyenv (if not already installed):
```bash
# Install pyenv via automatic installer
curl -fsSL https://pyenv.run | bash
```

2. Configure your shell environment:
```bash
# Set up shell environment for Pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
echo 'eval "$(virtualenv-init - bash)"' >> ~/.bashrc

# Restart your shell to load updates
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
# Install Python (3.10.17 is recommended)
pyenv install 3.10.17
```

### Setting up your Virtual Environment

1. Activate your virtual environment with pyenv-virtualenv
```bash
# Create a virtual environment
pyenv virtualenv 3.10.17 hive

# Activate the environment (creates .python-version file)
cd <project_root_directory>
pyenv local hive
```

2. Install the HIVE framework and its dependencies:
```bash
pip install -e hive
```

### API Configuration

1. Create a `.env` file in your project root with your API keys:
```yaml
OPENAI_API_KEY=<your-key-here>
# Add other provider keys as needed:
# ANTHROPIC_API_KEY=<your-key-here>
# AZURE_OPENAI_KEY=<your-key-here>
```

## Creating Your First Agent

### 1. Configure Your Agent

Create a configuration file in `src/.config/agents.yml`:
```yaml
my_assistant:
  client: 
    provider: openai  # or anthropic, azure, etc.
    model: gpt-4o-mini     # or your preferred model
  instructions: |
    You are a helpful AI assistant that specializes in Python development.
    Provide clear, concise responses and always include code examples when relevant.
```

### 2. Implement the Agent

Create a basic agent implementation in `src/agents/basic_agent.py`:
```python
from hive import BaseAgentType
from autogen_agentchat.agents import AssistantAgent
from typing_extensions import override

class BasicAgent(BaseAgentType):
    @override
    def generate_with_autogen(self, name: str, model_client):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions', 'You are a helpful assistant.'),
            model_client=model_client
        )
```
Since you are inheriting the functionality built into the HIVE `BaseAgentType` class, you only need to override the `generate_with_autogen()` function, which is where you would include your specific autogen Assistant logic.

### 3. Create a Runner

Create a runner file in `src/runner.py`:
```python
from hive import AgentFactory
from autogen_agentchat.ui import Console
from agents.basic_agent import BasicAgent
from dotenv import load_dotenv
import asyncio

load_dotenv()  # Load API keys from .env file

async def main():
    # Initialize the factory with your configs
    factory = AgentFactory(config_path="config/agents.yml")
    
    # Create an agent (using same name from config file)
    # Must also pass in the class you implemented in step 2
    assistant = factory.create("my_assistant", BasicAgent)
    
    # Run a conversation
    # All Pipelines and Agents are triggered by calling the run_stream()
    # function with a query/task
    # Console() provides a convenient way to display the asynchronous output
    # (a.k.a. stream) to your terminal
    stream = assistant.run_stream(task="Write a Python function that calculates the Fibonacci sequence.")
    await Console(stream)
    
    # Cleanup
    await factory.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Run Your Agent

Execute your agent from the terminal:
```bash
cd src
python runner.py
```

## Next Steps

Now that you have a basic agent running, you can explore more advanced features:

1. [**Custom Tools**](): Integrate external tools and APIs to add functional capabilities to your system
2. [**Memory Systems**](): Add memory (e.g. RAG) capabilities to your agent for improved context awareness
3. [**Multi-Agent Orchestration**](): Create pipelines with multiple agents working together
4. [**Advanced Configurations**](): Customize agent behavior and model settings

For examples of these advanced features, check out:
- Example implementations in `.example_src/`
- The [Development Guidelines](../dev-help/README.md)
- [Core Concepts](../concepts/README.md) documentation

## Troubleshooting

Common issues and solutions:

1. **API Key Issues**:
   - Ensure your `.env` file is in the project root directory
   - Check that `load_dotenv()` is called before accessing keys
   - Verify API key format and validity

2. **Python Environment**:
   - Confirm Python version with `> python --version`
      - with pyenv: `> pyenv versions`
   - Verify virtual environment activation (you should see `(hive)` in your terminal prompt)
   - Run `pip list` to check installed packages

For more help, refer to the [FAQ]() or contact the Valent development team (jack.easton@valentpartners.com).