#!/usr/bin/env bash
set -euxo pipefail

sudo apt-get install -y python3 python3-pip
sudo apt-get install -y postgresql postgresql-contrib postgresql-client
sudo apt-get install -y python3-psycopg2

echo NOTE: you'll need to add your p99tunnel directory to your PYTHONPATH.
