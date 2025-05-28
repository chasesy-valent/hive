import os
import aiofiles
from typing import List, Generic, TypeVar
from typing_extensions import override
from abc import ABC, abstractmethod
from autogen_core.memory import Memory, MemoryContent, MemoryMimeType, MemoryQueryResult, UpdateContextResult, ListMemory
from autogen_core.model_context import ChatCompletionContext
from autogen_core import CancellationToken
from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
from hive import RetrievalMemory

# def load_persistent_chromadb_memory(collection_name: str,persistence_path: str):
#     return ChromaDBVectorMemory(
#         config=PersistentChromaDBVectorMemoryConfig(
#             collection_name=collection_name,
#             persistence_path=persistence_path,
#             k=3,  # Return top 3 results
#             score_threshold=0.4,  # Minimum similarity score
#         )
#     )

class RAGMemory(RetrievalMemory[ChromaDBVectorMemory]):
    def __init__(self, collection_name: str, persistence_path: str) -> None:
        memory = ChromaDBVectorMemory(config=PersistentChromaDBVectorMemoryConfig(
            collection_name=collection_name,
            persistence_path=persistence_path,
            k=3,  # Return top 3 results
            score_threshold=0.4,  # Minimum similarity score
        ))
        super().__init__(memory)
    
    async def populate(self, directory: str = None, files: List[str] = None, verbose: bool = False) -> None:
        """
        Populate the memory with documents from a directory or a list of files.
        Note: Either directory or files must be provided, but not both.

        Args:
            directory (str, optional): The directory to index. Defaults to None.
            files (List[str], optional): The list of files to index. Defaults to None.
            verbose (bool, optional): Whether to print verbose output. Defaults to False.
        """
        if directory is not None and files is not None:
            raise ValueError("Cannot provide both directory and files.")
        
        if directory is not None:
            await self._index_directory(directory, verbose)
        elif files is not None:
            await self._index_documents(files, verbose)
        else:
            raise ValueError("Either directory or files must be provided.")
    
    async def _index_directory(self, directory: str, verbose: bool = False) -> None:
        if verbose: print(f"--------------------------------\nIndexing directory (recursively): {directory}")
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
                chunks = await self._chunk(content)
                for i, chunk in enumerate(chunks):
                    await self.add(chunk, {"source": source, "chunk_index": i, "content": content})
            
            if verbose: print(f"> Indexed {len(chunks)} chunks from {source}")
            total_chunks += len(chunks)
            
        if verbose: print(f"Indexed {total_chunks} chunks from {len(sources)} sources.")
    
    @override
    async def _chunk_content(self, content: str) -> List[str]:
        chunks: list[str] = []
        for i in range(0, len(content), 1500):
            chunk = content[i : i + 1500]
            chunks.append(chunk.strip())
        return chunks

class ChatMemory(ListMemory):
    def __init__(self, name: str | None = None, memory_contents: List[MemoryContent] | None = []) -> None:
        super().__init__(name, memory_contents)
    
    @override
    async def add(self, content: List[str]) -> None:
        for c in content:
            memory_content = MemoryContent(content=c, mime_type=MemoryMimeType.TEXT)
            await super().add(memory_content)

class DocumentIndexer:
    def __init__(self, memory: Memory) -> None:
        self.memory = memory
    
    async def _index_directory(self, directory: str, verbose: bool = False) -> None:
        if verbose: print(f"--------------------------------\nIndexing directory (recursively): {directory}")
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path)
        await self._index_documents(files, verbose)

        if verbose: print(f"--------------------------------")

    async def index_documents(self, sources: List[str], verbose: bool = False) -> None:
        total_chunks = 0
        for source in sources:
            chunks = await self.index_document(source, verbose)
            total_chunks += len(chunks)
            
        if verbose: print(f"Indexed {total_chunks} chunks from {len(sources)} sources.")
    
    async def index_document(self, source: str, verbose: bool = False) -> None:
        chunks = await self._chunk_file(source)
        for i, chunk in enumerate(chunks):
            await self._add_to_memory(chunk, {"source": source, "chunk_index": i})
        
        if verbose: print(f"> Indexed {len(chunks)} chunks from {source}")
        return chunks

    async def _chunk_file(self, source: str) -> List[str]:
        async with aiofiles.open(source, "r", encoding="utf-8") as f:
            content = await f.read()
        
        chunks: list[str] = []
        for i in range(0, len(content), 1500):
            chunk = content[i : i + 1500]
            chunks.append(chunk.strip())
        return chunks
    
    async def _add_to_memory(self, chunk: str, metadata: dict) -> None:
        await self.memory.add(MemoryContent(
            content=chunk,
            mime_type=MemoryMimeType.TEXT,
            metadata=metadata
        ))
    
    async def clear(self) -> None:
        await self.memory.clear()
    
    async def close(self) -> None:
        await self.memory.close()