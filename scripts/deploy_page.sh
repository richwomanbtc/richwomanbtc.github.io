#!/usr/bin/env bash

set -euo pipefail

if [[ -z "${RUNNER_TEMP:-}" ]]; then
  echo "RUNNER_TEMP is required" >&2
  exit 2
fi

site_snapshot="$(mktemp -d "${RUNNER_TEMP}/site-snapshot.XXXXXX")"
public_paths=(
  ".nojekyll"
  "index.html"
  "assets"
  "_auto_contents"
)
git archive --format=tar HEAD "${public_paths[@]}" | tar -xf - -C "${site_snapshot}"

required_files=(
  "index.html"
  ".nojekyll"
  "assets/css/style.css"
  "assets/js/main.js"
  "_auto_contents/metadata.yml"
  "_auto_contents/profile.html"
  "_auto_contents/research.html"
)

for required_file in "${required_files[@]}"; do
  if [[ ! -f "${site_snapshot}/${required_file}" ]]; then
    echo "Refusing to deploy: ${required_file} is missing from HEAD" >&2
    exit 1
  fi
done

git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git config user.name "github-actions[bot]"
git fetch origin page
git switch --force-create page origin/page
rsync --archive --delete --exclude=.git "${site_snapshot}/" ./

git add -u
while IFS= read -r -d '' path; do
  git add -- "${path}"
done < <(git ls-files --others --exclude-standard -z)

if git diff --cached --quiet; then
  echo "page branch is already current"
else
  git commit -m "Deploy updated researchmap site"
  git push origin page
fi
