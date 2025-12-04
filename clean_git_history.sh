#!/bin/bash
# Script to remove Claude co-author credits from git history
# WARNING: This rewrites git history - make a backup first!

echo "==========================================================="
echo "GIT HISTORY CLEANUP - REMOVE CLAUDE CO-AUTHOR"
echo "==========================================================="
echo ""
echo "This will remove the following from all commit messages:"
echo "  - 🤖 Generated with [Claude Code]"
echo "  - Co-Authored-By: Claude <noreply@anthropic.com>"
echo "  - Empty lines from cleanup"
echo ""
echo "⚠️  WARNING: This rewrites git history!"
echo "⚠️  Make sure you have a backup or can re-clone if needed."
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Creating backup branch..."
git branch backup-before-cleanup

echo "Rewriting commit history..."
git filter-branch -f --msg-filter '
    sed "/🤖 Generated with \[Claude Code\]/d" |
    sed "/Co-Authored-By: Claude/d" |
    sed "/^$/N;/^\n$/d"
' -- --all

echo ""
echo "✅ History rewritten locally"
echo ""
echo "To push to GitHub (this will FORCE PUSH):"
echo "  git push origin main --force"
echo ""
echo "If something goes wrong, restore with:"
echo "  git reset --hard backup-before-cleanup"
echo ""
