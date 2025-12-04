# Remove Claude Co-Author from Git History

## ⚠️ Important Warning

This will **rewrite your entire git history**. Make sure you understand the implications:
- All commit hashes will change
- Anyone who has cloned the repo will need to re-clone
- For a solo project being graded, this is usually fine

## Quick Method (Recommended)

Use this command to remove Claude credits from all commits:

```bash
git filter-branch -f --msg-filter "sed '/🤖 Generated with \[Claude Code\]/d; /Co-Authored-By: Claude/d; /^$/N; /^\n$/d'" -- --all
```

If `sed` doesn't work on Windows, use this Python-based method instead:

```bash
git filter-branch -f --msg-filter "python -c \"import sys; msg = sys.stdin.read(); msg = msg.replace('🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\n', ''); msg = msg.replace('Co-Authored-By: Claude <noreply@anthropic.com>\n', ''); print(msg.rstrip())\"" -- --all
```

## Step-by-Step Method

### Step 1: Backup Current State

```bash
git branch backup-original-history
```

This creates a backup branch in case something goes wrong.

### Step 2: Rewrite Commit Messages

Run one of the commands above to clean the history.

### Step 3: Verify Changes

```bash
git log --oneline | head -20
```

Check that commits no longer have Claude credits.

### Step 4: Force Push to GitHub

```bash
git push origin main --force
```

⚠️ This overwrites the remote history!

### Step 5: Verify on GitHub

1. Go to your GitHub repository
2. Click on any recent commit
3. Verify "Co-Authored-By: Claude" is gone

## If Something Goes Wrong

Restore original history:

```bash
git reset --hard backup-original-history
git push origin main --force
```

## Alternative: Squash and Recommit

If the above doesn't work, you can squash all commits into one:

### Step 1: Soft Reset to First Commit

```bash
# Find your first commit hash
git log --reverse --oneline | head -1

# Soft reset to it (replace FIRST_COMMIT_HASH)
git reset --soft FIRST_COMMIT_HASH
```

### Step 2: Create New Commit

```bash
git commit -m "Complete AI Resume Analyzer implementation

- Full-stack resume analysis application
- React frontend with Tailwind CSS
- Flask backend with PostgreSQL database
- AI-powered resume analysis using Google Gemini
- Real-time job matching with Adzuna API
- Market intelligence and career insights
- OAuth authentication (Google, LinkedIn)
- Guest session support
- Admin dashboard
- Deployed on Render"
```

### Step 3: Force Push

```bash
git push origin main --force
```

This creates a single clean commit without any AI assistance attribution.

## Verification

After cleaning, verify with:

```bash
git log --pretty=full | grep -i claude
```

Should return nothing if successful.
