from autogen_ext.auth.azure import AzureTokenProvider
from autogen_ext.models.openai import OpenAIChatCompletionClient, AzureOpenAIChatCompletionClient
from autogen_ext.models.azure import AzureAIChatCompletionClient
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient

from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from openai import AsyncOpenAI

import os
import yaml
from typing import List

from hive.agents import BaseAgentType
from hive.memory import BaseMemoryType

class ComponentFactory:
    valid_providers = ["azure", "openai", "foundry", "anthropic", "ollama", "gemini", "openai_assistant_api"]

    def __init__(self, agent_config_path: str = ".config/agents.yml", memory_config_path: str = ".config/memory.yml"):
        self.model_clients = {}
        self.memory_resources = {}
        with open(agent_config_path, "r") as f:
            self.agent_config = yaml.safe_load(f)
        
        if os.path.exists(memory_config_path):
            with open(memory_config_path, "r") as f:
                self.memory_config = yaml.safe_load(f)
        else:
            self.memory_config = {}
    
    def create_agent(self, name: str, agent_type: BaseAgentType, memory: List[BaseMemoryType] = []):
        blank_agent = agent_type()

        model_client = self._update_clients(name)
        return blank_agent.initialize(name, self.agent_config, model_client, memory=[m.memory for m in memory])
    
    def load_memory(self, name: str, memory_type: BaseMemoryType):
        if name in self.memory_resources:
            return self.memory_resources[name]
        else:
            memory = memory_type(name, self.memory_config)
            self.memory_resources[name] = memory
            return memory
        
    def _update_clients(self, name: str):
        """Initialize the client for the agent."""
        llm_configs = self.agent_config[name]['llm_config']
        search_key = llm_configs['model'] if llm_configs['provider'] != "openai_assistant_api" else llm_configs['provider']
        # if the model client is already in the cache, return it
        if search_key in self.model_clients:
            return self.model_clients[search_key]
        else:
            model_client = self._create_model_client(llm_configs)
            self.model_clients[search_key] = model_client
            return model_client
    
    def _create_model_client(self, llm_configs: dict):
        model = llm_configs['model']
        provider = llm_configs['provider']
        
        # pass any additional parameters to the model client
        kwargs = {}
        for key, value in llm_configs.items():
            if key not in ["model", "provider"]:
                kwargs[key] = value
        
        if provider == "azure":
            print("NOT IMPLEMENTED. REQUIRES CONFIGURATION.")
            token_provider = AzureTokenProvider(DefaultAzureCredential(),"https://cognitiveservices.azure.com/.default")
            model_client = AzureOpenAIChatCompletionClient(
                azure_deployment="{your-azure-deployment}",
                model=model,
                api_version="2024-06-01",
                azure_endpoint="https://{your-custom-endpoint}.openai.azure.com/",
                azure_ad_token_provider=token_provider,
                **kwargs
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
                },
                **kwargs
            )
        elif provider == "openai":
            if os.getenv("OPENAI_API_KEY") is None:
                raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
            model_client = OpenAIChatCompletionClient(model=model, **kwargs)
        elif provider == "anthropic":
            if os.getenv("ANTHROPIC_API_KEY") is None:
                raise ValueError("ANTHROPIC_API_KEY is not set in the environment variables.")
            model_client = AnthropicChatCompletionClient(model=model, **kwargs)
        elif provider == "ollama":
            if os.getenv("OLLAMA_API_KEY") is None:
                raise ValueError("OLLAMA_API_KEY is not set in the environment variables.")
            model_client = OllamaChatCompletionClient(model=model, **kwargs)
        elif provider == "gemini":
            if os.getenv("GEMINI_API_KEY") is None:
                raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
            model_client = OpenAIChatCompletionClient(model=model, **kwargs)
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
        for memory in self.memory_resources.values():
            await memory.close()