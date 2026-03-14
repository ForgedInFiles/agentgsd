---
name: claude-blog-browser
description: Browse and query the Anthropic/Claude blog (https://claude.com/blog) to stay up-to-date with the latest announcements, research, and product updates.
license: MIT
metadata:
  author: agentgsd
  version: "1.0"
  tags: browsing,research,claude,anthropic,blog
  compatibility: Universal
---

# Claude Blog Browser Skill

## Overview
This skill enables efficient browsing and querying of the Anthropic/Claude blog (https://claude.com/blog) using the agent-browser CLI. It allows users to ask questions about blog content and stay current with the latest announcements, research papers, and product updates from Anthropic.

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

### 1. Blog Navigation
- Open the Claude blog: `agent-browser open https://claude.com/blog`
- Navigate to specific blog posts using links found in snapshots

### 2. Observation (Snapshot)
- Get an interactive element tree of the blog: `agent-browser snapshot -i`
- This returns elements with IDs like `@e1`, `@e2` for navigation
- Use snapshots to identify blog post titles, dates, and links

### 3. Interaction
- Click on blog post links: `agent-browser click @e1` (where @e1 is a post link)
- Type in search fields if available: `agent-browser type @e2 "search term"`
- Press Enter: `agent-browser key @e2 Enter`
- Navigate back to blog listing: `agent-browser back`

## Best Practices

1. **Always Re-Snapshot**: After any navigation or interaction that changes the page, run `agent-browser snapshot -i` again. Element references (@e1, etc.) can change when the DOM updates.

2. **Context Efficiency**: Do not fetch the raw HTML. Use the snapshot results to understand the page structure and identify relevant blog posts.

3. **Content Extraction**: When viewing a specific blog post, use snapshot to get the content, then extract relevant information to answer user questions.

4. **State Management**: For multi-step workflows (e.g., search for a topic, then read specific posts), perform steps sequentially and observe results after each action.

## Example Workflow

### Finding Information About a Specific Topic
1. `agent-browser open https://claude.com/blog`
2. `agent-browser snapshot -i` to see the blog listing
3. Identify links to recent blog posts (e.g., `@e1`, `@e3`, `@e5`)
4. Click on a promising post: `agent-browser click @e1`
5. `agent-browser snapshot -i` to see the full post content
6. Extract relevant information to answer the user's question
7. If needed, go back and check other posts: `agent-browser back`

### Staying Up-to-Date
1. `agent-browser open https://claude.com/blog`
2. `agent-browser snapshot -i` to see the latest posts
3. Identify the most recent posts by looking at dates and titles
4. Open and snapshot the top 2-3 most recent posts
5. Summarize the key announcements or updates for the user

## Troubleshooting
- If "command not found", ask the user to install `@vercel-labs/agent-browser` via npm.
- If navigation fails, check internet connectivity.
- If element IDs are missing, ensure you are using the `-i` (interactive) flag with `snapshot`.
- If the blog structure changes, adjust the interaction strategy based on new snapshot results.

## Notes
- The Claude blog is regularly updated with new content about AI research, product releases, and company announcements.
- This skill works best when combined with clear user questions about specific topics they want to learn about from the blog.