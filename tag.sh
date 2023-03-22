#! /usr/bin/env bash

set -euo pipefail

VERSION="v$(grep '^version =' pyproject.toml | cut -d '"' -f 2)"
echo $VERSION
git tag -a -m "New version: $VERSION" "$VERSION"
