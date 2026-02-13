from typing import Any, Dict, List
import base64
import io


def ensure_api_key(api_key: str):
    if not api_key:
        raise ValueError("API key is required for this operation")


def bytes_to_data_uri(image_bytes: bytes, mime: str = "image/png") -> str:
    """Encode image bytes to a data URI (data:<mime>;base64,...)"""
    return f"data:{mime};base64,{base64.b64encode(image_bytes).decode('utf-8')}"


def normalize_response(resp: Any) -> Dict[str, List[str]]:
    """Normalize various API response shapes into {'urls': [...]}

    The function tries to find common keys like 'urls', 'result_urls', 'result' etc.
    If it finds a single 'result_url', it returns {'urls': [result_url]}.
    If nothing found, returns an empty dict.
    """
    if resp is None:
        return {}

    # If it's already a dict
    if isinstance(resp, dict):
        # Direct urls
        if 'urls' in resp and isinstance(resp['urls'], list):
            return {'urls': resp['urls']}
        if 'result_urls' in resp and isinstance(resp['result_urls'], list):
            return {'urls': resp['result_urls']}
        if 'result_url' in resp and isinstance(resp['result_url'], str):
            return {'urls': [resp['result_url']]}
        # 'result' may be list of dicts or list of urls
        if 'result' in resp and isinstance(resp['result'], list):
            urls: List[str] = []
            for item in resp['result']:
                if isinstance(item, dict):
                    # find urls key
                    if 'urls' in item and isinstance(item['urls'], list):
                        urls.extend(item['urls'])
                    elif 'result_url' in item and isinstance(item['result_url'], str):
                        urls.append(item['result_url'])
                elif isinstance(item, str):
                    urls.append(item)
                elif isinstance(item, list):
                    for sub in item:
                        if isinstance(sub, str):
                            urls.append(sub)
            if urls:
                return {'urls': urls}
        # Fallback: maybe resp contains list of urls directly
    # If resp is a list of strings
    if isinstance(resp, list):
        if all(isinstance(x, str) for x in resp):
            return {'urls': resp}

    return {}
