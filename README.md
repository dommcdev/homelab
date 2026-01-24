# Homelab Setup

Modular Docker Compose setup for homelab services.

## Structure

```
homelab/
├── caddy/           # Reverse proxy with auto HTTPS
│   ├── Caddyfile
│   ├── docker-compose.yml
│   └── Dockerfile
└── filebrowser/     # FileBrowser + OnlyOffice
    ├── docker-compose.yml
    ├── data/        # Your files
    └── database/    # FileBrowser DB
```

## Initial Setup

### 1. Create the shared network

```bash
docker network create homelab
```

### 2. Configure Caddy

```bash
cd caddy
cp .env.example .env
# Edit .env and add your Cloudflare API token
```

### 3. Configure FileBrowser

```bash
cd ../filebrowser
cp .env.example .env
# Edit .env and set a secure JWT secret

# Initialize the FileBrowser database
touch database/filebrowser.db
docker-compose run --rm filebrowser config init
docker-compose run --rm filebrowser users add admin yourpassword --perm.admin

# Configure OnlyOffice integration
docker-compose run --rm filebrowser config set --onlyoffice.url "https://docs.dommcdev.net"
docker-compose run --rm filebrowser config set --onlyoffice.fileBrowserUrl "http://filebrowser:8080"
docker-compose run --rm filebrowser config set --onlyoffice.jwtSecret "your-secret-key-here"  # Must match .env
```

### 4. Start everything

```bash
# Start Caddy first
cd ../caddy
docker-compose up -d

# Then FileBrowser + OnlyOffice
cd ../filebrowser
docker-compose up -d
```

## Access

- **FileBrowser:** https://cloud.dommcdev.net
- **OnlyOffice:** https://docs.dommcdev.net (used internally by FileBrowser)

## Adding More Services

1. Create a new directory: `mkdir ../immich`
2. Add your `docker-compose.yml` with `networks: homelab` (external)
3. Add an entry to `caddy/Caddyfile`
4. Reload Caddy: `docker-compose exec caddy caddy reload --config /etc/caddy/Caddyfile`
