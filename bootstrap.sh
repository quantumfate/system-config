#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  -h, --help      Show this help
  -v              Verbose mode
  -r "role [role ...]"  Only run the given roles (tags); space-separated, quoted
  -e "VAR=VALUE"  Pass an extra ansible variable (e.g. reset_confirm=<host>); repeatable
EOF
}

verbose=false
roles=()
extra_vars=()

# Parse options
while getopts "hvr:e:" opt; do
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
    e)
        extra_vars+=(-e "$OPTARG")
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

# Every host converges itself over a local connection, so a run is always
# limited to this machine's own inventory entry (and its host_vars).
host="$(hostname)"
if ! grep -q "^        ${host}:$" inventory/hosts.yml; then
    echo "No inventory entry for '${host}'. Add it to inventory/hosts.yml and create host_vars/${host}.yml." >&2
    exit 1
fi
limit=(--limit "$host")

if [[ "$verbose" == "true" && ${#roles[@]} -eq 0 ]]; then
    export ANSIBLE_DEBUG=1
    exec ansible-playbook site.yml "${limit[@]}" --ask-become-pass "${extra_vars[@]}" "$@" -vvvv
elif [[ ${#roles[@]} -gt 0 && "$verbose" == "false" ]]; then
    exec ansible-playbook site.yml "${limit[@]}" --ask-become-pass "${extra_vars[@]}" -t "$(
        IFS=,
        echo "${roles[*]}"
    )" "$@"
elif [[ ${#roles[@]} -gt 0 && "$verbose" == "true" ]]; then
    export ANSIBLE_DEBUG=1
    exec ansible-playbook site.yml "${limit[@]}" --ask-become-pass "${extra_vars[@]}" -vvvv -t "$(
        IFS=,
        echo "${roles[*]}"
    )" "$@"
else
    exec ansible-playbook site.yml "${limit[@]}" --ask-become-pass "${extra_vars[@]}" "$@"
fi
