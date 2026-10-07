# Atlas Industrial Management — production image (Django + Gunicorn).
# Nginx (see docker-compose.yml) serves /static/ and /media/ and proxies the rest here.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencies first, so code changes don't reinstall them.
# If pypi.org is unreachable from the server, build with a mirror, e.g.:
#   PIP_INDEX_URL=https://mirror-pypi.runflare.com/simple docker compose build
ARG PIP_INDEX_URL=https://pypi.org/simple
COPY requirements.txt .
# The Docker stack uses PostgreSQL; mysqlclient (MariaDB, cPanel host) needs a C compiler, so skip it.
RUN grep -v "^mysqlclient" requirements.txt > /tmp/requirements.txt \
    && pip install --index-url "$PIP_INDEX_URL" -r /tmp/requirements.txt

COPY . .

# Run as an unprivileged user; static and media are written to mounted volumes.
# The sed strips Windows line endings in case the project was copied from a Windows machine.
RUN useradd --create-home --uid 1000 atlas \
    && mkdir -p /app/staticfiles /app/media \
    && sed -i 's/\r$//' /app/docker/entrypoint.sh \
    && chmod +x /app/docker/entrypoint.sh \
    && chown -R atlas:atlas /app
USER atlas

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "Atlas.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-"]
