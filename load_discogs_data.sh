python3 run.py \
        --bz2 --apicounts \
        --export artist --export label \
        --export master --export release \
        --output /tmp/csv-files \
        ../dump \

python3 postgresql/psql.py < postgresql/sql/CreateTables.sql
python3 postgresql/importcsv.py /tmp/csv-files/*

python3 postgresql/psql.py < postgresql/sql/CreatePrimaryKeys.sql
python3 postgresql/psql.py < postgresql/sql/CreateFKConstraints.sql
python3 postgresql/psql.py < postgresql/sql/CreateIndexes.sql
