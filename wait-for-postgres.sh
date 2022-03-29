#!/bin/sh
set -e
shift
cmd="$@"
until mysql -u orderus -h mysqldb  -p2Lj2UkqXymn6 -e "show databases;"; do
  >&2 echo "MYSQL is unavailable - sleeping"
  sleep 2
done
>&2 echo "MYSQL is up - executing command"
exec ${cmd}