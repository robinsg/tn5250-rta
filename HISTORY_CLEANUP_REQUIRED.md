# Security Cleanup - History Rewrite Required

## Summary

This branch contains important security fixes to remove sensitive credential information from the repository. The following changes have been made:

### Completed Changes
1. ✅ Created `.env.template` and `.env.sh.template` with example/placeholder values
2. ✅ Updated `.gitignore` to exclude `.env` and `.env.sh` from version control
3. ✅ Removed `.env` and `.env.sh` from Git tracking
4. ✅ Added `ENV_SETUP.md` documentation for environment setup

### Still Required: History Cleanup

⚠️ **IMPORTANT**: While `.env` and `.env.sh` are no longer tracked and won't be included in future commits, these files still exist in the Git history in commits before `99dfd2c`.

Specifically, commit `8d87c4d` and earlier commits contain the sensitive `.env` and `.env.sh` files with actual credentials.

## Why History Cleanup is Needed

The current Git history contains sensitive credentials in older commits:
- Commits before `99dfd2c` (specifically `8d87c4d` and earlier) contain `.env` and `.env.sh` files with real credentials
- These credentials include:
  - TN5250_HOST
  - TN5250_USER  
  - TN5250_PASS
- Anyone with access to the repository can view these credentials by checking out old commits

To completely remove these credentials from the repository, the Git history must be rewritten to remove these files from all historical commits.

## How to Complete the Cleanup

### Option 1: Use BFG Repo-Cleaner (Recommended)

BFG Repo-Cleaner is a faster, simpler alternative to `git filter-branch` specifically designed for removing sensitive data.

1. Download BFG: https://rtyley.github.com/bfg-repo-cleaner/

2. Clone a fresh copy of the repository:
   ```bash
   git clone --mirror https://github.com/robinsg/tn5250-rt.git
   cd tn5250-rt.git
   ```

3. Run BFG to remove the sensitive files:
   ```bash
   bfg --delete-files .env
   bfg --delete-files .env.sh
   ```

4. Clean up and force push:
   ```bash
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push --force
   ```

### Option 2: Use git filter-branch

If you can't use BFG, use git filter-branch:

```bash
# Clone the repository
git clone https://github.com/robinsg/tn5250-rt.git
cd tn5250-rt

# Remove the files from all commits
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env .env.sh' \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push to all branches
git push --force --all origin
git push --force --tags origin
```

### Option 3: Use GitHub CLI

A repository administrator with push access needs to run:

```bash
# Pull the latest version of this branch locally
git fetch origin copilot/cleanup-secure-file-sync
git checkout copilot/cleanup-secure-file-sync

# Run one of the cleanup methods above (Option 1 or 2)

# Force push the cleaned history
gh repo clone robinsg/tn5250-rt
cd tn5250-rt
# ... perform cleanup ...
git push --force origin --all
```

### Option 3: Contact GitHub Support

If you don't have access to perform the history rewrite or prefer GitHub to handle the sensitive data removal:

1. Go to https://support.github.com/
2. Request removal of sensitive data from the repository
3. Provide the commit SHA and file paths:
   - Commits before `8568c00` may contain sensitive data in `.env` and `.env.sh`
   - These files contained TN5250 credentials

GitHub's support team can help remove this data using their internal tools.

## Verification Steps

After performing the history cleanup with any of the above methods, verify that sensitive files are removed:

```bash
# Check that old commits don't contain .env files
# This should fail with "path '.env' does not exist":
git show 8d87c4d:.env

# This should succeed (template file exists):
git show HEAD:.env.template

# Check the entire history for any .env files
# This should return no results:
git log --all --full-history --name-only -- .env .env.sh
```

## Alternative: Accept the Risk

If history cleanup cannot be performed, consider the exposed credentials as compromised:

1. Rotate all credentials that were exposed in the `.env` and `.env.sh` files:
   - Change the TN5250_PASS on the IBM i system
   - Consider changing the TN5250_USER if possible
   
2. Going forward, `.env` and `.env.sh` are properly excluded from Git tracking

3. Document that credentials before a certain date should be considered compromised

## Security Note

Until the force push is completed or the alternative branch approach is taken, the sensitive credentials remain in the GitHub repository history and should be considered compromised. Consider rotating any exposed credentials.
