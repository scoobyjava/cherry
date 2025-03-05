#!/bin/bash
# Simple deployment script to invoke staging_deployment.py.
# ...existing setup code...
python3 /workspaces/cherry/staging/staging_deployment.py "$@"
