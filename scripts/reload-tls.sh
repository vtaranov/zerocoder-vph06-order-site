#!/bin/sh
# Install as /etc/letsencrypt/renewal-hooks/deploy/vph04-nginx (root, 0755).
set -eu
cd /opt/vph04-orders
if docker compose ps --status running --services 2>/dev/null | grep -qx nginx; then
  docker compose exec -T nginx nginx -t
  docker compose exec -T nginx nginx -s reload
fi
