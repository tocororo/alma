#!/bin/bash

# Install pipenv if not present
pip install pipenv --user

# Rebuild lock file
pipenv lock --clear --pre

# Ensure proper permissions
chown ${HOST_UID:-1000}:${HOST_GID:-1000} Pipfile.lock