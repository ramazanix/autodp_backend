#!/bin/sh

# Apply migrations
sleep 1
alembic upgrade head
exec "$@"
