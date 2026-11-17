#!/usr/bin/env python3
"""
FootKG Data Generator:
Populates the FootKG RDF Knowledge Graph with teams, managers, tactical systems,
formations, tactical roles, spatial zones, players, career lineages, chemistry, and match events.
"""

from rdflib import Graph, Literal, Namespace, RDF, RDFS, XSD, URIRef
import os

FOOTKG = Namespace("http://tib.eu/footkg/ontology#")
FOOTRES = Namespace("http://tib.eu/footkg/resource/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")

def build_knowledge_graph():
    g = Graph()
    
    # Bind prefixes
    g.bind("footkg", FOOTKG)
    g.bind("footres", FOOTRES)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    
    # Load base ontology
    ontology_path = os.path.join(os.path.dirname(__file__), "..", "ontology", "footkg_ontology.ttl")
    g.parse(ontology_path, format="turtle")
    print(f"Loaded base ontology. Current triples: {len(g)}")

    # -------------------------------------------------------------
    # 1. Pitch Zones (1-18 grid + tactical corridors)
    # -------------------------------------------------------------
    zones = [
        # Defensive third
        ("Zone1_DefRightFlank", "Defensive Right Flank", "WideChannel"),
        ("Zone2_DefRightHalfSpace", "Defensive Right Half-Space", "HalfSpace"),
        ("Zone3_DefCentral", "Defensive Central Box (Penalty Area)", "CentralCorridor"),
        ("Zone4_DefLeftHalfSpace", "Defensive Left Half-Space", "HalfSpace"),
        ("Zone5_DefLeftFlank", "Defensive Left Flank", "WideChannel"),
        # Middle third
        ("Zone6_MidRightFlank", "Middle Third Right Flank", "WideChannel"),
        ("Zone7_MidRightHalfSpace", "Middle Third Right Half-Space", "HalfSpace"),
        ("Zone8_MidCentral", "Central Midfield Circle", "CentralCorridor"),
        ("Zone9_MidLeftHalfSpace", "Middle Third Left Half-Space", "HalfSpace"),
        ("Zone10_MidLeftFlank", "Middle Third Left Flank", "WideChannel"),
        # Attacking third
        ("Zone11_AttRightFlank", "Attacking Right Flank (Crossing Zone)", "WideChannel"),
        ("Zone12_AttRightHalfSpace", "Attacking Right Half-Space", "HalfSpace"),
        ("Zone13_AttZone14", "Zone 14 (Central Edge of Opponent Box)", "CentralCorridor"),
        ("Zone14_AttLeftHalfSpace", "Attacking Left Half-Space", "HalfSpace"),
        ("Zone15_AttLeftFlank", "Attacking Left Flank (Crossing Zone)", "WideChannel"),
        ("Zone16_BoxRight", "Opponent 6-yard Box Right", "CentralCorridor"),
        ("Zone17_BoxCentral", "Opponent Penalty Spot (Golden Zone)", "CentralCorridor"),
        ("Zone18_BoxLeft", "Opponent 6-yard Box Left", "CentralCorridor"),
    ]

    for zid, desc, ztype in zones:
        z_uri = FOOTRES[zid]
        g.add((z_uri, RDF.type, FOOTKG.PitchZone))
        g.add((z_uri, RDF.type, FOOTKG[ztype]))
        g.add((z_uri, RDFS.label, Literal(desc, lang="en")))
        g.add((z_uri, FOOTKG.zoneDescription, Literal(desc, datatype=XSD.string)))

    # Spatial adjacencies
    adjacencies = [
        ("Zone1_DefRightFlank", "Zone2_DefRightHalfSpace"),
        ("Zone2_DefRightHalfSpace", "Zone3_DefCentral"),
        ("Zone3_DefCentral", "Zone4_DefLeftHalfSpace"),
        ("Zone4_DefLeftHalfSpace", "Zone5_DefLeftFlank"),
        ("Zone6_MidRightFlank", "Zone7_MidRightHalfSpace"),
        ("Zone7_MidRightHalfSpace", "Zone8_MidCentral"),
        ("Zone8_MidCentral", "Zone9_MidLeftHalfSpace"),
        ("Zone9_MidLeftHalfSpace", "Zone10_MidLeftFlank"),
        ("Zone11_AttRightFlank", "Zone12_AttRightHalfSpace"),
        ("Zone12_AttRightHalfSpace", "Zone13_AttZone14"),
        ("Zone13_AttZone14", "Zone14_AttLeftHalfSpace"),
        ("Zone14_AttLeftHalfSpace", "Zone15_AttLeftFlank"),
        ("Zone8_MidCentral", "Zone13_AttZone14"),
        ("Zone7_MidRightHalfSpace", "Zone12_AttRightHalfSpace"),
        ("Zone9_MidLeftHalfSpace", "Zone14_AttLeftHalfSpace"),
    ]
    for z1, z2 in adjacencies:
        g.add((FOOTRES[z1], FOOTKG.adjacentTo, FOOTRES[z2]))
        g.add((FOOTRES[z2], FOOTKG.adjacentTo, FOOTRES[z1]))

    # -------------------------------------------------------------
    # 2. Tactical Systems & Role Synergies
    # -------------------------------------------------------------
    systems = [
        ("System_PositionalPlay", "Positional Play", "PositionalPlay"),
        ("System_Gegenpressing", "Gegenpressing", "Gegenpressing"),
        ("System_LowBlockCounter", "Low-Block Counter-Attack", "LowBlockCounter"),
        ("System_Relationism", "Relationism / Fluid Dynamic", "Relationism"),
        ("System_DirectVertical", "Direct Vertical Play", "DirectVertical"),
    ]
    for sid, sname, stype in systems:
        s_uri = FOOTRES[sid]
        g.add((s_uri, RDF.type, FOOTKG[stype]))
        g.add((s_uri, RDFS.label, Literal(sname, lang="en")))

    # Tactical Role Archetypes
    roles = [
        ("Role_InvertedFullback", "Inverted Fullback", "InvertedFullback", "Zone2_DefRightHalfSpace", "Zone7_MidRightHalfSpace"),
        ("Role_OverlappingWingback", "Overlapping Wingback", "OverlappingWingback", "Zone6_MidRightFlank", "Zone11_AttRightFlank"),
        ("Role_TouchlineWinger", "Touchline Winger", "TouchlineWinger", "Zone11_AttRightFlank", "Zone11_AttRightFlank"),
        ("Role_InsideForward", "Inside Forward", "InsideForward", "Zone14_AttLeftHalfSpace", "Zone13_AttZone14"),
        ("Role_DeepLyingPlaymaker", "Deep-Lying Playmaker (Regista)", "DeepLyingPlaymaker", "Zone3_DefCentral", "Zone8_MidCentral"),
        ("Role_BoxToBoxMidfielder", "Box-to-Box Midfielder", "BoxToBoxMidfielder", "Zone8_MidCentral", "Zone13_AttZone14"),
        ("Role_AnchorMan", "Anchor Man (Busquets Pivot)", "AnchorMan", "Zone3_DefCentral", "Zone8_MidCentral"),
        ("Role_Mezzala", "Mezzala (Half-space Runner)", "Mezzala", "Zone8_MidCentral", "Zone12_AttRightHalfSpace"),
        ("Role_BallPlayingDefender", "Ball-Playing Defender", "BallPlayingDefender", "Zone3_DefCentral", "Zone3_DefCentral"),
        ("Role_FalseNine", "False Nine", "FalseNine", "Zone13_AttZone14", "Zone8_MidCentral"),
        ("Role_Raumdeuter", "Raumdeuter (Space Finder)", "Raumdeuter", "Zone12_AttRightHalfSpace", "Zone17_BoxCentral"),
        ("Role_PressingForward", "Pressing Forward", "PressingForward", "Zone13_AttZone14", "Zone17_BoxCentral"),
    ]

    for rid, rname, rtype, out_zone, in_zone in roles:
        r_uri = FOOTRES[rid]
        g.add((r_uri, RDF.type, FOOTKG[rtype]))
        g.add((r_uri, RDFS.label, Literal(rname, lang="en")))
        g.add((r_uri, FOOTKG.outOfPossessionZone, FOOTRES[out_zone]))
        g.add((r_uri, FOOTKG.inPossessionZone, FOOTRES[in_zone]))

    # Role Synergies (Symmetric)
    role_synergies = [
        ("Role_InvertedFullback", "Role_TouchlineWinger"),
        ("Role_OverlappingWingback", "Role_InsideForward"),
        ("Role_DeepLyingPlaymaker", "Role_BoxToBoxMidfielder"),
        ("Role_DeepLyingPlaymaker", "Role_Mezzala"),
        ("Role_AnchorMan", "Role_DeepLyingPlaymaker"),
        ("Role_FalseNine", "Role_InsideForward"),
        ("Role_FalseNine", "Role_Raumdeuter"),
    ]
    for r1, r2 in role_synergies:
        g.add((FOOTRES[r1], FOOTKG.synergizesWith, FOOTRES[r2]))
        g.add((FOOTRES[r2], FOOTKG.synergizesWith, FOOTRES[r1]))

    # -------------------------------------------------------------
    # 3. Formations & Structural Counters
    # -------------------------------------------------------------
    formations = [
        ("Formation_4_3_3", "Base 4-3-3", "Formation_3_2_5_InPoss", ["Zone1_DefRightFlank", "Zone5_DefLeftFlank"]),
        ("Formation_3_2_5_InPoss", "3-2-5 In-Possession Shape", None, ["Zone1_DefRightFlank", "Zone5_DefLeftFlank"]),
        ("Formation_4_2_3_1", "4-2-3-1 Double Pivot", "Formation_2_3_5_InPoss", ["Zone13_AttZone14"]),
        ("Formation_3_5_2", "3-5-2 Wingback Structure", "Formation_3_1_4_2_InPoss", ["Zone6_MidRightFlank", "Zone10_MidLeftFlank"]),
        ("Formation_4_4_2_LowBlock", "4-4-2 Compact Low Block", None, ["Zone8_MidCentral"]),
        ("Formation_5_3_2_Counter", "5-3-2 Direct Counter", None, ["Zone11_AttRightFlank", "Zone15_AttLeftFlank"]),
    ]

    for fid, fname, trans_to, vuln_zones in formations:
        f_uri = FOOTRES[fid]
        g.add((f_uri, RDF.type, FOOTKG.Formation))
        g.add((f_uri, RDFS.label, Literal(fname, lang="en")))
        if trans_to:
            g.add((f_uri, FOOTKG.transitionsToInPossession, FOOTRES[trans_to]))
        for vz in vuln_zones:
            g.add((f_uri, FOOTKG.leavesVulnerableZone, FOOTRES[vz]))

    # Formation counter relationships
    g.add((FOOTRES["Formation_5_3_2_Counter"], FOOTKG.exploitsWeaknessIn, FOOTRES["Formation_4_3_3"]))
    g.add((FOOTRES["Formation_4_3_3"], FOOTKG.exploitsWeaknessIn, FOOTRES["Formation_3_5_2"]))
    g.add((FOOTRES["Formation_4_2_3_1"], FOOTKG.exploitsWeaknessIn, FOOTRES["Formation_4_4_2_LowBlock"]))

    # -------------------------------------------------------------
    # 4. Managers & Clubs
    # -------------------------------------------------------------
    managers = [
        ("Manager_PepGuardiola", "Pep Guardiola", "Spain", "System_PositionalPlay", "Formation_4_3_3"),
        ("Manager_MikelArteta", "Mikel Arteta", "Spain", "System_PositionalPlay", "Formation_4_3_3"),
        ("Manager_XabiAlonso", "Xabi Alonso", "Spain", "System_PositionalPlay", "Formation_3_5_2"),
        ("Manager_JurgenKlopp", "Jurgen Klopp", "Germany", "System_Gegenpressing", "Formation_4_3_3"),
        ("Manager_ArneSlot", "Arne Slot", "Netherlands", "System_PositionalPlay", "Formation_4_2_3_1"),
        ("Manager_DiegoSimeone", "Diego Simeone", "Argentina", "System_LowBlockCounter", "Formation_4_4_2_LowBlock"),
        ("Manager_SimoneInzaghi", "Simone Inzaghi", "Italy", "System_DirectVertical", "Formation_3_5_2"),
        ("Manager_CarloAncelotti", "Carlo Ancelotti", "Italy", "System_Relationism", "Formation_4_2_3_1"),
        ("Manager_RogerSchmidt", "Roger Schmidt", "Germany", "System_Gegenpressing", "Formation_4_2_3_1"),
        ("Manager_OliverGlasner", "Oliver Glasner", "Austria", "System_DirectVertical", "Formation_3_5_2"),
    ]

    for mid, mname, nat, sys_id, form_id in managers:
        m_uri = FOOTRES[mid]
        g.add((m_uri, RDF.type, FOOTKG.Manager))
        g.add((m_uri, RDFS.label, Literal(mname, lang="en")))
        g.add((m_uri, FOOTKG.nationality, Literal(nat, datatype=XSD.string)))
        g.add((m_uri, FOOTKG.employsSystem, FOOTRES[sys_id]))
        g.add((m_uri, FOOTKG.utilizesFormation, FOOTRES[form_id]))

    clubs = [
        ("Club_ManchesterCity", "Manchester City FC", "Premier League", "Manager_PepGuardiola"),
        ("Club_Arsenal", "Arsenal FC", "Premier League", "Manager_MikelArteta"),
        ("Club_Liverpool", "Liverpool FC", "Premier League", "Manager_ArneSlot"),
        ("Club_RealMadrid", "Real Madrid CF", "La Liga", "Manager_CarloAncelotti"),
        ("Club_BayerLeverkusen", "Bayer 04 Leverkusen", "Bundesliga", "Manager_XabiAlonso"),
        ("Club_AtleticoMadrid", "Club Atletico de Madrid", "La Liga", "Manager_DiegoSimeone"),
        ("Club_InterMilan", "FC Internazionale Milano", "Serie A", "Manager_SimoneInzaghi"),
        ("Club_CrystalPalace", "Crystal Palace FC", "Premier League", "Manager_OliverGlasner"),
        ("Club_Benfica", "SL Benfica", "Liga Portugal", "Manager_RogerSchmidt"),
        ("Club_Brighton", "Brighton & Hove Albion FC", "Premier League", "Manager_PepGuardiola"),
        ("Club_Porto", "FC Porto", "Liga Portugal", "Manager_SimoneInzaghi"),
        ("Club_PSV", "PSV Eindhoven", "Eredivisie", "Manager_ArneSlot"),
    ]

    for cid, cname, comp, mid in clubs:
        c_uri = FOOTRES[cid]
        g.add((c_uri, RDF.type, FOOTKG.ClubTeam))
        g.add((c_uri, RDFS.label, Literal(cname, lang="en")))
        g.add((c_uri, FOOTKG.managedBy, FOOTRES[mid]))

    # -------------------------------------------------------------
    # 5. Players (Stars, Anchors & Emerging Scouting Targets)
    # -------------------------------------------------------------
    # Format:
    # (id, name, age, nat, foot, value_eur, current_club, past_clubs, coached_by,
    #  primary_role, in_zone, out_zone, prog_passes, pressures, pass_pct, xg90, xa90)
    players = [
        # --- Manchester City & Benchmarks ---
        ("Player_Rodri", "Rodri Hernandez", 28, "Spain", "Right", 130000000,
         "Club_ManchesterCity", ["Club_AtleticoMadrid"], ["Manager_PepGuardiola", "Manager_DiegoSimeone"],
         "Role_DeepLyingPlaymaker", "Zone8_MidCentral", "Zone3_DefCentral", 8.8, 14.5, 92.4, 0.15, 0.18),

        ("Player_RicoLewis", "Rico Lewis", 20, "England", "Right", 40000000,
         "Club_ManchesterCity", [], ["Manager_PepGuardiola"],
         "Role_InvertedFullback", "Zone7_MidRightHalfSpace", "Zone2_DefRightHalfSpace", 7.2, 16.8, 91.0, 0.08, 0.14),

        ("Player_JeremyDoku", "Jeremy Doku", 22, "Belgium", "Right", 65000000,
         "Club_ManchesterCity", [], ["Manager_PepGuardiola"],
         "Role_TouchlineWinger", "Zone11_AttRightFlank", "Zone11_AttRightFlank", 4.1, 12.3, 84.5, 0.28, 0.42),

        # --- Arsenal ---
        ("Player_BukayoSaka", "Bukayo Saka", 23, "England", "Left", 140000000,
         "Club_Arsenal", [], ["Manager_MikelArteta"],
         "Role_TouchlineWinger", "Zone11_AttRightFlank", "Zone11_AttRightFlank", 5.6, 13.9, 81.2, 0.45, 0.38),

        ("Player_DeclanRice", "Declan Rice", 25, "England", "Right", 110000000,
         "Club_Arsenal", [], ["Manager_MikelArteta"],
         "Role_BoxToBoxMidfielder", "Zone13_AttZone14", "Zone8_MidCentral", 6.8, 18.2, 89.8, 0.18, 0.22),

        ("Player_OleksandrZinchenko", "Oleksandr Zinchenko", 27, "Ukraine", "Left", 35000000,
         "Club_Arsenal", ["Club_ManchesterCity"], ["Manager_MikelArteta", "Manager_PepGuardiola"],
         "Role_InvertedFullback", "Zone9_MidLeftHalfSpace", "Zone4_DefLeftHalfSpace", 8.1, 15.2, 88.5, 0.05, 0.19),

        # --- Real Madrid ---
        ("Player_JudeBellingham", "Jude Bellingham", 21, "England", "Right", 180000000,
         "Club_RealMadrid", [], ["Manager_CarloAncelotti"],
         "Role_Raumdeuter", "Zone17_BoxCentral", "Zone12_AttRightHalfSpace", 5.4, 17.5, 87.6, 0.52, 0.29),

        ("Player_EduardoCamavinga", "Eduardo Camavinga", 22, "France", "Left", 100000000,
         "Club_RealMadrid", [], ["Manager_CarloAncelotti"],
         "Role_BoxToBoxMidfielder", "Zone8_MidCentral", "Zone4_DefLeftHalfSpace", 7.1, 21.4, 90.2, 0.09, 0.15),

        # --- Bayer Leverkusen ---
        ("Player_FlorianWirtz", "Florian Wirtz", 21, "Germany", "Right", 130000000,
         "Club_BayerLeverkusen", [], ["Manager_XabiAlonso"],
         "Role_InsideForward", "Zone14_AttLeftHalfSpace", "Zone13_AttZone14", 8.4, 16.1, 85.3, 0.38, 0.44),

        ("Player_JeremieFrimpong", "Jeremie Frimpong", 23, "Netherlands", "Right", 50000000,
         "Club_BayerLeverkusen", ["Club_ManchesterCity"], ["Manager_XabiAlonso", "Manager_PepGuardiola"],
         "Role_OverlappingWingback", "Zone11_AttRightFlank", "Zone6_MidRightFlank", 4.9, 14.8, 82.0, 0.35, 0.31),

        # --- EMERGING SCOUTING TARGETS (<€35M, Young, High-Ceiling) ---
        ("Player_AdamWharton", "Adam Wharton", 20, "England", "Left", 30000000,
         "Club_CrystalPalace", [], ["Manager_OliverGlasner"],
         "Role_DeepLyingPlaymaker", "Zone8_MidCentral", "Zone3_DefCentral", 7.9, 16.2, 89.4, 0.06, 0.21),

        ("Player_CarlosBaleba", "Carlos Baleba", 20, "Cameroon", "Left", 22000000,
         "Club_Brighton", [], ["Manager_PepGuardiola"],
         "Role_AnchorMan", "Zone8_MidCentral", "Zone3_DefCentral", 6.9, 19.4, 88.1, 0.04, 0.11),

        ("Player_AlanVarela", "Alan Varela", 23, "Argentina", "Right", 35000000,
         "Club_Porto", [], ["Manager_SimoneInzaghi"],
         "Role_DeepLyingPlaymaker", "Zone8_MidCentral", "Zone3_DefCentral", 8.2, 17.0, 91.2, 0.07, 0.16),

        ("Player_RayanAitNouri", "Rayan Ait-Nouri", 23, "Algeria", "Left", 35000000,
         "Club_CrystalPalace", [], ["Manager_OliverGlasner"],
         "Role_InvertedFullback", "Zone9_MidLeftHalfSpace", "Zone4_DefLeftHalfSpace", 7.0, 16.5, 86.8, 0.12, 0.24),

        ("Player_JohanBakayoko", "Johan Bakayoko", 21, "Belgium", "Left", 35000000,
         "Club_PSV", [], ["Manager_ArneSlot"],
         "Role_TouchlineWinger", "Zone11_AttRightFlank", "Zone11_AttRightFlank", 5.2, 11.8, 83.0, 0.36, 0.35),

        ("Player_ArthurVermeeren", "Arthur Vermeeren", 19, "Belgium", "Right", 25000000,
         "Club_AtleticoMadrid", [], ["Manager_DiegoSimeone"],
         "Role_Mezzala", "Zone7_MidRightHalfSpace", "Zone8_MidCentral", 7.1, 18.0, 89.1, 0.09, 0.17),

        ("Player_OscarGloukh", "Oscar Gloukh", 20, "Israel", "Right", 25000000,
         "Club_Benfica", [], ["Manager_RogerSchmidt"],
         "Role_InsideForward", "Zone14_AttLeftHalfSpace", "Zone13_AttZone14", 7.6, 15.3, 84.9, 0.31, 0.39),
    ]

    for (pid, pname, age, nat, foot, val, club_id, past_clubs, coached,
         prole, in_z, out_z, prog, press, pass_pct, xg, xa) in players:
        p_uri = FOOTRES[pid]
        g.add((p_uri, RDF.type, FOOTKG.Player))
        g.add((p_uri, RDFS.label, Literal(pname, lang="en")))
        g.add((p_uri, FOOTKG.playerName, Literal(pname, datatype=XSD.string)))
        g.add((p_uri, FOOTKG.age, Literal(age, datatype=XSD.integer)))
        g.add((p_uri, FOOTKG.nationality, Literal(nat, datatype=XSD.string)))
        g.add((p_uri, FOOTKG.preferredFoot, Literal(foot, datatype=XSD.string)))
        g.add((p_uri, FOOTKG.marketValueEUR, Literal(val, datatype=XSD.decimal)))
        g.add((p_uri, FOOTKG.playsFor, FOOTRES[club_id]))
        g.add((p_uri, FOOTKG.primaryRole, FOOTRES[prole]))
        g.add((p_uri, FOOTKG.inPossessionZone, FOOTRES[in_z]))
        g.add((p_uri, FOOTKG.outOfPossessionZone, FOOTRES[out_z]))
        g.add((p_uri, FOOTKG.progressivePassesPer90, Literal(prog, datatype=XSD.float)))
        g.add((p_uri, FOOTKG.pressuresPer90, Literal(press, datatype=XSD.float)))
        g.add((p_uri, FOOTKG.passCompletionPct, Literal(pass_pct, datatype=XSD.float)))
        g.add((p_uri, FOOTKG.xGPer90, Literal(xg, datatype=XSD.float)))
        g.add((p_uri, FOOTKG.xAPer90, Literal(xa, datatype=XSD.float)))

        for pc in past_clubs:
            g.add((p_uri, FOOTKG.formerlyPlayedFor, FOOTRES[pc]))
        for cb in coached:
            g.add((p_uri, FOOTKG.coachedBy, FOOTRES[cb]))

    # Chemistry Links (Explicit multi-hop connections)
    chemistry_links = [
        ("Player_OleksandrZinchenko", "Player_RicoLewis"), # Shared City & Pep heritage
        ("Player_BukayoSaka", "Player_DeclanRice"),         # England NT & Arsenal
        ("Player_Rodri", "Player_RicoLewis"),              # Man City central-halfspace axis
        ("Player_JudeBellingham", "Player_BukayoSaka"),     # England NT right-channel axis
        ("Player_JeremyDoku", "Player_JohanBakayoko"),      # Belgium NT wingers
        ("Player_AlanVarela", "Player_Rodri"),             # Tactical style & shared agent network
    ]
    for p1, p2 in chemistry_links:
        g.add((FOOTRES[p1], FOOTKG.hasChemistryWith, FOOTRES[p2]))
        g.add((FOOTRES[p2], FOOTKG.hasChemistryWith, FOOTRES[p1]))

    # -------------------------------------------------------------
    # 6. Match Event Graph (StatsBomb Style Passing Sequence)
    # -------------------------------------------------------------
    # Sequence: Rodri progresses from Zone 8 -> passes to Rico Lewis (inverting in Zone 7)
    # -> passes to Jeremy Doku (Zone 11) -> shot by Bellingham or Doku
    events = [
        ("Event_001_Rodri_BallRecovery", "BallRecovery", "Player_Rodri", "Zone3_DefCentral", "Zone8_MidCentral"),
        ("Event_002_Rodri_ProgressivePass", "ProgressivePass", "Player_Rodri", "Zone8_MidCentral", "Zone7_MidRightHalfSpace"),
        ("Event_003_Lewis_HalfSpaceCarry", "Pass", "Player_RicoLewis", "Zone7_MidRightHalfSpace", "Zone11_AttRightFlank"),
        ("Event_004_Doku_CutbackCross", "ProgressivePass", "Player_JeremyDoku", "Zone11_AttRightFlank", "Zone13_AttZone14"),
    ]

    for i in range(len(events)):
        eid, etype, pid, oz, tz = events[i]
        e_uri = FOOTRES[eid]
        g.add((e_uri, RDF.type, FOOTKG[etype]))
        g.add((e_uri, FOOTKG.performedBy, FOOTRES[pid]))
        g.add((e_uri, FOOTKG.originatesInZone, FOOTRES[oz]))
        g.add((e_uri, FOOTKG.terminatesInZone, FOOTRES[tz]))

        if i > 0:
            prev_eid = events[i-1][0]
            g.add((FOOTRES[prev_eid], FOOTKG.directlyPrecedes, e_uri))

    # Output populated graph
    output_path = os.path.join(os.path.dirname(__file__), "footkg_triples.ttl")
    g.serialize(destination=output_path, format="turtle")
    print(f"Knowledge Graph successfully built and serialized to {output_path}")
    print(f"Total Triples in FootKG: {len(g)}")
    return g

if __name__ == "__main__":
    build_knowledge_graph()
