#!/usr/bin/env bash
set -euo pipefail

# Optional helper for agents. It discovers test projects and runs either all tests
# or a narrow filter supplied as the first argument.

FILTER="${1:-}"
mapfile -t TEST_PROJECTS < <(find . -name '*Tests.csproj' -o -name '*.Tests.csproj' | sort)

if [ ${#TEST_PROJECTS[@]} -eq 0 ]; then
  echo "No test projects found."
  exit 1
fi

for project in "${TEST_PROJECTS[@]}"; do
  echo "Running tests for $project"
  if [ -n "$FILTER" ]; then
    dotnet test "$project" --filter "$FILTER"
  else
    dotnet test "$project"
  fi
done
