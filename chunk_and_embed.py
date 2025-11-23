from pathlib import Path
from sentence_transformers import SentenceTransformer # type: ignore
import psycopg2
from pgvector.psycopg2 import register_vector

model = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_markdown(md_texts, max_len=1000):
    chunks = []
    current = []

    for line in md_texts.split("\n"):
        if line.startswith("# "):
            if current:
                chunks.append("\n".join(current))
                current = []
        current.append(line)
        if sum(len(l) for l in current) + len(line) > max_len:
            chunks.append("\n".join(current))
            current = []
    if current:
        chunks.append("\n".join(current))
    return chunks

for md_path in Path("scratch").glob("*.md"):
    md_texts = md_path.read_text()
    chunks = chunk_markdown(md_texts)

    print(md_path.name, len(chunks))


# """ Testing to see if the output actually comes out as expected """
# output_path = Path("scratch/chunks.txt")
# with output_path.open("w") as f:
#     for i, chunk in enumerate(chunks):
#         f.write(f"\n\n===== CHUNK {i} =====\n\n")
#         f.write(chunk)
#         f.write("\n")

def embed_chunks(chunks):
    embeddings = model.encode(chunks)
    with open("embeddings.txt", "w") as f:
        for i, emb in enumerate(embeddings):
            f.write(f"Chunk {i}:\n{emb.tolist() if hasattr(emb, 'tolist') else emb}\n\n")
    
embed_chunks(chunks) # Run the embedding function

# connect to the PostgreSQL database, casting the connection from variable -> to a vector type for psycopg2
conn = psycopg2.connect("dbname=pathways user=admin password=password host=localhost port=5432")
register_vector(conn)

# creates a cursor object to start executing SQL commands
cur = conn.cursor()
cur.execute('CREATE EXTENSION IF NOT EXISTS vector')

# create table of items with vector embeddings
cur.execute('CREATE TABLE IF NOT EXISTS items (id bigserial PRIMARY KEY, text TEXT, embedding vector(384))')

# embed by chunk, and insert into the database
for chunk in chunks:
    emb = model.encode(chunk)
    cur.execute('INSERT INTO items (text, embedding) VALUES (%s, %s)', (chunk, emb))
    conn.commit()

""" Index types for pgvector """
# Approximate Nearest Neighbor (ANN) indexes for faster search MEDIUM to LARGE datasets, bad space
cur.execute('CREATE INDEX IF NOT EXISTS ON items USING hnsw (embedding vector_l2_ops)')
# Cluster-based ANN 
# cur.execute('CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 100)')

# get the nearest neighbors for a given embedding/chunk to use for LLM context
query = "What is Pathways?"
query_emb = model.encode(query)
cur.execute('SELECT text FROM items ORDER BY embedding <-> %s LIMIT 5', (query_emb,))
results = cur.fetchall()
for r in results:
    print(r[0])
