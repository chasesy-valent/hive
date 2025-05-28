from autogen_ext.auth.azure import AzureTokenProvider
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from autogen_ext.models.azure import AzureAIChatCompletionClient
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.memory import Memory

from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from openai import AsyncOpenAI

import os
import yaml
from abc import ABC, abstractmethod
from typing import List

from hive.memory import BaseMemoryType

class BaseAgentType(ABC):
    def __init__(self):
        self.config = None
    
    def initialize(self, name: str, config: dict, model_client, memory: List[Memory] | None = None):
        """Initialize the agent with configuration."""
        self._load_config(name, config)
        if memory is not None:
            return self.generate_with_autogen(name, model_client, memory)
        return self.generate_with_autogen(name, model_client)
    
    @abstractmethod
    def generate_with_autogen(self, name, model_client, memory: List[Memory] | None = None):
        """Generate the agent using autogen. Must be implemented by child classes."""
        pass
    
    def _load_config(self, name: str, config: dict):
        # ensure agent name is located in config file
        if name not in config:
            raise ValueError(f"Agent {name} not found in config file.")
        self.config = config[name]

        # # check that all required parameters are present
        # required_params = ['client', 'instructions']
        # missing_params = [param for param in required_params if param not in self.config]
        # if missing_params:
        #     raise ValueError(f"Missing required parameters: {missing_params} for agent {name} in config file.")
        

class AgentFactory:
    valid_providers = ["azure", "openai", "foundry", "anthropic", "ollama", "gemini", "openai_assistant_api"]

    def __init__(self, config_path: str = ".config/agents.yml"):
        self.model_clients = {}
        self.memory_resources = {}
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

    def create(self, name: str, agent_type: BaseAgentType, memory: List[BaseMemoryType] = None):
        blank_agent = agent_type()

        model_client = self._update_clients(name)
        if memory is not None:
            return blank_agent.initialize(name, self.config, model_client, memory=[m.memory for m in memory])
        else:
            return blank_agent.initialize(name, self.config, model_client)
        
    def _update_clients(self, name: str):
        """Initialize the client for the agent."""
        model_name = self.config[name]['client']['model']
        provider = self.config[name]['client']['name']

        search_key = model_name if provider != "openai_assistant_api" else provider
        if search_key in self.model_clients:
            return self.model_clients[search_key]
        else:
            model_client = self._create_model_client(model_name, provider)
            self.model_clients[search_key] = model_client
            return model_client
    
    def _create_model_client(self, model: str, provider: str):
        if provider == "azure":
            print("NOT IMPLEMENTED. REQUIRES CONFIGURATION.")
            token_provider = AzureTokenProvider(DefaultAzureCredential(),"https://cognitiveservices.azure.com/.default")
            model_client = AzureOpenAIChatCompletionClient(
                azure_deployment="{your-azure-deployment}",
                model=model,
                api_version="2024-06-01",
                azure_endpoint="https://{your-custom-endpoint}.openai.azure.com/",
                azure_ad_token_provider=token_provider
            )
        elif provider == "foundry":
            print("NOT IMPLEMENTED. REQUIRES CONFIGURATION.")
            model_client = AzureAIChatCompletionClient(
                model="Phi-4",
                endpoint="https://models.inference.ai.azure.com",
                # To authenticate with the model you will need to generate a personal access token (PAT) in your GitHub settings.
                # Create your PAT token by following instructions here: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
                credential=AzureKeyCredential(os.environ["GITHUB_TOKEN"]),
                model_info={
                    "json_output": False,
                    "function_calling": False,
                    "vision": False,
                    "family": "unknown",
                    "structured_output": False,
                }
            )
        elif provider == "openai":
            if os.getenv("OPENAI_API_KEY") is None:
                raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
            model_client = OpenAIChatCompletionClient(model=model)
        elif provider == "anthropic":
            if os.getenv("ANTHROPIC_API_KEY") is None:
                raise ValueError("ANTHROPIC_API_KEY is not set in the environment variables.")
            model_client = AnthropicChatCompletionClient(model=model)
        elif provider == "ollama":
            if os.getenv("OLLAMA_API_KEY") is None:
                raise ValueError("OLLAMA_API_KEY is not set in the environment variables.")
            model_client = OllamaChatCompletionClient(model=model)
        elif provider == "gemini":
            if os.getenv("GEMINI_API_KEY") is None:
                raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
            model_client = OpenAIChatCompletionClient(model=model)
        elif provider == "openai_assistant_api":
            if os.getenv("OPENAI_API_KEY") is None:
                raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
            model_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            raise ValueError(f"Invalid provider: {provider}. Options are: {self.valid_providers}")
        return model_client
    
    async def close(self):
        for model_client in self.model_clients.values():
            await model_client.close()