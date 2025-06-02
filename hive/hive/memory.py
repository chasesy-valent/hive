from autogen_core.memory import Memory

from typing import List
from abc import ABC, abstractmethod
import os
from langchain_community.document_loaders import PyPDFLoader

class BaseMemoryType(ABC):
    def __init__(self, name: str, config: dict):
        self.name = name
        self._load_config(config)
        self.memory: Memory = self.generate_with_autogen()
    
    def _load_config(self, config: dict):
        # ensure agent name is located in config file
        if self.name not in config:
            raise ValueError(f"Memory {self.name} not found in config file.")
        self.config = config[self.name]
    
    @abstractmethod
    def generate_with_autogen(self, name: str):
        """Generate the agent using autogen. Must be implemented by child classes."""
        pass
        
    async def index_from_source(self, content: List[str] = None, verbose: bool = False) -> None:
        source_type = self.config.get("source_type", "content")
        source = self.config.get("source", content)
        if source is None:
            raise ValueError(f"Source not found in config file for memory {self.name}.")
            
        if source_type == "directory":
            if not os.path.isdir(source):
                raise ValueError(f"Directory {source} does not exist.")
            await self._index_directory(source, verbose)
        elif source_type == "files":
            if not all(os.path.isfile(file) for file in source):
                raise ValueError(f"Files {source} do not exist. Must be a list of file paths.")
            await self._index_documents(source, verbose)
        elif source_type == "content":
            if not isinstance(source, list):
                raise ValueError(f"Content must be a list of strings.")
            if not all(isinstance(item, str) for item in source):
                raise ValueError(f"Content must be a list of strings.")
            await self.load_with_langchain(source, verbose)
        else:
            raise ValueError(f"Invalid index source type: {source_type}. Must be one of: \"directory\", \"files\", or \"content\".")

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
            # if file is a pdf
            if source.endswith(".pdf"):
                pdf_loader = PyPDFLoader(source)
                pages = pdf_loader.load()
                await self.load_with_langchain([pages], verbose)
            else:
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