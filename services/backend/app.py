from datetime import datetime
from typing import List, Optional, Dict, Any
import os
import subprocess
import sys

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


# get local methods for RAG data preparation
from services.backend.rag.scrape_docs import main as scrape_docs
from services.backend.rag.transform_data import main as transform_data
from services.backend.rag.default_chunk import main as default_chunk
from services.backend.rag.docling_chunk import main as docling_chunk

def spin_up_docker():
    subprocess.run(["docker", "compose", "up", "-d", ])

def main():
    """ spin up all docker containers ->  prepare data for RAG -> chunk and embed data into pathways_db """
    # create and start all docker containers
    spin_up_docker()
    # transform the retrieved documents into usable data formats
    transform_data()
    # chunk and embed the transformed data for use in retrieval-augmented generation
    docling_chunk()
    # default_chunk()



if __name__ == "__main__": 
    main()
