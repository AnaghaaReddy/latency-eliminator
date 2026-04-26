import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

# Try to list models (if available)
try:
    models = client.models.list()
    print("Available models:")
    for model in models.data:
        print(f"  - {model.id}")
except Exception as e:
    print(f"Error: {e}")
    print("\nTry these models instead:")
    print("  - claude-3-5-haiku-20241022 (cheapest)")
    print("  - claude-3-5-sonnet-20241022 (medium)")
    print("  - claude-opus-4-1-20250805 (best)")