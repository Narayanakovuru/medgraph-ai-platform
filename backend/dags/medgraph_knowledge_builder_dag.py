from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from neo4j import GraphDatabase
import pandas as pd
import os

default_args = {
    'owner': 'medgraph',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# The NEO4J container is accessible as "neo4j" within the docker network
NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Narayana@24"

# The data path mapped in docker-compose.yml
DATA_PATH = "/opt/airflow/data"

def check_data_files():
    """Verify that all required data files exist before running ingestion."""
    required_files = [
        f"{DATA_PATH}/opentargets/diabetes_genes_clean.csv",
        f"{DATA_PATH}/string/diabetes_interactions_clean.csv"
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        raise FileNotFoundError(f"Missing required data files: {missing}")
        
    if not os.path.exists(f"{DATA_PATH}/chembl/diabetes_drugs_clean.csv"):
        print("Note: ChEMBL drugs dataset is not finished downloading yet. ETL will proceed with Genes and Proteins.")
    else:
        print("All datasets found, including ChEMBL.")

def load_genes():
    """Load Disease and Gene nodes from OpenTargets."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    df = pd.read_csv(f"{DATA_PATH}/opentargets/diabetes_genes_clean.csv")
    
    with driver.session() as session:
        for _, row in df.iterrows():
            session.run("""
                MERGE (d:Disease {name: $disease})
                MERGE (g:Gene {symbol: $gene})
                MERGE (d)-[r:ASSOCIATED_WITH {score: $score}]->(g)
            """, 
            disease=row['disease'], 
            gene=row['gene_symbol'],
            score=float(row['association_score']) if pd.notnull(row['association_score']) else 0.0)
    
    driver.close()
    print(f"Loaded {len(df)} genes.")

def load_interactions():
    """Load Protein-Protein interactions from STRING."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    df = pd.read_csv(f"{DATA_PATH}/string/diabetes_interactions_clean.csv")
    
    with driver.session() as session:
        for _, row in df.iterrows():
            # For this graph, we'll map Gene to Protein if it interacts,
            # or we can just treat them as interacting genes/proteins.
            session.run("""
                MERGE (p1:Protein {symbol: $protein_a})
                MERGE (p2:Protein {symbol: $protein_b})
                MERGE (p1)-[r:INTERACTS_WITH {score: $score}]->(p2)
                
                // Link Gene to Protein if symbol matches
                WITH p1, p2
                MATCH (g1:Gene {symbol: p1.symbol})
                MERGE (g1)-[:TRANSLATES_TO]->(p1)
                
                WITH p2
                MATCH (g2:Gene {symbol: p2.symbol})
                MERGE (g2)-[:TRANSLATES_TO]->(p2)
            """, 
            protein_a=row['protein_a'], 
            protein_b=row['protein_b'],
            score=float(row['interaction_score']) if pd.notnull(row['interaction_score']) else 0.0)
            
    driver.close()
    print(f"Loaded {len(df)} interactions.")

def load_drugs():
    """Load Drugs targeting Proteins from ChEMBL."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    chembl_path = f"{DATA_PATH}/chembl/diabetes_drugs_clean.csv"
    if not os.path.exists(chembl_path):
        print("ChEMBL data not ready yet. Skipping drug load.")
        return
        
    df = pd.read_csv(chembl_path)
    
    with driver.session() as session:
        for _, row in df.iterrows():
            session.run("""
                MERGE (d:Drug {chembl_id: $drug_id})
                MERGE (p:Protein {symbol: $target_symbol})
                MERGE (d)-[r:TARGETS {action: $action}]->(p)
            """, 
            drug_id=row['molecule_chembl_id'], 
            target_symbol=row['gene_symbol'],
            action=str(row['action_type']) if pd.notnull(row['action_type']) else "UNKNOWN")
            
    driver.close()
    print(f"Loaded {len(df)} drug relationships.")

with DAG(
    'medgraph_knowledge_builder',
    default_args=default_args,
    description='ETL pipeline to ingest MedGraph data into Neo4j',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['medgraph', 'neo4j', 'etl'],
) as dag:

    t1_check_data = PythonOperator(
        task_id='check_data_files',
        python_callable=check_data_files,
    )

    t2_load_genes = PythonOperator(
        task_id='load_genes',
        python_callable=load_genes,
    )

    t3_load_interactions = PythonOperator(
        task_id='load_interactions',
        python_callable=load_interactions,
    )

    t4_load_drugs = PythonOperator(
        task_id='load_drugs',
        python_callable=load_drugs,
    )

    # Define DAG execution order
    t1_check_data >> t2_load_genes >> t3_load_interactions >> t4_load_drugs
