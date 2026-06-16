import pandas as pd
import os

def main():
    input_path = "data/chembl/diabetes_drugs_raw.csv"
    output_path = "data/chembl/diabetes_drugs_clean.csv"
    
    if not os.path.exists(input_path):
        print(f"Error: Raw file {input_path} not found. Run download script first.")
        return

    print(f"Loading raw data from {input_path}...")
    df = pd.read_csv(input_path)
    
    print(f"Original shape: {df.shape}")

    # Columns we care about for our graph
    cols_to_keep = [
        'gene_symbol',          # The target gene
        'molecule_chembl_id',   # The drug
        'action_type',          # How it acts (e.g., INHIBITOR, AGONIST)
        'mechanism_of_action'   # Text description
    ]

    # Only select columns that exist in the raw dataframe
    existing_cols = [col for col in cols_to_keep if col in df.columns]
    
    clean_df = df[existing_cols].copy()

    # Drop records that are missing the crucial identifiers needed for graph edges
    if 'gene_symbol' in clean_df.columns and 'molecule_chembl_id' in clean_df.columns:
        clean_df = clean_df.dropna(subset=['gene_symbol', 'molecule_chembl_id'])

    # Remove any duplicates
    clean_df = clean_df.drop_duplicates()

    # Save cleaned data
    clean_df.to_csv(output_path, index=False)
    
    print("\nCleaning Complete!")
    print(f"Final shape: {clean_df.shape}")
    print("\nTop 5 Drug-Target Relationships:")
    print(clean_df.head())

if __name__ == "__main__":
    main()
