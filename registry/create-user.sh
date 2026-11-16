#!/bin/sh
# Usage: ./registry/create-user.sh USER [--stdin]
set -eu
cd "$(dirname "$0")/.."
user=${1:?Usage: create-user.sh USER [--stdin]}
mkdir -p secrets/registry
chmod 700 secrets secrets/registry
touch secrets/registry/htpasswd
if [ "${2:-}" = --stdin ]; then
  docker run --rm -i -v "$PWD/secrets/registry:/auth" httpd:2.4-alpine htpasswd -Bi /auth/htpasswd "$user"
else
  docker run --rm -it -v "$PWD/secrets/registry:/auth" httpd:2.4-alpine htpasswd -B /auth/htpasswd "$user"
fi
chmod 644 secrets/registry/htpasswd
