# Fork-Based Milestone Experiment Workflow

## Purpose

Use this workflow when you fork a large shared repository and want to experiment freely, while keeping your work organized into clear milestones before proposing changes back to the original repository.

This workflow is useful when:

- The original repository is managed by multiple people.
- Your work starts from a historical tag, branch, or commit, not necessarily from the latest upstream `main`.
- You want freedom to experiment in your fork.
- You want stable checkpoints such as database cleanup, installation setup, and refactoring.
- You want to avoid one messy development branch that mixes unrelated work.
- You eventually want to prepare clean pull requests back to the original repository.

## Core idea

Do not put everything into one continuously growing `dev` branch.

Instead, use milestone branches as stable checkpoints:

```text
base/<start-point>
    ↓
milestone/01-database-cleanup
    ↓
milestone/02-pixi-installation
    ↓
milestone/03-refactoring
```

Each milestone has its own experiments and features around it. When a milestone becomes stable, you can tag it and use it as the base for the next milestone.

## Recommended branch types

| Branch type | Pattern | Purpose | Example |
|---|---|---|---|
| Official mirror | `main` | Optional mirror of upstream `main`; do not use as your personal experimental line | `main` |
| Frozen base | `base/<start-point>` | Exact historical point where your work starts | `base/v0.1.0-alpha` |
| Milestone | `milestone/<number>-<topic>` | Stable checkpoint for a major phase of work | `milestone/01-database-cleanup` |
| Experiment | `exp/m<number>-<topic>` | Messy trial branch for testing ideas | `exp/m01-db-cleaning-strategy` |
| Feature | `feat/m<number>-<topic>` | Cleaner implementation branch for work you may keep | `feat/m02-add-pixi-environment` |
| Integration | `integration/<purpose>` | Optional combined branch when milestones are developed in parallel | `integration/prototype` |
| Pull request candidate | `pr/<number>-<topic>` | Clean branch prepared for review and PR | `pr/01-database-cleanup` |
| Archive | `archive/<topic>` | Preserved but inactive branch | `archive/old-cli-redesign` |

## Recommended naming convention

Use numbered milestones so the intended sequence is obvious:

```text
milestone/01-database-cleanup
milestone/02-pixi-installation
milestone/03-refactoring
milestone/04-docs-and-examples
```

Use matching prefixes for experiments and features:

```text
exp/m01-db-schema-test
exp/m01-db-cleaning-strategy
exp/m02-pixi-lockfile-test
exp/m03-api-layout-test

feat/m01-normalize-database
feat/m02-add-pixi-environment
feat/m03-simplify-config-loader
```

Use PR branches only when you are ready to share a clean version:

```text
pr/01-database-cleanup
pr/02-pixi-installation
pr/03-refactoring
```

## Step 1. Fork the original repository

On GitHub:

1. Open the original repository.
2. Click **Fork**.
3. Create the fork under your own GitHub account.

Example:

```text
Original repository: github.com/original-owner/project
Your fork:           github.com/your-username/project
```

## Step 2. Clone your fork locally

```bash
git clone https://github.com/your-username/project.git
cd project
```

Check remotes:

```bash
git remote -v
```

At this point, your fork should appear as `origin`.

## Step 3. Add the original repository as upstream

```bash
git remote add upstream https://github.com/original-owner/project.git
```

Verify:

```bash
git remote -v
```

Expected structure:

```text
origin    https://github.com/your-username/project.git
upstream  https://github.com/original-owner/project.git
```

## Step 4. Fetch branches and tags from upstream

```bash
git fetch upstream --tags
```

This gives you access to upstream branches, tags, and historical commits.

## Step 5. Choose the correct starting point

Your work does not have to start from the latest upstream `main`.

Choose one of these:

| Starting point | When to use | Example |
|---|---|---|
| Tag or release | Your experiments start from a known release | `v0.1.0-alpha` |
| Commit SHA | Your experiments start from a specific historical commit | `a1b2c3d` |
| Upstream branch | Your experiments start from an existing branch | `upstream/develop` |

### Option A. Start from a tag or release

```bash
git checkout -b base/v0.1.0-alpha v0.1.0-alpha
git push -u origin base/v0.1.0-alpha
```

### Option B. Start from a specific commit

```bash
git checkout -b base/pre-api-refactor <commit-sha>
git push -u origin base/pre-api-refactor
```

### Option C. Start from an upstream branch

```bash
git checkout -b base/develop-snapshot upstream/develop
git push -u origin base/develop-snapshot
```

Treat the `base/*` branch as frozen. Do not edit it.

## Step 6. Create milestone 1

Example milestone:

```text
Clean up the database and make it work smoothly.
```

Create the branch from your frozen base:

```bash
git checkout -b milestone/01-database-cleanup base/v0.1.0-alpha
git push -u origin milestone/01-database-cleanup
```

This branch should contain only stable work related to milestone 1.

## Step 7. Create experiment branches for milestone 1

Create messy trial branches from the milestone branch:

```bash
git checkout milestone/01-database-cleanup
git checkout -b exp/m01-db-cleaning-strategy
```

Work freely:

```bash
git add .
git commit -m "Test database cleanup strategy"
git push -u origin exp/m01-db-cleaning-strategy
```

You can create multiple experiments for the same milestone:

```bash
git checkout milestone/01-database-cleanup
git checkout -b exp/m01-db-schema-test

# or

git checkout milestone/01-database-cleanup
git checkout -b exp/m01-db-validation-checks
```

## Step 8. Promote useful work into a cleaner feature branch

When an experiment becomes useful, create a cleaner feature branch from the milestone:

```bash
git checkout milestone/01-database-cleanup
git checkout -b feat/m01-normalize-database
```

Bring in selected changes from the experiment.

### Option A. Cherry-pick selected commits

Use this when the experiment has useful commits but also messy history:

```bash
git cherry-pick <commit-sha>
```

### Option B. Merge the experiment branch

Use this only when the experiment branch is already clean enough:

```bash
git merge exp/m01-db-cleaning-strategy
```

### Option C. Manually copy the final version of selected files

Use this when the experiment history is too messy, but the final file content is useful.

Then commit and push:

```bash
git add .
git commit -m "Normalize database structure"
git push -u origin feat/m01-normalize-database
```

## Step 9. Merge clean feature work into milestone 1

When the feature branch is acceptable, merge it into the milestone branch:

```bash
git checkout milestone/01-database-cleanup
git merge feat/m01-normalize-database
git push origin milestone/01-database-cleanup
```

Repeat this for other accepted feature branches belonging to milestone 1.

## Step 10. Tag milestone 1 when stable

Once milestone 1 is stable, create a tag:

```bash
git checkout milestone/01-database-cleanup
git tag m01-database-cleanup
git push origin m01-database-cleanup
```

A tag is a permanent checkpoint. Unlike a branch, it should not move.

## Step 11. Create milestone 2

Example milestone:

```text
Set up a smoother installation process with Pixi.
```

If milestone 2 depends on milestone 1, create it from milestone 1:

```bash
git checkout -b milestone/02-pixi-installation milestone/01-database-cleanup
git push -u origin milestone/02-pixi-installation
```

Then create experiments and features around milestone 2:

```bash
git checkout milestone/02-pixi-installation
git checkout -b exp/m02-pixi-lockfile-test
```

When stable, tag it:

```bash
git checkout milestone/02-pixi-installation
git tag m02-pixi-installation
git push origin m02-pixi-installation
```

## Step 12. Create milestone 3

Example milestone:

```text
Refactor the codebase after the database and installation workflow are stable.
```

If milestone 3 depends on milestone 2, create it from milestone 2:

```bash
git checkout -b milestone/03-refactoring milestone/02-pixi-installation
git push -u origin milestone/03-refactoring
```

Then use the same pattern:

```bash
git checkout milestone/03-refactoring
git checkout -b exp/m03-api-layout-test

git checkout milestone/03-refactoring
git checkout -b feat/m03-simplify-config-loader
```

## Stacked milestones versus parallel milestones

Use stacked milestones when later work depends on earlier work:

```text
base/v0.1.0-alpha
    ↓
milestone/01-database-cleanup
    ↓
milestone/02-pixi-installation
    ↓
milestone/03-refactoring
```

Use parallel milestones when workstreams are independent:

```text
base/v0.1.0-alpha
    ├── milestone/01-database-cleanup
    ├── milestone/02-pixi-installation
    └── milestone/03-refactoring
```

If you develop milestones in parallel but want a combined tested version, create an integration branch:

```bash
git checkout -b integration/prototype base/v0.1.0-alpha

git merge milestone/01-database-cleanup
git merge milestone/02-pixi-installation
git merge milestone/03-refactoring

git push -u origin integration/prototype
```

## How to decide between stacked and parallel milestones

| Situation | Recommended structure |
|---|---|
| Milestone 2 requires milestone 1 | Stacked milestones |
| Milestone 3 requires milestones 1 and 2 | Stacked milestones |
| Pixi installation is independent of database cleanup | Parallel milestones |
| You want a tested combined prototype | Add `integration/prototype` |
| You want easy review by maintainers | One PR per milestone |

For your described case, stacked milestones are probably best:

```text
base/v0.1.0-alpha
    ↓
milestone/01-database-cleanup
    ↓
milestone/02-pixi-installation
    ↓
milestone/03-refactoring
```

## Preparing pull requests back to upstream

The cleanest approach is usually one pull request per milestone.

```text
PR 1: pr/01-database-cleanup
PR 2: pr/02-pixi-installation
PR 3: pr/03-refactoring
```

### Create PR branch for milestone 1

```bash
git checkout milestone/01-database-cleanup
git checkout -b pr/01-database-cleanup
git push -u origin pr/01-database-cleanup
```

Open a pull request from:

```text
your-username:pr/01-database-cleanup
```

to the appropriate upstream branch.

### Create PR branch for milestone 2

Only do this after PR 1 is accepted or after maintainers agree to review stacked PRs:

```bash
git checkout milestone/02-pixi-installation
git checkout -b pr/02-pixi-installation
git push -u origin pr/02-pixi-installation
```

### Create PR branch for milestone 3

```bash
git checkout milestone/03-refactoring
git checkout -b pr/03-refactoring
git push -u origin pr/03-refactoring
```

## Choosing the PR target branch

Do not automatically target upstream `main` if your work started from an older midpoint.

| Your base | Likely PR target |
|---|---|
| `v0.1.0-alpha` | Maintenance branch based on that release |
| `upstream/develop` | `upstream/develop` |
| Historical commit | Branch created by maintainers from that commit |
| Latest upstream main | `upstream/main` |

If no matching upstream branch exists, coordinate with maintainers. They may need to create a branch from the same historical base.

## What not to do

Avoid merging latest upstream `main` into your milestone branches unless you intentionally want to move your work to the latest repository state.

Avoid this if your work should remain based on a historical midpoint:

```bash
git checkout milestone/01-database-cleanup
git merge upstream/main
```

Also avoid using your fork's `main` as your personal milestone branch. Keep `main` either untouched or as a clean mirror of the official upstream `main`.

## Typical full workflow

```bash
# Clone your fork
git clone https://github.com/your-username/project.git
cd project

# Add original repository
git remote add upstream https://github.com/original-owner/project.git

# Fetch upstream branches and tags
git fetch upstream --tags

# Create frozen base from tag
git checkout -b base/v0.1.0-alpha v0.1.0-alpha
git push -u origin base/v0.1.0-alpha

# Milestone 1: database cleanup
git checkout -b milestone/01-database-cleanup base/v0.1.0-alpha
git push -u origin milestone/01-database-cleanup

# Experiment for milestone 1
git checkout -b exp/m01-db-cleaning-strategy milestone/01-database-cleanup
# Work, commit, push
git add .
git commit -m "Test database cleanup strategy"
git push -u origin exp/m01-db-cleaning-strategy

# Clean feature branch for milestone 1
git checkout -b feat/m01-normalize-database milestone/01-database-cleanup
git cherry-pick <commit-sha>
git push -u origin feat/m01-normalize-database

# Merge clean feature into milestone 1
git checkout milestone/01-database-cleanup
git merge feat/m01-normalize-database
git push origin milestone/01-database-cleanup

# Tag milestone 1
git tag m01-database-cleanup
git push origin m01-database-cleanup

# Milestone 2: Pixi installation
git checkout -b milestone/02-pixi-installation milestone/01-database-cleanup
git push -u origin milestone/02-pixi-installation

# Milestone 3: refactoring
git checkout -b milestone/03-refactoring milestone/02-pixi-installation
git push -u origin milestone/03-refactoring

# PR branch for milestone 1
git checkout milestone/01-database-cleanup
git checkout -b pr/01-database-cleanup
git push -u origin pr/01-database-cleanup
```

## Summary

| Need | Recommended branch |
|---|---|
| Preserve exact historical starting point | `base/<start-point>` |
| Keep stable checkpoint for a phase | `milestone/<number>-<topic>` |
| Try messy ideas freely | `exp/m<number>-<topic>` |
| Prepare cleaner implementation | `feat/m<number>-<topic>` |
| Combine independent milestones | `integration/<purpose>` |
| Prepare reviewable contribution | `pr/<number>-<topic>` |
| Preserve old work | `archive/<topic>` |

## Recommended default for your case

Use this structure:

```text
base/v0.1.0-alpha
milestone/01-database-cleanup
milestone/02-pixi-installation
milestone/03-refactoring
exp/m01-*
exp/m02-*
exp/m03-*
feat/m01-*
feat/m02-*
feat/m03-*
pr/01-database-cleanup
pr/02-pixi-installation
pr/03-refactoring
```

Treat milestone branches as stable checkpoints, not as messy working branches. Use experiment and feature branches for the messy work. Use PR branches only when you are ready to share with the original repository.
