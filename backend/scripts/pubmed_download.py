import os
from pathlib import Path

from Bio import Entrez


def main() -> None:
    """
    Download PubMed abstracts for 'type 2 diabetes' and save them locally.

    Uses the NCBI Entrez API (Biopython). Requires internet access.
    The output file is written relative to this script's location so the
    path is correct regardless of the current working directory.
    """

    Entrez.email = "k.lakshminarayana0924@gmail.com"

    print("Searching PubMed for 'type 2 diabetes'...")
    search = Entrez.esearch(
        db="pubmed",
        term="type 2 diabetes",
        retmax=1000,
    )

    result = Entrez.read(search)
    ids = result["IdList"]

    print(f"Found {len(ids)} articles. Downloading abstracts...")
    fetch = Entrez.efetch(
        db="pubmed",
        id=",".join(ids),
        rettype="abstract",
        retmode="text",
    )

    data = fetch.read()

    # Resolve the output directory relative to *this script's* location so
    # it works regardless of where the user launches the command from.
    script_dir = Path(__file__).resolve().parent
    output_dir = script_dir.parent / "data" / "pubmed"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "diabetes_abstracts.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(data)

    print(f"Successfully saved {len(ids)} abstracts to {output_file}")


if __name__ == "__main__":
    main()