# HIVE Agentic Orchestration Methods

## Overview

Orchestration in HIVE provides patterns and methods for coordinating multiple AI agents to solve complex tasks. Built on top of AutoGen's foundation, HIVE orchestration focuses on creating reliable, maintainable, and efficient multi-agent systems.

## Core Concepts

### Pipeline Pattern

The primary orchestration pattern in HIVE is the Pipeline, which allows you to create structured workflows of agents. A pipeline:
- Inherits from `BaseChatAgent`
- Defines a workflow through a directed graph
- Manages message flow between agents
- Supports streaming execution

For example, to create a research pipeline:

```python
class ResearchPipeline(Pipeline):
    def build(self, researcher, analyst, writer):
        # Build a simple sequential pipeline:
        # researcher -> analyst -> writer
        builder = DiGraphBuilder()
        
        # Add agents and connections
        builder.add_node(researcher).add_node(analyst).add_node(writer)
        builder.add_edge(researcher, analyst)
        builder.add_edge(analyst, writer)
        
        # Create the executable pipeline
        graph = builder.build()
        self.participants = builder.get_participants()
        self.pipeline = GraphFlow(
            participants=self.participants,
            graph=graph
        )
```

### Message Flow Control

HIVE provides tools to manage how messages flow between agents:

1. **Message Filtering**: Control what messages each agent sees
2. **Context Management**: Maintain relevant conversation history
3. **Information Flow**: Direct output from one agent to specific other agents

Example of controlling message flow using `MessageFilterAgent`:

```python
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.agents import MessageFilterAgent, MessageFilterConfig, PerSourceFilter

class CodeReviewPipeline(Pipeline):
    def build(self, developer, reviewer1, reviewer2, integrator):
        # Create a parallel review process where:
        # - Two reviewers see only the latest code from developer
        # - Integrator sees all review comments
        
        # Filter reviewers to only see the latest message from developer
        filtered_reviewer1 = MessageFilterAgent(
            name=reviewer1.name,
            wrapped_agent=reviewer1,
            filter=MessageFilterConfig(per_source=[
                PerSourceFilter(source=developer.name, position="last", count=1)
            ])
        )
        filtered_reviewer2 = MessageFilterAgent(
            name=reviewer2.name,
            wrapped_agent=reviewer2,
            filter=MessageFilterConfig(per_source=[
                PerSourceFilter(source=developer.name, position="last", count=1)
            ])
        )

        # Build the workflow graph
        builder = DiGraphBuilder()
        builder.add_node(developer).add_node(filtered_reviewer1).add_node(filtered_reviewer2).add_node(integrator)
        
        # Fan-out from developer to both reviewers
        builder.add_edge(developer, filtered_reviewer1)
        builder.add_edge(developer, filtered_reviewer2)

        # Fan-in both reviewers into integrator
        builder.add_edge(filtered_reviewer1, integrator)
        builder.add_edge(filtered_reviewer2, integrator)

        # Create the executable pipeline
        graph = builder.build()
        self.participants = builder.get_participants()
        self.pipeline = GraphFlow(
            participants=self.participants,
            graph=graph,
        )
```

**Key Message Filtering Features:**

1. **PerSourceFilter**: Filters messages from specific sources
   - `source`: The agent whose messages to filter
   - `position`: "last" to get only the most recent message
   - `count`: Number of messages to include (1 for latest only)

2. **MessageFilterAgent**: Wraps existing agents with filtering behavior
   - `name`: Preserves the original agent's name
   - `wrapped_agent`: The agent to apply filtering to
   - `filter`: Configuration defining what messages to show

3. **Parallel Processing**: Multiple filtered agents can process the same input simultaneously

This pattern ensures that reviewers only see the latest code from the developer, preventing information overload while maintaining parallel review capabilities.

## Common Workflow Patterns

### AutoGen Built-in Workflows

AutoGen provides several built-in workflow patterns that are ideal for simpler, more standard multi-agent interactions:

#### 1. RoundRobinGroupChat
**When to use**: When you need agents to take turns in a structured conversation, each contributing their expertise in sequence.

**Best for**:
- Sequential task completion
- Multi-step problem solving
- Collaborative brainstorming
- Agent handoffs

```python
from autogen_agentchat.teams import RoundRobinGroupChat

# Create agents
factory = ComponentFactory()
researcher = factory.create_agent("researcher", BasicAgent)
analyst = factory.create_agent("analyst", BasicAgent)
writer = factory.create_agent("writer", BasicAgent)

# Create round-robin workflow
group_chat = RoundRobinGroupChat([researcher, analyst, writer], max_turns=3)
await Console(group_chat.run_stream(task="Research and write a report on AI trends."))
```

#### 2. SelectorGroupChat
**When to use**: When you need dynamic agent selection based on the current context or task requirements.

**Best for**:
- Dynamic task routing
- Expert selection based on content
- Adaptive workflows
- Conditional agent involvement

```python
from autogen_agentchat.teams import SelectorGroupChat

# Create specialized agents
factory = ComponentFactory()
python_expert = factory.create_agent("python_expert", BasicAgent)
data_scientist = factory.create_agent("data_scientist", BasicAgent)
web_developer = factory.create_agent("web_developer", BasicAgent)

# Create selector workflow
selector_chat = SelectorGroupChat([python_expert, data_scientist, web_developer])
await Console(selector_chat.run_stream(task="Help me build a machine learning web application."))
```

### HIVE Pipeline Patterns

HIVE Pipelines are ideal for complex, structured workflows with specific message flow requirements:

#### 1. Fan-out/Fan-in Pattern
**When to use**: When you need to distribute work to multiple agents in parallel, then consolidate results.

**Best for**:
- Parallel processing
- Multi-agent reviews
- Distributed analysis
- Competitive evaluation

```python
class ReviewPipeline(Pipeline):
    def build(self, coordinator, reviewer1, reviewer2, reviewer3, integrator):
        # Filter reviewers to only see coordinator's latest message
        filtered_reviewers = [
            MessageFilterAgent(
                name=reviewer.name,
                wrapped_agent=reviewer,
                filter=MessageFilterConfig(per_source=[
                    PerSourceFilter(source=coordinator.name, position="last", count=1)
                ])
            ) for reviewer in [reviewer1, reviewer2, reviewer3]
        ]

        # Build fan-out/fan-in graph
        builder = DiGraphBuilder()
        builder.add_node(coordinator).add_node(integrator)
        for reviewer in filtered_reviewers:
            builder.add_node(reviewer)
            builder.add_edge(coordinator, reviewer)  # Fan-out
            builder.add_edge(reviewer, integrator)   # Fan-in

        # Create pipeline
        graph = builder.build()
        self.participants = builder.get_participants()
        self.pipeline = GraphFlow(participants=self.participants, graph=graph)
```

#### 2. Sequential Processing Pipeline
**When to use**: When tasks must happen in a specific order with clear handoffs.

**Best for**:
- Multi-stage processing
- Quality assurance workflows
- Approval processes
- Sequential data transformation

```python
class DocumentPipeline(Pipeline):
    def build(self, researcher, writer, editor, publisher):
        builder = DiGraphBuilder()
        builder.add_node(researcher).add_node(writer).add_node(editor).add_node(publisher)
        
        # Sequential flow
        builder.add_edge(researcher, writer)
        builder.add_edge(writer, editor)
        builder.add_edge(editor, publisher)

        graph = builder.build()
        self.participants = builder.get_participants()
        self.pipeline = GraphFlow(participants=self.participants, graph=graph)
```

#### 3. Reviewer-Critic Pattern
**When to use**: When you need iterative improvement with feedback loops.

**Best for**:
- Content refinement
- Code review cycles
- Design iterations
- Quality improvement

```python
class ContentRefinementPipeline(Pipeline):
    def build(self, creator, critic, finalizer):
        # Filter critic to only see creator's latest output
        filtered_critic = MessageFilterAgent(
            name=critic.name,
            wrapped_agent=critic,
            filter=MessageFilterConfig(per_source=[
                PerSourceFilter(source=creator.name, position="last", count=1)
            ])
        )

        builder = DiGraphBuilder()
        builder.add_node(creator).add_node(filtered_critic).add_node(finalizer)
        
        # Creator -> Critic -> Creator (feedback loop) -> Finalizer
        builder.add_edge(creator, filtered_critic)
        builder.add_edge(filtered_critic, creator)
        builder.add_edge(creator, finalizer)

        graph = builder.build()
        self.participants = builder.get_participants()
        self.pipeline = GraphFlow(participants=self.participants, graph=graph)
```

### Combining AutoGen and HIVE Workflows

You can combine AutoGen built-ins with HIVE pipelines for complex workflows:

#### Nested Pipeline Pattern
**When to use**: When you need to use a pipeline as a component within a larger workflow.

```python
# Create a pipeline that can be used as an agent
factory = ComponentFactory()
emberwoods_memory = factory.load_memory("emberwoods_memory", SemanticMemory)

# Pipeline as a component
poem_pipeline = PoemWriterPipeline(
    writer=factory.create_agent("poetry_writer", BasicAgent),
    editor1=factory.create_agent("grammar_editor", BasicAgent),
    editor2=factory.create_agent("style_editor", BasicAgent),
    final_reviewer=factory.create_agent("final_reviewer", BasicAgent),
)

# Use pipeline in a group chat
researcher = factory.create_agent("researcher", BasicAgent, memory=[emberwoods_memory])
group_chat = RoundRobinGroupChat([researcher, poem_pipeline], max_turns=2)
await Console(group_chat.run_stream(task="Write a poem about Aldor's Shop."))
```

#### Hybrid Workflow Pattern
**When to use**: When different parts of your workflow need different coordination patterns.

```python
# Use AutoGen for initial coordination
factory = ComponentFactory()
coordinator = factory.create_agent("coordinator", BasicAgent)
specialist1 = factory.create_agent("specialist1", BasicAgent)
specialist2 = factory.create_agent("specialist2", BasicAgent)

# Use HIVE pipeline for complex processing
processing_pipeline = ComplexProcessingPipeline(
    processor1=factory.create_agent("processor1", BasicAgent),
    processor2=factory.create_agent("processor2", BasicAgent),
    validator=factory.create_agent("validator", BasicAgent)
)

# Combine in a group chat
group_chat = RoundRobinGroupChat([coordinator, specialist1, specialist2, processing_pipeline], max_turns=3)
await Console(group_chat.run_stream(task="Analyze and process the data."))
```

### When to Use Each Approach

#### Use AutoGen Built-ins When:
- **Simple coordination**: Basic turn-taking or agent selection
- **Standard patterns**: Common multi-agent conversation patterns
- **Quick prototyping**: Rapid development of agent interactions
- **Dynamic routing**: Need for adaptive agent selection
- **Limited complexity**: Straightforward message flow requirements

#### Use HIVE Pipelines When:
- **Complex message flow**: Need precise control over what each agent sees
- **Structured workflows**: Multi-stage processes with specific handoffs
- **Message filtering**: Require agents to only see relevant information
- **Parallel processing**: Need fan-out/fan-in patterns
- **Iterative refinement**: Feedback loops and improvement cycles
- **Production workflows**: Complex, maintainable multi-agent systems

#### Use Combined Approaches When:
- **Mixed complexity**: Some parts need simple coordination, others need complex flow
- **Modular design**: Want to reuse pipeline components in different contexts
- **Scalable architecture**: Need to compose workflows from smaller components
- **Flexible coordination**: Different coordination patterns for different workflow stages

## Best Practices

1. **Message Flow Control**
   - Filter messages to prevent information overload
   - Maintain clear communication paths
   - Consider message relevance for each agent

2. **Graph Structure**
   - Keep workflows as simple as possible
   - Use clear entry and exit points
   - Consider message volume at each node

3. **Error Handling**
   - Plan for agent failures
   - Implement retry mechanisms
   - Have fallback strategies

4. **Performance**
   - Balance parallel vs sequential processing
   - Monitor agent response times
   - Optimize message filtering

## Common Challenges and Solutions

1. **Message Overload**
   - Challenge: Agents receiving too much context
   - Solution: Implement appropriate message filters
   - Example: Only pass relevant messages to each agent

2. **Workflow Deadlocks**
   - Challenge: Agents waiting for each other
   - Solution: Design clear workflow paths
   - Example: Use timeouts and circuit breakers

3. **Error Recovery**
   - Challenge: Handling agent failures
   - Solution: Implement robust error handling
   - Example: Retry logic and fallback paths

## Next Steps

1. Review the Pipeline base class in HIVE
2. Experiment with different workflow structures
3. Learn about message filtering options
4. Study advanced orchestration patterns

Remember: The goal of orchestration is to create efficient, reliable workflows that make the best use of each agent's capabilities while maintaining clear communication paths and error handling.