#!/usr/bin/env bash
set -euxo pipefail

sudo apt-get install -y python3 python3-pip
sudo apt-get install -y postgresql postgresql-contrib postgresql-client
sudo apt-get install -y python3-psycopg2
