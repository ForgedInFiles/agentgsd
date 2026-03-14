# Command Line Interface (CLI)

Both `agentgsd` and `onyx` support several command-line flags to configure the provider, model, and API key at startup.

## Global Flags

These flags are available for both `agentgsd` and `onyx` packages.

| Flag | Description | Overrides |
|------|-------------|-----------|
| `--provider` | The LLM provider to use (e.g., `openrouter`, `gemini`, `groq`, `mistral`, `ollama`, `lmstudio`). | `PROVIDER` environment variable |
| `--model` | The specific model identifier to use. | `MODEL` environment variable |
| `--api-key` | The API key for the selected provider. | Provider-specific environment variables (e.g., `OPENROUTER_API_KEY`, `GEMINI_API_KEY`) |
| `-h`, `--help` | Show the help message and exit. | N/A |

## Usage Examples

### Using OpenRouter (Default)
```bash
# Uses default OpenRouter model
python3 -m packages.agentgsd.main

# Specify a different OpenRouter model
python3 -m packages.agentgsd.main --model anthropic/claude-3-5-sonnet
```

### Using Groq
```bash
python3 -m packages.agentgsd.main --provider groq --model llama3-70b-8192
```

### Using Gemini
```bash
python3 -m packages.agentgsd.main --provider gemini --model gemini-1.5-pro --api-key YOUR_GEMINI_KEY
```

### Using Local Models (Ollama/LMStudio)
Local providers typically do not require an API key.

```bash
# Using Ollama
python3 -m packages.agentgsd.main --provider ollama --model llama3

# Using LMStudio
python3 -m packages.agentgsd.main --provider lmstudio --model local-model
```

## Interactive Commands

Once the assistant is running, the following interactive commands are available:

| Command | Description |
|---------|-------------|
| `/q`, `/quit`, `/exit` | Quit the application |
| `/c`, `/clear` | Clear conversation history and reset token statistics |
| `/h`, `/help` | Show detailed help with all commands and key bindings |
| `/stats` | Display current token usage statistics and context window percentage |
| `/s`, `/skills` | List all available and loaded skills |
| `/compact` | Compact conversation to save context tokens |

## Professional Terminal UI

agentgsd features a beautiful, professional terminal interface inspired by top-tier AI coding assistants:

### Visual Elements

- **Banner** - Shows model, provider, skills count, and quick commands on startup
- **Tool Calls** - Color-coded icons for each tool (📖 read, 📝 write, 💻 bash, 🔍 grep, etc.)
- **Message Blocks** - Unicode box-drawing characters for assistant responses
- **Thinking Animation** - Animated spinner shows when AI is processing
- **Context Bar** - Visual progress bar showing token usage

### Color Scheme

| Element | Color |
|---------|-------|
| Success messages | Bright Green |
| Error messages | Bright Red |
| Warning messages | Bright Yellow |
| Info messages | Bright Cyan |
| Tool calls | Bright Yellow |
| Assistant messages | Bright Cyan |

### Notifications

The UI displays styled notifications for:
- ✓ Success (green)
- ✗ Error (red)  
- ⚠️ Warning (yellow)
- ℹ️ Info (cyan)

### ESC Interrupt

Press `ESC` to interrupt ongoing API requests. This is useful for:
- Stopping long-running responses
- Canceling requests that are taking too long
- Regaining control when the AI is processing

The interrupt works during API calls and will gracefully stop the request without crashing the application.

## Autocomplete

The CLI features rich autocompletion for:
- Commands (starting with `/`)
- Tool names
- File paths (triggered by `path:`, `read`, `write`, `edit`)
- Skill names (triggered by `skill:` or `activate`)

Press `Tab` to trigger or cycle through completions.

## Custom Slash Commands

agentgsd supports custom slash commands similar to Claude Code. Commands are defined as markdown files with YAML frontmatter.

### Command Locations

Commands are loaded from (in order of priority):
1. **Per-project**: `.agentgsd/commands/` (in project root)
2. **Package-installed**: Commands bundled with agentgsd (e.g., `/commit`, `/test`, `/fix`)
3. **Global**: `~/.agentgsd/commands/` (user home directory)

### Command File Format

```markdown
---
name: command-name
description: Human-readable description
aliases: [alias1, alias2]
---

# Command instructions
Your command prompt here...
Use $ARGUMENTS to include user-provided arguments.
Use $FILE for the first selected file.
Use $SELECTED_FILES for all selected files.
```

### Placeholders

| Placeholder | Description |
|-------------|-------------|
| `$ARGUMENTS` | User-provided arguments after command name |
| `$FILE` | First selected file |
| `$SELECTED_FILES` | All selected files (comma-separated) |
| `$FILE_COUNT` | Number of selected files |

### Example Commands

```markdown
---
name: review
description: Review code for bugs and issues
aliases: [code-review]
---

Review the code in $FILE for:
1. Bugs and potential errors
2. Security vulnerabilities
3. Performance concerns

Provide specific line numbers and fixes.
```

### Usage

```bash
/review src/main.py
/test utils/helper.py
/commit
```

### Managing Commands

| Command | Description |
|---------|-------------|
| `/cmds`, `/commands` | List all custom commands |
| Tab completion | Auto-complete command names |

### Built-in Commands

agentgsd comes with these default commands:

| Command | Description |
|---------|-------------|
| `/commit` | Create a git commit with proper conventions |
| `/test` | Generate unit tests for a file |
| `/fix` | Fix bugs using systematic debugging |

---

[← Back to Documentation](./README.md)
