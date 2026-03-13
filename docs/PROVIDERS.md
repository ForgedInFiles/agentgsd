# Language Model Providers

`agentgsd` supports several major language model providers and local endpoints through its unified API client.

## Supported Providers

| Provider | Default URL | Supported Method | Required Key |
|----------|-------------|------------------|--------------|
| **OpenRouter** | `https://openrouter.ai/api/v1/messages` | Bearer Token | `OPENROUTER_API_KEY` |
| **Gemini** | `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions` | OpenAI-compatible | `GEMINI_API_KEY` |
| **Groq** | `https://api.groq.com/openai/v1/chat/completions` | OpenAI-compatible | `GROQ_API_KEY` |
| **Mistral** | `https://api.mistral.ai/v1/chat/completions` | OpenAI-compatible | `MISTRAL_API_KEY` |
| **Ollama** | `http://localhost:11434/v1/chat/completions` | Local (No Auth) | (None) |
| **LMStudio** | `http://localhost:1234/v1/chat/completions` | Local (No Auth) | (None) |

## Provider Details

### OpenRouter (Default)
OpenRouter provides unified access to dozens of models, including those from Anthropic, Google, Meta, and OpenAI. It uses a custom messaging format that supports both text and tool use.

- **Recommended Models:**
  - `anthropic/claude-3-5-sonnet`
  - `google/gemini-pro-1.5`
  - `meta-llama/llama-3-70b-instruct`

### Gemini
Native Google Gemini integration using the OpenAI-compatible endpoint.

- **Models:**
  - `gemini-1.5-pro`
  - `gemini-1.5-flash`

### Groq
Ultra-fast inference using Groq's LPU (Language Processing Unit).

- **Models:**
  - `llama3-70b-8192`
  - `llama3-8b-8192`
  - `mixtral-8x7b-32768`

### Mistral
Native Mistral AI integration.

- **Models:**
  - `mistral-large-latest`
  - `mistral-medium-latest`
  - `codestral-latest` (Optimized for code)

### Ollama (Local)
Run models locally on your own hardware using Ollama.

- **Models:** (depends on what you have pulled)
  - `llama3`
  - `mistral`
  - `codellama`

### LMStudio (Local)
Run models locally with LMStudio's local server.

- **Models:**
  - `local-model` (Default identifier used by LMStudio)

## Environment Configuration

You can configure the preferred provider via environment variables:

```bash
# Set global provider
export PROVIDER="groq"

# Set provider-specific keys
export GROQ_API_KEY="gsk_..."
export MISTRAL_API_KEY="...mi..."
export GEMINI_API_KEY="AIza..."
```

## Troubleshooting

### Connection Issues
If you encounter connection errors:
1. Verify the `api_url` is correct in `shared/config/settings.py` or through the CLI.
2. Check your internet connection or ensuring local servers (Ollama/LMStudio) are running.
3. Ensure your API key is valid and has not expired.

### Model Mismatch
Some providers have specific requirements for model naming. If a model is not found, check the provider's official documentation for the exact model string.
