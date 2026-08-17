#!/usr/bin/env bash
# Regenerate v12..v18 from v11.html + themes/theme{NN}.css.
#
# v11.html is the ONLY file where content is edited. Every other style page is
# v11 + its theme block, so run this after any change to v11.
#
#   usage:  bash tools/regen.sh
set -euo pipefail
cd "$(dirname "$0")/.."

LIGHT=" 12 13 16 17 "     # themes whose background is light → need the dark-ink logo

norm() { tr -d '\r' < "$1"; }
norm v11.html > .v11.norm

for v in 12 13 14 15 16 17 18; do
  [[ -f "themes/theme$v.css" ]] || { echo "missing themes/theme$v.css" >&2; exit 1; }

  # 1. point self-referencing URLs (og:url) at this version
  sed "s|v11\.html|v$v.html|g" .v11.norm > ".v$v.tmp"

  # 2. inject the theme block immediately before </head>
  awk 'FNR==NR{t=t $0 ORS;next} /<\/head>/{printf "%s",t} {print}' \
      "themes/theme$v.css" ".v$v.tmp" > "v$v.html"

  # 3. light themes need the light-background logo variant
  if [[ "$LIGHT" == *" $v "* ]]; then
    sed -i 's|img/opt/logo-dark\.png|img/opt/logo-light.png|g' "v$v.html"
  fi

  rm -f ".v$v.tmp"
  printf 'v%s.html  %s lines  %s\n' "$v" "$(wc -l < "v$v.html")" \
    "$(grep -o 'logo-[a-z]*\.png' "v$v.html" | head -1)"
done

rm -f .v11.norm
echo
echo "regenerated 7 pages from v11.html"
