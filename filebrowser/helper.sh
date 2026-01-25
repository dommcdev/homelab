#!/bin/bash
set -e

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Setting up FileBrowser with OnlyOffice..."

# 1. Configure .env
if [ ! -f .env ]; then
    echo "Copying .env.example to .env..."
    cp .env.example .env
else
    echo ".env already exists."
fi

# Generate and set JWT Secret if it's still the default or empty
# We blindly update it to a new secure one if it looks like the default
if grep -q "your-secret-key-here" .env; then
    echo "Generating secure JWT secret..."
    JWT_SECRET=$(openssl rand -hex 32)
    sed -i "s|ONLYOFFICE_JWT_SECRET=your-secret-key-here|ONLYOFFICE_JWT_SECRET=$JWT_SECRET|" .env
    echo "Updated ONLYOFFICE_JWT_SECRET in .env"
fi

# 2. Build Docker Image
echo "Building FileBrowser binary and Docker image..."
if [ ! -d "$HOME/dev/projects/filebrowser-onlyoffice" ]; then
    echo "Cloning filebrowser-onlyoffice repository..."
    gh repo clone dommcdev/filebrowser-onlyoffice ~/dev/projects/filebrowser-onlyoffice
fi

pushd ~/dev/projects/filebrowser-onlyoffice > /dev/null

if ! command_exists task; then
    echo "Error: 'task' is not installed. Please install go-task."
    exit 1
fi

CGO_ENABLED=0 task build
docker build -t filebrowser-onlyoffice .
popd > /dev/null

# 3. Create Directories and Set Permissions
echo "Creating data directories..."
mkdir -p ~/filebrowser/config ~/filebrowser/database ~/files
chown -R 1000:1000 ~/filebrowser ~/files

# 4. Start Docker Compose
echo "Starting containers..."
docker compose up -d
sleep 5

# 5. Retrieve password
echo "Retrieving initial admin password from logs..."
docker compose logs filebrowser 2>&1 | grep "password:" || echo "Password not found in logs yet. Check manually with: docker compose logs filebrowser"
echo "---------------------------------------------------"
