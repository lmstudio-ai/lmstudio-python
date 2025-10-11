#!/bin/sh
set -eu

usage() {
	echo "Usage: $(basename "$0") [--push]"
	echo
	echo "Create an annotated git tag from the current pdm project version."
	echo "  --push   Push the created tag to 'origin' after creating it."
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
	usage
	exit 0
fi

PUSH=false
if [ "${1:-}" = "--push" ]; then
	PUSH=true
fi

if ! command -v pdm >/dev/null 2>&1; then
	echo "Error: 'pdm' command not found. Please install PDM or run this from an environment with pdm available." >&2
	exit 2
fi

version_tag="$(pdm show --version)"
if [ -z "$version_tag" ]; then
	echo "Error: pdm did not return a version." >&2
	exit 3
fi

# Ensure tag doesn't already exist
if git rev-parse --verify "refs/tags/$version_tag" >/dev/null 2>&1; then
	echo "Error: tag '$version_tag' already exists." >&2
	exit 4
fi

# Ensure working tree is clean to avoid tagging uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
	echo "Error: working directory has uncommitted changes. Commit or stash them before tagging." >&2
	git status --short
	exit 5
fi

echo "Creating annotated tag: $version_tag"
git tag -a "$version_tag" -m "$version_tag"
echo "Tag '$version_tag' created locally."

if [ "$PUSH" = true ]; then
	echo "Pushing tag '$version_tag' to origin..."
	git push origin "refs/tags/$version_tag"
	echo "Push complete."
else
	echo "Run 'git push origin refs/tags/$version_tag' to push the tag to the remote."
fi
