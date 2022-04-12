# Discogs Graph Visualization Tool

## Installation

### Start Postgres (in docker or locally)

`docker-compose up`

### Fetch and Load Data

```
cd dump && ./get_latest_dumps.sh
docker build -t load_discogs -f Dockerfile.load-discogs .
docker run -it -v $(pwd)/dump:/dump load_discogs
```
