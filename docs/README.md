# agentgsd Documentation

Welcome to the **agentgsd** documentation. This directory contains detailed references and guides for using, configuring, and extending the elite AI coding assistant.

## Quick Links

- [🚀 **CLI Reference**](./CLI.md) - Command-line flags and interactive usage.
- [🔌 **Providers Reference**](./PROVIDERS.md) - Supported LLM providers and setup.
- [🛠 **Tools Reference**](./TOOLS.md) - Detailed guide to built-in file, search, and web tools.
- [🧠 **Skills Reference**](./SKILLS.md) - The agentskills.io standard and creating custom skills.
- [💻 **API Reference**](./API.md) - Architecture of the `ApiClient` and message normalization.

## Core Concepts

### Multi-Provider Support
agentgsd is designed to be provider-agnostic. You can switch between cloud providers like **OpenRouter**, **Groq**, and **Gemini**, or run local models via **Ollama** and **LMStudio**. All providers are normalized to a single consistent interface.

### The Tool System
Everything the assistant does (outside of chatting) is powered by **Tools**. From reading files to searching the web, tools provide the agent with the capabilities it needs to be an effective coding partner.

### Agent Skills
Based on the [agentskills.io](https://agentskills.io) open standard, **Skills** are portable instructions that teach the agent how to follow complex workflows or use specific sets of tools (like Playwright for web automation).

---

[Back to main README](../README.md)
