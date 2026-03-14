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

## Autocomplete

The CLI features rich autocompletion for:
- Commands (starting with `/`)
- Tool names
- File paths (triggered by `path:`, `read`, `write`, `edit`)
- Skill names (triggered by `skill:` or `activate`)

Press `Tab` to trigger or cycle through completions.

---

[← Back to Documentation](./README.md)
