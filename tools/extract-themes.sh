#!/usr/bin/env bash
# Extract the <style id="theme-*"> block from v12..v18 into themes/*.css,
# then verify that each page is EXACTLY v11 + that block (modulo the known
# og:url and logo substitutions). Restores the gap noted in HANDOFF.md §3.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p themes

declare -A NAME=( [12]=klaf [13]=modern [14]=yayin [15]=shas [16]=midbar [17]=shacharit [18]=chatzot )

norm() { tr -d '\r' < "$1"; }

echo "=== extracting ==="
for v in 12 13 14 15 16 17 18; do
  norm "v$v.html" | awk '/<style id="theme-/{f=1} f{print} /<\/style>/{if(f){exit}}' > "themes/theme$v.css"
  printf 'themes/theme%s.css  %s lines  (%s)\n' "$v" "$(wc -l < "themes/theme$v.css")" "${NAME[$v]}"
done

echo
echo "=== verifying each page == v11 + theme block ==="
norm v11.html > /tmp/_v11.norm
for v in 12 13 14 15 16 17 18; do
  # strip the theme block back out
  norm "v$v.html" | awk '/<style id="theme-/{f=1} !f{print} /<\/style>/{if(f){f=0}}' > "/tmp/_v$v.stripped"
  # undo the known per-version substitutions so it should equal v11
  sed -e "s|v$v\.html|v11.html|g" -e 's|img/logo-light\.png|img/logo-dark.png|g' \
      "/tmp/_v$v.stripped" > "/tmp/_v$v.cmp"
  if diff -q /tmp/_v11.norm "/tmp/_v$v.cmp" >/dev/null; then
    printf 'v%s: IDENTICAL to v11 base ✓\n' "$v"
  else
    printf 'v%s: DIFFERS — residual diff:\n' "$v"
    diff /tmp/_v11.norm "/tmp/_v$v.cmp" | head -20
  fi
done
