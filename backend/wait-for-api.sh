#!/bin/sh
set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z "$host" "$port"; do
  >&2 echo "L'API n'est pas encore prête - en attente..."
  sleep 1
done

>&2 echo "L'API est prête !"
exec $cmd
