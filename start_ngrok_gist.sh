#!/bin/bash

ngrok tcp 22 > /dev/null &

sleep 10

NGROK_URL=$(curl --silent http://127.0.0.1:4040/api/tunnels | jq -r '.tunnels[0].public_url')
GIST_ID="314f1376a9fd813b485fa1d3219bf1aa"

NGROK_HOST=$(echo $NGROK_URL | cut -d':' -f 2 | tr -d '/')
NGROK_PORT=$(echo $NGROK_URL | cut -d':' -f 3)

SSH_COMMAND="ssh -p $NGROK_PORT cabin@$NGROK_HOST"

RESPONSE=$(curl -X PATCH -H "Authorization: token $GIST_PAT" \
  -d "{\"description\": \"Description of Gist\", \"public\": false, \"files\": {\"ngrok.conf\": {\"content\": \"$SSH_COMMAND\"}}}" "https://api.github.com/gists/$GIST_ID")

echo "GIST response: $RESPONSE"
