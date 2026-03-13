---
name: skill-creator
description: A meta-skill for designing, structuring, and implementing new agent skills following the agentskills.io open standard. Helps define capabilities, write instructions, and ensure proper metadata.
license: MIT
metadata:
  author: agentgsd
  version: "1.0"
  tags: meta,skill-development,agentskills,standard
  compatibility: Universal
---

# Skill Creator Skill

## Overview
This meta-skill provides a standardized framework for creating new agent skills. It follows the **Agent Skills open standard** (hosted at [agentskills.io](https://agentskills.io)), ensuring that all skills are portable, token-efficient, and easy for AI agents to discover and execute.

## Prerequisites & Setup

### 1. Project Structure
Ensure your project has a dedicated `skills/` directory where each skill will reside as its own subdirectory.

### 2. Skill Template
A compliant skill must have a `SKILL.md` file. The directory structure looks like this:
```text
skills/
└── my-new-skill/
    ├── SKILL.md          # Required: Instructions & Metadata
    ├── scripts/          # Optional: Executable scripts
    ├── references/       # Optional: API docs/references
    └── assets/           # Optional: Templates/Static files
```

## Capabilities

### 1. Metadata Generation
- Define a clear, unique `name`.
- Write a concise `description` (the "trigger" that helps the agent decide to load the skill).
- Add relevant `tags` for categorization.

### 2. Instruction Writing
- **Overview**: Define the skill's purpose.
- **Prerequisites**: List required tools (e.g., Node.js, Python libraries).
- **Setup**: Provide installation commands (`npm install`, `pip install`).
- **Capabilities**: Enumerate specific actions the agent can perform.
- **Best Practices**: Include token optimization and guardrails.

### 3. Progressive Disclosure Design
- Keep the `description` in the YAML frontmatter high-signal and short.
- Put detailed examples and long lists in the main Markdown body to save context space during initial discovery.

## Best Practices

1. **High Signal, Low Noise**: Avoid filler text. Instructions should be direct commands for the agent.
2. **Token Efficiency**: Use bullet points and tables instead of long paragraphs.
3. **Guardrails**: Explicitly tell the agent what *not* to do or when to ask for human confirmation.
4. **Reproducible Examples**: Provide at least one concrete "Example Workflow" for the agent to follow.
5. **Setup Logic**: Always include a section on how to verify if the required tools are installed.

## Step-by-Step Creation Process

### Phase 1: Planning
1. Identify the core capability (e.g., "Post to Slack", "Review PRs").
2. Determine required tools (e.g., Slack API, GitHub CLI).

### Phase 2: Implementation
1. `mkdir skills/<skill-name>`
2. Create `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: <skill-name>
   description: <one-sentence-description>
   ---
   ```
3. Write the instruction body following the standard sections (Overview, Setup, Capabilities, etc.).

### Phase 3: Validation
1. Use `ls skills/` to ensure the directory exists.
2. Check `read skills/<skill-name>/SKILL.md` for proper formatting.

## Example: "My First Skill"
```markdown
---
name: hello-world
description: A simple skill to demonstrate the standard.
---
# Hello World Skill
1. Greet the user with "Hello!".
2. Print the current date and time.
```

## Troubleshooting
- If the agent doesn't "see" the skill, check if the `SKILL.md` file is in the correct directory.
- If the description is too long, the agent might skip it. Keep it under 150 characters.
- Ensure the YAML frontmatter is correctly delimited by `---`.
