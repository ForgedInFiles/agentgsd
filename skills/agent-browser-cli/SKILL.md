---
name: agent-browser-cli
description: Efficient web interaction and browsing using the Snapshot + Refs system. Ideal for data extraction, navigation, and interacting with web elements using compact accessibility trees.
license: MIT
metadata:
  author: agentgsd
  version: "1.0"
  tags: browsing,web-automation,snapshot,agent-browser
  compatibility: Universal
---

# Agent Browser CLI Skill

## Overview
This skill enables high-efficiency web browsing by using the `agent-browser` CLI. It uses a "Snapshot + Refs" system that converts complex web pages into compact accessibility trees with short reference IDs (e.g., `@e1`), reducing token usage by up to 90%.

## Prerequisites & Setup

### 1. Check for Installation
Before using this skill, check if `agent-browser` is installed:
```bash
agent-browser --version
```

### 2. Automatic Setup
If not installed, walk the user through or perform the following:
1. Ensure Node.js is installed.
2. Install the CLI:
   ```bash
   npm install -g @vercel-labs/agent-browser
   ```
3. Initialize (if required):
   ```bash
   agent-browser init
   ```

## Capabilities

### 1. Navigation
- Open any URL: `agent-browser open <url>`
- Go back/forward: `agent-browser back`, `agent-browser forward`

### 2. Observation (Snapshot)
- Get an interactive element tree: `agent-browser snapshot -i`
- This returns elements with IDs like `@e1`, `@e2`. Use these IDs for interaction.

### 3. Interaction
- Click an element: `agent-browser click @e1`
- Type into an element: `agent-browser type @e2 "search query"`
- Press Enter: `agent-browser key @e2 Enter`
- Select option: `agent-browser select @e3 "Value"`

## Best Practices

1. **Always Re-Snapshot**: After any navigation or interaction that changes the page, run `agent-browser snapshot -i` again. Element references (@e1, etc.) can change when the DOM updates.
2. **Context Efficiency**: Do not fetch the raw HTML. Use the snapshot results to understand the page structure.
3. **State Management**: If multiple steps are needed, perform them sequentially and observe the result after each action.

## Example Workflow

### Search on Google
1. `agent-browser open https://google.com`
2. `agent-browser snapshot -i`
3. Identify the search box ID (e.g., `@e5`)
4. `agent-browser type @e5 "agentskills.io"`
5. `agent-browser key @e5 Enter`
6. `agent-browser snapshot -i` to see results.

## Troubleshooting
- If "command not found", ask the user to install `@vercel-labs/agent-browser` via npm.
- If navigation fails, check internet connectivity.
- If element IDs are missing, ensure you are using the `-i` (interactive) flag with `snapshot`.
