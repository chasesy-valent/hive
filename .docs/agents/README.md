# HIVE Agents

## Overview

HIVE agents are autonomous components that work together to accomplish specific tasks within your application. Each agent has a defined objective and action space, allowing them to make decisions and take actions based on their configuration and capabilities.

## Understanding Agent Components

### Configuration Parameters
The agent configuration (in `agents.yml`) defines the agent's capabilities and behavior:

```yml
my_assistant:
  llm_config: 
    provider: openai
    model: gpt-4-turbo-preview
    temperature: 0.7
  instructions: |
    You are a helpful AI assistant that specializes in Python development.
    Provide clear, concise responses and always include code examples when relevant.
```

**Key Parameters Explained:**
- `client`: Defines how the agent interacts with LLM services
  - `provider`: Which LLM service to use (affects available models and features)
  - `model`: The specific model to use (impacts capabilities and cost)
  - `temperature`: Controls randomness in responses (0 = deterministic, 1 = most random)
  
- `instructions`: The agent's core programming
  - Defines the agent's role and personality
  - Sets boundaries for what the agent can/should do
  - Establishes any specific domain expertise

### Agent Types and Their Uses

#### Base Agent Type
The foundation for all HIVE agents:
```python
class BasicAgent(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client, memory):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions'),
            model_client=model_client
        )
```

**Key Components:**
- `BaseAgentType`: Provides core HIVE functionality
  - Configuration management
  - Memory integration capabilities
  - Tool integration framework
  
- `generate_with_autogen()`: Bridge to AutoGen's agent system
  - `name`: Unique identifier for the agent, taken from `agents.yml`
  - `model_client`: Configured LLM interface
  - Returns an AutoGen agent instance

### Memory Integration
Memory gives agents context and learning capabilities:

```python
class AgentWithMemory(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client, memory):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions'),
            model_client=model_client,
            memory=memory
        )
```

**Memory Types and Their Uses:**
- `SemanticMemory`: For knowledge-based tasks
  - Stores and retrieves relevant information
  - Useful for maintaining context across conversations
  
- `EpisodicMemory`: For learning from past interactions
  - Records sequences of events
  - Helps agents improve over time

- `ProceduralMemory`: For storing action patterns and skills
  - Captures learned procedures and workflows
  - Enables agents to refine and optimize task execution
  - Useful for repetitive or structured tasks

### Tool Integration
Tools extend an agent's capabilities:

```python
class WeatherAgent(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client, memory):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions'),
            model_client=model_client,
            tools=[self.get_weather_data]
        )

    def get_weather_data(self, city: str) -> str:
        """Get weather data for a specific city."""
        tool_configs = self.tool_configs["weather_tool"]
        
        # fetch_weather(city, tool_configs)
        return weather_details
```

**Tool Configuration:**
```yaml
weather_agent:
  llm_config: 
    provider: openai
    model: gpt-4-turbo-preview
  instructions: You are a helpful assistant that can tell the weather of a queried city.
  tool_config:
    weather_tool:
      api_key: ${WEATHER_API_KEY}
      cache_duration: 300  # Cache weather data for 5 minutes
      units: metric
```

**Tool Components Explained:**
- Tool Function:
  - Must be self-contained and focused
  - Should handle its own error cases
  - Can access agent configuration
  
- Tool Configuration:
  - Stored in agent's config under a tool-specific key
  - Can include API keys, settings, and preferences
  - Should use environment variables for sensitive data

## Specialized AutoGen Agent Types
*For the most current list of pre-generated AutoGen Agents, review [this link](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html#other-preset-agents).*

### AssistantAgent
Best for: General conversation and task completion
```python
class SpecializedAssistant(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client, memory):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions'),
            model_client=model_client
        )
```

### UserProxyAgent
Best for: Testing and automation
```python
class AutomatedTester(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client, memory):
        return UserProxyAgent(
            name=name
        )
```

### CodeExecutorAgent
Best for: Code execution and development tasks
```python
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor

class DevAgent(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client):
        code_executor = DockerCommandLineCodeExecutor(work_dir=self.tool_configs.get('work_dir', './'))
        await code_executor.start()

        return CodeExecutorAgent(
            name=name,
            code_executor=code_executor
        )
```

## Error Handling and Monitoring

### Error Recovery
***Not currently implemented in HIVE, but a great idea. Maybe YOU could be the one to contribute this to HIVE.***
```python
class RobustAgent(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions'),
            model_client=model_client,
            error_handler=self._handle_errors
        )

    def _handle_errors(self, error):
        """
        Handle different types of errors appropriately:
        - API errors: Retry with backoff
        - Memory errors: Fall back to stateless operation
        - Tool errors: Try alternative tools or skip
        """
        if isinstance(error, APIError):
            return self._retry_with_backoff()
        elif isinstance(error, MemoryError):
            return self._operate_without_memory()
        elif isinstance(error, ToolError):
            return self._find_alternative_tool()
```

### Performance Considerations
- Memory Usage:
  - Use streaming for large responses
  - Implement caching for frequent queries
  - Clean up memory after task completion

- Response Time:
  - Use async/await for I/O operations
  - Implement timeouts for external calls
  - Monitor and log slow operations

## Testing Strategies
***Not currently implemented in HIVE, but a great idea. Maybe YOU could be the one to contribute this to HIVE.***

### Unit Testing
```python
@pytest.fixture
def weather_agent():
    config = {
        "instructions": "Test weather agent",
        "weather_tool": {"api_key": "test_key"}
    }
    return WeatherAgent(config)

def test_weather_data_retrieval(weather_agent):
    """Test the core weather data retrieval functionality"""
    result = weather_agent.get_weather_data("Dallas")
    assert isinstance(result, str)
    assert "temperature" in result.lower()

def test_error_handling(weather_agent):
    """Test how the agent handles invalid inputs"""
    with pytest.raises(ValueError):
        weather_agent.get_weather_data("")
```

### Integration Testing
```python
async def test_agent_memory_integration(agent_with_memory):
    """Test memory integration with the agent"""
    # First conversation
    response1 = await agent_with_memory.run("Remember that my name is Alice")
    
    # Second conversation should recall the name
    response2 = await agent_with_memory.run("What's my name?")
    assert "Alice" in response2
```

## Next Steps

After understanding agent components:
1. Explore agent orchestration in the [Workflows Documentation](../workflows/README.md)
2. Learn about memory integration in the [Memory Documentation](../memory/README.md)
3. Understand how to monitor and debug agents in the [Monitoring Guide](../monitoring/README.md)
