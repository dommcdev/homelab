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

# If necessary, build local docker image
gh repo clone dommcdev/filebrowser-onlyoffice && cd filebrowser-onlyoffice
CGO_ENABLED=0 task build
docker build -t filebrowser-onlyoffice

docker compose up -d

# Run once to configure onlyoffice stuff (replace YOUR_SECRET_HERE with above JWT secret)
docker compose stop filebrowser
docker compose run --rm --entrypoint /bin/filebrowser filebrowser config set \
    --onlyoffice.url="https://office.dommcdev.net" \
    --onlyoffice.jwtSecret="YOUR_SECRET_HERE" \
    --onlyoffice.fileBrowserUrl="http://filebrowser:80"

# Get admin password (username is admin)
docker compose logs filebrowser | grep "password:"
```

### 3. Configure Immich

```bash
cd immich
cp .env.example .env #change postgress secret if desired

mkdir -p ~/immich ~/files && chown -R 1000:1000 ~/immich ~/files

docker-compose up -d
```
