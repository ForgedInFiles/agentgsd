---
name: playwright-cli
description: Advanced web automation and testing using the Playwright CLI. Supports navigation, form filling, screenshots, PDF generation, and trace capture.
license: MIT
metadata:
  author: agentgsd
  version: "1.0"
  tags: web-automation,testing,playwright,scraping
  compatibility: Universal
---

# Playwright CLI Skill

## Overview
This skill provides advanced web automation capabilities using the `playwright-cli`. It's a powerful tool for complex scraping, automated testing, and interacting with dynamic web applications.

## Prerequisites & Setup

### 1. Check for Installation
Before using this skill, check if `npx` (from Node.js) is available:
```bash
npx --version
```

### 2. Automatic Setup
If `playwright` or its browsers are not ready, walk the user through or perform the following:
1. Ensure Node.js and npm are installed.
2. Install Playwright and browsers:
   ```bash
   npx playwright install --with-deps
   ```

## Capabilities

### 1. Navigation & Content
- Navigate to a URL: `npx playwright open <url>`
- Get page content: `npx playwright screenshot <url> <filename>.png`
- Generate PDF: `npx playwright pdf <url> <filename>.pdf`

### 2. Form Filling & Interaction
- Fill form field: `npx playwright fill <selector> <value>`
- Click button: `npx playwright click <selector>`
- Check checkbox: `npx playwright check <selector>`

### 3. Trace and Debug
- Capture trace for later analysis: `npx playwright test --trace on`
- Run in headed mode for visual debugging (if requested by user): `npx playwright open --headed <url>`

## Best Practices

1. **Selector Precision**: Use precise CSS or XPath selectors to interact with elements.
2. **Handle Dynamic Content**: Allow the page to load by using waiting mechanisms if needed.
3. **Stateless Commands**: Each `npx playwright` command is typically discrete. Use persistent state files if session management is required across multiple steps.
4. **Token Optimization**: Use screenshots and text-based outputs instead of raw HTML when possible.

## Example Workflow

### Extract Data from a Page
1. `npx playwright open https://example.com`
2. Analyze selectors using `read` tool or screenshots.
3. `npx playwright click ".login-button"`
4. `npx playwright fill "#username" "user"`
5. `npx playwright screenshot https://example.com/dashboard dashboard.png`

## Troubleshooting
- If "npx command not found", ask the user to install Node.js.
- If browser binaries are missing, run `npx playwright install`.
- For persistent issues, check network connectivity and site permissions.
