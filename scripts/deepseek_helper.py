import os
import sys
import json
import urllib.request
import urllib.error

# Configuration Defaults
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"

class DeepSeekAPIError(Exception):
    """Base exception class for API operations."""
    pass

class MissingAPIKeyError(DeepSeekAPIError):
    """Raised when no API key is configured in the environment."""
    pass

class DeepSeekConnectionError(DeepSeekAPIError):
    """Raised when connection to API fails."""
    pass


def has_api_key():
    """Returns True if any supported LLM provider is configured in the environment."""
    return any(os.environ.get(k) for k in [
        "DEEPSEEK_API_KEY",
        "GEMINI_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "CUSTOM_OPENAI_KEY",
        "USE_OLLAMA",
        "OLLAMA_MODEL",
        "OLLAMA_API_BASE"
    ])


def call_deepseek(prompt, system_prompt="You are a helpful assistant."):
    """Unified LLM entrypoint that routes requests based on available environment keys.
    Maintains the 'call_deepseek' name for codebase compatibility.
    """
    # Precedence: DeepSeek -> Gemini -> OpenAI -> Anthropic -> Custom OpenAI/Ollama
    
    # 1. DeepSeek
    if os.environ.get("DEEPSEEK_API_KEY"):
        return _call_deepseek_native(prompt, system_prompt)
        
    # 2. Gemini
    if os.environ.get("GEMINI_API_KEY"):
        return _call_gemini_native(prompt, system_prompt)
        
    # 3. OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        return _call_openai_native(prompt, system_prompt)
        
    # 4. Anthropic
    if os.environ.get("ANTHROPIC_API_KEY"):
        return _call_anthropic_native(prompt, system_prompt)
        
    # 5. Custom OpenAI compatible endpoint
    if os.environ.get("CUSTOM_OPENAI_URL"):
        return _call_custom_openai(prompt, system_prompt)
        
    # 6. Ollama
    if os.environ.get("USE_OLLAMA") or os.environ.get("OLLAMA_API_BASE") or os.environ.get("OLLAMA_MODEL"):
        return _call_ollama(prompt, system_prompt)
        
    raise MissingAPIKeyError("Warning: No LLM API key or provider configured in the environment.")


def _send_json_post(url, payload, headers, provider_name):
    """Helper function to perform standard JSON POST request with retry logic."""
    import time
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    max_retries = 3
    retry_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            print(f"Sending reasoning query to {provider_name} ({payload.get('model')})... (Attempt {attempt + 1}/{max_retries})")
            with urllib.request.urlopen(req, timeout=45) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                answer = res_json["choices"][0]["message"]["content"]
                return answer
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                print(f"Temporary API error {e.code} from {provider_name}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise DeepSeekAPIError(f"HTTP Error: {provider_name} returned code {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                print(f"Network error connecting to {provider_name}: {e.reason}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise DeepSeekConnectionError(f"Network Warning: Failed to connect to {provider_name}: {e}")
        except Exception as e:
            raise DeepSeekAPIError(f"General Warning: {provider_name} call encountered an error: {e}")


def _call_deepseek_native(prompt, system_prompt):
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    api_url = os.environ.get("DEEPSEEK_API_URL", API_URL)
    model = os.environ.get("DEEPSEEK_MODEL", MODEL)
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    return _send_json_post(api_url, payload, headers, "DeepSeek API")


def _call_gemini_native(prompt, system_prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "generationConfig": {
            "temperature": 0.2
        }
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
    import time
    max_retries = 3
    retry_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            print(f"Sending reasoning query to Gemini API ({model})... (Attempt {attempt + 1}/{max_retries})")
            with urllib.request.urlopen(req, timeout=45) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                answer = res_json["candidates"][0]["content"]["parts"][0]["text"]
                return answer
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                print(f"Temporary API error {e.code} from Gemini API. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise DeepSeekAPIError(f"HTTP Error: Gemini API returned code {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                print(f"Network error connecting to Gemini API: {e.reason}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise DeepSeekConnectionError(f"Network Warning: Failed to connect to Gemini API: {e}")
        except Exception as e:
            raise DeepSeekAPIError(f"General Warning: Gemini API call encountered an error: {e}")


def _call_openai_native(prompt, system_prompt):
    api_key = os.environ.get("OPENAI_API_KEY")
    api_url = "https://api.openai.com/v1/chat/completions"
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    return _send_json_post(api_url, payload, headers, "OpenAI API")


def _call_anthropic_native(prompt, system_prompt):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    api_url = "https://api.anthropic.com/v1/messages"
    model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    payload = {
        "model": model,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.2
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
    import time
    max_retries = 3
    retry_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            print(f"Sending reasoning query to Anthropic API ({model})... (Attempt {attempt + 1}/{max_retries})")
            with urllib.request.urlopen(req, timeout=45) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                answer = res_json["content"][0]["text"]
                return answer
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                print(f"Temporary API error {e.code} from Anthropic API. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise DeepSeekAPIError(f"HTTP Error: Anthropic API returned code {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                print(f"Network error connecting to Anthropic API: {e.reason}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            raise DeepSeekConnectionError(f"Network Warning: Failed to connect to Anthropic API: {e}")
        except Exception as e:
            raise DeepSeekAPIError(f"General Warning: Anthropic API call encountered an error: {e}")


def _call_custom_openai(prompt, system_prompt):
    api_key = os.environ.get("CUSTOM_OPENAI_KEY")
    api_url = os.environ.get("CUSTOM_OPENAI_URL")
    model = os.environ.get("CUSTOM_OPENAI_MODEL", "custom-model")
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    headers = {
        "Content-Type": "application/json"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
        
    return _send_json_post(api_url, payload, headers, "Custom OpenAI API")


def _call_ollama(prompt, system_prompt):
    api_url = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434/v1/chat/completions")
    model = os.environ.get("OLLAMA_MODEL", "llama3")
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "stream": False
    }
    headers = {
        "Content-Type": "application/json"
    }
    return _send_json_post(api_url, payload, headers, "Ollama Local API")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/deepseek_helper.py \"<prompt>\" [\"<system_prompt>\"]")
        sys.exit(1)
        
    prompt = sys.argv[1]
    system_prompt = sys.argv[2] if len(sys.argv) > 2 else "You are a helpful assistant."
    
    try:
        answer = call_deepseek(prompt, system_prompt)
        print("\n=== LLM RESPONSE ===")
        print(answer)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
