import pandas as pd
from chembl_webresource_client.new_client import new_client
import os

def main():
    print("Loading genes from OpenTargets dataset...")
    # Load dynamically without hardcoding
    input_file = "data/opentargets/diabetes_genes_clean.csv"
    if not os.path.exists(input_file):
        print(f"Error: Could not find {input_file}")
        return

    df_genes = pd.read_csv(input_file)
    
    import time
    # Let's run all 1000 without sleep!
    genes = df_genes["gene_symbol"].tolist()
    
    target_api = new_client.target
    mechanism_api = new_client.mechanism
    
    all_mechanisms = []
    
    print(f"Querying ChEMBL API for targets corresponding to top {len(genes)} genes...")
    
    for gene in genes:
        print(f"Processing gene: {gene}")
        time.sleep(0.5) # Sleep to respect API rate limits
        
        # 1. Find the target ChEMBL ID for the gene
        try:
            targets = target_api.search(gene)
            if not targets:
                continue
        except Exception as e:
            print(f"  -> Skipping {gene} due to API error: {e}")
            continue
            
        # Filter for human single proteins
        human_targets = [
            t for t in targets 
            if t.get('target_type') == 'SINGLE PROTEIN' and t.get('organism') == 'Homo sapiens'
        ]
        
        if not human_targets:
            continue
            
        # Take the most relevant target match
        target_chembl_id = human_targets[0]['target_chembl_id']
        
        # 2. Find the drugs/mechanisms for this target
        mechs = mechanism_api.filter(target_chembl_id=target_chembl_id)
        
        for m in mechs:
            m['gene_symbol'] = gene # Add our gene symbol so we can link it later
            all_mechanisms.append(m)

    # Save raw data
    os.makedirs("data/chembl", exist_ok=True)
    output_path = "data/chembl/diabetes_drugs_raw.csv"
    
    if all_mechanisms:
        raw_df = pd.DataFrame(all_mechanisms)
        raw_df.to_csv(output_path, index=False)
        print(f"\nSuccessfully saved {len(raw_df)} raw drug mechanisms to {output_path}")
    else:
        print("\nNo mechanisms found for the given genes.")

if __name__ == "__main__":
    main()
