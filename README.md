# Hyper Intelligent Valent Entity (H.I.V.E.) Framework

HIVE is Valent's internal framework for multi-agent AI development, built on top of Microsoft's AutoGen library. It simplifies the development of multi-agent systems by:
- Providing a standardized workflow for multi-agent development (with current best practices in mind)
- Offering starter code and ready-to-use examples and templates
- Including comprehensive documentation on modern AI concepts
- Ensuring consistent patterns across multi-agent applications

## Key Features

- **Standardized Agent Development**: Common patterns and best practices for creating AI agents
- **Memory Systems**: Built-in support for various memory types including RAG (Retrieval Augmented Generation)
- **Tool Integration**: Framework for adding custom tools and capabilities
- **Workflow Management**: Pipeline system for orchestrating multiple agents
- **Example Code**: Production-ready examples to accelerate development
- **Multi-Model Support**: Integration with various LLM providers including OpenAI, Anthropic, Azure, and Ollama

## Prerequisites

- Python 3.10 or higher
- A valid API key for one (or more) of the supported LLM providers:
  - OpenAI
  - Anthropic
  - Azure OpenAI
  - Ollama
  - Gemini

## Environment Setup

1. Set up your Python environment (we recommend using pyenv):
```bash
# Create a virtual environment (and activate it)
pyenv virtualenv 3.10 <environment_name>
pyenv local <environment_name>

# Install dependencies
pip install -e hive
```

2. Create a `.env` file in your project root with your API keys:
```yaml
OPENAI_API_KEY=<your-key-here>
# Add other provider keys as needed:
# ANTHROPIC_API_KEY=<your-key-here>
# AZURE_OPENAI_KEY=<your-key-here>
```

## Project Structure

```yaml
.
├── .docs/              # Quick Start, HIVE documentation, Valent AI Knowledgebase
│
├── hive/               # Core framework code
│
├── src/                # Multi-agent system code
│   ├── .config/        # Agent configurations (YAML)
│   ├── agents/         # Agent implementations
│   ├── memory/         # Memory implementations
│   ├── pipelines/      # Workflow implementations
│   └── runner.py       # Main entry point
│
├── .env                # Environment variables and API keys
├── .gitignore
├── .python-version     # Python version management (if using pyenv)
├── README.md
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:
- [Quick Start](.docs/quick-start.md): Create your first agent and run it with HIVE
- [Core Concepts](.docs/concepts/README.md): AI concepts and best practices
- [Development Guidelines](.docs/dev-help/README.md): Outlines the basics for multi-agent system development
- [Example Implementations](.docs/examples/README.md): Detailed example walkthroughs

## Getting Started with Development

For Valent developers:
1. Run through the [Quick Start](.docs/dev-help/quick-start.md) tutorial to set up your environment and create and run your first agent.
2. (optional) Download the [starter project]() from github
3. Refer to the [HIVE Development Guidelines](.docs/dev-help/README.md) for best practices

## Contributing
HIVE is still in beta development. If you find a bug or would like to add further integration with AutoGen or another technology, please reach out to the jack.easton@valentpartners.com. 

To contribute, you must:
1. Fork the repository
2. Create a feature branch
3. Follow the established code patterns and practices
4. Ensure documentation is updated
5. Submit a pull request with your changes

## License

Internal use only - Valent proprietary software
