import re

import psycopg2
import psycopg2.extras

def sanitize(s):
    return re.sub(r'[^a-zA-Z0-9 ]', '', s)

graph = "graph TD\n"

# Connect to an existing database
conn = psycopg2.connect("dbname=discogs user=alon password=the3Qguy")

# Open a cursor to perform database operations
cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

# Get release
master_title = "Narrow Stairs"
cur.execute("SELECT * FROM master WHERE title = %s;", [master_title])
master = cur.fetchone()
# Add to graph
graph += f"    {master.main_release}[{sanitize(master.title)}]\n"

# Get release_artist associations
cur.execute("SELECT * FROM release_artist WHERE release_id = %s LIMIT 10", [master.main_release])
release_artists = cur.fetchall()
for ra in release_artists:
    # Add artist node
    graph += f"    {ra.artist_id}[{sanitize(ra.artist_name)}]\n"
    # Add connection
    if ra.role:
        graph += f"    {ra.release_id} -->|{sanitize(ra.role)}| {ra.artist_id}\n"

# Use dict to deduplicate artists
artists = { ra.artist_id : ra for ra in release_artists }
# Get associated albums for each artist
for a in artists.values():
    cur.execute("SELECT release_id, title, role FROM release_artist JOIN release ON release_artist.release_id = release.id WHERE artist_id = %s LIMIT 5;", [a.artist_id])
    releases = cur.fetchall()
    for r in releases:
        # Add album node
        graph += f"    {r.release_id}[{sanitize(r.title)}]\n"
        # Add connection
        if r.role:
            graph += f"    {r.release_id} -->|{sanitize(r.role)}| {a.artist_id}\n"


print(graph)

cur.close()
conn.close()
