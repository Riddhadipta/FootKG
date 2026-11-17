# FootKG: Football Knowledge Graph & Tactical Scouting Engine ⚽

**Course:** Creation and Application of Knowledge Graphs (WS26/27)  
**Institutions:** Leibniz University Hannover, L3S Research Center, TIB  
**Author(s):** Riddhadipta Nath  
**Submission Target:** `xinyue.gong@l3s.de`  
**Ontology Namespace:** `http://tib.eu/footkg/ontology#`

---

## 🌟 Overview

**FootKG** is a graph-native football analytics and scouting intelligence system built with **OWL 2 DL**, **RDFLib**, **SPARQL**, and **Streamlit**. 

Unlike conventional football analytics systems that rely on flat tabular numbers or opaque vector embeddings, **FootKG** models football as a relational topological network:
1. **Multi-Hop Player Replacement:** Identifying affordable scouting targets matching high-level tactical archetypes (e.g. *Inverted Fullback*, *Deep-Lying Playmaker*), spatial pitch-zone occupancy, and managerial system lineages (e.g. *Positional Play*, *Gegenpressing*).
2. **Tactical Counter-Strategy Reasoning:** Inferring spatial pitch corridors left vulnerable during structural in-possession transitions (e.g., 4-3-3 shifting to 3-2-5) and prescribing counter-formations and exploitative squad roles.
3. **Network Chemistry Explorer:** Traversing multi-hop graph paths connecting players via shared former clubs, common managers, national teams, and positional synergies.
4. **Natural Language KGQA:** Translating user questions into structured SPARQL queries executed with sub-10ms response latencies.

---

## 📁 Repository Structure

```text
footkg/
├── ontology/
│   └── footkg_ontology.ttl         # OWL 2 DL ontology definitions
├── data/
│   ├── generate_data.py            # Graph construction & enrichment pipeline
│   └── footkg_triples.ttl          # Populated RDF Turtle triplestore (895 triples)
├── src/
│   ├── engine.py                   # RDFLib SPARQL execution & query engine
│   ├── scout.py                    # Multi-hop player replacement algorithm
│   ├── tactics.py                  # Formation matchup & spatial vulnerability solver
│   ├── chemistry.py                # Career network & chemistry pathfinder
│   └── kgqa.py                     # Natural language to SPARQL translation engine
├── evaluation/
│   ├── benchmark_queries.json      # 20 benchmark tactical/scouting queries
│   ├── evaluate.py                 # Automated evaluation harness
│   └── evaluation_results.json     # Saved quantitative benchmark results
├── report/
│   └── FootKG_Project_Report.md    # 5-section academic project report
├── app.py                          # Interactive Streamlit dashboard
├── requirements.txt                # Python dependencies
└── README.md                       # Setup and execution guide
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- `pip` package manager

### 2. Installation
Install required dependencies:
```bash
pip install -r requirements.txt
```

*(Alternatively: `pip install rdflib streamlit pandas`)*

### 3. Rebuild / Verify the Knowledge Graph (Optional)
To regenerate or inspect the populated Turtle RDF graph:
```bash
python data/generate_data.py
```

### 4. Run the 20-Query Benchmark Evaluation
To execute the automated evaluation test suite across all 20 benchmark queries:
```bash
python evaluation/evaluate.py
```

### 5. Launch the Interactive Dashboard
Launch the web interface:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Benchmark Evaluation Summary

Tested against the 20 comprehensive benchmark queries covering:
- **Player Replacement (Multi-Hop):** 100% pass (Avg latency: 24.3 ms)
- **Coach Lineage & System Pedigree:** 100% pass (Avg latency: 2.2 ms)
- **Tactical Vulnerability & Counters:** 100% pass (Avg latency: 5.6 ms)
- **Chemistry & Career Networks:** 100% pass (Avg latency: 11.1 ms)
- **Role Synergies & Spatial Overlaps:** 100% pass (Avg latency: 1.9 ms)
- **Transitive Possession Chains:** 100% pass (Avg latency: 1.2 ms)

**Overall Accuracy:** **100.0%**  
**Mean Query Latency:** **6.94 ms**
