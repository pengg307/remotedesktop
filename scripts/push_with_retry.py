import subprocess
import time
import sys
import os

"""
Git Push with Auto-Retry Script (Python)
For unstable network connections (China -> GitHub)
"""

def push_with_retry(repo_dir=".", max_retries=10, retry_delay=10):
    print("=" * 50)
    print("Git Push Auto-Retry Script (Python)")
    print("=" * 50)
    print(f"Repository: {repo_dir}")
    print(f"Max retries: {max_retries}")
    print(f"Retry delay: {retry_delay}s")
    print()
    
    os.chdir(repo_dir)
    
    # Check if there are changes to push
    print("Checking git status...")
    result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
    print(result.stdout)
    print()
    
    # Try to push with retry logic
    for i in range(1, max_retries + 1):
        print(f"[{i}/{max_retries}] Attempting to push...")
        
        result = subprocess.run(["git", "push", "origin", "main"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print()
            print("=" * 50)
            print("✓ Push successful!")
            print("=" * 50)
            return True
        
        # Check if error is network-related
        if any(keyword in result.stderr.lower() for keyword in ["connection", "timeout", "reset", "failed"]):
            print("⚠ Network error detected")
        
        if i < max_retries:
            print(f"Waiting {retry_delay}s before retry...")
            time.sleep(retry_delay)
    
    print()
    print("=" * 50)
    print("✗ Failed after {} attempts".format(max_retries))
    print("=" * 50)
    print()
    print("Suggestions:")
    print("1. Check your network connection")
    print("2. Try using a VPN/proxy")
    print("3. Wait a few minutes and try again")
    print("4. Consider using SSH instead of HTTPS")
    return False

if __name__ == "__main__":
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    success = push_with_retry(repo_dir)
    sys.exit(0 if success else 1)
