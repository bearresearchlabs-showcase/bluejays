---
name: product-management-roadmap
description: Create and update epics, features, user stories, and todos for product development. Use when planning work, breaking down epics, writing user stories, or updating docs/ROADMAP.md.
---

# Product Management and Roadmap

## Purpose

Create and update epics, features, user stories, and todos. Align implementation with [docs/ROADMAP.md](docs/ROADMAP.md) and [.cursor/rules/update-roadmap.mdc](../rules/update-roadmap.mdc).

## Actions

### Create/Update Epics

- Add to ROADMAP as `## Epic N: Title`
- Include scope, features, and user stories
- Link to plan files when applicable

### Break into Features

- Use `### N.M Feature Name` under epics
- Each feature: clear scope, acceptance criteria
- Map features to implementation files (see plan "Files to Create or Modify")

### Write User Stories

Format: **US-N.M**: As a [role], I want [action] so that [benefit]

Examples:
- US-2.1: Staff sees "Role" selector with options: Annotator | Staff | Customer | System owner
- US-3.1: User in any role sees schema view for selected db-N

### Generate Todos

- One todo per major implementation step
- Use TodoWrite: `in_progress` when starting, `completed` when done
- Reference plan implementation order

## References

- **ROADMAP.md**: Product pillars, database portfolio, deliverable pipeline, validation
- **update-roadmap.mdc**: Format, versioning, linking rules
- **Plan files**: `.cursor/plans/*.plan.md` for implementation details
