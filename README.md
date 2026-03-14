# agentgsd

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-integrated-blue)](https://openrouter.ai)
[![Skills System](https://img.shields.io/badge/Skills-Available-green)](https://agentskills.io)

## Overview

**agentgsd** is an elite AI coding assistant with multi-provider support (OpenRouter, Gemini, Groq, Mistral, Ollama, LMStudio) and a rich terminal UI. It combines the power of diverse LLMs with a comprehensive toolset and an extensible skills system based on the [agentskills.io](https://agentskills.io) open standard.

Designed for developers who demand precision and efficiency, agentgsd offers:
- Multi-provider support: Choose between cloud APIs (OpenRouter, Gemini, Groq, Mistral) or local endpoints (Ollama, LMStudio)
- **Professional terminal UI** - Beautiful, color-coordinated interface inspired by Claude Code and OpenCode with:
  - Semantic color palette for different message types
  - Rich tool call formatting with color-coded icons
  - Beautiful message blocks with Unicode framing
  - Animated thinking spinners
  - Progress bars for context usage
  - Styled notifications (success/error/warning)
- Comprehensive file manipulation, search, shell, **git**, and **web browsing** tools
- **Semantic code indexer** - TF-IDF based search without external APIs
- **Autonomous task execution** - State machine workflows for bug fixes, features, refactoring
- **Self-correcting code generation** - Automatic validation and fix loops
- **Interactive planning** - Reviewable plans with user approval
- **Real-time thought visualization** - See the agent's reasoning
- Extensible skills system with built-in GSDMode workflow
- Real-time token usage tracking and statistics
- Markdown rendering for beautiful terminal output

## Monorepo Structure

agentgsd follows a monorepo structure with shared infrastructure and package-specific code:

```
agentgsd/
├── packages/
│   ├── agentgsd/                 # Core agentgsd package
│   │   ├── __init__.py           # Package info and exports
│   │   ├── main.py               # Main application logic
│   │   └── __main__.py           # Entry point for python -m agentgsd
│   └── onyx/                     # Additional package (example)
├── shared/                       # Shared modules across packages
│   ├── api/                      # API client implementations
│   │   ├── client.py             # OpenRouter API client
│   │   └── __init__.py
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── skills/                   # Skills system implementation
│   │   ├── __init__.py
│   │   └── loader.py
│   ├── indexer/                  # TF-IDF semantic code indexer
│   │   └── __init__.py
│   ├── tools/                    # Built-in tools (file, search, shell, git)
│   │   ├── __init__.py
│   │   ├── base.py               # Tool base class and registry
│   │   ├── file_tools.py         # File manipulation tools
│   │   ├── search_tools.py       # Search tools (grep, glob, find)
│   │   ├── shell_tools.py        # Shell operation tools
│   │   ├── git_tools.py          # Git operation tools
│   │   ├── indexer_tools.py      # Semantic indexer tools
│   │   └── web_tools.py          # Web search/fetch tools
│   ├── workflows/                # Autonomous task execution
│   │   ├── __init__.py
│   │   ├── engine.py             # State machine workflow engine
│   │   ├── corrector.py          # Self-correcting code generation
│   │   ├── planner.py             # Interactive planning
│   │   └── thoughts.py            # Thought visualization
│   ├── ui/                       # UI components and prompts
│   │   ├── __init__.py
│   │   ├── completer.py          # Auto-completion
│   │   ├── keybindings.py        # Keyboard shortcuts
│   │   ├── layout.py             # UI layout
│   │   └── prompts.py            # Prompt templates
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── colors.py             # Terminal colors and spinners
│       └── formatters.py         # Output formatting
├── skills/                       # Available agent skills
│   ├── ai-code-slop-removal/     # Skill for removing AI-generated code slop
│   │   └── SKILL.md
│   ├── code-review/              # Skill for conducting code reviews
│   │   └── SKILL.md
│   ├── flask-apps/               # Skill for Flask application development
│   │   └── SKILL.md
│   └── gsdmode/                  # GSDMode - Superpowers workflow
│       └── SKILL.md
├── docs/                         # Documentation
│   ├── API.md                    # API documentation
│   ├── TOOLS.md                  # Tools documentation
│   ├── SKILLS.md                 # Skills documentation
│   ├── PROVIDERS.md              # Provider configuration
│   └── CLI.md                    # CLI reference
├── tests/                        # Test suite
├── pyproject.toml                # Project configuration
├── README.md                     # This file
└── LICENSE                       # MIT License
```

## Installation

### Prerequisites

- Python 3.9 or higher
- An API key for your preferred provider (see [Providers](./docs/PROVIDERS.md))

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd agentgsd

# Install dependencies
pip install -e .
```

## Usage

### Starting the Assistant

```bash
# Start with default OpenRouter
python3 -m packages.agentgsd.main

# Start with a specific provider and model
python3 -m packages.agentgsd.main --provider groq --model llama3-70b-8192
```

See the [CLI Documentation](./docs/CLI.md) for more usage examples and flag details.

### Documentation

Full documentation is available in the [**Documentation Hub**](./docs/README.md):

- [🚀 **CLI Reference**](./docs/CLI.md) - Flags, commands, and interactive usage
- [🔌 **Providers Reference**](./docs/PROVIDERS.md) - Supported LLM providers and configuration
- [🛠 **Tools Reference**](./docs/TOOLS.md) - Built-in tools for files, search, and web
- [🧠 **Skills Reference**](./docs/SKILLS.md) - How to use and create agent skills
- [💻 **API Reference**](./docs/API.md) - Deep dive into the `ApiClient` architecture

## Available Commands

Once running, you can use these commands:

| Command | Description |
|---------|-------------|
| `/q`, `/quit`, `/exit` | Quit the application |
| `/c`, `/clear` | Clear conversation history & reset tokens |
| `/h`, `/help` | Show help message |
| `/stats` | Show token statistics |
| `/s`, `/skills` | List available skills |

### Key Bindings

| Key Binding | Description |
|-------------|-------------|
| `Tab` | Trigger autocomplete |
| `Ctrl+P` | Show commands popup |
| `F1` | Show detailed help |
| `Ctrl+C` | Cancel current input |
| `Ctrl+D` | Quit application |

### Tool Usage

The assistant can use various tools to help with coding tasks. You can either ask the assistant to use tools naturally, or invoke them directly:

#### File Tools
- `read(path, offset?, limit?)` - Read file with line numbers
- `write(path, content)` - Write content to file
- `edit(path, old, new, all?)` - Replace text in file
- `mkdir(path)` - Create directory
- `ls(path?)` - List directory contents
- `tree(path?, depth?)` - Show directory tree
- `head(path, n?)` - Show first N lines
- `tail(path, n?)` - Show last N lines
- `wc(path)` - Count lines/words/chars
- `pwd()` - Get current directory

#### Search Tools
- `grep(pat, path?)` - Search files for regex pattern
- `find(name, path?)` - Find files by name pattern
- `glob(pat, path?)` - Find files by glob pattern

#### Git Tools
- `git_status(repo_path?)` - Show working tree status
- `git_diff(repo_path?, staged?, staged_only?)` - Show changes
- `git_log(repo_path?, max_count?)` - Show commit logs
- `git_branch(repo_path?, branch_name?, create?, delete?)` - List/create/delete branches
- `git_commit(repo_path?, message?, amend?, all?)` - Record changes
- `git_add(repo_path?, files?, all_files?)` - Stage file changes
- `git_reset(repo_path?, mode?, target?, unstage?)` - Unstage changes
- `git_checkout(repo_path?, branch_name?, create_branch?, file_path?)` - Switch branches
- `git_push(repo_path?, remote?, branch?, set_upstream?)` - Push to remote
- `git_pull(repo_path?, remote?, branch?)` - Pull from remote

#### Indexer Tools
- `index_build(max_files?, path?)` - Build semantic code index
- `index_search(query, top_k?)` - Search indexed code
- `index_stats()` - Show index statistics

#### System Tools
- `bash(cmd)` - Run shell command
- `env(key?)` - Get environment variable value

#### Skills Tool
- `skill(name)` - Activate an agent skill

#### Web Tools
- `web_search(query, max_results?)` - Search the web
- `web_fetch(url)` - Fetch web page content

Example interaction:
```
❯ What files are in the current directory?
[📋 LS](.)
  📄 README.md (11,582 bytes · 2026-03-13 03:59)
  📄 pyproject.toml (1,798 bytes · 2026-03-13 03:50)
  📄 setup.py (637 bytes · 2026-03-13 03:50)
  📁 packages/
  📁 shared/
  📁 skills/
  📁 docs/
  📁 tests/

❯ Read the main application file
[📖 READ](packages/agentgsd/main.py)
     1    """
     2    Main implementation for the agentgsd package.
     3    
     4    This module provides the core functionality for the agentgsd coding assistant,
     5    including tool registry setup, API interaction, prompt_toolkit UI integration,
     6    and the main agentic loop for processing user requests.
     7    """
     8    
     9    import os
    10    import sys
    11    from typing import Any, Dict, List, Optional
    12    
    13    from prompt_toolkit import prompt
    14    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    15    from prompt_toolkit.completion import Completer, Completion
    16    from prompt_toolkit.formatted_text import HTML
    17    from prompt_toolkit.history import FileHistory
    18    from prompt_toolkit.key_binding import KeyBindings
    19    
    20    from shared.api import ApiClient
    21    from shared.config import load_config
    22    from shared.skills import load_skills, skills_xml, activate_skill
    23    from shared.tools import (
    24        Tool,
    25        ToolRegistry,
    26        ReadTool,
    27        WriteTool,
    28        EditTool,
    29        MkdirTool,
    30        LsTool,
    31        TreeTool,
    32        GrepTool,
    33        FindTool,
    34        BashTool,
    35    )
    36    from shared.utils.colors import thinking_spinner, loading_spinner
    37    from shared.utils.formatters import (
    38        format_tokens,
    39        context_bar,
    40        render_markdown,
    41        separator,
    42    )
    43    from shared.ui import (
    44        style,
    45        print_banner,
    46        print_tool_call,
    47        print_tool_result,
    48        print_stats,
    49        show_help_popup,
    50        create_keybindings,
    51    )
```

## Architecture Overview

agentgsd follows a modular architecture designed for extensibility and maintainability:

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   User Interface│    │   Agent Core     │    │   Tool System      │
│  (prompt_toolkit)│◄──►│ (LLM Interaction)│◄──►│ (File, Search,    │
│  - Input handling│    │  - API calls     │    │   Shell, Skills)   │
│  - Output rendering│  │  - Token tracking│    │                    │
│  - Autocomplete  │    │  - System prompt │    │                    │
└─────────────────┘    └──────────────────┘    └────────────────────┘
          ▲                         ▲                         ▲
          │                         │                         │
          └─────────────┬───────────┴─────────────┬───────────┘
                        ▼                         ▼
                ┌────────────────────┐    ┌────────────────────┐
                │   Configuration    │    │   Skills System    │
                │   (Environment)    │    │   (agentskills.io)│
                │   - API keys       │    │   - Skill discovery│
                │   - Model selection│    │   - Skill loading  │
                │   - Tool enablement│    │   - Skill activation │
                └────────────────────┘    └────────────────────┘
```

### Core Components

1. **User Interface Layer**: Built with prompt_toolkit for rich terminal experience
2. **Agent Core**: Handles LLM interactions via OpenRouter API, token tracking, and system prompt management (located in `packages/agentgsd/main.py`)
3. **Tool System**: Provides file manipulation, search, shell execution, and skills activation (in `shared/tools/`)
4. **Configuration System**: Manages environment variables and runtime settings (in `shared/config/`)
5. **Skills System**: Implements the agentskills.io framework for extensible workflows (in `shared/skills/` and `skills/` directories)

### Data Flow

1. User input is received through the prompt_toolkit interface
2. Input is processed and sent to the LLM via the API client with appropriate system prompt
3. LLM responds with either text content or tool use requests
4. Tool results are fed back to the LLM for further processing
5. Final response is rendered to the user with markdown formatting
6. Token usage is tracked throughout the interaction

## Extending agentgsd

### Adding Custom Tools

To create a custom tool:

1. Implement a function that takes an `args` dictionary and returns a string result
2. Add the tool to the `TOOLS` dictionary in `shared/tools/__init__.py` or register it dynamically
3. Follow the naming convention and provide appropriate documentation

Example:
```python
def my_custom_tool(args):
    """My custom tool description"""
    param = args.get("param", "default")
    # Tool implementation here
    return f"Result: {param}"

# In shared/tools/__init__.py or during registry creation:
# registry.register(MyCustomTool())
```

### Creating Skills

Skills follow the agentskills.io standard. Create a directory with:

1. `SKILL.md` - Contains YAML frontmatter and skill instructions
2. Optional: Additional files, scripts, or resources needed by the skill

Example SKILL.md:
```yaml
name: code-review
description: Conduct thorough code reviews with security and best practices focus
version: 1.0.0
author: agentgsd team
```

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Keep functions focused and under 50 lines when possible
- Add docstrings to all public functions and classes
- Use type hints for function parameters and return values

### Git Workflow

1. Create feature branches from `main`
2. Write tests for new functionality
3. Ensure all tests pass before merging
4. Squash commits when appropriate
5. Write clear, descriptive commit messages

### Testing

- Run tests with `pytest`
- Aim for high test coverage
- Test both unit and integration scenarios
- Mock external API calls in tests

### Documentation

- Keep documentation in sync with code changes
- Update README when adding major features
- Document all public APIs and tools
- Include usage examples in documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenRouter](https://openrouter.ai) for providing access to diverse LLMs
- [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for the excellent UI library
- [agentskills.io](https://agentskills.io) for the skills system framework
- All contributors to the open-source ecosystem that make tools like this possible

---

*Built with ❤️ for developers who demand excellence in their tools.*