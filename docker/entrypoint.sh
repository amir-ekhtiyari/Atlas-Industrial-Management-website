#!/bin/sh
# Container start-up: wait for PostgreSQL, apply migrations, collect static files,
# fill the database with the company's content on the very first deploy only.
set -e

echo "Waiting for the database..."
python - <<'PY'
import os, sys, time
import psycopg2

for attempt in range(60):
    try:
        psycopg2.connect(
            dbname=os.environ['DB_NAME'], user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'], host=os.environ.get('DB_HOST', 'db'),
            port=os.environ.get('DB_PORT', '5432'),
        ).close()
        sys.exit(0)
    except psycopg2.OperationalError:
        time.sleep(2)
sys.exit("Database is not reachable after 120 seconds.")
PY

python manage.py migrate --noinput
python manage.py collectstatic --noinput --verbosity 0

# Only on an empty database: never overwrites what the client edits in the admin.
python manage.py load_client_content --if-empty

exec "$@"
