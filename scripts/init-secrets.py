#!/usr/bin/env python3
"""Create private deployment configuration using the Python standard library."""
import argparse
from pathlib import Path
import secrets
parser = argparse.ArgumentParser()
parser.add_argument("--host", required=True)
parser.add_argument("--email", required=True)
parser.add_argument("--port", default="18443", type=int)
a = parser.parse_args()
root = Path(__file__).resolve().parent.parent
if (root / ".env").exists():
    raise SystemExit(".env already exists; refusing to replace credentials")
s = (root / ".env.example").read_text()
s = s.replace("your-server.example.com", a.host).replace("admin@example.com", a.email)
s = s.replace("HTTPS_PORT=18443", f"HTTPS_PORT={a.port}")
for placeholder in ["replace-with-unique-password", "replace-with-another-unique-password", "replace-with-random-hex-string", "replace-with-secret-key", "replace-with-bootstrap-token"]:
    s = s.replace(placeholder, secrets.token_hex(24))
f = root / ".env"
f.write_text(s)
f.chmod(0o600)
private = root / "secrets"
private.mkdir(mode=0o700, exist_ok=True)
private.chmod(0o700)
cfg = private / "docker-config.json"
if not cfg.exists():
    cfg.write_text("{}\n")
    cfg.chmod(0o600)
print("Created .env and secrets/docker-config.json. Do not commit these files.")
