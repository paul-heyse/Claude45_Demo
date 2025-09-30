# 🤖 Agentic Development Resources

This directory contains structured documentation optimized for AI-assisted development on the Aker Investment Platform.

## Purpose

These files provide **context engineering** for AI coding assistants to:

- Understand project architecture and patterns
- Generate code that follows established conventions
- Access concrete examples and schemas
- Follow a systematic development workflow
- Maintain consistency across the codebase

## Files Overview

### 🚀 [initialization](./initialization) - **START HERE FOR AI AGENTS**

**Complete initialization instructions with ready-to-use prompts.**

Contains:

- Three initialization prompts (full, condensed, minimal)
- Priority reading order with time estimates
- Development workflow overview
- Success indicators checklist
- Troubleshooting guide

**When to use:** First file to read when starting AI agent work on this project. Contains copy-paste prompts for initializing any AI coding assistant.

---

### 📘 [CONTEXT.md](./CONTEXT.md) - **PRIMARY REFERENCE**

**Core context document for AI agents.**

Contains:

- Project overview and current state
- Module structure and organization
- Core coding patterns (data classes, abstract connectors, scoring)
- Test patterns and fixtures
- Documentation standards
- Common commands
- Error handling conventions
- State-specific notes (CO/UT/ID)
- Agent workflow checklist

**When to use:** Read this FIRST before any development task.

---

### 💡 [EXAMPLES.md](./EXAMPLES.md)

**Concrete, runnable code examples.**

Contains:

- API connector pattern (abstract base + concrete implementation)
- Caching layer with SQLite
- Score calculation and normalization
- Geospatial operations
- Test fixtures and mocking
- Configuration loading
- CLI command structure
- Data validation patterns

**When to use:** Copy these patterns when implementing similar functionality.

---

### 📋 [SCHEMAS.md](./SCHEMAS.md)

**Data schemas and type definitions.**

Contains:

- Core data models (Submarket, MarketMetrics, RiskAssessment, ScoredMarket)
- JSON Schemas for validation
- API response structures
- Configuration schema
- Exception schema
- TypedDict definitions for AI clarity

**When to use:** Reference when defining data structures or validating inputs.

---

### 🔄 [WORKFLOW.md](./WORKFLOW.md)

**Step-by-step development process.**

Contains:

- Pre-development checklist
- Test-Driven Development (TDD) workflow
- Red-Green-Refactor cycle
- Integration testing approach
- Quality checks
- Git commit conventions
- Debugging strategies
- Incremental delivery strategy

**When to use:** Follow this workflow for every task from `tasks.md`.

---

## Quick Start for AI Agents

### Before Starting Any Task

**New AI agent? Start here:**

```bash
cat .agentic/initialization
# Copy one of the three initialization prompts and provide to AI
```

**Already initialized? Quick reference:**

1. **Read the spec:**

   ```bash
   cat openspec/changes/add-aker-investment-platform/specs/<capability>/spec.md
   ```

2. **Review patterns:**

   ```bash
   cat .agentic/CONTEXT.md
   ```

3. **Check examples:**

   ```bash
   cat .agentic/EXAMPLES.md | grep -A 50 "<pattern-name>"
   ```

4. **Follow workflow:**

   ```bash
   cat .agentic/WORKFLOW.md
   ```

### Development Cycle

```
Spec → Context → Examples → Write Tests → Implement → Quality Checks → Commit
  ↑                                                                        ↓
  └────────────────────── Mark Complete in tasks.md ──────────────────────┘
```

## File Organization

```
.agentic/
├── README.md          # This file - overview and guide
├── initialization     # AI agent initialization (START HERE!)
├── CONTEXT.md         # Primary context and patterns
├── WORKFLOW.md        # Step-by-step TDD process
├── EXAMPLES.md        # Copy-paste code templates
└── SCHEMAS.md         # Data models and types
```

## Integration with OpenSpec

These agentic resources **complement** OpenSpec:

| Document | Purpose | Authority |
|----------|---------|-----------|
| **OpenSpec specs/** | WHAT to build (requirements) | Source of truth for behavior |
| **OpenSpec design.md** | WHY and high-level HOW | Architecture decisions |
| **OpenSpec tasks.md** | WHAT to do (checklist) | Implementation roadmap |
| **.agentic/CONTEXT.md** | HOW to build (patterns) | Code conventions |
| **.agentic/EXAMPLES.md** | HOW (concrete code) | Copy-paste templates |
| **.agentic/SCHEMAS.md** | WHAT data looks like | Type definitions |
| **.agentic/WORKFLOW.md** | HOW to proceed | Process guide |

**Rule:** OpenSpec specs define behavior; `.agentic/` defines implementation patterns.

## Context Engineering Principles

### 1. Structured Context

All information is organized into scannable sections with clear headers and examples.

### 2. Concrete Examples

Every pattern includes runnable code, not just descriptions.

### 3. Type Clarity

Strong typing and schemas help AI agents understand data structures.

### 4. Scenario Mapping

OpenSpec scenarios map directly to test cases.

### 5. Pattern Reuse

Similar problems solved similarly; check EXAMPLES.md first.

### 6. Explicit Conventions

Don't rely on implicit knowledge; document everything.

## For Human Developers

While optimized for AI agents, these resources are equally valuable for human developers:

- **Onboarding:** New developers start with CONTEXT.md
- **Reference:** Quick lookup of patterns in EXAMPLES.md
- **Standards:** Maintain consistency via WORKFLOW.md
- **Types:** IDE autocomplete benefits from SCHEMAS.md

## Maintaining These Resources

### When to Update

**Update CONTEXT.md when:**

- Adding new architectural patterns
- Changing module structure
- Adding new coding conventions
- State-specific logic changes

**Update EXAMPLES.md when:**

- Creating reusable patterns (3+ uses)
- Solving complex integration problems
- Establishing new test fixture patterns

**Update SCHEMAS.md when:**

- Adding core data models
- Changing API contracts
- Adding validation rules

**Update WORKFLOW.md when:**

- Development process changes
- New quality checks added
- Debugging strategies proven useful

### Quality Standards

Each update should:

- [ ] Be concrete and actionable
- [ ] Include working code examples
- [ ] Follow existing formatting
- [ ] Link to relevant OpenSpec sections
- [ ] Be tested (if code example)

## Success Metrics

These resources are successful if:

✅ AI agents generate code matching project patterns without additional guidance
✅ Generated code passes linting and formatting checks
✅ Test structure matches spec scenarios automatically
✅ New developers can onboard in <1 hour
✅ Code reviews focus on logic, not style/structure

## Related Documentation

- **OpenSpec Proposal:** `openspec/changes/add-aker-investment-platform/README.md`
- **Project README:** `README.md`
- **Contributing Guide:** `CONTRIBUTING.md` (to be created)
- **API Documentation:** Generated from docstrings

## Feedback

If these resources aren't helping AI agents (or humans) work effectively:

1. Note what's confusing or missing
2. Add concrete examples of desired behavior
3. Update the relevant `.agentic/*.md` file
4. Test with next development task

**Remember:** The goal is to make AI agents highly productive by providing perfect context, not by writing perfect specifications.

---

**Version:** 1.0.0
**Last Updated:** 2025-09-30
**Status:** Active - Ready for development
