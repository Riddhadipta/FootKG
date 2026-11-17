"""
FootKG QA Module (KGQA):
Natural Language Question Answering over the Football Knowledge Graph.
Converts user intents into validated SPARQL queries and synthesizes explanations.
"""

import re
from typing import Dict, Any, Optional
from .engine import FootKGEngine

class FootKGQA:
    def __init__(self, engine: FootKGEngine):
        self.engine = engine

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Parses user questions, routes to appropriate SPARQL templates,
        executes against the graph, and formats a human-readable response.
        """
        q_lower = question.lower().strip()
        sparql = None
        intent = "unknown"

        # 1. Replacement questions: e.g., "replace Rodri under 40M"
        if "replace" in q_lower or "alternative to" in q_lower or "successor" in q_lower:
            intent = "player_replacement"
            target = "Player_Rodri"
            if "zinchenko" in q_lower: target = "Player_OleksandrZinchenko"
            elif "saka" in q_lower: target = "Player_BukayoSaka"
            elif "rice" in q_lower: target = "Player_DeclanRice"
            elif "wirtz" in q_lower: target = "Player_FlorianWirtz"
            elif "bellingham" in q_lower: target = "Player_JudeBellingham"

            # Check budget
            budget = 40000000
            m_budget = re.search(r'(\d+)\s*(m|million|k)', q_lower)
            if m_budget:
                val = int(m_budget.group(1))
                unit = m_budget.group(2)
                budget = val * 1_000_000 if unit in ("m", "million") else val * 1_000

            sparql = f"""
            PREFIX footkg: <http://tib.eu/footkg/ontology#>
            PREFIX footres: <http://tib.eu/footkg/resource/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?candidateName ?clubName ?marketValue ?roleName ?progPasses
            WHERE {{
                footres:{target} footkg:primaryRole ?targetRole .
                ?candidate a footkg:Player ;
                           footkg:playerName ?candidateName ;
                           footkg:playsFor ?club ;
                           footkg:marketValueEUR ?marketValue ;
                           footkg:primaryRole ?role ;
                           footkg:progressivePassesPer90 ?progPasses .
                ?club rdfs:label ?clubName .
                ?role rdfs:label ?roleName .
                FILTER(?candidate != footres:{target})
                FILTER(?role = ?targetRole)
                FILTER(?marketValue <= {budget})
            }}
            ORDER BY DESC(?progPasses) ASC(?marketValue)
            LIMIT 5
            """

        # 2. Coached by / Manager lineage: e.g., "who played under Pep Guardiola?"
        elif "coached by" in q_lower or "played under" in q_lower or "manager" in q_lower:
            intent = "coach_lineage"
            coach = "Manager_PepGuardiola"
            if "arteta" in q_lower: coach = "Manager_MikelArteta"
            elif "klopp" in q_lower: coach = "Manager_JurgenKlopp"
            elif "alonso" in q_lower: coach = "Manager_XabiAlonso"
            elif "ancelotti" in q_lower: coach = "Manager_CarloAncelotti"

            sparql = f"""
            PREFIX footkg: <http://tib.eu/footkg/ontology#>
            PREFIX footres: <http://tib.eu/footkg/resource/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?playerName ?clubName ?roleName ?managerName
            WHERE {{
                ?player a footkg:Player ;
                        footkg:playerName ?playerName ;
                        footkg:coachedBy footres:{coach} ;
                        footkg:playsFor ?club ;
                        footkg:primaryRole ?role .
                footres:{coach} rdfs:label ?managerName .
                ?club rdfs:label ?clubName .
                ?role rdfs:label ?roleName .
            }}
            ORDER BY ?playerName
            """

        # 3. Countering tactics / Weakness: e.g., "how to counter Manchester City?" or "vulnerable zones of 4-3-3"
        elif "counter" in q_lower or "vulnerab" in q_lower or "weakness" in q_lower:
            intent = "tactical_counter"
            team = "Club_ManchesterCity"
            if "arsenal" in q_lower: team = "Club_Arsenal"
            elif "leverkusen" in q_lower: team = "Club_BayerLeverkusen"
            elif "atletico" in q_lower: team = "Club_AtleticoMadrid"
            elif "inter" in q_lower: team = "Club_InterMilan"

            sparql = f"""
            PREFIX footkg: <http://tib.eu/footkg/ontology#>
            PREFIX footres: <http://tib.eu/footkg/resource/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?teamName ?managerName ?formationName ?vulnZoneDesc ?counterFormName
            WHERE {{
                footres:{team} rdfs:label ?teamName ;
                               footkg:managedBy ?mgr .
                ?mgr rdfs:label ?managerName ;
                     footkg:utilizesFormation ?form .
                ?form rdfs:label ?formationName ;
                      footkg:leavesVulnerableZone ?vz .
                ?vz footkg:zoneDescription ?vulnZoneDesc .
                OPTIONAL {{
                    ?counterForm footkg:exploitsWeaknessIn ?form ;
                                 rdfs:label ?counterFormName .
                }}
            }}
            """

        # 4. Chemistry / Synergy: e.g., "who has chemistry with Saka?"
        elif "chemistry" in q_lower or "synerg" in q_lower or "connect" in q_lower:
            intent = "chemistry_network"
            player = "Player_BukayoSaka"
            if "rodri" in q_lower: player = "Player_Rodri"
            elif "zinchenko" in q_lower: player = "Player_OleksandrZinchenko"
            elif "bellingham" in q_lower: player = "Player_JudeBellingham"

            sparql = f"""
            PREFIX footkg: <http://tib.eu/footkg/ontology#>
            PREFIX footres: <http://tib.eu/footkg/resource/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?targetName ?connectedName ?connection
            WHERE {{
                footres:{player} footkg:playerName ?targetName .
                {{
                    footres:{player} footkg:hasChemistryWith ?other .
                    ?other footkg:playerName ?connectedName .
                    BIND("Direct Tactical Link" AS ?connection)
                }}
                UNION
                {{
                    footres:{player} footkg:playsFor ?club .
                    ?other footkg:playsFor ?club ;
                           footkg:playerName ?connectedName .
                    FILTER(?other != footres:{player})
                    BIND("Current Club Teammate" AS ?connection)
                }}
            }}
            LIMIT 10
            """

        # 5. Role & Stats: e.g., "find inverted fullbacks" or "best deep-lying playmakers"
        else:
            intent = "role_discovery"
            sparql = """
            PREFIX footkg: <http://tib.eu/footkg/ontology#>
            PREFIX footres: <http://tib.eu/footkg/resource/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?name ?clubName ?roleName ?progPasses ?marketValue
            WHERE {
                ?player a footkg:Player ;
                        footkg:playerName ?name ;
                        footkg:playsFor ?club ;
                        footkg:primaryRole ?role ;
                        footkg:progressivePassesPer90 ?progPasses ;
                        footkg:marketValueEUR ?marketValue .
                ?club rdfs:label ?clubName .
                ?role rdfs:label ?roleName .
            }
            ORDER BY DESC(?progPasses)
            LIMIT 5
            """

        res = self.engine.query(sparql)
        
        # Formulate human explanation
        results = res["results"]
        if not results:
            answer_text = "No matching records found in the knowledge graph for your criteria."
        else:
            if intent == "player_replacement":
                top = results[0]
                answer_text = (
                    f"Top tactical replacement identified: **{top['candidateName']}** ({top['clubName']}). "
                    f"Role: {top['roleName']}, Market Value: €{top['marketValue']:,.0f}, "
                    f"Progressive Passes: {top['progPasses']}/90."
                )
            elif intent == "coach_lineage":
                names = [r["playerName"] for r in results]
                answer_text = f"Players in FootKG coached by {results[0]['managerName']}: " + ", ".join(names) + "."
            elif intent == "tactical_counter":
                vuln = list({r['vulnZoneDesc'] for r in results if r.get('vulnZoneDesc')})
                counters = list({r['counterFormName'] for r in results if r.get('counterFormName')})
                answer_text = (
                    f"Against {results[0]['teamName']} ({results[0]['formationName']}), the vulnerable transition zones are: "
                    + "; ".join(vuln) + f". Recommended counter-formation: {counters[0] if counters else '5-3-2 Counter'}."
                )
            elif intent == "chemistry_network":
                links = [f"{r['connectedName']} ({r['connection']})" for r in results]
                answer_text = f"High-chemistry connections for {results[0]['targetName']}: " + ", ".join(links) + "."
            else:
                answer_text = f"Found {len(results)} top tactical players based on progressive performance metrics."

        return {
            "question": question,
            "intent": intent,
            "answer": answer_text,
            "results": results,
            "sparql": sparql,
            "latency_ms": res["latency_ms"]
        }
