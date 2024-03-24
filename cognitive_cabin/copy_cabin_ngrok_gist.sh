#!/bin/bash

# Define variables
GIST_ID="314f1376a9fd813b485fa1d3219bf1aa"
GIST_FILENAME="ngrok.conf"

GIST_CONTENT=$(curl -H "Authorization: token $GIST_PAT" "https://api.github.com/gists/$GIST_ID" | jq -r ".files.\"$GIST_FILENAME\".content")

echo "Gist Content:"
echo "$GIST_CONTENT"
echo "$GIST_CONTENT" | xclip -selection clipboard
