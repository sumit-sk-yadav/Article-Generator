"""Configuration constants for the application"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration (optional defaults from .env)
DEFAULT_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DEFAULT_TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Rate Limiting Configuration
REQUESTS_PER_SECOND = 0.2
CHECK_EVERY_N_SECONDS = 5
MAX_BUCKET_SIZE = 2

# LLM Models
PLANNER_MODEL = "groq/llama-3.3-70b-versatile"
WRITER_MODEL = "groq/qwen/qwen3-32b"
EDITOR_MODEL = "groq/llama-3.3-70b-versatile"

# Agent Settings
MAX_RPM = 5
CREW_MAX_RPM = 10

# Retry Settings
RETRY_MULTIPLIER = 2
RETRY_MIN_WAIT = 4
RETRY_MAX_WAIT = 120
RETRY_MAX_ATTEMPTS = 5
RETRY_DELAY = 5
