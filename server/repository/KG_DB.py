import re
from neo4j import GraphDatabase
from config.Config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from models.GraphModels import KnowledgeGraph

class Neo4jGraphDB:
    def __init__(self):
        """Initializes the Neo4j Python Driver."""
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def close(self):
        """Closes the connection to the database."""
        if self.driver:
            self.driver.close()

    def sanitize_relationship_name(self, name: str) -> str:
        """
        Cypher does not allow parameterized relationship types (e.g. `-[r:$type]->`).
        We must securely format the string directly into the query, which means we 
        MUST sanitize the string to prevent Cypher injection.
        """
        # Convert to uppercase and replace any non-alphanumeric character with an underscore
        clean_name = re.sub(r'[^A-Z0-9_]', '_', name.upper())
        
        # Ensure it doesn't start with a number (valid Cypher identifier requirement)
        if clean_name and clean_name[0].isdigit():
            clean_name = "REL_" + clean_name
            
        return clean_name if clean_name else "RELATED_TO"

    def insert_graph(self, kg: KnowledgeGraph):
        """
        Iterates over the Pydantic KnowledgeGraph and idempotently inserts Nodes and Edges.
        """
        with self.driver.session() as session:
            # 1. Insert all Nodes safely
            for node in kg.nodes:
                session.execute_write(self._merge_node, node)
                
            # 2. Insert all Edges securely
            for edge in kg.edges:
                session.execute_write(self._merge_edge, edge)

    @staticmethod
    def _merge_node(tx, node):
        """
        Uses MERGE to ensure we never duplicate an entity.
        If it exists, we just update its properties.
        """
        query = """
        MERGE (n:Entity {id: $id})
        ON CREATE SET 
            n.name = $name, 
            n.type = $type, 
            n.description = $description,
            n.source_type = $source_type
        ON MATCH SET
            n.name = CASE WHEN $name <> "" THEN $name ELSE n.name END,
            n.type = CASE WHEN $type <> "" THEN $type ELSE n.type END,
            n.description = CASE WHEN $description <> "" THEN $description ELSE n.description END,
            n.source_type = CASE WHEN $source_type IS NOT NULL THEN $source_type ELSE n.source_type END
        """
        tx.run(query, 
               id=node.id, 
               name=node.name, 
               type=node.type, 
               description=node.description,
               source_type=node.source_type)

    def _merge_edge(self, tx, edge):
        """
        Finds the existing source and target nodes, and MERGEs the relationship between them.
        """
        rel_type = self.sanitize_relationship_name(edge.relationship_name)
        
        # We dynamically insert the relationship type (safely sanitized)
        query = f"""
        MATCH (source:Entity {{id: $source_id}})
        MATCH (target:Entity {{id: $target_id}})
        MERGE (source)-[r:`{rel_type}`]->(target)
        ON CREATE SET 
            r.description = $description,
            r.source_type = $source_type
        ON MATCH SET 
            r.description = CASE WHEN $description <> "" THEN $description ELSE r.description END,
            r.source_type = CASE WHEN $source_type IS NOT NULL THEN $source_type ELSE r.source_type END
        """
        tx.run(query,
               source_id=edge.source_node_id,
               target_id=edge.target_node_id,
               description=edge.description,
               source_type=edge.source_type
        )

    def get_subgraph(self, entities: list[str], limit: int = 50) -> list[str]:
        """
        Retrieves all immediate relationships for the requested entities.
        Returns a list of formatted string relationships (e.g. "Paris IS_LOCATED_IN France").
        """
        if not entities:
            return []
            
        with self.driver.session() as session:
            # Match any node whose name is in the list, and grab its relationships
            query = f"""
            MATCH (n:Entity)-[r]-(m:Entity)
            WHERE toLower(n.name) IN [e IN $entities | toLower(e)] OR toLower(m.name) IN [e IN $entities | toLower(e)]
            RETURN n.name AS source, type(r) AS rel, m.name AS target, r.description AS desc, r.source_type AS source_type
            LIMIT {limit}
            """
            result = session.run(query, entities=entities)
            
            graph_context = []
            for record in result:
                desc = f" ({record['desc']})" if record['desc'] else ""
                stype = f" [Source: {record['source_type']}]" if record['source_type'] else ""
                graph_context.append(f"{record['source']} -[{record['rel']}]-> {record['target']}{desc}{stype}")
                
            return list(set(graph_context))

    def get_causal_chain(self, entities: list[str], max_depth: int = 3, limit: int = 100) -> list[str]:
        """
        Retrieves multi-hop causal chains starting from the requested entities.
        """
        if not entities:
            return []
            
        with self.driver.session() as session:
            # Match paths of length 1 to max_depth consisting only of causal relationships
            query = f"""
            MATCH path = (n:Entity)-[rels:CAUSES|PREVENTS|ENABLES|RESULTS_IN*1..{max_depth}]->(m:Entity)
            WHERE toLower(n.name) IN [e IN $entities | toLower(e)]
            UNWIND relationships(path) AS r
            WITH startNode(r) AS start_node, r, endNode(r) AS end_node
            RETURN DISTINCT start_node.name AS source, type(r) AS rel, end_node.name AS target, r.description AS desc, r.source_type AS source_type
            LIMIT {limit}
            """
            result = session.run(query, entities=entities)
            
            chain_context = []
            for record in result:
                desc = f" ({record['desc']})" if record['desc'] else ""
                stype = f" [Source: {record['source_type']}]" if record['source_type'] else ""
                chain_context.append(f"{record['source']} -[{record['rel']}]-> {record['target']}{desc}{stype}")
                
            return list(set(chain_context))