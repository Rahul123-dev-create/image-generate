from typing import Dict, Any, Optional
import requests
import json
from .utils import ensure_api_key

def enhance_prompt(
    api_key: str,
    prompt: str,
    **kwargs
) -> str:
    """
    Enhance a prompt using Bria AI's prompt enhancement service.
    
    Args:
        api_key: Bria AI API key
        prompt: Original prompt to enhance
        **kwargs: Additional parameters for the API
    
    Returns:
        Enhanced prompt string
    """
    url = "https://engine.prod.bria-api.com/v1/prompt_enhancer"
    
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    data = {
        'prompt': prompt,
        **kwargs
    }
    
    ensure_api_key(api_key)

    try:
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        result = response.json()
        # Try to extract an enhanced prompt from the API response by normalizing keys.
        # We normalize keys by removing non-alphanumeric characters and lowercasing so
        # variants like 'prompt variations' or 'prompt-variations' are matched.
        if isinstance(result, dict):
            def normalize(k: str) -> str:
                return ''.join(ch for ch in k.lower() if ch.isalnum())

            preferred_keys = {
                'enhancedprompt', 'enhanced', 'promptenhanced', 'prompt',
                'promptvariation', 'promptvariations', 'variations'
            }

            for k, v in result.items():
                nk = normalize(k)
                if nk in preferred_keys and v:
                    if isinstance(v, (list, tuple)) and len(v) > 0:
                        return v[0]
                    if isinstance(v, str):
                        return v

            # If nothing matched, try to find any string value in the response and return it
            for v in result.values():
                if isinstance(v, str) and v.strip():
                    return v

        # Fallback: return original prompt
        return prompt
    except requests.HTTPError as he:
        print(f"HTTP error enhancing prompt: {str(he)} - {getattr(he, 'response', None)}")
        return prompt
    except Exception as e:
        print(f"Error enhancing prompt: {str(e)}")
        return prompt  # Return original prompt on error 