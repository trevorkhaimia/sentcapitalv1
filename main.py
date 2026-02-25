# llm_autonomous_python_only.py
import subprocess
import requests
import time
import re

API_KEY = "sk-f12a6d43d43841e8b7dd5fe40792ed07"  # Replace with your DeepSeek key

# Memory stores all previous Python code/functions
memory = []

def ask_llm(task_prompt):
    """
    Ask DeepSeek to generate Python code for a given task.
    LLM can include subprocess calls if system commands or installations are needed.
    """
    memory_context = ""
    if memory:
        memory_context = "\nPrevious Python code:\n" + "\n".join(memory)

    system_prompt = (
        "You are an autonomous Python code generator. "
        "Generate Python code to accomplish the user's task. "
        "You may use subprocess for shell commands or package installation. "
        "Include previous code if needed. "
        "Do NOT use Bash. "
        "Output only Python code.  real python code do not use , ```python or any sort of hyphens pure real  python code nothing else"
        "If you define functions, call them and print results automatically."
    )

    messages = [
        {"role": "system", "content": system_prompt + memory_context},
        {"role": "user", "content": task_prompt}
    ]

    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": "deepseek-coder", "messages": messages}
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[LLM Error]: {e}")
        return None

def run_code(code):
    """
    Execute Python code safely.
    Auto-call last defined function if not already called.
    """
    # Detect last function definition
    function_names = re.findall(r'def (\w+)\(', code)
    if function_names:
        last_fn = function_names[-1]
        if not re.search(rf'{last_fn}\s*\(', code):
            code += f"\nprint({last_fn}())"

    # Save to file and execute
    filename = "generated.py"
    with open(filename, "w") as f:
        f.write(code)

    try:
        result = subprocess.run(
            ["python3", filename],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "", "[Execution Error]: Script timed out."

def main():
    print("Autonomous Python LLM Agent with Memory & Subprocess — type 'exit' to quit\n")
    while True:
        task = input("Enter a task: ")
        if task.lower() == "exit":
            break

        code = ask_llm(task)
        if not code:
            print("[LLM returned no code]")
            continue

        # Store code in memory
        memory.append(code)

        print("\n[Generated Code]:\n", code)

        stdout, stderr = run_code(code)
        print("\n[Execution Output]:")
        print(stdout)
        if stderr:
            print("\n[Execution Errors]:")
            print(stderr)

        print("\n" + "="*60 + "\n")
        time.sleep(0.3)

if __name__ == "__main__":
    main()