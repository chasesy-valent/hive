# HIVE Documentation

describe how to use this documentation

## Quick Start Tutorial
brief description of what you'll do

You can find the tutorial [here](quick-start.md).

## Development Guidelines
General Development Guidelines


### Additional Resources:
For help with Agents and Tools, look [here](agents/README.md).

For help with Memory, look [here](memory/README.md).

For help with multi-agent orchestration, look [here](orchestration/README.md).

## Frequently Asked Questions (FAQs)

You can find a compiled list of FAQs [here](faq.md).




# WIP
# HIVE Development Help

## General Development Guidelines

## Agents
To add an agent to your project, you need to do **3 things**:
1. Add the agent to your configuration file (default location `src/.config/agents.yml`)
2. Create an agent class in the `agents/` directory, which allows us wrap AutoGen agents and use them in our HIVE code.
3. Create the agent in your `runner.py` file, using the `AgentFactory`.

### 1. Update Agent Configurations
```yml
my_assistant:
  client: 
    provider: openai  # or anthropic, azure, etc.
    model: gpt-4o-mini     # or your preferred model
  instructions: |
    You are a helpful AI assistant that specializes in Python development.
    Provide clear, concise responses and always include code examples when relevant.
```
- The name of your assistant (e.g. "my_assistant") is the root parameter used to extract that agent's configurations in your HIVE code.
- `client`: describes the LLM configurations your agent will use
- `instructions`: outlines any instructions you want to provide your agent to guide it on its task.
    - Tip: You can type across mutliple lines using the pipe ('|') syntax shown above.

### 2. Define Agent Implementation
In general, each new agent should be implemented as a class in a new file within the agents/ directory. Think of agent classes as type definitions. New agent classes should be added if:
- The agent is using a specific tool
- You want to use a different AutoGen agent

You do not need to add a new agent class if you are adding an agent with:
- a different task/instruction set
- different LLM configurations
- different memory configurations (these can be passed into any agent class)
You have a few agents that use different memories

Here is an example implementation
```python
# src/agents/basic_agent.py
from hive import BaseAgentType
from autogen_agentchat.agents import AssistantAgent

class BasicAgent(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions', 'You are a helpful assistant.'),
            model_client=model_client
        )
```
- All Agents should inherit from the HIVE `BaseAgentType`, which loads configurations and sets basic functionality to be able to interface with other HIVE components.
- The only function you need to implement is the `generate_with_autogen()` function, which gives you the flexibility to choose and configure any of the [predefined AutoGen Assistant types](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html#other-preset-agents).
    - `name` and `model_client` are required parameters for this function and are pulled from your config file.
    - You may pass any necessary information to your agent via the config file (e.g. instructions)
    - NOTE: `AssistantAgent` is the default

### 3. Running your Agent
To generate the agent in `runner.py`, we must use the `AgentFactory`, defined in the HIVE package:
```python
# runner.py
async def main():
    factory = AgentFactory()
    agent1 = factory.create("<agent name from config file>", BasicAgent)
```
- If you have a different config path than *'.config/agents.yml'*, you pass it to the factory as `AgentFactory(config_path='<path_to_agent_configs>')`.
- You must pass both the name of the agent from the config file and the type defined in your class implementation.

For more information, consult the [Agent Documentation]().

### Adding Tools to your Agent
Tools should be wrapped in a python function directly below your agent class, and passed into the agent via the `tools` parameter.

```python
class WeatherAgent(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions', 'You are a helpful assistant.'),
            model_client=model_client,
            tools=[get_weather_data]
        )

def get_weather_data(city: str) -> str:
    tool_configs = self.config["weather_tool"]
    if city == tool_configs["local_city"]:
        return "Sunny, with a slight breeze."
    else:
        return "Cloudy and gross."
```
In general, you should stick to 1 or 2 tools per agent.

You can add any tool-specific parameters (if necessary) to your agent configs. For example:
```yaml
my_assistant:
  client: 
    provider: openai  # or anthropic, azure, etc.
    model: gpt-4o-mini     # or your preferred model
  instructions: You are a helpful assistant that can tell the weather of a queried city.
  weather_tool:
    local_city: Dallas
```

### Predefined AutoGen Agents
In addition to the default AssistantAgent, AutoGen provides a [series of helpful agents](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html) for you to use in your agent class implementations:
- AssistantAgent:
- UserProxyAgent: An agent that takes user input returns it as responses.
- CodeExecutorAgent: An agent that can execute code.
- OpenAIAssistantAgent: An agent that is backed by an OpenAI Assistant, with ability to use custom tools.
- MultimodalWebSurfer: A multi-modal agent that can search the web and visit web pages for information.
- FileSurfer: An agent that can search and browse local files for information.
- VideoSurfer: An agent that can watch videos for information.

## Memory
Memory is defined as any context source outside of the main thread that an agent has access to. There are four types of memory we have control over:
1. Thread: Adding chat history is done by default with AutoGen. We can implement content summary for long chat threads and content filtering for agents that do not require the content from all messages.
2. Semantic (facts): Adding knowledge bases for fact retrieval.
3. Episodic (events): Adding user events and outcomes for feedback loops.
4. Procedural (how-to): For complex tasks, we can organize the desired flow of agentic execution. Think a database of instructions, executed based on certain conditions being met.

Thread Management and Semantic Retrieval are the most common.

To add memory to your agent you need to do **4 things**:
1. Add an entry to the memory configuration file (default location `src/.config/memory.yml`)
2. Create a memory class in the `memory/` directory, which allows us to wrap AutoGen and other technologies (e.g. for chunking) and use them in our HIVE code.
3. Create the memory object in your `runner.py` and index with content if necessary.
4. Pass the memory to your agent in the AgentFactory `create()` function.

### 1. Update Memory Configurations

### 2. Define Memory Implementation

### 3. Create/Index the Memory

### 4. Add Memory to your Agents

### 

## Orchestration

For more information, consult the [Orchestration Documentation]().




