# Agent Skills System

`agentgsd` implements the **Agent Skills open standard** (hosted at [agentskills.io](https://agentskills.io)), providing a portable and extensible way to teach your AI assistant new workflows, domain expertise, and specialized capabilities.

## Overview

A "skill" in `agentgsd` is a self-contained directory that instructs the agent on how to perform specific tasks or use certain tools. Skills follow a **progressive disclosure** model: the agent only loads the skill's name and description at startup, and only "activates" the full instructions when it determines the skill is relevant to the user's request.

## Directory Structure

Skills are located in the `skills/` directory (or other paths defined in `SKILLS_PATH`). Each skill has the following structure:

```text
skills/
└── my-skill/
    ├── SKILL.md      # Required: Instructions + YAML Metadata
    ├── scripts/      # Optional: Executable automation
    ├── references/   # Optional: API docs/specs
    └── assets/       # Optional: Templates/static files
```

## Creating a New Skill

Use the `skill-creator` skill to help you design and structure new skills according to the standard.

### 1. The SKILL.md File

This is the core of any skill. It must start with YAML frontmatter:

```markdown
---
name: skill-name
description: Concise explanation of when to use this skill.
---
# Skill Instructions
Detailed steps, best practices, and guardrails for the agent.
```

### 2. Best Practices for Skills

- **Conciseness:** Keep instructions direct and high-signal.
- **Token Efficiency:** Use lists, tables, and clear headings.
- **Guardrails:** Explicitly tell the agent what NOT to do.
- **Setup Guidance:** Include a section explaining how to install any required CLI tools or libraries.

## Built-in Skills

`agentgsd` comes with several powerful skills:

| Skill | Description |
|-------|-------------|
| **agent-browser-cli** | Efficient web browsing using accessibility tree snapshots. |
| **playwright-cli** | Advanced web automation and form-filling with Playwright. |
| **code-review** | Conduct security-focused, best-practice-aligned code reviews. |
| **skill-creator** | A meta-skill for designing new agentskills.io-compliant skills. |
| **ai-code-slop-removal** | Identify and remove redundant AI-generated comments and code. |
| **gsdmode** | Superpowers-inspired workflow for structured software development cycles |

## Activating Skills

Skills can be activated in two ways:
1. **Automatically:** The agent identifies a match between the skill's description and your request.
2. **Manually:** Using the `skill(name)` tool or the `/s` interactive command.

Example:
```
❯ Review the authentication logic in src/auth.py
[🧠 Activation: code-review]
Searching for security vulnerabilities in src/auth.py...
```

## Environment Configuration

Configure the discovery path for skills via environment variables:

```bash
# Path to built-in and custom skills
export SKILLS_PATH="./skills:/home/user/.agentgsd/skills"
```

## Interoperability

Because `agentgsd` follows the `agentskills.io` standard, skills you create here are portable. They can be shared and used in other compatible assistants like **Claude Code**, **GitHub Copilot**, and **Cursor** without modification.

---

For more information, visit [agentskills.io](https://agentskills.io).

---

[← Back to Documentation](./README.md)
