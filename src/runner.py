from hive import AgentFactory
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination, ExternalTermination
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_agentchat.messages import TextMessage
from agents.basic_agent import BasicAgent
from agents.rag_agent import RAGAgent
from agents.openai_assistant import OpenAIAssistant
from pipelines.poem_writer import PoemWriterPipeline
from memory.semantic import SemanticMemory
from dotenv import load_dotenv
import asyncio
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow


load_dotenv()

async def main():
    # prepare memory for RAG agent
    emberwoods_memory = SemanticMemory("emberwoods_info", config_path=".config/memory.yml")
    # await emberwoods_memory.index("/home/jeaston/Valent/Internal/hive/data/The Emberwoods", type="directory")

    # create agents
    agent_factory = AgentFactory()

    researcher = agent_factory.create("emberwooods_specialist", RAGAgent, memory=[emberwoods_memory])
    writer = agent_factory.create("poetry_writer", BasicAgent)
    editor1 = agent_factory.create("editor1", BasicAgent)
    editor2 = agent_factory.create("editor2", BasicAgent)
    final_reviewer = agent_factory.create("final_reviewer", OpenAIAssistant)

    # create a group of agents
    poem_writer = PoemWriterPipeline(writer=writer, editor1=editor1, editor2=editor2, final_reviewer=final_reviewer)
    
    group_chat = RoundRobinGroupChat(
        [researcher, poem_writer],
        max_turns=2 # 1 for researcher, 1 for poem_writer pipeline
    )

    # run multi-agent system
    task = "Write a poem about Aldor's Shop."
    # task = "What can you tell me about Aldor's Shop?"
    await Console(group_chat.run_stream(task=task))

    # cleanup
    await agent_factory.close()
    await emberwoods_memory.close()

if __name__ == "__main__":
    asyncio.run(main())