# Memory in AI Agents

## Overview

Memory in AI agents serves as the bridge between raw computational power and meaningful, contextual interactions. Unlike traditional software that relies on databases or caches, agent memory systems are designed to mimic aspects of human memory, allowing agents to maintain context, learn from experiences, and make informed decisions.

## Types of Memory

### Working Memory (Short-Term)

Working memory in an AI agent is the content of the agent's context window—the complete set of information that is sent to the LLM in a single prompt. This is how the agent "puts everything together": by accumulating all relevant information into one long string (or structured message sequence) that the LLM can process at once.

A typical working memory window for an agent includes, in order:

1. **System Message / Instructions**: The agent's core role, rules, and behavioral guidelines.
2. **Task Description**: The specific task or user request the agent is currently working on.
3. **Contextual Information**: Any relevant context, such as:
   - Results from tool calls (e.g., API responses, database lookups)
   - Retrieved knowledge from semantic or episodic memory
   - Summaries of previous interactions or important facts
4. **Conversation History**: The most recent exchanges between the user and the agent, often truncated to fit within the window.
5. **Temporary Calculations or Reasoning Steps**: Any intermediate results or scratchpad notes needed for the current reasoning process.

All of this information is concatenated (or structured as a list of messages) in a specific order—usually starting with the system message, followed by the task, then context, and finally the most recent conversation turns. The total size of this working memory is limited by the LLM's context window (typically 4K to 32K tokens), so agents must manage what to include and what to omit or summarize to stay within these bounds.

### Semantic Memory (Knowledge)

Semantic memory stores factual knowledge and understanding. This is where agents keep their "knowledge of the world," including:

- Domain-specific information
- Learned concepts and relationships
- Reference materials and documentation
- Organizational knowledge

In practice, semantic memory is often implemented through vector stores and retrieval systems. Here's a simplified version of HIVE's semantic memory implementation:

```python
class SemanticMemory(BaseMemoryType):
    def generate_with_autogen(self) -> Memory:
        """Initialize the vector store for semantic memory."""
        return ChromaDBVectorMemory(config=PersistentChromaDBVectorMemoryConfig(
            collection_name=self.name,
            persistence_path="./chroma_db",
            k=2,  # Number of results to retrieve
            score_threshold=0.4,  # Minimum similarity score
        ))
    
    async def load_with_langchain(self, content: List[str], verbose: bool = False):
        """Process and store content with intelligent chunking."""
        chunker = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Characters per chunk
            chunk_overlap=200,  # Overlap between chunks
            length_function=len,
        )

        for source in content:
            chunks = chunker.split_text(source)
            for chunk in chunks:
                await self.memory.add(MemoryContent(
                    content=chunk,
                    mime_type=MemoryMimeType.TEXT,
                    metadata={"source": source}
                ))
```

This implementation showcases several key concepts:

1. **Vector Store Integration**: Using ChromaDB for efficient similarity search
2. **Intelligent Chunking**: Breaking content into manageable pieces while preserving context
3. **Metadata Tracking**: Maintaining source information for retrieved content
4. **Configurable Retrieval**: Adjustable parameters for precision vs. recall

### Episodic Memory (Experience)

Episodic memory captures the agent's experiences and interactions. This includes:

- Past conversations and outcomes
- User preferences and behaviors
- Problem-solving attempts (both successful and failed)
- Temporal sequences of events

This type of memory enables agents to learn from experience and maintain consistency across interactions.

### Procedural Memory (Skills)

Procedural memory stores the "how-to" knowledge - the methods and procedures for completing tasks. This includes:

- Workflow patterns
- Standard operating procedures
- Learned optimization strategies
- Tool usage patterns

## Memory Management Techniques

### Chunking

Chunking is a fundamental technique for managing large amounts of information in AI systems. It's similar to how humans break down phone numbers into smaller groups of digits for easier recall.

**Purpose and Benefits:**
1. Manages context window limitations
2. Improves information retrieval accuracy
3. Enables efficient processing of large documents
4. Maintains semantic coherence

**Types of Chunking:**

1. **Token-based Chunking**
   - Splits content based on token count
   - Best for: Working with specific LLM context windows
   - Challenge: May break semantic units

2. **Semantic Chunking**
   - Splits content based on meaning
   - Best for: Maintaining context and coherence
   - Challenge: More complex to implement

3. **Structural Chunking**
   - Uses document structure (paragraphs, sections)
   - Best for: Formatted documents, code, documentation
   - Challenge: Requires consistent document structure

**HIVE's Chunking Implementation:**

HIVE implements chunking through the `load_with_langchain()` method in memory classes that extend `BaseMemoryType`. The implementation uses LangChain's `RecursiveCharacterTextSplitter` for intelligent text processing:

```python
async def load_with_langchain(self, content: List[str], verbose: bool = False):
    """Process and store content with intelligent chunking."""
    chunker = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Characters per chunk
        chunk_overlap=200,  # Overlap between chunks
        length_function=len,
    )

    for source in content:
        chunks = chunker.split_text(source)
        for chunk in chunks:
            await self.memory.add(MemoryContent(
                content=chunk,
                mime_type=MemoryMimeType.TEXT,
                metadata={"source": source}
            ))
```

**Key Features of HIVE's Chunking:**

1. **LangChain Integration**: Uses `RecursiveCharacterTextSplitter` for intelligent text splitting that preserves semantic meaning
2. **Configurable Parameters**:
   - `chunk_size`: Number of characters per chunk (default: 1000)
   - `chunk_overlap`: Overlap between chunks to maintain context (default: 200)
   - `length_function`: Function to measure chunk size (default: `len`)
3. **Metadata Preservation**: Each chunk maintains source information for traceability
4. **Async Processing**: Handles content loading asynchronously for better performance
5. **Document Type Support**: Works with various document types including PDFs and text files

**Configuration-Driven Chunking:**

Chunking parameters can be configured through YAML configuration files, allowing customization without code changes:

```yaml
semantic_memory:
  source: "./data/documents"
  source_type: "directory"
  chunking_config:
    chunk_size: 1000
    chunk_overlap: 200
    length_function: "len"
```

**Integration with Document Processing:**

The chunking system is integrated into HIVE's document processing pipeline:

```python
async def _index_documents(self, sources: List[str], verbose: bool = False) -> None:
    for source in sources:
        if source.endswith(".pdf"):
            pdf_loader = PyPDFLoader(source)
            pages = pdf_loader.load()
            await self.load_with_langchain([pages], verbose)
        else:
            with open(source, "r", encoding="utf-8") as f:
                content = f.read()
                await self.load_with_langchain([content], verbose)
```

This implementation ensures that chunking is applied consistently across different document types while maintaining the semantic integrity of the content.

### Memory Compression

Memory compression helps manage large amounts of information efficiently. Unlike traditional data compression, AI memory compression focuses on preserving semantic meaning while reducing token usage.

**Compression Strategies:**

1. **Summarization**
   - Creates concise versions of longer content
   - Preserves key information and context
   - Useful for long-term storage

2. **Information Distillation**
   - Extracts essential concepts and relationships
   - Removes redundant or less important details
   - Maintains core meaning

3. **Progressive Compression**
   - More aggressive compression for older memories
   - Maintains detailed recent information
   - Balances storage and accessibility

### Memory Retrieval

Effective memory retrieval is crucial for agent performance. The goal is to surface relevant information when needed without overwhelming the agent's working memory.

In HIVE, memory retrieval is built into the base memory system:

```python
class BaseMemoryType(ABC):
    async def index_from_source(self, content: List[str] = None):
        """Index content from various sources."""
        source_type = self.config.get("source_type", "content")
        source = self.config.get("source", content)
        
        if source_type == "directory":
            await self._index_directory(source)
        elif source_type == "files":
            await self._index_documents(source)
        elif source_type == "content":
            await self.load_with_langchain(source)
    
    async def _index_documents(self, sources: List[str]):
        """Process different document types."""
        for source in sources:
            if source.endswith(".pdf"):
                pages = PyPDFLoader(source).load()
                await self.load_with_langchain([pages])
            else:
                with open(source, "r") as f:
                    await self.load_with_langchain([f.read()])
```

This implementation demonstrates:
1. **Flexible Source Handling**: Support for directories, files, or raw content
2. **Document Type Support**: Built-in handling for PDFs and text files
3. **Extensible Design**: Easy to add support for new document types

## Best Practices

1. **Memory Organization**
   - Structure memories by type and importance
   - Implement clear retention policies
   - Regular cleanup of outdated information

2. **Context Management**
   - Maintain relevant context without overflow
   - Balance detail versus summary
   - Consider temporal relevance

3. **Performance Optimization**
   - Monitor memory usage patterns
   - Implement caching for frequent access
   - Regular performance audits

4. **Security and Privacy**
   - Clear policies for sensitive information
   - Regular memory sanitization
   - Access control implementation

## Common Challenges and Solutions

1. **Context Window Limitations**
   - Challenge: Limited space for active memory
   - Solution: Efficient chunking and compression
   - Strategy: Progressive summarization

2. **Retrieval Accuracy**
   - Challenge: Finding truly relevant information
   - Solution: Multi-stage retrieval systems
   - Strategy: Context-aware filtering

3. **Memory Coherence**
   - Challenge: Maintaining consistent knowledge
   - Solution: Regular memory consolidation
   - Strategy: Cross-reference validation

4. **Scale and Performance**
   - Challenge: Managing large memory systems
   - Solution: Tiered storage architecture
   - Strategy: Predictive caching

## Next Steps

After understanding memory systems:
1. Explore memory integration patterns
2. Study memory optimization techniques
3. Learn about memory security best practices