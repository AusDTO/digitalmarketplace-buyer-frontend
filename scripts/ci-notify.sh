#!/bin/bash

curl -g -X POST --data-urlencode 'payload={"channel": "#marketplace", "username": "releasebot", "text": "Some code went live! '"$CIRCLE_REPOSITORY_URL"'/releases/tag/'"$CIRCLE_TAG"'", "icon_emoji": ":lightning:"}' "$SLACK_WEBHOOK_URL"