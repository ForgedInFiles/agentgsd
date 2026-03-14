# agentgsd Documentation

Welcome to the **agentgsd** documentation. This directory contains detailed references and guides for using, configuring, and extending the elite AI coding assistant.

## Quick Links

- [🚀 **CLI Reference**](./CLI.md) - Command-line flags and interactive usage.
- [🔌 **Providers Reference**](./PROVIDERS.md) - Supported LLM providers and setup.
- [🛠 **Tools Reference**](./TOOLS.md) - Detailed guide to built-in file, search, git, and web tools.
- [🧠 **Skills Reference**](./SKILLS.md) - The agentskills.io standard and creating custom skills.
- [💻 **API Reference**](./API.md) - Architecture of the `ApiClient` and message normalization.

## Core Concepts

### Multi-Provider Support
agentgsd is designed to be provider-agnostic. You can switch between cloud providers like **OpenRouter**, **Groq**, and **Gemini**, or run local models via **Ollama** and **LMStudio**. All providers are normalized to a single consistent interface.

### The Tool System
Everything the assistant does (outside of chatting) is powered by **Tools**. From reading files to searching the web, git operations to semantic code indexing, tools provide the agent with the capabilities it needs to be an effective coding partner.

### Semantic Code Indexer
agentgsd includes a **TF-IDF based semantic indexer** that provides intelligent code search without requiring external APIs. The indexer parses code symbols (functions, classes, methods) and enables semantic search using cosine similarity.

### Autonomous Task Execution
The **workflow engine** provides state machine-based task execution for common coding workflows:
- Bug Fix Workflow
- Feature Addition Workflow
- Refactoring Workflow
- Test Writing Workflow

### Self-Correcting Code Generation
The **corrector module** automatically validates generated code using:
- Syntax checking (ast.parse)
- Linting (ruff)
- Test execution (pytest)
- Predefined fix patterns for common errors

### Interactive Planning
The **planner module** generates structured plans before execution with:
- Risk assessment
- File impact analysis
- Rollback procedures
- User approval workflows

### Thought Visualization
The **thoughts module** provides real-time visualization of the agent's reasoning process with different thought types (analysis, planning, decision, execution, validation, correction).

### Agent Skills
Based on the [agentskills.io](https://agentskills.io) open standard, **Skills** are portable instructions that teach the agent how to follow complex workflows or use specific sets of tools. Includes **GSDMode** - a Superpowers-inspired workflow for structured software development.

---

[Back to main README](../README.md)
