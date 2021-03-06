import os
import re

import psycopg2
import psycopg2.extras

from pyvis.network import Network

RELEASE_COLOR = "blue"
ARTIST_COLOR = "red"

def sanitize(s):
    return re.sub(r'[^a-zA-Z0-9 ]', '', s)

# Create network object
network = Network(height='750px', width='100%', font_color="#ffffff")
network.set_options(
     """
 var options = {
   "nodes": {
     "font": {
       "size": 74
     }
   },
   "edges": {
     "color": {
       "inherit": true
     },
     "smooth": false,
     "font": {
       "size" : 74
     }
   },
   "physics": {
     "barnesHut": {
       "gravitationalConstant": -800000,
       "springLength": 250,
       "springConstant": 0.001
     },
     "minVelocity": 0.75
   }
 }
     """)

# Connect to an existing database
conn = psycopg2.connect("dbname=discogs user=alon password=the3Qguy")

# Open a cursor to perform database operations
cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)


master_title = input("Enter an album name: ")
# Get release
# master_title = "An Evening With Silk Sonic"
# master_title = "Head Hunters"
cur.execute(
    """
    SELECT master.id, artist_name, master.year, main_release, title
    FROM master
    JOIN master_artist ON master_id = master.id
    WHERE title = %s;
    """,
    [master_title]
)

all_masters = cur.fetchall()
for i, m in enumerate(all_masters):
    print(f"{i:<2} | {master_title} - {m.artist_name} ({m.year})")

master_index = int(input("Please select which album you would like: "))
master = all_masters[master_index]

# Add to graph
network.add_node(
    master.main_release,
    label = master.title,
    shape = "box",
    color = RELEASE_COLOR,
)

NUM_RECURSIONS = 3

for i in range(NUM_RECURSIONS):
    nodes = list(network.get_nodes())
    for n_id in nodes:
        node = network.get_node(n_id)
        if node["color"] == RELEASE_COLOR:
            # Find artists
            cur.execute(
                """
                SELECT artist_id, artist_name, release_id, role
                FROM release_artist
                JOIN artist ON release_artist.artist_id = artist.id
                WHERE release_id = %s
                LIMIT 10;
                """,
                [n_id]
            )
            artists = cur.fetchall()
            for a in artists:
                # Add artist node
                network.add_node(
                    a.artist_id,
                    shape = "box",
                    label = a.artist_name,
                    color = ARTIST_COLOR
                )
                # Add connection
                network.add_edge(a.release_id, a.artist_id, label = a.role or "")
        elif node["color"] == ARTIST_COLOR:
            cur.execute(
                """
                SELECT release_id, title, role, released
                FROM release_artist
                JOIN release ON release_artist.release_id = release.id
                WHERE artist_id = %s
                LIMIT 5;
                """,
                [n_id]
            )
            releases = cur.fetchall()
            for r in releases:
                # Add album node
                network.add_node(
                    r.release_id,
                    shape = "box",
                    label = f"{r.title} - {r.released}",
                    color = RELEASE_COLOR
                )
                # Add connection
                network.add_edge(r.release_id, n_id, label = r.role or "")
        else:
            raise Exception()

# network.show_buttons()
network.show("graph.html")

os.system("open graph.html")

cur.close()
conn.close()
