"""
FootKG Chemistry Module:
Calculates multi-hop network synergies between players based on shared clubs,
managers, national teams, and tactical pairings.
"""

from typing import Dict, Any, List
from .engine import FootKGEngine

class FootKGChemistry:
    def __init__(self, engine: FootKGEngine):
        self.engine = engine

    def get_player_connections(self, player_id: str) -> Dict[str, Any]:
        """
        Finds all players connected to a given player via direct chemistry,
        shared clubs, shared managers, or shared nationality.
        """
        if not player_id.startswith("footres:"):
            p_uri = f"footres:{player_id}"
        else:
            p_uri = player_id

        query = f"""
        PREFIX footkg: <http://tib.eu/footkg/ontology#>
        PREFIX footres: <http://tib.eu/footkg/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?p1Name ?connectedPlayer ?connectedName ?connectionType ?detail
        WHERE {{
            {p_uri} footkg:playerName ?p1Name .

            {{
                {p_uri} footkg:hasChemistryWith ?connectedPlayer .
                ?connectedPlayer footkg:playerName ?connectedName .
                BIND("Direct Tactical Synergy" AS ?connectionType)
                BIND("Established in-game spatial chemistry" AS ?detail)
            }}
            UNION
            {{
                {p_uri} footkg:playsFor ?club .
                ?connectedPlayer footkg:playsFor ?club ;
                                 footkg:playerName ?connectedName .
                ?club rdfs:label ?detail .
                FILTER(?connectedPlayer != {p_uri})
                BIND("Current Teammate" AS ?connectionType)
            }}
            UNION
            {{
                {p_uri} footkg:formerlyPlayedFor ?pastClub .
                ?connectedPlayer (footkg:formerlyPlayedFor|footkg:playsFor) ?pastClub ;
                                 footkg:playerName ?connectedName .
                ?pastClub rdfs:label ?detail .
                FILTER(?connectedPlayer != {p_uri})
                BIND("Shared Club Heritage" AS ?connectionType)
            }}
            UNION
            {{
                {p_uri} footkg:coachedBy ?manager .
                ?connectedPlayer footkg:coachedBy ?manager ;
                                 footkg:playerName ?connectedName .
                ?manager rdfs:label ?detail .
                FILTER(?connectedPlayer != {p_uri})
                BIND("Shared Coach / System Pedigree" AS ?connectionType)
            }}
            UNION
            {{
                {p_uri} footkg:nationality ?nat .
                ?connectedPlayer footkg:nationality ?nat ;
                                 footkg:playerName ?connectedName .
                FILTER(?connectedPlayer != {p_uri})
                BIND("National Team Synergy" AS ?connectionType)
                BIND(?nat AS ?detail)
            }}
        }}
        ORDER BY ?connectionType ?connectedName
        """
        res = self.engine.query(query)
        connections = res["results"]
        p_name = connections[0]["p1Name"] if connections else player_id

        return {
            "player": p_name,
            "connections": connections,
            "total_links": len(connections),
            "latency_ms": res["latency_ms"]
        }
