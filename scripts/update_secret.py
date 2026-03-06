"""
update_secret.py - Updates GitHub repository secrets via API
Called automatically by GitHub Actions to save updated tokens/topics
"""
import sys
import os
import requests
import base64
import json
from nacl import encoding, public  # pip install pynacl

def get_repo_public_key(repo, token):
    url = f"https://api.github.com/repos/{repo}/actions/secrets/public-key"
    r = requests.get(url, headers={"Authorization": f"token {token}",
                                    "Accept": "application/vnd.github.v3+json"})
    return r.json()

def encrypt_secret(public_key_str, secret_value):
    pk = public.PublicKey(public_key_str.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(pk)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def update_secret(repo, token, secret_name, secret_value):
    key_data = get_repo_public_key(repo, token)
    encrypted = encrypt_secret(key_data["key"], secret_value)
    url = f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}"
    r = requests.put(url, 
        headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
        json={"encrypted_value": encrypted, "key_id": key_data["key_id"]}
    )
    return r.status_code in [201, 204]

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python update_secret.py SECRET_NAME VALUE")
        sys.exit(1)

    secret_name = sys.argv[1]
    secret_value = sys.argv[2]
    repo = os.environ.get("REPO", "")
    gh_token = os.environ.get("GH_TOKEN", "")

    if not repo or not gh_token:
        print("Missing REPO or GH_TOKEN environment variable")
        sys.exit(0)  # Don't fail pipeline for this

    try:
        # Install pynacl if needed
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "pynacl", "--quiet"], check=False)
        from nacl import encoding, public

        success = update_secret(repo, gh_token, secret_name, secret_value)
        if success:
            print(f"✅ Secret {secret_name} updated!")
        else:
            print(f"⚠️  Secret {secret_name} update failed (non-critical)")
    except Exception as e:
        print(f"Secret update skipped: {e}")
        sys.exit(0)
