"""
FootKG Scouting Engine:
Performs multi-hop graph similarity, role taxonomy matching, and tactical lineage scoring
to identify replacement targets for any football player.
"""

from typing import List, Dict, Any, Optional
from .engine import FootKGEngine

class FootKGScout:
    def __init__(self, engine: FootKGEngine):
        self.engine = engine

    def get_all_players(self) -> List[Dict[str, Any]]:
        query = """
        PREFIX footkg: <http://tib.eu/footkg/ontology#>
        PREFIX footres: <http://tib.eu/footkg/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?player ?name ?age ?nationality ?club ?clubName ?marketValue ?role ?roleName
        WHERE {
            ?player a footkg:Player ;
                    footkg:playerName ?name ;
                    footkg:age ?age ;
                    footkg:nationality ?nationality ;
                    footkg:marketValueEUR ?marketValue ;
                    footkg:playsFor ?club ;
                    footkg:primaryRole ?role .
            ?club rdfs:label ?clubName .
            ?role rdfs:label ?roleName .
        }
        ORDER BY ?name
        """
        return self.engine.query(query)["results"]

    def find_replacements(
        self,
        target_player_id: str,
        max_budget_eur: Optional[float] = None,
        max_age: Optional[int] = None,
        require_system_lineage: bool = False
    ) -> Dict[str, Any]:
        """
        Finds replacements using multi-hop graph patterns:
        - Role taxonomy match (primary role or synergistic sibling)
        - Spatial in/out possession zone equivalence
        - Tactical coach pedigree (coachedBy -> employsSystem)
        """
        if not target_player_id.startswith("footres:"):
            target_uri_str = f"footres:{target_player_id}"
        else:
            target_uri_str = target_player_id

        budget_filter = f"FILTER(?marketValue <= {max_budget_eur})" if max_budget_eur else ""
        age_filter = f"FILTER(?age <= {max_age})" if max_age else ""
        
        system_clause = """
        OPTIONAL {
            ?candidate footkg:coachedBy ?coach .
            ?coach footkg:employsSystem ?sys ;
                   rdfs:label ?coachName .
            ?sys rdfs:label ?sysName .
        }
        """

        query = f"""
        PREFIX footkg: <http://tib.eu/footkg/ontology#>
        PREFIX footres: <http://tib.eu/footkg/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?candidate ?name ?age ?nationality ?clubName ?marketValue
                        ?roleName ?progPasses ?pressures ?passPct ?inZone ?outZone
                        ?coachName ?sysName
        WHERE {{
            # Target player profile
            {target_uri_str} footkg:primaryRole ?targetRole ;
                             footkg:inPossessionZone ?targetInZone ;
                             footkg:outOfPossessionZone ?targetOutZone .

            # Candidate player
            ?candidate a footkg:Player ;
                       footkg:playerName ?name ;
                       footkg:age ?age ;
                       footkg:nationality ?nationality ;
                       footkg:marketValueEUR ?marketValue ;
                       footkg:playsFor ?club ;
                       footkg:primaryRole ?candidateRole ;
                       footkg:inPossessionZone ?inZone ;
                       footkg:outOfPossessionZone ?outZone ;
                       footkg:progressivePassesPer90 ?progPasses ;
                       footkg:pressuresPer90 ?pressures ;
                       footkg:passCompletionPct ?passPct .
            ?club rdfs:label ?clubName .
            ?candidateRole rdfs:label ?roleName .

            FILTER(?candidate != {target_uri_str})
            {budget_filter}
            {age_filter}

            # Spatial or Role matching
            FILTER(?candidateRole = ?targetRole || ?inZone = ?targetInZone)

            {system_clause}
        }}
        ORDER BY DESC(?progPasses) ASC(?marketValue)
        LIMIT 10
        """

        res = self.engine.query(query)
        candidates = []
        for r in res["results"]:
            # Compute a tactical similarity & value score
            fit_score = 70.0
            reasons = []

            if r.get("roleName"):
                reasons.append(f"Identical Role: {r['roleName']}")
                fit_score += 15.0

            if r.get("sysName"):
                reasons.append(f"Coached under {r['coachName']} ({r['sysName']})")
                fit_score += 10.0

            if float(r.get("progPasses", 0)) >= 7.0:
                reasons.append(f"Elite Ball Progression ({r['progPasses']}/90)")
                fit_score += 5.0

            candidates.append({
                "id": r["candidate"],
                "name": r["name"],
                "age": r["age"],
                "nationality": r["nationality"],
                "club": r["clubName"],
                "market_value_eur": r["marketValue"],
                "role": r["roleName"],
                "prog_passes_90": r["progPasses"],
                "pressures_90": r["pressures"],
                "pass_pct": r["passPct"],
                "tactical_fit_score": min(100.0, fit_score),
                "tactical_reasons": reasons,
                "coach_pedigree": r.get("coachName", "N/A"),
                "tactical_system": r.get("sysName", "Standard")
            })

        # Deduplicate candidates across coach options
        seen = set()
        deduped = []
        for c in candidates:
            if c["id"] not in seen:
                seen.add(c["id"])
                deduped.append(c)

        return {
            "target": target_player_id,
            "replacements": deduped,
            "query_latency_ms": res["latency_ms"],
            "sparql_used": query
        }
