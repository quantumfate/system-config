#!/usr/bin/env bash
set -euo pipefail

role_paths=$(printf '%s:' "$HOME"/Projects/codeberg/quantumfate/{quickshell,hypr,nvim}/ansible/roles)
export ANSIBLE_ROLES_PATH="./roles:$role_paths"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  -h, --help      Show this help
  -v              Verbose mode
  -r "role [role ...]"  Only run the given roles (tags); space-separated, quoted
EOF
}

verbose=false
roles=()

# Parse options
while getopts "hvr:" opt; do
    case "${opt}" in
    h)
        usage
        exit 0
        ;;
    v)
        verbose=true
        ;;
    r)
        read -r -a roles <<<"$OPTARG"
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

if [[ "$verbose" == "true" && ${#roles[@]} -eq 0 ]]; then
    export ANSIBLE_DEBUG=1
    exec ansible-playbook site.yml --ask-become-pass "$@" -vvvv
elif [[ ${#roles[@]} -gt 0 && "$verbose" == "false" ]]; then
    exec ansible-playbook site.yml --ask-become-pass -t "${roles[@]}" "$@"
elif [[ ${#roles[@]} -gt 0 && "$verbose" == "true" ]]; then
    export ANSIBLE_DEBUG=1
    exec ansible-playbook site.yml --ask-become-pass -vvvv -t "${roles[@]}" "$@"
else
    exec ansible-playbook site.yml --ask-become-pass "$@"
fi
