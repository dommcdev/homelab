# Deployment Instructions

## 1. Initial Setup (One-time)

Create the necessary directories on your server:
```bash
mkdir -p ~/filebrowser/config ~/filebrowser/database ~/files
chown -R 1000:1000 ~/filebrowser ~/files
```

Create the external network (shared by Caddy and other stacks):
```bash
docker network create homelab
```

## 2. Configuration

1.  Navigate to `homelab/filebrowser`
2.  Copy `.env.example` to `.env` and set your secrets:
    *   Set `ONLYOFFICE_JWT_SECRET` (generate a strong random string)

## 3. Build & Start

Build the custom image locally (or pull if you pushed to a registry) and start the stack:

```bash
# Build the image from your project directory

# Start the services
docker compose up -d
```

## 4. Configure OnlyOffice Integration

Run this command once to configure FileBrowser to talk to OnlyOffice.
**Note:** Replace `YOUR_SECRET_HERE` with the value from your `.env` file.

```bash
docker compose exec filebrowser filebrowser config set \
    --onlyoffice.url="https://office.dommcdev.net" \
    --onlyoffice.jwtSecret="YOUR_SECRET_HERE" \
    --onlyoffice.fileBrowserUrl="http://filebrowser:80" \
    --onlyoffice.enableFullscreen=true
```

## 5. Get Admin Password

FileBrowser generates a random password on first launch. Find it in the logs:

```bash
docker compose logs filebrowser | grep "Password:"
```

## 6. Access

*   **FileBrowser:** https://cloud.dommcdev.net
*   **OnlyOffice:** https://office.dommcdev.net (Health check page)

## Troubleshooting

If OnlyOffice fails to load documents:
1.  Check that the JWT secret matches in both `.env` and step 4.
2.  Ensure `https://office.dommcdev.net` is accessible from your browser.
3.  Check container logs: `docker compose logs -f`
