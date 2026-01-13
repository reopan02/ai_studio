#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/scripts/manage.sh" stop
"$SCRIPT_DIR/scripts/manage.sh" db-stop
