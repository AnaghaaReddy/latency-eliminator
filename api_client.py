"""
API Client for Claude API
Handles all communication with Anthropic's Claude model
"""

import anthropic
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

class ClaudeAPIClient:
    def __init__(self):
        """Initialize Claude API client with API key from .env"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-haiku-4-5-20251001"
    
    def fix_script(self, script_content, error_output, past_fixes=None):
        """
        Ask Claude to fix a broken Python script
        
        Args:
            script_content (str): The broken Python script
            error_output (str): Error message from running the script
            past_fixes (list): List of similar past fixes (for learning)
        
        Returns:
            str: Fixed Python code
        """
        
        # Build context from past fixes
        past_context = ""
        if past_fixes:
            past_context = "\n\nPast similar fixes:\n"
            for fix in past_fixes:
                past_context += f"- Error: {fix['error_type']}\n"
                past_context += f"  Solution: {fix['solution']}\n"
        
        # Craft the prompt
        prompt = f"""You are a Python debugging expert. Fix this broken Python script.

{past_context}

BROKEN SCRIPT:
```python
{script_content}
```

ERROR OUTPUT:
{error_output}

INSTRUCTIONS:
1. Identify the root cause
2. Fix the script
3. Return ONLY the fixed Python code in a code block (```python ... ```)
4. No explanations, no comments, just the fixed code

FIXED SCRIPT:"""
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract the fixed code
            text = response.content[0].text
            
            # Parse code from response (between ```python and ```)
            if "```python" in text:
                start = text.find("```python") + 9
                end = text.find("```", start)
                fixed_code = text[start:end].strip()
            else:
                # Fallback: just use the text as-is
                fixed_code = text.strip()
            
            return fixed_code
        
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    def explain_error(self, error_output):
        """
        Ask Claude to explain what an error means
        
        Args:
            error_output (str): Error message
        
        Returns:
            str: Explanation of the error
        """
        
        prompt = f"""Briefly explain what this Python error means and how to fix it:

ERROR:
{error_output}

Keep it short (1-2 sentences)."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.content[0].text
        
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")


if __name__ == "__main__":
    # Test the API client
    client = ClaudeAPIClient()
    print("✓ Claude API client initialized successfully!")
