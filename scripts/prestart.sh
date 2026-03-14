#!/bin/bash
# Run required pre-start actions like running migrations
alembic upgrade head
