from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.agents import MessageFilterAgent, MessageFilterConfig, PerSourceFilter
from typing_extensions import override
from hive import Pipeline

class PoemWriterPipeline(Pipeline):
    def __init__(self, **agents):
        name = "poem_writer"
        description = "A pipeline that uses multiple agents to write a poem about the given context."
        super().__init__(name, description, **agents)

    @override
    def build(self, writer, editor1, editor2, final_reviewer):
        filtered_editor1 = MessageFilterAgent(
            name=editor1.name,
            wrapped_agent=editor1,
            filter=MessageFilterConfig(per_source=[PerSourceFilter(source=writer.name, position="last", count=1)])
        )
        filtered_editor2 = MessageFilterAgent(
            name=editor2.name,
            wrapped_agent=editor2,
            filter=MessageFilterConfig(per_source=[PerSourceFilter(source=writer.name, position="last", count=1)])
        )

        # Build the workflow graph
        builder = DiGraphBuilder()
        builder.add_node(writer).add_node(filtered_editor1).add_node(filtered_editor2).add_node(final_reviewer)
        
        # Fan-out from writer to editor1 and editor2
        builder.add_edge(writer, editor1)
        builder.add_edge(writer, editor2)

        # Fan-in both editors into final reviewer
        builder.add_edge(editor1, final_reviewer)
        builder.add_edge(editor2, final_reviewer)

        # build the final flow for execution
        # Build and validate the graph
        graph = builder.build()

        # Create the flow
        self.participants = builder.get_participants()
        self.pipeline = GraphFlow(
            participants=self.participants,
            graph=graph,
        )