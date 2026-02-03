#!/usr/bin/env bash
# WARNING: This script rewrites git history. BACKUP your repo and confirm before running.
# Requires: git-filter-repo (https://github.com/newren/git-filter-repo)

set -euo pipefail

echo "This script will rewrite git history to remove sensitive paths/strings."
echo "Make a full backup and push to a temporary remote before running."

echo "Example usage (dry-run):\n  git clone --mirror <repo_url> repo-mirror.git\n  cd repo-mirror.git\n  # Edit the --invert-paths and --paths to match secrets/files to remove\n  git filter-repo --path blacklist_file.txt --invert-paths --force\n
# Replace the following with patterns/files to remove
# Example: git filter-repo --path secrets.json --path big-data/ --replace-text replacements.txt --force

cat <<'EOF'
# SAMPLE git-filter-repo commands (DO NOT RUN UNTIL YOU'RE READY)
# Remove specific files permanently:
# git filter-repo --path secrets.json --path configs/old_creds/ --force

# Replace matching text occurrences (use replacements.txt where each line has format: 'literal==>REPLACEMENT'):
# git filter-repo --replace-text replacements.txt --force

# After rewrite, verify, then force-push to the protected branch remote:
# git push --force --all origin
# git push --force --tags origin
EOF

echo "Review the sample commands above. Edit this script to supply your files/patterns and run with extreme caution." 
