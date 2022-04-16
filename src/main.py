import re

import psycopg2
import psycopg2.extras

def sanitize(s):
    return re.sub(r'[^a-zA-Z0-9 ]', '', s)

allowed_roles = [
    "Mastered By", "Mixed By", "Produced By", "Performer", "Written By", "Written-By",
    "Producer"
]

graph = "graph LR\n"

# Connect to an existing database
conn = psycopg2.connect("dbname=discogs user=alon password=the3Qguy")

# Open a cursor to perform database operations
cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

# Get release
# master_title = "An Evening With Silk Sonic"
master_title = "Head Hunters"
cur.execute("SELECT * FROM master WHERE title = %s;", [master_title])
master = cur.fetchone()
# Add to graph
graph += f"    {master.main_release}[{sanitize(master.title)}]\n"

# Get release_artist associations
cur.execute(
    """
    SELECT * FROM release_artist
    WHERE release_id = %s
    AND (release_artist.role IN %s OR release_artist.role IS NULL)
    LIMIT 20
    """,
    [master.main_release, tuple(allowed_roles)]
)
release_artists = cur.fetchall()
for ra in release_artists:
    # Add artist node
    graph += f"    {ra.artist_id}[{sanitize(ra.artist_name)}]\n"
    # Add connection
    if ra.role:
        graph += f"    {ra.release_id} -->|{sanitize(ra.role)}| {ra.artist_id}\n"
    else:
        graph += f"    {ra.release_id} --> {ra.artist_id}\n"

# Use dict to deduplicate artists
artists = { ra.artist_id : ra for ra in release_artists }
# Get associated albums for each artist
for a in artists.values():
    cur.execute(
        """
        SELECT release_id, title, role
        FROM release_artist JOIN release ON release_artist.release_id = release.id
        WHERE artist_id = %s
        AND (release_artist.role IN %s OR release_artist.role IS NULL)
        LIMIT 5;
        """,
        [a.artist_id, tuple(allowed_roles)]
    )
    releases = cur.fetchall()
    for r in releases:
        # Add album node
        graph += f"    {r.release_id}[{sanitize(r.title)}]\n"
        # Add connection
        if r.role:
            graph += f"    {r.release_id} -->|{sanitize(r.role)}| {a.artist_id}\n"
        else:
            graph += f"    {r.release_id} --> {a.artist_id}\n"


print(graph)

cur.close()
conn.close()
