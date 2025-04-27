#!/bin/bash
set -e

# Default to development environment unless specified
ENV=${1:-development}
if [[ "$ENV" != "development" && "$ENV" != "production" ]]; then
  echo "Invalid environment. Use 'development' or 'production'."
  exit 1
fi

echo "Testing $ENV environment..."

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Testing in $TEMP_DIR"

# Copy files (excluding unnecessary ones)
echo "Copying files to test environment..."
rsync -a --exclude '.git/' --exclude 'venv/' --exclude '__pycache__/' \
  --exclude '*.pyc' --exclude '.vscode/' $(pwd)/ $TEMP_DIR/

# Verify docker-compose.yml exists in the correct subdirectory
if [ ! -f "$TEMP_DIR/docker/$ENV/docker-compose.yml" ]; then
  echo "Error: docker-compose.yml not found in docker/$ENV directory!"
  ls -la "$TEMP_DIR/docker/$ENV"
  rm -rf $TEMP_DIR
  exit 1
fi

# Make sure we have a test .env file
if [ ! -f "$TEMP_DIR/.env" ]; then
  echo "Creating test .env file..."
  echo "DJANGO_SECRET_KEY=test_secret_key_for_testing_only" > "$TEMP_DIR/.env"
  echo "DJANGO_DEBUG=1" >> "$TEMP_DIR/.env"
  echo "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1" >> "$TEMP_DIR/.env"
fi

# Change to the appropriate directory
cd "$TEMP_DIR/docker/$ENV"

# Build and test
echo "Starting Docker containers with docker-compose..."
docker-compose up --build -d

# Check if containers are running
echo "Checking container status..."
if ! docker-compose ps | grep -q "Up"; then
  echo "❌ Containers failed to start! Check docker-compose logs:"
  docker-compose logs
  docker-compose down
  rm -rf $TEMP_DIR
  exit 1
fi

# Wait for containers to start
echo "Waiting for services to initialize..."
sleep 30  # Increased wait time

# Test if the web server responds
echo "Testing application response..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 http://localhost || echo "CONNECTION_FAILED")
echo "Received HTTP status: $HTTP_STATUS"

# Accept both 200 (OK) and 302 (Redirect) as successful responses
if [[ "$HTTP_STATUS" == "200" || "$HTTP_STATUS" == "302" ]]; then
  echo "✅ Test successful! Application is responding with status code $HTTP_STATUS"
elif [[ "$HTTP_STATUS" == "CONNECTION_FAILED" ]]; then
  echo "❌ Test failed! Could not connect to the application"
  docker-compose logs
  echo "Container status:"
  docker-compose ps
  docker-compose down || true
  cd /tmp  # Move outside the temp directory before removing it
  rm -rf $TEMP_DIR || true
  exit 1
else
  echo "❌ Test failed! Application returned status code $HTTP_STATUS"
  docker-compose logs
  docker-compose down || true
  cd /tmp  # Move outside the temp directory before removing it
  rm -rf $TEMP_DIR || true
  exit 1
fi

# Clean up
echo "Cleaning up..."
docker-compose down || true
cd /tmp  # Move outside the temp directory before removing it
rm -rf $TEMP_DIR || true
echo "✅ Test completed and cleaned up successfully." 