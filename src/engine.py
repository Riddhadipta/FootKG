"""
FootKG Engine:
RDFLib-backed Knowledge Graph store and SPARQL execution engine with performance metrics.
"""

import os
import time
from typing import List, Dict, Any, Optional
from rdflib import Graph, Namespace, URIRef, Literal

FOOTKG = Namespace("http://tib.eu/footkg/ontology#")
FOOTRES = Namespace("http://tib.eu/footkg/resource/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")

class FootKGEngine:
    def __init__(self, ttl_path: Optional[str] = None):
        if ttl_path is None:
            ttl_path = os.path.join(os.path.dirname(__file__), "..", "data", "footkg_triples.ttl")
        self.ttl_path = os.path.abspath(ttl_path)
        self.graph = Graph()
        self.load_graph()

    def load_graph(self):
        t0 = time.time()
        self.graph.parse(self.ttl_path, format="turtle")
        self.load_time_ms = round((time.time() - t0) * 1000, 2)
        print(f"Loaded {len(self.graph)} triples in {self.load_time_ms} ms from {self.ttl_path}")

    def query(self, sparql_str: str) -> Dict[str, Any]:
        """
        Executes a SPARQL query and returns results along with execution latency.
        """
        t0 = time.time()
        res = self.graph.query(sparql_str)
        latency_ms = round((time.time() - t0) * 1000, 2)
        
        rows = []
        for row in res:
            row_dict = {}
            for var in res.vars:
                val = row[var]
                if val is not None:
                    # Clean up representation
                    if isinstance(val, URIRef):
                        row_dict[str(var)] = str(val).split("/")[-1].split("#")[-1]
                    elif isinstance(val, Literal):
                        row_dict[str(var)] = val.toPython()
                    else:
                        row_dict[str(var)] = str(val)
                else:
                    row_dict[str(var)] = None
            rows.append(row_dict)
            
        return {
            "results": rows,
            "count": len(rows),
            "latency_ms": latency_ms,
            "vars": [str(v) for v in res.vars] if res.vars else []
        }

    def get_summary_stats(self) -> Dict[str, int]:
        """
        Computes high-level KG entity and relationship metrics.
        """
        q = """
        PREFIX footkg: <http://tib.eu/footkg/ontology#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT 
            (COUNT(DISTINCT ?p) AS ?players)
            (COUNT(DISTINCT ?t) AS ?teams)
            (COUNT(DISTINCT ?m) AS ?managers)
            (COUNT(DISTINCT ?r) AS ?roles)
            (COUNT(DISTINCT ?z) AS ?zones)
        WHERE {
            { ?p a footkg:Player }
            UNION
            { ?t a footkg:ClubTeam }
            UNION
            { ?m a footkg:Manager }
            UNION
            { ?r rdfs:subClassOf* footkg:TacticalRole }
            UNION
            { ?z a footkg:PitchZone }
        }
        """
        player_count = len(list(self.graph.subjects(FOOTKG.playerName, None)))
        team_count = len(list(self.graph.subjects(None, FOOTRES.Club_ManchesterCity))) + 12 # approx clubs
        triple_count = len(self.graph)
        return {
            "total_triples": triple_count,
            "total_players": player_count,
            "graph_load_time_ms": self.load_time_ms
        }
