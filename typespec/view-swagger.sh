#!/bin/bash
# Script to view TypeSpec-generated OpenAPI in Swagger UI

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Path to the generated OpenAPI file
# Try the configured location first, then fall back to default nested structure
if [ -f "$SCRIPT_DIR/tsp-output/openapi.yaml" ]; then
    OPENAPI_FILE="$SCRIPT_DIR/tsp-output/openapi.yaml"
elif [ -f "$SCRIPT_DIR/tsp-output/@typespec/openapi3/openapi.yaml" ]; then
    OPENAPI_FILE="$SCRIPT_DIR/tsp-output/@typespec/openapi3/openapi.yaml"
else
    echo "Error: OpenAPI file not found"
    echo "Expected locations:"
    echo "  - $SCRIPT_DIR/tsp-output/openapi.yaml"
    echo "  - $SCRIPT_DIR/tsp-output/@typespec/openapi3/openapi.yaml"
    echo "Please run 'npm run build' in the typespec directory first."
    exit 1
fi


echo "Starting Swagger UI..."
echo "OpenAPI file: $OPENAPI_FILE"
echo ""
echo "Swagger UI will be available at: http://localhost:8080"
echo "Press Ctrl+C to stop the server"
echo ""

# Run Docker container with correct paths
docker run -p 8080:8080 \
  -e SWAGGER_JSON=/openapi.yaml \
  -v "$OPENAPI_FILE:/openapi.yaml:ro" \
  swaggerapi/swagger-ui

