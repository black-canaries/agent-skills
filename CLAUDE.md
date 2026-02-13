# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

A library of AI agent skills targeting Claude Code, Codex, and Gemini. Skills are self-contained folders of instructions, scripts, and resources that AI agents load dynamically to improve performance on specialized tasks. The repo was seeded from Anthropic's public `anthropics/skills` repo but will diverge—most existing skills will be replaced.

Skills follow the [Agent Skills specification](https://agentskills.io/specification). The only difference across agents is the directory they install into: `.claude/`, `.codex/`, or `.gemini/`.

## Repository Structure

```
skills/          # Each subdirectory is a self-contained skill
  <skill-name>/
    SKILL.md     # Required: YAML frontmatter (name, description) + markdown instructions
    scripts/     # Optional: executable code for deterministic tasks
    references/  # Optional: documentation loaded into context as needed
    assets/      # Optional: files used in output (templates, images, fonts)
spec/            # Agent Skills specification (points to agentskills.io)
template/        # Minimal SKILL.md template for new skills
```

## Skill Anatomy

Every skill requires a `SKILL.md` with:
- **YAML frontmatter**: `name` (kebab-case identifier) and `description` (what it does + when to trigger it). Only these two fields—no extras.
- **Markdown body**: Instructions, loaded only after the skill triggers. Keep under 500 lines; split into `references/` files when approaching this limit.

The `description` field is the primary triggering mechanism. It must include both what the skill does and specific contexts for when to use it. All "when to use" information belongs in the description, not in the body.

## Creating Skills

The `skill-creator` skill in `skills/skill-creator/` defines the canonical process:

1. Understand the skill with concrete examples
2. Plan reusable contents (scripts, references, assets)
3. Initialize: `skills/skill-creator/scripts/init_skill.py <skill-name> --path <output-dir>`
4. Implement resources and write SKILL.md
5. Package: `skills/skill-creator/scripts/package_skill.py <path/to/skill-folder> [output-dir]`
6. Iterate based on real usage

Validation runs automatically during packaging (frontmatter, naming, structure, description quality).

## Commands

- **Generate distribution:** `python scripts/generate.py` — validates all skills and copies them into `dist/.claude/skills/`, `dist/.codex/skills/`, `dist/.gemini/skills/`

## Key Design Principles

- **Context window is a public good**: Skills share context with system prompts, conversation history, and user requests. Only include information the agent doesn't already know. Challenge every paragraph's token cost.
- **Progressive disclosure**: Three levels—metadata (~100 words, always loaded), SKILL.md body (<5k words, on trigger), bundled resources (on demand).
- **Degrees of freedom**: Match specificity to task fragility. Narrow bridge = guardrails (scripts). Open field = flexibility (text instructions).
- **No extraneous files**: No README.md, CHANGELOG.md, or auxiliary docs inside skills. Only files the agent needs to do the job.
