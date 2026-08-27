#!/usr/bin/env bash
set -euo pipefail

# Roles come from the canonical checkouts in ~/Projects, mirroring
# group_vars/all/externals.yml. Serving the hypr role from ~/.config/hypr would
# let the deploy symlink that dir over the running role's own path and crash
# ansible's role cache.
export ANSIBLE_ROLES_PATH="./roles:$HOME/Projects/codeberg/quantumfate/quickshell/ansible/roles:$HOME/Projects/codeberg/quantumfate/hypr/ansible/roles:$HOME/Projects/codeberg/quantumfate/nvim/ansible/roles"

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
