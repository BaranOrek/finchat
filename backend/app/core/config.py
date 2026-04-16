import os
from dotenv import load_dotenv

load_dotenv()

COINGECKO_BASE_URL = os.getenv("COINGECKO_BASE_URL")
AI_BASE_URL = os.getenv("AI_BASE_URL")
AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")

if not COINGECKO_BASE_URL:
    raise ValueError("COINGECKO_BASE_URL is not set")

if not AI_BASE_URL:
    raise ValueError("AI_BASE_URL is not set")

if not AI_API_KEY:
    raise ValueError("AI_API_KEY is not set")

if not AI_MODEL:
    raise ValueError("AI_MODEL is not set")