import os
import sys
import json
import urllib.request
import urllib.error

# DeepSeek Configuration
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"  # Default model (can also be deepseek-reasoner)

def call_deepseek(prompt, system_prompt="You are a helpful assistant."):
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    
    # 1. Fallback Check: Check if API key is configured
    if not api_key:
        print("Warning: DEEPSEEK_API_KEY environment variable is not configured.")
        print("Gracefully transitioning to Local Fallback Mode (Exit Code 2).")
        sys.exit(2)
        
    # Prepare payload
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    data = json.dumps(payload).encode("utf-8")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
    
    # 2. Execution & Error Handling with Local Fallback
    try:
        print(f"Sending reasoning query to DeepSeek API ({MODEL})...")
        with urllib.request.urlopen(req, timeout=30) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            
            # Extract content
            answer = res_json["choices"][0]["message"]["content"]
            return answer
            
    except urllib.error.URLError as e:
        print(f"Network Warning: Failed to connect to DeepSeek API: {e}")
        print("Gracefully transitioning to Local Fallback Mode (Exit Code 2).")
        sys.exit(2)
    except Exception as e:
        print(f"General Warning: DeepSeek API call encountered an error: {e}")
        print("Gracefully transitioning to Local Fallback Mode (Exit Code 2).")
        sys.exit(2)

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/deepseek_helper.py \"<prompt>\" [\"<system_prompt>\"]")
        sys.exit(1)
        
    prompt = sys.argv[1]
    system_prompt = sys.argv[2] if len(sys.argv) > 2 else "You are a helpful assistant."
    
    answer = call_deepseek(prompt, system_prompt)
    print("\n=== DEEPSEEK RESPONSE ===")
    print(answer)

if __name__ == "__main__":
    main()
