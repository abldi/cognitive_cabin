#!/bin/bash

# Start localtunnel and output to log
lt --port 22 > /tmp/localtunnel.log 2>&1 &

sleep 10

# Check if lt started successfully and captured URL
if ! grep -q 'https://' /tmp/localtunnel.log; then
  echo "LocalTunnel failed to start or URL not captured."
  exit 1
fi

LOCAL_TUNNEL_URL=$(grep -o 'https://.*' /tmp/localtunnel.log | tail -1)
GIST_ID="190de21abf03c3d2503d32269167d6da"
LOCAL_TUNNEL_HOST=$(echo $LOCAL_TUNNEL_URL | cut -d'/' -f 3)
SSH_COMMAND="ssh -o ProxyCommand='nc -X connect -x $LOCAL_TUNNEL_HOST %h %p' cabin@localhost"

# Updating Gist
RESPONSE=$(curl -X PATCH -H "Authorization: token $GIST_PAT" \
  -d "{\"description\": \"Updated LocalTunnel SSH Command\", \"public\": false, \"files\": {\"localtunnel.conf\": {\"content\": \"$SSH_COMMAND\"}}}" "https://api.github.com/gists/$GIST_ID")

echo "GIST response: $RESPONSE"

