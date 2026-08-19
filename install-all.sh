#!/usr/bin/env bash
# Install the WHOLE Kojiki Decision System package in one go:
#   kojiki-ontology + all 20 line departments + 21 (org builder) + 22 (installer).
# Each repo is cloned from github.com/robfuj. Idempotent (skips if already present).
set -e
OWNER="robfuj"
OUT="${1:-./kojiki-decision-system}"
mkdir -p "$OUT"
cd "$OUT"
for repo in kojiki-ontology kojiki-executive-strategy kojiki-finance-department kojiki-marketing-department kojiki-sales-department kojiki-business-development kojiki-customer-success kojiki-product-department kojiki-engineering-department kojiki-operations-department kojiki-supply-chain-procurement-department kojiki-data-analytics kojiki-ai-intelligence-department kojiki-IT-department kojiki-security-department kojiki-legal-department kojiki-risk-compliance-department kojiki-hr-department kojiki-corporate-development-department kojiki-communications-public-affairs-department kojiki-executive-office-department kojiki-executive-org-builder-department kojiki-decision-system-installer; do
  if [ -d "$repo" ]; then echo "skip (exists): $repo"; else
    echo "clone: $repo"
    git clone --depth 1 "https://github.com/$OWNER/$repo.git" "$repo"
  fi
done
echo ""
echo "Whole package installed into $OUT"
echo "Next: open a department (e.g. 03-marketing) and follow its AGENT.md Orientation Protocol."
