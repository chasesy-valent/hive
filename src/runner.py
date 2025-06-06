"""
This runner provides various examples of how to use the hive framework.
Select a main function and replace the asyncio.run(main()) call with it.
"""

from hive import ComponentFactory
from agents.basic_agent import BasicAgent
from agents.openai_assistant import OpenAIAssistant
from agents.tool_agent import WeatherAgent
from memory.semantic import SemanticMemory
from pipelines.poem_writer import PoemWriterPipeline

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination, ExternalTermination
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_agentchat.messages import TextMessage

from memory.semantic import SemanticMemory
from agents.tool_agent import WeatherAgent
from dotenv import load_dotenv
import asyncio
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow


load_dotenv()

async def simple_main():
    """
    This is a simple example of how to use the hive framework to create and run an agent.
    """
    # initialize component factory
    factory = ComponentFactory()

    # create and run agent on a simple task
    agent = factory.create_agent("poetry_writer", BasicAgent)
    await Console(agent.run_stream(task="Write a poem about interstellar travel."))

    # cleanup
    await factory.close()

async def index_rag_memory_test():
    """
    This is intended to be called before the rag_main function for testing the RAG memory object and its
    indexing functionality.
    """
    # initialize component factory
    factory = ComponentFactory()

    # load memory (+ index directory into semantic memory, if necessary)
    emberwoods_memory = factory.load_memory("emberwoods_memory", SemanticMemory)
    await emberwoods_memory.index_from_source() # only needs to be run once, because we are using persistent storage (i.e. saving the memory to a local file)

    emberwoods_memory.query("What is the name of the shop in Aldor's Shop?")

    # cleanup
    await factory.close()

async def rag_main():
    """
    This is an example of how to use the hive framework to create and run an agent that uses a local vector database for RAG.
    """
    # initialize component factory
    factory = ComponentFactory()

    # load memory and add it to the agent
    emberwoods_memory = factory.load_memory("emberwoods_memory", SemanticMemory)    
    rag_agent = factory.create_agent("researcher", BasicAgent, memory=[emberwoods_memory])
    await Console(rag_agent.run_stream(task="Tell me about Aldor's Shop."))

    # cleanup
    await factory.close()

async def multi_agent_main():
    """
    This is an example of how to use the hive framework to run a group chat with multiple agents.
    
    Note:
    - the WeatherAgent is defined by the tool it has access to, which can search through a (manufactured) DB to get the weather of a specific location.
    """
    # create agents
    factory = ComponentFactory()
    tool_agent = factory.create_agent("weather_agent", WeatherAgent)
    poetry_writer = factory.create_agent("poetry_writer", BasicAgent)

    # create group chat (RoundRobin iterates through all agents in order, context is shared amongst all agents)
    # setting max_turns to 2 means that the group chat will run each of the two agents once
    group_chat = RoundRobinGroupChat([tool_agent, poetry_writer], max_turns=2)
    await Console(group_chat.run_stream(task="Write a poem about the weather in New York."))

    # cleanup
    await factory.close()

async def oai_assistant_main():
    """
    This is an example of how to use the hive framework to run an OpenAI assistant.

    Note:
    - after running this once, check the openai playground to see assistant you just created
    - Add the assistant_id (e.g. 'asst_...') to the agent configurations to limit redundant agents
    - Example:
    ```yaml # .config/agents.yml
    oai_assistant:
      assistant_id: "asst_..."
      llm_config: ...
      instructions: ...
    ```
    """
    # create agent
    factory = ComponentFactory()
    assistant = factory.create_agent("oai_specialist", OpenAIAssistant)

    # run agent
    await Console(assistant.run_stream(task="Which is better: openai or anthropic?"))

    # cleanup
    await factory.close()

async def cusom_pipeline_main():
    """
    This is an example of how to use the hive framework to run a custom pipeline.
    """
    # create agents
    factory = ComponentFactory()
    
    # create pipeline
    pipeline = PoemWriterPipeline(
        writer=factory.create_agent("poetry_writer", BasicAgent),
        editor1=factory.create_agent("grammar_editor", BasicAgent),
        editor2=factory.create_agent("style_editor", BasicAgent),
        final_reviewer=factory.create_agent("final_reviewer", BasicAgent),
    )
    
    # run pipeline
    await Console(await pipeline.run_stream(task="Dallas is a up-and-coming city. It has a lot of potential."))
    
    # cleanup
    await factory.close()

async def nested_pipeline_main():
    """
    This is an example of how to use the hive framework to run a nested pipeline.

    Note:
    - Because HIVE pipelines extend the autogen Agent class, they can be used in the same way as other agents.
    - This means that they can be used in a group chat, or as part of a nested pipeline, if you want to control context.
    """
    # create agents
    factory = ComponentFactory()

    # prepare memory
    emberwoods_memory = factory.load_memory("emberwoods_memory", SemanticMemory)

    # set up pipeline elements
    researcher = factory.create_agent("researcher", BasicAgent, memory=[emberwoods_memory]) # basic researcher to provide context for the poem writer pipeline
    pipeline = PoemWriterPipeline(
        writer=factory.create_agent("poetry_writer", BasicAgent),
        editor1=factory.create_agent("grammar_editor", BasicAgent),
        editor2=factory.create_agent("style_editor", BasicAgent),
        final_reviewer=factory.create_agent("final_reviewer", BasicAgent),
    )
    
    # create and run groupchat
    group_chat = RoundRobinGroupChat([researcher, pipeline], max_turns=2)
    await Console(group_chat.run_stream(task="Write a poem about Aldor's Shop."))

if __name__ == "__main__":
    # pick one:

    asyncio.run(simple_main())
    # asyncio.run(rag_main())
    # asyncio.run(multi_agent_main())
    # asyncio.run(oai_assistant_main())
    # asyncio.run(cusom_pipeline_main())
    # asyncio.run(nested_pipeline_main())