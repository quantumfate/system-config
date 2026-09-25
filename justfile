# Task runner. Run `just` to list recipes.
# Recipes are generated from the detected toolchain; edit freely.

default:
    @just --list

# Reformat the tree in place
fmt:
    stylua .
    ruff format .
    shfmt -w -i 4 .
    prettier --write '**/*.md'

# Verify formatting without writing
fmt-check:
    stylua --check .
    ruff format --check .
    shfmt -d -i 4 .
    prettier --check '**/*.md'

# Static analysis
lint:
    luacheck .
    ruff check .
    git ls-files '*.sh' '*.bash' | xargs -r shellcheck
    yamllint .
    ansible-lint

test:
    pytest

# CI/pre-commit gate: formatting + tests (lint is advisory)
check: fmt-check test
	@../hypr/bin/,privacy-check


