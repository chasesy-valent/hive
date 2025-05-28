from autogen_agentchat.agents import AssistantAgent
from autogen_core.memory import Memory
from typing_extensions import override, List
from hive import BaseAgentType

class RAGAgent(BaseAgentType):
    @override
    def generate_with_autogen(self, name: str, model_client, memory: List[Memory] | None):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions', 'You are a helpful assistant.'),
            model_client=model_client,
            # tools=[], # refer to AutoGen documentation for available tools
            memory=memory # refer to AutoGen documentation for memory details (e.g. for RAG applications)
        )