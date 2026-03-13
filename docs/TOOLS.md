# Tools Reference

## Overview

The agentgsd tool system provides a comprehensive set of utilities for file manipulation, searching, shell operations, and more. All tools inherit from a common base class and follow a consistent interface.

## Tool Base Classes

### Tool Base Class

All tools inherit from the `shared.tools.base.Tool` base class:

```python
from shared.tools.base import Tool

class MyTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="What my tool does",
            parameters={"param": "string"}
        )
    
    def execute(self, args):
        # Tool implementation
        return "result"
```

### ToolRegistry

Tools are managed by a `ToolRegistry` which provides:
- Registration and retrieval of tools
- Schema generation for API function calling
- Tool execution with error handling

## Available Tools

### File Tools

#### ReadTool
Read file content with line numbers.

**Parameters:**
- `path` (string): File path to read
- `offset` (number?, optional): Line offset to start from (0-indexed)
- `limit` (number?, optional): Maximum number of lines to read

**Returns:** File content with line numbers prefixed

**Example:**
```python
result = read_tool.execute({"path": "./src/main.py", "offset": 10, "limit": 20})
```

#### WriteTool
Write content to a file.

**Parameters:**
- `path` (string): File path to write to
- `content` (string): Content to write

**Returns:** Success message with file path

**Example:**
```python
result = write_tool.execute({"path": "./output.txt", "content": "Hello World"})
```

#### EditTool
Replace text in a file.

**Parameters:**
- `path` (string): File path to edit
- `old` (string): Text to replace
- `new` (string): Replacement text
- `all` (boolean?, optional): Replace all occurrences (default: false)

**Returns:** Success message with file path

**Example:**
```python
result = edit_tool.execute({
    "path": "./config.txt",
    "old": "DEBUG=True",
    "new": "DEBUG=False"
})
```

#### MkdirTool
Create a directory.

**Parameters:**
- `path` (string): Directory path to create

**Returns:** Success message with directory path

**Example:**
```python
result = mkdir_tool.execute({"path": "./new/sub/dir"})
```

#### LsTool
List directory contents.

**Parameters:**
- `path` (string?, optional): Directory path (default: current directory)

**Returns:** Formatted listing of files and directories

**Example:**
```python
result = ls_tool.execute({"path": "./src"})
```

#### TreeTool
Show directory tree structure.

**Parameters:**
- `path` (string?, optional): Directory path (default: current directory)
- `depth` (number?, optional): Maximum depth to show

**Returns:** Tree-formatted directory listing

**Example:**
```python
result = tree_tool.execute({"path": "./project", "depth": 2})
```

#### HeadTool
Show first N lines of a file.

**Parameters:**
- `path` (string): File path
- `n` (number?, optional): Number of lines (default: 20)

**Returns:** First N lines with line numbers

**Example:**
```python
result = head_tool.execute({"path": "./log.txt", "n": 10})
```

#### TailTool
Show last N lines of a file.

**Parameters:**
- `path` (string): File path
- `n` (number?, optional): Number of lines (default: 20)

**Returns:** Last N lines with line numbers

**Example:**
```python
result = tail_tool.execute({"path": "./error.log", "n": 5})
```

#### WcTool
Count lines, words, and characters in a file.

**Parameters:**
- `path` (string): File path

**Returns:** Formatted count of lines, words, and characters

**Example:**
```python
result = wc_tool.execute({"path": "./document.txt"})
```

#### PwdTool
Get current working directory.

**Parameters:** None

**Returns:** Current directory path

**Example:**
```python
result = pwd_tool.execute({})
```

### Search Tools

#### GrepTool
Search files for regex pattern.

**Parameters:**
- `pat` (string): Regex pattern to search for
- `path` (string?, optional): Directory or file to search (default: current directory)

**Returns:** Matching lines with file paths and line numbers

**Example:**
```python
result = grep_tool.execute({
    "pat": "def .*\\(",
    "path": "./src"
})
```

#### GlobTool
Find files by pattern.

**Parameters:**
- `pat` (string): Glob pattern (e.g., "*.py", "**/*.js")
- `path` (string?, optional): Base directory (default: current directory)

**Returns:** Matching file paths sorted by modification time

**Example:**
```python
result = glob_tool.execute({
    "pat": "*.py",
    "path": "./project"
})
```

#### FindTool
Find files by name pattern.

**Parameters:**
- `name` (string?, optional): Filename pattern regex (default: ".*")
- `path` (string?, optional): Directory to search (default: current directory)

**Returns:** Matching file paths

**Example:**
```python
result = find_tool.execute({
    "name": ".*test.*",
    "path": "./project"
})
```

### Shell Tools

#### BashTool
Run shell command.

**Parameters:**
- `cmd` (string): Shell command to execute

**Returns:** Command output (stdout)

**Example:**
```python
result = bash_tool.execute({"cmd": "ls -la | head -5"})
```

#### EnvTool
Get environment variable value.

**Parameters:**
- `key` (string?, optional): Environment variable name (default: returns all vars)

**Returns:** Environment variable value or all variables

**Example:**
```python
result = env_tool.execute({"key": "HOME"})
# or
result = env_tool.execute({})  # Returns all environment variables
```

### Skills Tool

#### SkillTool
Activate an agent skill.

**Parameters:**
- `name` (string): Skill name to activate

**Returns:** Skill instructions or error message

**Example:**
```python
result = skill_tool.execute({"name": "code-review"})
```

## Tool Registration

Tools are typically registered in a `ToolRegistry`:

```python
from shared.tools.base import ToolRegistry
from shared.tools.file_tools import *
from shared.tools.search_tools import *
from shared.tools.shell_tools import *

# Create registry and register all standard tools
registry = ToolRegistry()
registry.register(ReadTool())
registry.register(WriteTool())
registry.register(EditTool())
# ... register all other tools

# Or use convenience function to register multiple tools
from shared.tools import register_standard_tools
registry = ToolRegistry()
register_standard_tools(registry)
```

## Schema Generation

For API function calling, generate schemas from the registry:

```python
from shared.api.client import ApiClient

# Generate schema for all registered tools
schema = ApiClient.make_schema(registry.get_all_tools())

# Use in API call
response = client.call_api(
    messages=[{"role": "user", "content": "List files"}],
    system_prompt="You are a helpful assistant.",
    tools=schema
)
```

## Creating Custom Tools

To create a custom tool:

1. Inherit from `shared.tools.base.Tool`
2. Implement the `execute` method
3. Register with the tool registry

```python
from shared.tools.base import Tool
from shared.utils.colors import GREEN, RESET

class HelloTool(Tool):
    def __init__(self):
        super().__init__(
            name="hello",
            description="Say hello to someone",
            parameters={"name": "string"}
        )
    
    def execute(self, args):
        name = args.get("name", "World")
        return f"{GREEN}Hello, {name}!{RESET}"

# Register the tool
registry = ToolRegistry()
registry.register(HelloTool())
```

## Tool Categories

### File Manipulation
- Read, Write, Edit, Mkdir, Ls, Tree, Head, Tail, Wc, Pwd

### Search Operations
- Grep, Glob, Find

### Shell Operations
- Bash, Env

### System Operations
- Skill (activate agent skills)

## Error Handling

All tools return formatted error messages when appropriate:

- File not found errors
- Permission denied errors
- Invalid parameter errors
- Tool-specific errors (e.g., pattern not found)

Error messages are formatted with ANSI colors for visibility in the terminal.

## Best Practices

1. **Parameter Validation**: Validate parameters in the execute method
2. **Error Handling**: Catch and return descriptive error messages
3. **Consistent Output**: Use shared utilities for colored output when appropriate
4. **Documentation**: Provide clear descriptions and parameter documentation
5. **Thread Safety**: Tools should be stateless or handle concurrent access properly

## See Also

- [API Documentation](./API.md) - For information about the API client
- [Skills Documentation](./SKILLS.md) - For information about the skills system
- [Shared Tools Source](../shared/tools/) - For implementation details