import subprocess
import sys

from scrape_docs import main as scrape_docs
from transform_data import main as transform_data
from chunk_and_embed import main as chunk_and_embed

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
    chunk_and_embed()

if __name__ == "__main__": 
    main()
