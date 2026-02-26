import subprocess
import sys
import os
import time
import requests
import traceback
from datetime import datetime

# ======================
# CONFIG
# ======================

OPENROUTER_API_KEY = "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"

MODEL = "anthropic/claude-3.5-sonnet"

MAX_FIX_ATTEMPTS = 50

MEMORY_FILE = "agent_memory.txt"

WORKSPACE = "workspace"

os.makedirs(WORKSPACE, exist_ok=True)

# ======================
# MEMORY SYSTEM
# ======================

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_memory(entry):
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now()}]\n{entry}\n")

# ======================
# LLM CALL
# ======================

def call_llm(system_prompt, user_prompt):

    memory = load_memory()

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt + "\n\nMemory:\n" + memory
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "temperature": 0
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=120
    )

    result = response.json()

    try:
        return result["choices"][0]["message"]["content"]
    except:
        print(result)
        return ""

# ======================
# EXECUTOR
# ======================

def run_python(code):

    path = os.path.join(WORKSPACE, "generated.py")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    try:

        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=300
        )

        output = result.stdout + result.stderr

        success = result.returncode == 0

        return success, output

    except Exception as e:

        return False, traceback.format_exc()

# ======================
# FILE CREATION
# ======================

def extract_and_create_files(code):

    lines = code.splitlines()

    current_file = None
    buffer = []

    for line in lines:

        if line.startswith("FILE:"):
            if current_file:
                save_file(current_file, "\n".join(buffer))
                buffer = []

            current_file = line.replace("FILE:", "").strip()

        else:
            buffer.append(line)

    if current_file:
        save_file(current_file, "\n".join(buffer))

def save_file(path, content):

    full_path = os.path.join(WORKSPACE, path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Created file: {path}")

# ======================
# PROMPTS
# ======================

GENERATOR_PROMPT = """
You are an autonomous Python engineer.

Rules:

Do not use markdown
Do not use code fences
Do not explain anything
Return only executable Python code

You may create multiple files using:

FILE: filename.py

Code must:

auto install packages
fix errors automatically when rerun
complete the task fully


CRITICAL OUTPUT RULES:

1. Output ONLY raw executable Python code
2. Do NOT use markdown
3. Do NOT use code fences
4. Do NOT write ```python
5. Do NOT write ```
6. Do NOT explain anything
7. Do NOT write comments unless they are valid Python comments
8. Do NOT write FILE:
9. Do NOT write requirements.txt
10. Do NOT write shell commands
11. Do NOT output anything except valid Python code

DEPENDENCY RULES:

You MUST install dependencies using Python subprocess like this:

import subprocess, sys

def install(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

install("package_name")

Never use pip outside Python.

COLUMN HANDLING RULES:

When using yfinance, ALWAYS flatten MultiIndex columns using:

if hasattr(data.columns, 'levels'):
    data.columns = data.columns.get_level_values(0)

Then use Close column.

ERROR PREVENTION:

Code must run successfully on first execution.

Output ONLY Python code. 
or if python doesnt work then use bash commands and run them 
"""

FIX_PROMPT = """
Fix this Python code.
 do no tuse ‘‘‘ python or any symbols just pure python code nothing else
Return full corrected code.

Do not explain.

Broken code:
"""

SEARCH_PROMPT = """
The previous fixes failed.

Analyze deeply and generate completely new working code.

Install missing packages automatically.

Return only Python code.
"""

# ======================
# CORE AUTONOMOUS LOOP
# ======================

def autonomous_task(task):

    print("\nGenerating code...\n")

    code = call_llm(GENERATOR_PROMPT, task)

    save_memory(f"TASK:\n{task}\nCODE:\n{code}")

    extract_and_create_files(code)

    attempt = 0

    while True:

        print(f"\n=== Attempt {attempt+1} ===\n")

        success, output = run_python(code)

        print(output)

        save_memory(output)

        if success:

            print("\nSUCCESS\n")

            return

        print("\nFixing autonomously...\n")

        fixed = call_llm(FIX_PROMPT, code + "\nERROR:\n" + output)

        extract_and_create_files(fixed)

        success2, output2 = run_python(fixed)

        print(output2)

        save_memory(output2)

        if success2:

            print("\nSUCCESS AFTER FIX\n")

            return

        print("\nDeep search fix...\n")

        code = call_llm(SEARCH_PROMPT, fixed + "\nERROR:\n" + output2)

        extract_and_create_files(code)

        attempt += 1

        time.sleep(1)

# ======================
# CLI
# ======================

def main():

    print("\nAutonomous God-Mode Agent Ready\n")

    while True:

        task = input("\nEnter task: ")

        if task.lower() == "exit":
            break

        autonomous_task(task)

if __name__ == "__main__":
    main()