# Shared by the HTTP and HTTPS server blocks in atlas.conf.

client_max_body_size 25m;          # admin uploads: product photos, PDF catalogues

gzip on;
gzip_types text/css application/javascript image/svg+xml application/json text/plain;
gzip_min_length 1024;

# Static files have content hashes in their names (ManifestStaticFilesStorage) -> cache for a year.
location /static/ {
    alias /app/staticfiles/;
    expires 365d;
    add_header Cache-Control "public, immutable";
    access_log off;
}

location /media/ {
    alias /app/media/;
    expires 30d;
    add_header Cache-Control "public";
    add_header X-Content-Type-Options "nosniff";
    access_log off;
}

location / {
    proxy_pass http://atlas_web;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $atlas_proto;
    proxy_redirect off;
    proxy_read_timeout 60s;
}
