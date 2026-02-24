# Thinking Levels - controls reasoning verbosity for models that support it
# Maps abstract levels to provider-specific parameters

THINKING_LEVELS = {
    'off': 0,      # No reasoning/thinking output
    'minimal': 1,  # Very brief reasoning
    'low': 2,      # Light reasoning
    'medium': 3,   # Balanced reasoning (default for reasoning models)
    'high': 4,     # Detailed reasoning
    'xhigh': 5     # Maximum reasoning depth
}

# Provider-specific mappings for thinking levels
# Note: For GPT-OSS models, thinking cannot be fully disabled - only low/medium/high levels
# For other Ollama models (Qwen3, DeepSeek), think=False works
THINKING_LEVEL_OLLAMA = {
    'off': False,      # Disable reasoning (not supported by GPT-OSS)
    'minimal': 'low',
    'low': 'low',
    'medium': 'medium',
    'high': 'high',
    'xhigh': 'high'
}

THINKING_LEVEL_OPENAI = {
    'off': None,       # Not applicable for non-reasoning models
    'minimal': 'low',
    'low': 'low',
    'medium': 'medium',
    'high': 'high',
    'xhigh': 'high'
}

THINKING_LEVEL_ANTHROPIC = {
    'off': None,
    'minimal': 1024,    # budget_tokens
    'low': 2048,
    'medium': 8192,
    'high': 16384,
    'xhigh': 32768
}

# Google Gemini uses reasoning_effort for OpenAI-compatible API
THINKING_LEVEL_GOOGLE = {
    'off': 'none',
    'minimal': 'low',
    'low': 'low',
    'medium': 'medium',
    'high': 'high',
    'xhigh': 'high'
}
