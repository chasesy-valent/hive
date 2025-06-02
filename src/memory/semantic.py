from hive import BaseMemoryType
from autogen_core.memory import Memory, MemoryContent, MemoryMimeType
from autogen_ext.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from typing import List
from typing_extensions import override

class SemanticMemory(BaseMemoryType):
    @override
    def generate_with_autogen(self) -> Memory:
        retrieval_config = self.config.get("retrieval_config", {})
        return ChromaDBVectorMemory(config=PersistentChromaDBVectorMemoryConfig(
            collection_name=self.name,
            persistence_path=retrieval_config.get("persistence_path", "./chroma_db"),
            k=retrieval_config.get("k", 2),
            score_threshold=retrieval_config.get("score_threshold", 0.4),
        ))
    
    @override
    async def load_with_langchain(self, content: List[str], verbose: bool = False) -> None:
        chunking_config = self.config.get("initialization_config", {}).get("chunking_config", {})
        chunker = RecursiveCharacterTextSplitter(
            chunk_size=chunking_config.get("chunk_size", 1000),
            chunk_overlap=chunking_config.get("chunk_overlap", 200),
            length_function=len,
            is_separator_regex=False,
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