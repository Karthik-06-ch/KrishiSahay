import requests
import json
import sys

def pull_model(model_name="llava"):
    url = "http://localhost:11434/api/pull"
    payload = {"name": model_name, "stream": True}
    
    print(f"Attempting to pull model '{model_name}' via API...")
    try:
        with requests.post(url, json=payload, stream=True, timeout=300) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    decoded = json.loads(line.decode('utf-8'))
                    status = decoded.get("status", "")
                    if "downloading" in status or "pulling" in status:
                        # Print progress every now and then or just status
                        total = decoded.get("total")
                        completed = decoded.get("completed")
                        if total and completed:
                            percent = (completed / total) * 100
                            sys.stdout.write(f"\r{status}: {percent:.1f}%")
                        else:
                            sys.stdout.write(f"\r{status}")
                    else:
                        print(f"\n{status}")
                        
        print(f"\nSuccessfully pulled {model_name}!")
    except Exception as e:
        print(f"\nError pulling model: {e}")

if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "llava"
    pull_model(model)
