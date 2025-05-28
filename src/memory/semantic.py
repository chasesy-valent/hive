from hive import BaseMemoryType
from autogen_core.memory import Memory, MemoryContent, MemoryMimeType
from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from typing import List
from typing_extensions import override

class SemanticMemory(BaseMemoryType):
    @override
    def generate_with_autogen(self, name: str) -> Memory:
        return ChromaDBVectorMemory(config=PersistentChromaDBVectorMemoryConfig(
            collection_name=name,
            persistence_path=self.config["persistence_path"],
            k=self.config["k"],
            score_threshold=self.config["score_threshold"],
        ))
    
    @override
    async def load_with_langchain(self, content: List[str], verbose: bool = False) -> None:
        chunker = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.config["headers_to_split_on"],
            strip_headers=False,
        )

        total_chunks = 0
        for i, source in enumerate(content):
            chunks = chunker.split_text(source)
            for j, chunk in enumerate(chunks):
                # Extract the text content from the Document object
                chunk_text = chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
                await self.memory.add(MemoryContent(
                    content=chunk_text, 
                    mime_type=MemoryMimeType.TEXT, 
                    metadata=chunk.metadata if hasattr(chunk, 'metadata') else {"source": source, "chunk_index": j}
                ))
                if verbose:
                    print(f"\n\nChunk {j}:\n{chunk_text}\n\n")

            total_chunks += len(chunks)
        
        print(f"> Indexed {total_chunks} chunks from {len(content)} sources.")