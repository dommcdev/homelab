# Stop and remove all Nextcloud containers and volumes
docker compose down --volumes
docker rm -f $(docker ps -aq --filter name=^nextcloud-aio --filter name=^nextcloud_aio)
docker volume rm $(docker volume list -q --filter name=^nextcloud-aio --filter name=^nextcloud_aio)
docker network remove nextcloud-aio

# Optional: Remove data directories (uncomment if needed)
#sudo rm -rf /mnt/ncdata

# Restart system services
sudo systemctl daemon-reload
sudo systemctl restart docker
