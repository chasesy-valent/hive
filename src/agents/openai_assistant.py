from openai import AsyncOpenAI
from autogen_ext.agents.openai import OpenAIAssistantAgent
from typing_extensions import override
from hive import BaseAgentType
from typing import List
from autogen_core.memory import Memory

class OpenAIAssistant(BaseAgentType):
    @override
    def generate_with_autogen(self, name: str, model_client: AsyncOpenAI, memory: List[Memory]):
        # NOTE: memory is not used for OpenAI Assistant API. Instead use openai vector stores, accessible through the openai playground.
        self.assistant_id = self.config.get('assistant_id', None)
        if self.assistant_id is not None:
            return self.load_assistant(name, model_client)
        else:
            return self.create_assistant(name, model_client)
    
    def load_assistant(self, name: str, model_client: AsyncOpenAI):
        """Load an existing OpenAI assistant."""
        try:
            agent = OpenAIAssistantAgent(
                name=name,
                description="", # unnessesary if using assistant_id, but required for AutoGen wrapper
                client=model_client,
                model="", # unnessesary if using assistant_id, but required for AutoGen wrapper
                instructions="", # unnessesary if using assistant_id, but required for AutoGen wrapper
                
                assistant_id=self.assistant_id
            )

            print("Warning: Using Assistant ID will use the existing assistant's parameters. Any parameters provided will be ignored.")

            return agent
        except Exception as e:
            raise ValueError(f"Failed to load assistant with ID {self.assistant_id}: {str(e)}")
    
    def create_assistant(self, name: str, model_client: AsyncOpenAI):
        """Create a new OpenAI assistant."""
        try:
            kwargs = {}
            for key, value in self.config['llm_config'].items():
                if key not in ["model", "provider"]:
                    kwargs[key] = value

            agent = OpenAIAssistantAgent(
                name=name,
                description="",
                client=model_client,
                model=self.config['llm_config']['model'],
                instructions=self.config.get('instructions', 'You are a helpful assistant.'),
                **kwargs
            )

            return agent
        except Exception as e:
            raise ValueError(f"Failed to create assistant: {str(e)}")
