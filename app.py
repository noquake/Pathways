import subprocess
import sys

from services.rag.scrape_docs import main as scrape_docs
from services.rag.transform_data import main as transform_data
from services.rag.default_chunk import main as default_chunk
from services.rag.docling_chunk import main as docling_chunk

def spin_up_docker():
    subprocess.run(["docker", "compose", "up", "-d", ])

def main():
    # retrieve the needed clinical documentation
    # scrape_docs() UNCOMMENT FOR FULL DATABASE EXTRACTION

    # spin up db services
    spin_up_docker()

    # transform the retrieved documents into usable data formats
    transform_data()

    # chunk and embed the transformed data for use in retrieval-augmented generation
    docling_chunk()

if __name__ == "__main__": 
    main()
