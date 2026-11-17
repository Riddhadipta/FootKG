"""
FootKG: Interactive Football Knowledge Graph Dashboard
Built with Streamlit and RDFLib
"""

import streamlit as st
import pandas as pd
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(__file__))
from src.engine import FootKGEngine
from src.scout import FootKGScout
from src.tactics import FootKGTactics
from src.chemistry import FootKGChemistry
from src.kgqa import FootKGQA

st.set_page_config(
    page_title="FootKG: Tactical Football Knowledge Graph",
    page_icon="⚽",
    layout="wide"
)

@st.cache_resource
def load_footkg():
    engine = FootKGEngine()
    scout = FootKGScout(engine)
    tactics = FootKGTactics(engine)
    chemistry = FootKGChemistry(engine)
    qa = FootKGQA(engine)
    return engine, scout, tactics, chemistry, qa

engine, scout, tactics, chemistry, qa = load_footkg()
stats = engine.get_summary_stats()

# Title & Header
st.title("⚽ FootKG: Football Knowledge Graph & Tactical Intelligence")
st.caption("A Graph-Native Reasoning System for Intelligent Scouting, Multi-Hop Lineages, and Counter-Tactics")

# Metrics row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Triples in FootKG", f"{stats['total_triples']:,}")
with col2:
    st.metric("Curated Players", f"{stats['total_players']}")
with col3:
    st.metric("Graph Load Time", f"{stats['graph_load_time_ms']} ms")
with col4:
    st.metric("SPARQL Reasoning Engine", "OWL 2 DL / RDFLib")

st.divider()

# Navigation tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Intelligent Player Scouting",
    "🛡️ Tactical Counter-Strategy",
    "🔗 Team Chemistry & Networks",
    "💬 Natural Language KGQA",
    "📊 Ontology & Benchmark Eval"
])

# -------------------------------------------------------------
# TAB 1: Intelligent Player Scouting
# -------------------------------------------------------------
with tab1:
    st.subheader("Multi-Hop Tactical Player Replacement Finder")
    st.write(
        "Find tactical replacements by reasoning over **role taxonomies**, **spatial in/out-possession zones**, "
        "and **managerial coaching pedigrees**."
    )

    all_players = scout.get_all_players()
    player_options = {p["name"]: p["player"] for p in all_players}
    
    col_p, col_b, col_a = st.columns([2, 1, 1])
    with col_p:
        selected_pname = st.selectbox("Select Player to Replace:", list(player_options.keys()), index=0)
        target_pid = player_options[selected_pname]
    with col_b:
        max_budget = st.slider("Max Budget (€ Millions):", min_value=15, max_value=150, value=40, step=5) * 1_000_000
    with col_a:
        max_age = st.slider("Max Player Age:", min_value=18, max_value=32, value=25)

    if st.button("🚀 Find Tactical Twins in Graph"):
        rep_res = scout.find_replacements(target_pid, max_budget_eur=max_budget, max_age=max_age)
        reps = rep_res["replacements"]
        
        st.success(f"Discovered {len(reps)} matching candidates in {rep_res['query_latency_ms']} ms.")
        
        if reps:
            df_reps = pd.DataFrame([{
                "Player": r["name"],
                "Club": r["club"],
                "Age": r["age"],
                "Role": r["role"],
                "Market Value": f"€{r['market_value_eur']:,.0f}",
                "Prog. Passes / 90": r["prog_passes_90"],
                "Pressures / 90": r["pressures_90"],
                "Tactical Fit": f"{r['tactical_fit_score']}%",
                "Coach Pedigree": r["coach_pedigree"]
            } for r in reps])
            st.dataframe(df_reps, use_container_width=True)

            st.write("### 📌 Detailed Candidate Breakdown")
            for r in reps[:3]:
                with st.expander(f"⭐ {r['name']} ({r['club']}) — Fit Score: {r['tactical_fit_score']}%"):
                    st.write(f"- **Tactical Role:** {r['role']}")
                    st.write(f"- **System Lineage:** Coached by {r['coach_pedigree']} ({r['tactical_system']})")
                    st.write("- **Graph Reasoning Evidence:**")
                    for reason in r["tactical_reasons"]:
                        st.markdown(f"  * {reason}")

        with st.expander("🔍 View Executed SPARQL Query"):
            st.code(rep_res["sparql_used"], language="sparql")

# -------------------------------------------------------------
# TAB 2: Tactical Counter-Strategy
# -------------------------------------------------------------
with tab2:
    st.subheader("Opponent Vulnerability & Counter-Formation Reasoning")
    st.write(
        "Analyze the opponent's manager, base formation, in-possession structural transition, "
        "and infer pitch zones left vulnerable during defensive recovery."
    )

    all_teams = tactics.get_all_teams()
    team_options = {t["teamName"]: t["team"] for t in all_teams}
    
    selected_team = st.selectbox("Select Opponent Club:", list(team_options.keys()))
    team_id = team_options[selected_team]

    if st.button("⚡ Analyze Tactical Matchup"):
        tac_res = tactics.analyze_tactical_matchup(team_id)
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.info(f"**Manager:** {tac_res['manager']}")
            st.write(f"**Tactical Philosophy:** {tac_res['tactical_system']}")
            st.write(f"**Base Shape:** {tac_res['base_formation']}")
            st.write(f"**In-Possession Shift:** {tac_res['in_possession_transition']}")
        
        with col_t2:
            st.warning(f"**Recommended Counter-Formation:** {', '.join(tac_res['recommended_counter_formations'])}")
            st.error(f"**Vulnerable Transition Corridors:**\n* " + "\n* ".join(tac_res['vulnerable_transition_zones']))

        st.write("### 🎯 Squad Attackers Suited to Exploit These Corridors")
        if tac_res["key_exploit_players"]:
            df_exploit = pd.DataFrame([{
                "Player": p["playerName"],
                "Role": p["roleName"],
                "Attacking Zone": p["inZoneDesc"],
                "xG / 90": p["xG"],
                "xA / 90": p["xA"]
            } for p in tac_res["key_exploit_players"]])
            st.dataframe(df_exploit, use_container_width=True)

        with st.expander("🔍 View Executed SPARQL Query"):
            st.code(tac_res["sparql_used"], language="sparql")

# -------------------------------------------------------------
# TAB 3: Team Chemistry & Networks
# -------------------------------------------------------------
with tab3:
    st.subheader("Relational Chemistry & Career Network Pathfinding")
    st.write(
        "Traces multi-hop relationships between players across shared former clubs, "
        "national teams, and common tactical coaches."
    )

    chem_player = st.selectbox("Select Player for Network Analysis:", list(player_options.keys()), index=0)
    chem_pid = player_options[chem_player]

    if st.button("🕸️ Map Chemistry Graph"):
        c_res = chemistry.get_player_connections(chem_pid)
        st.success(f"Identified {c_res['total_links']} multi-hop connections in {c_res['latency_ms']} ms.")
        
        conns = c_res["connections"]
        if conns:
            df_conns = pd.DataFrame([{
                "Connected Player": c["connectedName"],
                "Relationship Type": c["connectionType"],
                "Entity / Context": c["detail"]
            } for c in conns])
            st.dataframe(df_conns, use_container_width=True)

# -------------------------------------------------------------
# TAB 4: Natural Language KGQA
# -------------------------------------------------------------
with tab4:
    st.subheader("Natural Language Question Answering over FootKG")
    st.write("Ask natural language tactical questions; FootKG will parse intents, generate SPARQL, and execute in real-time.")

    sample_questions = [
        "Find replacements for Rodri under 40M",
        "Who has been coached by Pep Guardiola?",
        "What formation counters Manchester City?",
        "Who shares chemistry with Bukayo Saka?",
        "Find replacements for Zinchenko under 35M",
        "Find players coached by Xabi Alonso at Bayer Leverkusen",
    ]
    selected_sample = st.selectbox("Quick Sample Prompts:", ["Custom Question"] + sample_questions)
    
    user_q = st.text_input(
        "Enter question:",
        value=selected_sample if selected_sample != "Custom Question" else "Find replacements for Rodri under 40M"
    )

    if st.button("💬 Ask FootKG"):
        ans = qa.answer_question(user_q)
        st.markdown(f"### 🤖 Response\n{ans['answer']}")
        st.caption(f"Intent Classified: `{ans['intent']}` | Query Latency: {ans['latency_ms']} ms")
        
        if ans["results"]:
            with st.expander("📋 View Raw Result Triples / Rows"):
                st.dataframe(pd.DataFrame(ans["results"]), use_container_width=True)

        with st.expander("🔍 View Generated SPARQL"):
            st.code(ans["sparql"], language="sparql")

# -------------------------------------------------------------
# TAB 5: Ontology & Benchmark Evaluation
# -------------------------------------------------------------
with tab5:
    st.subheader("Ontology Overview & Benchmark Evaluation Results")
    
    st.markdown("""
    #### 📚 FootKG Ontology Hierarchy
    * **Namespace:** `http://tib.eu/footkg/ontology#`
    * **Ontology Format:** OWL 2 DL / Turtle
    * **Key Classes:** `Player`, `Team`, `Manager`, `TacticalRole`, `Formation`, `SpatialZone`, `MatchEvent`
    * **Special Axioms:** Symmetric properties (`synergizesWith`, `adjacentTo`), Transitive properties (`directlyPrecedes+`).
    """)

    eval_json_path = os.path.join(os.path.dirname(__file__), "evaluation", "evaluation_results.json")
    if os.path.exists(eval_json_path):
        import json
        with open(eval_json_path, "r") as f:
            eval_data = json.load(f)
        
        st.write("### 🏆 Benchmark Suite Performance (20 Mandatory Test Queries)")
        ecol1, ecol2, ecol3 = st.columns(3)
        with ecol1:
            st.metric("Benchmark Queries", eval_data["total"])
        with ecol2:
            st.metric("Accuracy Rate", f"{eval_data['accuracy_pct']}%")
        with ecol3:
            st.metric("Avg Latency", f"{eval_data['avg_latency_ms']} ms")

        st.write("#### Category-by-Category Results")
        cat_df = pd.DataFrame([{
            "Category": cat,
            "Passed": f"{val['passed']} / {val['total']}",
            "Avg Latency (ms)": f"{val['avg_latency_ms']} ms"
        } for cat, val in eval_data["category_stats"].items()])
        st.dataframe(cat_df, use_container_width=True)
