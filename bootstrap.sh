#!/usr/bin/env bash
# Full convergence from a clean checkout. Extra args pass through to ansible.
set -euo pipefail

cd "$(dirname "$0")"

command -v ansible-playbook >/dev/null || sudo pacman -S --needed --noconfirm ansible

ansible-galaxy collection install -r requirements.yml
exec ansible-playbook site.yml --ask-become-pass "$@"
