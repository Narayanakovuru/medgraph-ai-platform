import pandas as pd
import requests
import os

print("Loading genes from OpenTargets dataset...")
df = pd.read_csv("data/opentargets/diabetes_genes_clean.csv")
# Use all 1000 genes to match PubMed's scale
genes = df["gene_symbol"].tolist()

print(f"Querying STRING API for interactions among top {len(genes)} genes...")
url = "https://string-db.org/api/tsv/network"
params = {
    "identifiers": "\r".join(genes),
    "species": 9606, # Human
    "required_score": 700 # High confidence interactions only
}

# Use POST request since the identifiers list is long
response = requests.post(url, data=params)

os.makedirs("data/string", exist_ok=True)
output_file = "data/string/diabetes_interactions.tsv"

with open(output_file, "w", encoding="utf-8") as f:
    f.write(response.text)

print(f"STRING data saved to {output_file}")