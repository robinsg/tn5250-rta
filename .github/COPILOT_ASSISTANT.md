# Copilot Assistant — Minimal workflow for this repo

Purpose
- Let Copilot help inside VS Code while keeping all branching and PR control manual.

High-level rules
1. Copilot must NOT create issues, branches, or PRs automatically.
2. You (the human) will create feature branches from `develop`, use Copilot Edit locally, and decide when to merge.
3. Only create a PR into `main` from `develop` when you explicitly want to release.

When an issue is assigned to @copilot
- Assignment indicates you want Copilot to help with code suggestions in-editor only.
- Do NOT expect any GitHub-side automation to create branches or PRs.
- Start work locally by creating a branch (see commands below), then open the files in VS Code and use Copilot Edit to implement changes.

Branch naming
- Use: feature/ISSUE-<number>-short-desc
  Example: feature/ISSUE-123-fix-login

Typical local workflow (copyable)
1) Create feature branch
```bash
git checkout develop
git pull origin develop
git checkout -b feature/ISSUE-123-short-desc