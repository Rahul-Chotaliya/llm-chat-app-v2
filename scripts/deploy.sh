APP_NAME="llm-chat-app-v2"
IMAGE_NAME="llm-chat-app-v2:latest"

set -e

DOCKER_IMAGE="$1"
BLUE_PORT=8000
GREEN_PORT=8001
NGINX_CONFIG_PATH="/etc/nginx/sites-available/${APP_NAME}"

echo "Building Docker image..."

CURRENT_ENV=$(docker ps --filter "name=${APP_NAME}" --format "{{.Names}}" | grep -o "blue\|green" || echo "none")

if [ "$CURRENT_ENV" = "blue" ]; then
    echo "Current environment: blue. Deploying to green..."
    NEW_ENV="green"
    NEW_PORT=$GREEN_PORT
else
    echo "Current environment: green or none. Deploying to blue..."
    NEW_ENV="blue"
    NEW_PORT=$BLUE_PORT
fi

for DOCKER_IMAGE in "$@"; do
    echo "Building image: $DOCKER_IMAGE"
    docker build -t "$DOCKER_IMAGE" .
done

docker stop "${APP_NAME}-${CURRENT_ENV}" || true
docker rm "${APP_NAME}-${CURRENT_ENV}" || true
echo "Starting new container: ${APP_NAME}-${NEW_ENV} on port ${NEW_PORT}..."
docker run -d --name "${APP_NAME}-${NEW_ENV}" -p "${NEW_PORT}:8000" "$DOCKER_IMAGE"

# Health check for the new container
HEALTHY=0
for i in {1..20}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${NEW_PORT}/health || true)
    if [ "$STATUS" = "200" ]; then
        HEALTHY=1
        echo "Health check passed for ${APP_NAME}-${NEW_ENV} on port ${NEW_PORT}."
        break
    else
        echo "Waiting for health check on port ${NEW_PORT}... ($i/20)"
        sleep 2
    fi
done

if [ "$HEALTHY" -ne 1 ]; then
    echo "Health check failed for ${APP_NAME}-${NEW_ENV} on port ${NEW_PORT}. Rolling back."
    docker stop "${APP_NAME}-${NEW_ENV}"
    docker rm "${APP_NAME}-${NEW_ENV}"
    exit 1
fi

# Wait for the new environment to accept connections
for i in {1..10}; do
    if nc -z localhost ${NEW_PORT}; then
        echo "Connection established to ${APP_NAME}-${NEW_ENV} on port ${NEW_PORT}."
        break
    else
        echo "Waiting for connection to port ${NEW_PORT}... ($i/10)"
        sleep 1
    fi
done

# Switch Nginx config
echo "Updating Nginx configuration to point to ${APP_NAME}-${NEW_ENV}..."
cat > "$NGINX_CONFIG_PATH" <<EOL
server {
    listen 80;
    server_name localhost;
    location / {
        proxy_pass http://localhost:${NEW_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Reload Nginx to switch traffic
echo "Reloading Nginx to switch traffic..."
sudo nginx -s reload

# Stop and remove the old environment after switch
if [ "$CURRENT_ENV" != "none" ]; then
    echo "Stopping and removing old environment: ${APP_NAME}-${CURRENT_ENV}"
    docker stop "${APP_NAME}-${CURRENT_ENV}" || true
    docker rm "${APP_NAME}-${CURRENT_ENV}" || true
fi

# Cleanup old Docker images (dangling and unused)
echo "Cleaning up old Docker images..."
docker image prune -af`