import os
from Bio import Entrez

Entrez.email = "k.lakshminarayana0924@gmail.com"

print("Searching PubMed for 'type 2 diabetes'...")
search = Entrez.esearch(
    db="pubmed",
    term="type 2 diabetes",
    retmax=1000
)

result = Entrez.read(search)
ids = result["IdList"]

print(f"Found {len(ids)} articles. Downloading abstracts...")
fetch = Entrez.efetch(
    db="pubmed",
    id=",".join(ids),
    rettype="abstract",
    retmode="text"
)

data = fetch.read()

output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "pubmed")
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "diabetes_abstracts.txt")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(data)

print(f"Successfully saved {len(ids)} abstracts to {os.path.abspath(output_file)}")