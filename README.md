# Discogs Graph Visualization Tool

## Installation

### Start Postgres

`docker-compose up`

### Fetch and Load Data

```
cd dump && ./get_latest_dumps.sh
docker build -t load_discogs -f Dockerfile.load-discogs .
docker run -it load_discogs
```
