import json
from pydantic import BaseModel, Field
from typing import List

class Node(BaseModel):
    id: str = Field(description="A unique identifier for the entity (e.g. 'john_doe_1'). Must not contain spaces.")
    name: str = Field(description="The display name of the entity.")
    type: str = Field(description="The type or category of the entity (e.g., PERSON, ORGANIZATION, CONCEPT).")
    description: str = Field(description="A brief description of the entity based on the text.")
    source_type: str = Field(default=None, description="The modality source (e.g., pdf, image, video, raw_text).")

class Edge(BaseModel):
    source_node_id: str = Field(description="The ID of the source node.")
    target_node_id: str = Field(description="The ID of the target node.")
    relationship_name: str = Field(description="The type of relationship (e.g., WORKS_FOR, IS_A, RELATED_TO).")
    description: str = Field(description="A brief description explaining how they are related.")
    source_type: str = Field(default=None, description="The modality source (e.g., pdf, image, video, raw_text).")

class KnowledgeGraph(BaseModel):
    nodes: List[Node] = Field(default_factory=list, description="A list of nodes extracted from the text.")
    edges: List[Edge] = Field(default_factory=list, description="A list of edges connecting the nodes.")
