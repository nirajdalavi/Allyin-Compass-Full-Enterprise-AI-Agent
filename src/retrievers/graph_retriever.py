from neo4j import GraphDatabase

# 🔑 Update this with your Neo4j credentials
URI = "bolt://3.86.59.217"
AUTH = ("neo4j", "diaphragm-whirls-claps")  # Change "your-password" to your actual one

driver = GraphDatabase.driver(URI, auth=AUTH)

# --- Creates 10 entities and relationships in Neo4j ---
def create_sample_graph():
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        # Step 2: Insert new data across domains
        session.run("""
            CREATE (:Facility {name: "Plant A", domain: "energy"})-[:EXCEEDS]->(:Regulation {type: "CO2 Limit"}),
                   (:Facility {name: "Plant B", domain: "energy"})-[:EXCEEDS]->(:Regulation {type: "Water Usage"}),
                   (:Facility {name: "Plant C", domain: "energy"})-[:COMPLIES_WITH]->(:Regulation {type: "CO2 Limit"}),

                   (:ResearchLab {name: "Lab X", domain: "biotech"})-[:RESEARCHES]->(:Molecule {name: "ZY-102"}),
                   (:ResearchLab {name: "Lab Y", domain: "biotech"})-[:PUBLISHED]->(:Paper {title: "Cancer Immunotherapy Results"}),
                   (:ResearchLab {name: "Lab Z", domain: "biotech"})-[:RESEARCHES]->(:Molecule {name: "AB-77"}),

                   (:Client {name: "ABC Corp", domain: "finance"})-[:ASSESSED_FOR]->(:RiskCategory {type: "High Risk"}),
                   (:Client {name: "XYZ Ltd", domain: "finance"})-[:ASSESSED_FOR]->(:RiskCategory {type: "Medium Risk"}),
                   (:Client {name: "FinSecure", domain: "finance"})-[:FLAGGED_BY]->(:Auditor {name: "RegCheck Inc."})
        """)
        print("✅ Created new domain-aware graph with energy, biotech, and finance data.")



def get_graph_facts():
    with driver.session() as session:
        result = session.run("""
            MATCH (a)-[r]->(b)
            RETURN
                coalesce(a.name, a.title, a.type) AS from,
                type(r) AS relation,
                coalesce(b.name, b.title, b.type) AS to
        """)
        return [{"from": record["from"], "relation": record["relation"], "to": record["to"]} for record in result]

if __name__ == "__main__":
    # create_sample_graph()
    facts = get_graph_facts()
    for f in facts:
        print(f"🔗 {f['from']} {f['relation']} {f['to']}")

