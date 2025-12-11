#!/usr/bin/env bash
set -euo pipefail
# Helper to build AIDE agent images.
# Usage: ./build_agent.sh [tabular|vision|full]
# - tabular: uses requirements_tabular_nlp.txt (fast)
# - vision: uses existing requirements.txt (includes vision deps)
# - full: same as vision but no-cache

FLAVOR=${1:-tabular}
TAG="aide-${FLAVOR}"
BUILD_ARGS=(--platform=linux/amd64 -f Dockerfile)

if [ "$FLAVOR" = "tabular" ]; then
  # Build using the lightweight requirements file (Dockerfile chooses it if present)
  docker build --no-cache -t ${TAG} "${BUILD_ARGS[@]}" . \
    --build-arg SUBMISSION_DIR=/home/submission \
    --build-arg LOGS_DIR=/home/logs \
    --build-arg CODE_DIR=/home/code \
    --build-arg AGENT_DIR=/home/agent
elif [ "$FLAVOR" = "vision" ]; then
  # Vision build will pick up full requirements.txt (may be large)
  docker build --no-cache -t ${TAG} "${BUILD_ARGS[@]}" . \
    --build-arg SUBMISSION_DIR=/home/submission \
    --build-arg LOGS_DIR=/home/logs \
    --build-arg CODE_DIR=/home/code \
    --build-arg AGENT_DIR=/home/agent
else
  echo "Unknown flavor: $FLAVOR"
  exit 1
fi

echo "Built image ${TAG}"
