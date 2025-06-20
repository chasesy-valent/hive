# Hyper Intelligent Valent Entity (H.I.V.E.) Framework

HIVE is Valent's internal framework for multi-agent AI development, built on top of Microsoft's AutoGen library. It simplifies the development of multi-agent systems by:
1. Providing a standardized workflow for multi-agent development (with current best practices in mind)
2. Offering starter code and ready-to-use examples and templates (via the [hive-starter repository](README.md#))
3. Including comprehensive documentation on modern AI concepts alongside practical HIVE code (found in the [HIVE documentation](.docs/README.md))

## Understanding the HIVE Repo

The repository is organized to separate framework code from your multi-agent implementations:

```yaml
.
├── .docs/              # Documentation and guides
│
├── hive/               # Core framework code
│
├── data/               # Optional, for storing data and persistent memory
│
├── src/                # Your multi-agent system code
│   ├── .config/        # Configuration files
│   │   ├── agents.yml  # Agent parameters and settings
│   │   └── memory.yml  # Memory and RAG configurations
│   │
│   ├── agents/         # Custom agent implementations
│   │
│   ├── memory/         # Custom memory implementations
│   │
│   ├── workflows/      # Custom workflow implementations
│   │
│   └── runner.py       # Main entry point
│
└── .env                # Environment variables and API keys
```

### Key Components

1. **Core Framework (`hive/`)**
   - Contains the base framework code that wraps Microsoft's AutoGen
   - Provides foundational classes and utilities
   - Should not be modified unless extending the framework itself

2. **Data Storage (`data/`)**
   - Optional directory for storing persistent data
   - Used for maintaining memory systems and knowledge bases
   - Suitable for storing vector databases, conversation logs, and other persistent data

3. **Your Implementation (`src/`)**
   - `.config/`: YAML configurations for your agents and memory systems
     - `agents.yml`: Define agent parameters, models, and settings
     - `memory.yml`: Configure vector stores, chunking, and retrieval settings
   
   - `agents/`: Where you define agent types
     - Create a new agent type when using a different AutoGen agent or specific tools
     - Agent types can be reused when only changing configs (instructions, model params, etc.)

   - `memory/`: Add memory to give agents access to:
     - Knowledge bases and documents (via vector stores)
     - Past conversations and interactions
     - Learned procedures and workflows
     - Need to define your base AutoGen memory structure and indexing process (i.e. how you load data into memory)

   - `workflows/`: Custom agent orchestration
     - Define how agents communicate and collaborate
     - Use AutoGen's `DiGraphBuilder` for complex workflows
     - Can create nested structures for modular designs

   - `runner.py`: Your system's entry point
     - Initializes the Component Factory
     - Creates and configures agents
     - Sets up memory systems
     - Manages the execution flow

4. **Configuration and Environment**
   - `.env`: Stores sensitive information like API keys


## Quick Start

This guide will walk you through creating your first HIVE agent. For environment setup instructions, see our [Environment Setup Guide](.docs/environment-setup.md).

### 1. Configure Your Agent

First, we'll create a configuration for your agent. HIVE uses YAML files to define agent parameters, making it easy to modify behavior without changing code.

Create a configuration file in `src/.config/agents.yml`:

```yaml
my_assistant:
  llm_config: 
    provider: openai  # Supports: openai, anthropic, azure, ollama, gemini
    model: gpt-4-turbo-preview  # Use your preferred model
  instructions: |
    You are a helpful AI assistant that specializes in Python development.
    Provide clear, concise responses and always include code examples when relevant.
```

The configuration defines:
- The agent's name (`my_assistant`)
- Which LLM provider and model to use
- The agent's base instructions/personality
  - IMPORTANT: must use the pipe ('|') operator to span multiple lines for your instructions

### 2. Create Your Agent Type Implementation

Next, we'll create a basic agent implementation. HIVE provides base classes that handle most of the complexity, so you only need to define how your agent integrates with AutoGen.

Create `src/agents/basic_agent.py`:

```python
from hive import BaseAgentType
from autogen_agentchat.agents import AssistantAgent
from typing_extensions import override

class BasicAgent(BaseAgentType):
    @override
    def create_with_autogen(self, name: str, model_client, memory):
        """Create an AutoGen assistant with our configuration."""
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions', 'You are a helpful assistant.'),
            model_client=model_client
        )
```

This implementation:
- Inherits from HIVE's `BaseAgentType`
- Overrides `create_with_autogen()` to specify how the agent should be created
- Uses AutoGen's `AssistantAgent` with our configured instructions

### 3. Build Your Runner

Now we'll create the entry point that brings everything together. The runner initializes your agent and handles the conversation flow.

Create `src/runner.py`:

```python
from hive import ComponentFactory
from autogen_agentchat.ui import Console
from agents.basic_agent import BasicAgent
from dotenv import load_dotenv
import asyncio

load_dotenv()  # Load API keys from .env

async def main():
    # Initialize the factory with your configs
    factory = ComponentFactory()
    
    # Create your agent
    assistant = factory.create_agent("my_assistant", BasicAgent)
    
    # Run a conversation with streaming output
    stream = assistant.run_stream(
        task="Say 'Hello World!'."
    )
    await Console(stream)
    
    # Always cleanup when done
    await factory.close()

if __name__ == "__main__":
    asyncio.run(main())
```

The runner:
- Creates a `ComponentFactory` to manage HIVE components
- Uses the factory to create your agent with the configuration
- Runs a conversation with streaming output
- Handles proper cleanup

### 4. Run Your Agent

NOTE: you must navigate to the directory with your `runner.py` script.
```bash
cd src
python runner.py
```

You should see your agent respond to the task by printing "Hello World" to your console.

### Next Steps

Now that you have a basic agent running, you can explore more advanced features:

1. **Add Memory**: Enhance your agent with semantic (RAG) memory:
```python
# In your runner.py
memory = factory.load_memory("semantic_memory", MemoryImplementation)  # Configure in memory.yml
assistant = factory.create_agent("my_assistant", BasicAgent, memory=memory)
```

2. **Create Multi-Agent Teams**: Have multiple agents collaborate:
```python
from autogen_agentchat.teams import RoundRobinGroupChat
# In your runner.py
assistant = factory.create_agent("assistant", BasicAgent)
expert = factory.create_agent("expert", ExpertAgent)
team = RoundRobinGroupChat([assistant, expert], max_turns=2)
```

3. **Add Custom Tools**: Give your agents new capabilities with tools:
```python
# In your agent implementation
class ToolAgent
    def create_with_autogen(self, name: str, model_client):
        return AssistantAgent(
            name=name,
            system_message=self.config['instructions'],
            model_client=model_client,
            tools=[my_custom_tool]  # Add your tools here
        )

    def my_custom_tool(self, **agent_parameters):
        # enter code here
        # use parameters from agent config with self.tool_configs.get('<param>', {})
```

*NOTE: full implementations and more in-depth walkthroughs provided in the [HIVE Documentation](.docs/README.md).*

## General Development Guidelines for HIVE Projects

### Development Process

1. **Planning Phase**
   - Define your agents' roles and responsibilities
   - Map out the interaction flow between agents
   - Identify required external tools and APIs
   - Plan your memory strategy (semantic, episodic, procedural)

2. **Configuration First**
   - Start by defining configurations in YAML files
   - `agents.yml`: Configure each agent's parameters
     ```yaml
     expert_agent:
       llm_config:
         provider: openai
         model: gpt-4-turbo-preview
       instructions: |
         You are an expert Python developer...
       tool_config:
         - code_analysis:
            enabled: true
     ```
   - `memory.yml`: Set up memory systems
     ```yaml
     semantic_memory:
       source: "./data/The Emberwoods"
       source_type: "directory" # 'directory', 'files', 'content'
      chunking_config:
        # ... used in load_with_langchain() function
      retrieval_config:
        # ... used in generate_with_autogen() function
     ```

3. **Iterative Development**
   - Start with a single agent implementation
   - Test thoroughly before adding complexity
   - Add features incrementally:
     1. Basic agent functionality
     2. Memory integration
     3. Tool integration
     4. Multi-agent orchestration

4. **Testing Strategy**
   - Test agent behaviors with simple prompts first
   - Validate memory retrieval accuracy
   - Test tool integrations independently
   - Verify multi-agent interactions
   - Document edge cases and limitations

### Best Practices

1. **Agent Development**
   - Keep agent definitions focused and single-purpose
   - Store agent-specific tools in the same file as the agent
   - Use the factory pattern via `factory.create_agent()` for instantiation

2. **Memory Management**
   - Test memory systems independently before integration
   - Consider chunking strategies carefully for optimal retrieval
   - Use appropriate memory types (semantic, procedural, or episodic) for different use cases

3. **Workflow Design**
   - Start with built-in AutoGen teams before custom pipelines
   - Extract complex workflows into separate pipeline modules
   - Document the flow of information between agents

4. **Resource Management**
   - Always use try/finally blocks for cleanup
   - Monitor API usage and costs
   - Handle long-running tasks with timeouts or termination criteria

5. **Monitoring**
   - Use structured logging
   - Monitor agent performance metrics
   - Track memory usage, tool calls, and API calls

Remember: Start simple and add complexity only when needed. Test each component thoroughly before integration.

## Where to go next

**Explore Core Concepts**
   - [Agent Fundamentals](.docs/concepts/agents.md)
     - Agent types and capabilities
     - System messages and instructions
     - Tool integration patterns
   
   - [Memory Systems](.docs/concepts/memory.md)
     - Semantic (RAG) memory
     - Episodic conversation history
     - Procedural task memory
   
   - [Agent Workflows](.docs/concepts/orchestration.md)
     - AutoGen teams
     - Custom pipelines
     - Communication patterns

**Walk Through Practical Examples**
   - Clone the starter examples into project root:
     ```bash
     git clone https://github.com/JackEaston-valent/hive-starter.git
     cd hive-starter
     ```
   
   - Consult the documentation provided in the `hive-starter/README.md`.
   - Feel free to run any of the examples. Assuming your environment is properly set up, you should be able to run `hive-starter/runner.py` just like you would your own runner.py.

### Getting Help

- Check our [FAQ](.docs/faq.md) for common questions
- Report issues on our [Issue Tracker](https://github.com/JackEaston-valent/hive/issues)
- Contact the development team: jack.easton@valentpartners.com

## Contributing
HIVE is still in beta development. If you find a bug or would like to add further integration with AutoGen or another technology, please reach out to the development team: jack.easton@valentpartners.com. 

To contribute, you must:
1. Fork the repository
2. Create a feature branch
3. Follow the established code patterns and practices
4. Ensure documentation is updated
5. Submit a pull request with your changes

## License

Internal use only - Valent proprietary software