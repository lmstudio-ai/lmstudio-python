#!/usr/bin/env bash

# See http://redsymbol.net/articles/unofficial-bash-strict-mode/ for benefit of these options
set -euo pipefail
IFS=$'\n\t'

usage() {
	cat <<EOF
Usage: $(basename "$0") [--branch BRANCH] [--no-pull]

Update the `sdk-schema/lmstudio-js` submodule to the specified branch (default: main)
and regenerate the exported schema by running tox -e sync-sdk-schema -- --regen-schema.

Options:
  --branch BRANCH   Branch to switch the submodule to (default: main)
  --no-pull         Don't run 'git pull' in the submodule
  -h, --help        Show this help message
EOF
}

branch="main"
do_pull=true

while [ "$#" -gt 0 ]; do
	case "$1" in
		--branch)
			shift
			branch=${1:-}
			;;
		--no-pull)
			do_pull=false
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			echo "Unknown arg: $1" >&2
			usage
			exit 2
			;;
	esac
	shift || true
done

# Resolve script directory portably. Prefer readlink -f when available.
resolve_path() {
	local path="$1"
	if command -v readlink >/dev/null 2>&1 && readlink -f / >/dev/null 2>&1; then
		readlink -f "$path"
	else
		# macOS or systems without GNU readlink: fall back to python if available
		if command -v python3 >/dev/null 2>&1; then
			python3 -c "import os,sys; print(os.path.realpath(sys.argv[1]))" -- "$path"
		else
			# Best-effort fallback: canonicalize using pwd
			(cd "$(dirname -- "$path")" && pwd -P)/$(basename -- "$path")
		fi
	fi
}

script_dir="$(resolve_path "${BASH_SOURCE[0]}")"
script_dir="$(cd -- "$(dirname -- "$script_dir")" &> /dev/null && pwd)"

# Ensure required commands are present
for cmd in git tox; do
	if ! command -v "$cmd" >/dev/null 2>&1; then
		echo "Error: required command '$cmd' not found in PATH." >&2
		exit 3
	fi
done

submodule_dir="$script_dir/../sdk-schema/lmstudio-js"
if [ ! -d "$submodule_dir" ]; then
	echo "Error: expected submodule directory '$submodule_dir' not found." >&2
	exit 4
fi

echo "Updating submodule at: $submodule_dir"
pushd "$submodule_dir" >/dev/null || exit 1

echo "Switching to branch: $branch"
git switch "$branch"
if [ "$do_pull" = true ]; then
	echo "Pulling latest changes for $branch"
	git pull --ff-only
else
	echo "Skipping git pull as requested (--no-pull)"
fi

echo "Initializing/updating nested submodules"
git submodule update --init --recursive

popd >/dev/null || exit 1

echo "Regenerating Python SDK schema with tox"
tox -e sync-sdk-schema -- --regen-schema
