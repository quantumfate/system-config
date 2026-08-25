#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  -h, --help      Show this help
  -v              Verbose mode
EOF
}

verbose=false

# Parse options
while getopts ":h:v" opt; do
  case "${opt}" in
  h)
    usage
    ;;
  v)
    verbose=true
    ;;
  [?])
    echo "Invalid option: -${OPTARG}" >&2
    exit 1
    ;;
  :)
    echo "Option -${OPTARG} requires an argument" >&2
    exit 1
    ;;
  esac
done
shift $((OPTIND - 1))

cd "$(dirname "$0")"

command -v ansible-playbook >/dev/null || sudo pacman -S --needed --noconfirm ansible

ansible-galaxy collection install -r requirements.yml

if [[ "$verbose" == "true" ]]; then
  export ANSIBLE_DEBUG=1
  exec ansible-playbook site.yml --ask-become-pass "$@" -vvvv
else
  exec ansible-playbook site.yml --ask-become-pass "$@"
fi
