#!/usr/bin/env sh
# Deploy the Worker for an environment.
#
# Requires Cloudflare auth (interactive `wrangler login`, or CLOUDFLARE_API_TOKEN
# + CLOUDFLARE_ACCOUNT_ID in the environment). This script only deploys the Worker;
# it does NOT run migrations. Follow the deployment order in docs/deployment.md.
#
# Usage: scripts/deploy.sh <staging|production>
set -eu

ENV="${1:?usage: deploy.sh <staging|production>}"
case "$ENV" in
  staging | production) ;;
  *)
    echo "environment must be 'staging' or 'production'"
    exit 1
    ;;
esac

exec uv run pywrangler deploy --env "$ENV"
