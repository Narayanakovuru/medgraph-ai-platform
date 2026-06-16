import pandas as pd

# Read raw STRING file
df = pd.read_csv(
    "data/string/diabetes_interactions.tsv",
    sep="\t"
)

print("Original Shape:", df.shape)

# Keep only required columns
clean_df = df[
    [
        "preferredName_A",
        "preferredName_B",
        "score"
    ]
]

# Rename columns
clean_df = clean_df.rename(
    columns={
        "preferredName_A": "protein_a",
        "preferredName_B": "protein_b",
        "score": "interaction_score"
    }
)

# Remove missing values
clean_df = clean_df.dropna()

# Keep strongest interactions first
clean_df = clean_df.sort_values(
    by="interaction_score",
    ascending=False
)

# Remove duplicate rows
clean_df = clean_df.drop_duplicates()

# Save cleaned data
clean_df.to_csv(
    "data/string/diabetes_interactions_clean.csv",
    index=False
)

print("\nCleaning Complete")
print("Final Shape:", clean_df.shape)
print("\nTop Interactions:")
print(clean_df.head())