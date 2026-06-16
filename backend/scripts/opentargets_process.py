import pandas as pd

df = pd.read_csv(
    "data/opentargets/type2_diabetes.tsv",
    sep="\t"
)

clean_df = df[
    [
        "symbol",
        "globalScore"
    ]
]

clean_df = clean_df.rename(
    columns={
        "symbol": "gene_symbol",
        "globalScore": "association_score"
    }
)

clean_df["disease"] = "Type 2 Diabetes"

clean_df = clean_df.dropna()

clean_df = clean_df.sort_values(
    by="association_score",
    ascending=False
)

clean_df = clean_df.head(1000)

clean_df.to_csv(
    "data/opentargets/diabetes_genes_clean.csv",
    index=False
)

print("Cleaning complete!")
print(clean_df.head())