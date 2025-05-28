from hive import BaseAgentType
from autogen_agentchat.agents import AssistantAgent
from typing_extensions import override

class BasicAgent(BaseAgentType):
    @override
    def generate_with_autogen(self, name, model_client):
        return AssistantAgent(
            name=name,
            system_message=self.config.get('instructions', 'You are a helpful assistant.'),
            model_client=model_client,
            # tools=[], # a tool is simply a python function, or you can use a built-in tool from autogen (autogen_ext.tools)
            # memory=[] # refer to AutoGen documentation for memory details (e.g. for RAG applications)
        )