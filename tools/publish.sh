#!/usr/bin/env bash
# Bouwt de site opnieuw op na een nieuw of gewijzigd artikel. Draai vanuit de repo-root: bash tools/publish.sh
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/check_articles.py
python3 tools/articles.py
python3 tools/stadspaginas.py
python3 tools/funnel.py
python3 tools/seo.py
python3 tools/booking.py
python3 tools/order.py
python3 tools/analytics.py G-6QJJ46JVWW
python3 tools/battery.py
python3 tools/cookie.py
python3 tools/meta_pixel.py
python3 tools/fonts.py
python3 tools/attributie.py
if grep -rli "voltier\|zonne-installaties noord" --include=*.html . >/dev/null; then echo "Verboden naam gevonden in HTML"; exit 1; fi
echo "Klaar. Controleer met: git status"
