#!/bin/bash

# See http://redsymbol.net/articles/unofficial-bash-strict-mode/ for benefit of these options
set -euo pipefail
IFS=$'\n\t'

# Note: `readlink -f` (long available in GNU coreutils) is available on macOS 12.3 and later
script_dir="$(cd -- "$(dirname -- "$(readlink -f "${BASH_SOURCE[0]}")")" &> /dev/null && pwd)"

# Update submodule to tip of the lmstudio-js main branch and regenerate the exported schema
# (to incorporate Python data model template changes, just run `tox -e sync-sdk-schema`)

pushd "$script_dir/../sdk-schema/lmstudio-js" || exit 1
git switch main
git pull
git submodule update --init --recursive
popd || exit 1
tox -e sync-sdk-schema -- --regen-schema
