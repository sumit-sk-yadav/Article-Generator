
"""Configuration constants for the application"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration - Support multiple providers
DEFAULT_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DEFAULT_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
DEFAULT_TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Provider Selection - Change this to switch providers
SELECTED_PROVIDER = os.getenv("LLM_PROVIDER", "cerebras")  # Options: "groq", "openai", "cerebras"

# Rate Limiting Configuration
REQUESTS_PER_SECOND = 0.2
CHECK_EVERY_N_SECONDS = 5
MAX_BUCKET_SIZE = 2

# LLM Models - Configure based on provider
if SELECTED_PROVIDER == "groq":
    PLANNER_MODEL = "groq/qwen/qwen3-32b"
    WRITER_MODEL = "groq/qwen/qwen3-32b"
    EDITOR_MODEL = "groq/qwen/qwen3-32b"
    MAX_RPM = 3
    CREW_MAX_RPM = 5
    RETRY_DELAY = 10
elif SELECTED_PROVIDER == "openai":
    # PLANNER_MODEL = "gpt-4o"
    # WRITER_MODEL = "gpt-4o"
    # EDITOR_MODEL = "gpt-4o"
    # Or use cheaper option:
    PLANNER_MODEL = "gpt-4o-mini"
    WRITER_MODEL = "gpt-4o-mini"
    EDITOR_MODEL = "gpt-4o-mini"
    MAX_RPM = 10
    CREW_MAX_RPM = 20
    RETRY_DELAY = 2
elif SELECTED_PROVIDER == "cerebras":
    # Cerebras models - ultra-fast inference
    PLANNER_MODEL = "cerebras/llama3.3-70b"
    WRITER_MODEL = "cerebras/llama3.3-70b"
    EDITOR_MODEL = "cerebras/llama3.3-70b"  
    # Alternative Cerebras models:
    # PLANNER_MODEL = "cerebras/llama3.3-70b"
    # WRITER_MODEL = "cerebras/llama3.1-8b"  # Faster, cheaper
    MAX_RPM = 30  # Cerebras is VERY fast - 2200+ tokens/sec
    CREW_MAX_RPM = 50
    RETRY_DELAY = 1  # Much shorter delay due to speed
else:
    raise ValueError(f"Invalid LLM_PROVIDER: {SELECTED_PROVIDER}. Choose 'groq', 'openai', or 'cerebras'")

# Retry Settings
RETRY_MULTIPLIER = 2
RETRY_MIN_WAIT = 4
RETRY_MAX_WAIT = 120
RETRY_MAX_ATTEMPTS = 5

# Provider-specific API key mapping
PROVIDER_API_KEYS = {
    "groq": DEFAULT_GROQ_API_KEY,
    "openai": DEFAULT_OPENAI_API_KEY,
    "cerebras": DEFAULT_CEREBRAS_API_KEY,
}
