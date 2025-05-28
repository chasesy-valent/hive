from autogen_core.memory import Memory

from typing import List, Literal
from abc import ABC, abstractmethod
import os
import yaml

class BaseMemoryType(ABC):
    def __init__(self, name: str, config_path: str):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            self._load_config(name, config)
        self.memory: Memory = self.generate_with_autogen(name)
    
    def _load_config(self, name: str, config: dict):
        # ensure agent name is located in config file
        if name not in config:
            raise ValueError(f"Agent {name} not found in config file.")
        self.config = config[name]
    
    @abstractmethod
    def generate_with_autogen(self, name: str):
        """Generate the agent using autogen. Must be implemented by child classes."""
        pass
        
    async def index(self, source: str | List[str], type: Literal["directory", "files", "content"] = "content", verbose: bool = False) -> None:
        """
        Index a memory instance from various sources.

        Args:
            source (str | List[str]): The source to index. This can be:
                - For type="directory": A string path to a directory containing files to index
                - For type="files": A list of file paths to index
                - For type="content": A list of text content strings to index directly
            type (Literal["directory", "files", "content"]): The type of source to index:
                - "directory": Index all files in a directory recursively
                - "files": Index specific files provided in a list
                - "content": Index raw text content directly without file I/O
            verbose (bool, optional): Whether to print progress information. Defaults to False.
        """
        if type == "directory":
            await self._index_directory(source, verbose)
        elif type == "files":
            await self._index_documents(source, verbose)
        elif type == "content":
            await self.load_with_langchain(source, verbose)
        else:
            raise ValueError(f"Invalid index source type: {type}. Must be one of: \"directory\", \"files\", or \"content\".")

    async def _index_directory(self, directory: str, verbose: bool = False) -> None:
        print(f"--------------------------------\nIndexing directory (recursively): {directory}")
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path)
        await self._index_documents(files, verbose)
    
    async def _index_documents(self, sources: List[str], verbose: bool = False) -> None:
        total_chunks = 0
        for source in sources:
            with open(source, "r", encoding="utf-8") as f:
                content = f.read()
                await self.load_with_langchain([content], verbose)
    
    @abstractmethod
    async def load_with_langchain(self, content: List[str], verbose: bool = False) -> None:
        """
        Load content into memory using LangChain.
        
        Args:
            content (List[str]): Content to load into memory
            verbose (bool, optional): Whether to print progress information. Defaults to False.
            
        This method must be implemented by child classes.
        """
        raise NotImplementedError("load_with_langchain must be implemented by child classes")
    
    async def clear(self):
        await self.memory.clear()

    async def close(self):
        await self.memory.close()