import sys
sys.path.insert(0, '/Users/liuzimin/.hermes/hermes-agent')

import base64
from pathlib import Path
import urllib.request
import json

# Load token from credential pool
from agent.credential_pool import load_pool
pool = load_pool('minimax-cn')
token = pool.entries()[0].access_token
print(f"Token: {token[:15]}...")

# Read image
img_path = Path('/Users/liuzimin/.hermes/image_cache/img_f6c9f9c6afb7.jpg')
img_bytes = img_path.read_bytes()
img_b64 = base64.b64encode(img_bytes).decode('utf-8')
print(f"Image: {len(img_bytes)} bytes -> base64 {len(img_b64)} chars")

# Try different MiniMax vision endpoints
endpoints = [
    ("https://api.minimaxi.com/v1/images/understand", "MiniMax-M2.7-Granite"),
    ("https://api.minimaxi.com/v1/multi_modality", "MiniMax-M2.7-Granite"),
    ("https://api.minimaxi.com/v1/text/understandvision", "MiniMax-Vision"),
]

for url, model in endpoints:
    print(f"\n=== Trying {url} with model {model} ===")
    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                {"type": "text", "text": "这张图片里有什么？请详细描述。"}
            ]
        }]
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url, data=data,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            print(f"SUCCESS: {json.dumps(result, ensure_ascii=False)[:500]}")
            break
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'read'):
            try:
                body = e.read()
                print(f"Response body: {body.decode('utf-8')[:300]}")
            except:
                pass
