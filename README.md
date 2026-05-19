# Homelab

Filebrowser, OnlyOffice, Immich, Gitea, etc. Accessable on my Tailscale network via Caddy and the Cloudflare DNS-01 challenge.

## Setup

### Start docker containers

```bash
cd container-dir
cp .env.example .env #edit as needed
make up
```
Start the Caddy container last (otherwise it won't know about all the other containers it is proxying).

## Troubleshooting
Start and stop the containers a few times. This usually fixes things.
