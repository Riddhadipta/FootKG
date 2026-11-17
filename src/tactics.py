"""
FootKG Tactics Module:
Analyzes formation matchups, in-possession structural transitions,
spatial zone vulnerabilities, and automated tactical counter-strategies.
"""

from typing import Dict, Any, List
from .engine import FootKGEngine

class FootKGTactics:
    def __init__(self, engine: FootKGEngine):
        self.engine = engine

    def get_all_teams(self) -> List[Dict[str, Any]]:
        query = """
        PREFIX footkg: <http://tib.eu/footkg/ontology#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?team ?teamName ?managerName ?systemName ?formationName
        WHERE {
            ?team a footkg:ClubTeam ;
                  rdfs:label ?teamName ;
                  footkg:managedBy ?manager .
            ?manager rdfs:label ?managerName ;
                     footkg:employsSystem ?system ;
                     footkg:utilizesFormation ?formation .
            ?system rdfs:label ?systemName .
            ?formation rdfs:label ?formationName .
        }
        ORDER BY ?teamName
        """
        return self.engine.query(query)["results"]

    def analyze_tactical_matchup(self, opponent_team_id: str) -> Dict[str, Any]:
        """
        Reason over opponent's manager, nominal formation, in-possession transition,
        vulnerable pitch zones, and recommend counter-formations and attacking roles.
        """
        if not opponent_team_id.startswith("footres:"):
            opp_uri = f"footres:{opponent_team_id}"
        else:
            opp_uri = opponent_team_id

        query = f"""
        PREFIX footkg: <http://tib.eu/footkg/ontology#>
        PREFIX footres: <http://tib.eu/footkg/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?oppTeamName ?managerName ?systemName ?formationName ?transFormationName
               ?vulnZone ?vulnZoneDesc ?counterFormation ?counterFormName
        WHERE {{
            {opp_uri} rdfs:label ?oppTeamName ;
                      footkg:managedBy ?manager .
            ?manager rdfs:label ?managerName ;
                     footkg:employsSystem ?system ;
                     footkg:utilizesFormation ?formation .
            ?system rdfs:label ?systemName .
            ?formation rdfs:label ?formationName .

            OPTIONAL {{
                ?formation footkg:transitionsToInPossession ?transFormation .
                ?transFormation rdfs:label ?transFormationName .
            }}

            # Spatial vulnerabilities left in transition
            ?formation footkg:leavesVulnerableZone ?vulnZone .
            ?vulnZone footkg:zoneDescription ?vulnZoneDesc .

            # Formations that counter this setup
            OPTIONAL {{
                ?counterFormation footkg:exploitsWeaknessIn ?formation ;
                                  rdfs:label ?counterFormName .
            }}
        }}
        """
        res = self.engine.query(query)

        if not res["results"]:
            return {"error": f"No tactical data found for {opponent_team_id}"}

        first = res["results"][0]
        vuln_zones = list({r["vulnZoneDesc"] for r in res["results"] if r.get("vulnZoneDesc")})
        counter_forms = list({r["counterFormName"] for r in res["results"] if r.get("counterFormName")})

        # Find players in the KG who operate in these attacking zones
        exploit_query = f"""
        PREFIX footkg: <http://tib.eu/footkg/ontology#>
        PREFIX footres: <http://tib.eu/footkg/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?player ?playerName ?roleName ?inZoneDesc ?xG ?xA
        WHERE {{
            {opp_uri} footkg:managedBy/footkg:utilizesFormation/footkg:leavesVulnerableZone ?vZone .
            ?player a footkg:Player ;
                    footkg:playerName ?playerName ;
                    footkg:primaryRole ?role ;
                    footkg:inPossessionZone ?vZone ;
                    footkg:xGPer90 ?xG ;
                    footkg:xAPer90 ?xA .
            ?role rdfs:label ?roleName .
            ?vZone footkg:zoneDescription ?inZoneDesc .
        }}
        ORDER BY DESC(?xG)
        LIMIT 5
        """
        exploit_res = self.engine.query(exploit_query)

        return {
            "opponent_team": first["oppTeamName"],
            "manager": first["managerName"],
            "tactical_system": first["systemName"],
            "base_formation": first["formationName"],
            "in_possession_transition": first.get("transFormationName", "Maintains base structure"),
            "vulnerable_transition_zones": vuln_zones,
            "recommended_counter_formations": counter_forms if counter_forms else ["High-Press 4-3-3 with Touchline Wingers"],
            "key_exploit_players": exploit_res["results"],
            "sparql_used": query,
            "latency_ms": res["latency_ms"]
        }
