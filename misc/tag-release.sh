#!/bin/sh
version_tag="$(pdm show --version)"
git tag -a "$version_tag" -m "$version_tag"
