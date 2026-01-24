# Homelab Setup

Filebrowser, OnlyOffice, Immich, Gitlab, etc, via Caddy w/DNS-01 challenge


### 1. Configure Caddy

```bash
cd caddy
cp .env.example .env
# Edit .env and add your Cloudflare API token
docker compose up -d
```

### 2. Configure FileBrowser

```bash
cd filebrowser
cp .env.example .env
# Edit .env and set a secure JWT secret

mkdir -p ~/filebrowser/config ~/filebrowser/database ~/files && chown -R 1000:1000 ~/filebrowser ~/files

docker compose up -d

# Run once to configure onlyoffice stuff (replace YOUR_SECRET_HERE with above JWT secret)
docker compose exec filebrowser filebrowser config set \
    --onlyoffice.url="https://office.dommcdev.net" \
    --onlyoffice.jwtSecret="YOUR_SECRET_HERE" \
    --onlyoffice.fileBrowserUrl="http://filebrowser:80" \
    --onlyoffice.enableFullscreen=true

# Get admin password (username is admin)
docker compose logs filebrowser | grep "Password:"
```

### 3. Configure Immich

```bash
cd immich
cp .env.example .env #change postgress secret if desired

mkdir -p ~/immich ~/files && chown -R 1000:1000 ~/immich ~/files

docker-compose up -d
```
