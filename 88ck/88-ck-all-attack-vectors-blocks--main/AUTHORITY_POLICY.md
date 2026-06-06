# Change Authority Policy

This repository is owner-controlled.

## Objective

No code change should reach `main` without explicit owner approval.

## Repository Controls

1. `CODEOWNERS` at repository root assigns all files to `@rock4007`.
2. Pull requests are mandatory for `main`.
3. Code owner review is mandatory for `main`.
4. Status checks are mandatory before merge.
5. Force pushes and branch deletion are disabled on `main`.

## Required GitHub Settings (one-time)

In GitHub: Settings -> Branches -> Add branch protection rule (or Ruleset) for `main`.

Enable:

1. Require a pull request before merging.
2. Require approvals (recommended: at least 1).
3. Require review from Code Owners.
4. Require status checks to pass before merging.
5. Require branches to be up to date before merging.
6. Restrict who can push to matching branches (set to `@rock4007` only, if desired).
7. Do not allow force pushes.
8. Do not allow deletions.

## Optional Hardening

1. Require signed commits.
2. Enable vigilant mode for verified signatures.
3. Require linear history.
4. Enforce secret scanning and push protection.

## Human-Readable Code Standard

For maintainability, every change should include:

1. Clear naming (no ambiguous abbreviations unless standard in the domain).
2. Small functions focused on one responsibility.
3. Comments only where logic is non-obvious.
4. Tests or validation notes for behavior changes.
5. Update docs when architecture or behavior changes.
