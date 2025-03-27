import os
import logging
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIModel

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def get_model():
    """Initialize and return the OpenAI model with correct API configuration."""

    # Retrieve environment variables
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("BASE_URL", "https://api.openai.com/v1").strip()
    model_choice = os.getenv("MODEL_CHOICE", "gpt-4o-mini").strip()

    # Debugging: Log the API configuration (without exposing secrets)
    logging.debug(f"Base URL: {base_url}")
    logging.debug(f"Using Model: {model_choice}")
    logging.debug(f"API Key Loaded: {'Yes' if api_key else 'No (Missing)'}")

    # Validate API key
    if not api_key:
        raise ValueError("Missing API key. Please set LLM_API_KEY in your .env file.")

    # Return the OpenAI model instance
    return OpenAIModel(
        model_choice,
        base_url=base_url,
        api_key=api_key
    )
