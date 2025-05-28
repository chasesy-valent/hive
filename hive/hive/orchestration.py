from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.teams import DiGraphBuilder
from autogen_agentchat.messages import BaseChatMessage, TextMessage, StopMessage, BaseAgentEvent, ThoughtEvent, HandoffMessage
from autogen_core.models import CreateResult, AssistantMessage
from autogen_core.model_context import ChatCompletionContext
from autogen_agentchat.base import Response, TaskResult
from autogen_core import CancellationToken

from typing import Sequence, AsyncGenerator, List
from abc import ABC, abstractmethod

class Pipeline(BaseChatAgent):
    def __init__(self, name: str, description: str, **agents):
        super().__init__(name, description)
        # Pass through the agents dictionary to build using **agents
        # This allows child classes to unpack specific agents as parameters
        self.build(**agents)
    
    @abstractmethod
    def build(self, **agents):
        """Build the pipeline workflow.
        Child classes can unpack specific agents from **agents as needed.
        Example:
            def build(self, writer, editor1, editor2, **_):
                # Use writer, editor1, editor2 specifically
                pass
        """
        pass

    async def run_stream(self, task: str) -> str:
        """Run the pipeline directly on a given task."""
        return self.pipeline.run_stream(task=task)
    
    async def obfuscate_nonpipeline_agents(self, messages: Sequence[BaseChatMessage]) -> Sequence[BaseChatMessage]:
        """Obfuscate the messages from non-pipeline agents."""
        # Convert any external agent messages to TextMessages for context
        converted_messages = []
        for msg in messages:
            if msg.source not in self.participants and msg.source.lower() != "user":
                # Convert external agent message to TextMessage while preserving content
                converted_messages.append(TextMessage(
                    source="user",
                    content=f"Context from {msg.source}: {msg.content}"
                ))
            else:
                converted_messages.append(msg)
        
        return converted_messages
    
    async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
        """Run the pipeline within a multi-agent system."""
        obfuscated_messages = await self.obfuscate_nonpipeline_agents(messages)
        return await self.pipeline.run(task=obfuscated_messages, cancellation_token=cancellation_token)
    
    async def on_messages_stream(
        self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
        """Stream messages through the pipeline."""
        obfuscated_messages = await self.obfuscate_nonpipeline_agents(messages)
        stream = self.pipeline.run_stream(task=obfuscated_messages, cancellation_token=cancellation_token)
        final_messages = []
        
        async for message in stream: 
            if message not in obfuscated_messages and not isinstance(message, TaskResult):
                final_messages.append(message)
                if not isinstance(message, StopMessage):
                    yield message
        
        yield Response(chat_message=final_messages[-1], inner_messages=final_messages[:-1])
    
    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass
    
    @property
    def produced_message_types(self) -> Sequence[type[BaseChatMessage]]:
        return (TextMessage,)