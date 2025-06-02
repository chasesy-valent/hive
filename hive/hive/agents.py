from autogen_core.memory import Memory
from abc import ABC, abstractmethod
from typing import List

class BaseAgentType(ABC):
    def __init__(self):
        self.config = None
    
    def initialize(self, name: str, config: dict, model_client, memory: List[Memory]):
        """Initialize the agent with configuration."""
        self._load_config(name, config)
        self.tool_configs = self.config.get('tool_config', {})
        return self.generate_with_autogen(name, model_client, memory)
    
    @abstractmethod
    def generate_with_autogen(self, name, model_client, memory: List[Memory]):
        """Generate the agent using autogen. Must be implemented by child classes."""
        pass
    
    def _load_config(self, name: str, config: dict):
        # ensure agent name is located in config file
        if name not in config:
            raise ValueError(f"Agent {name} not found in config file.")
        self.config = config[name]