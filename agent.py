import json
import re
import sys
import urllib.request
from tools.file_read import file_read
from tools.file_write import file_write
from tools.shell_execute import shell_execute
from tools.search import search
from skills.loader import load_skills, run_skill


# This project uses ollama to run DeepSeek R1:8b locally. This makes it so that
# the coding agent can be run on edge devices & more secure workflows.

def call_ollama(messages: list[dict], model: str = "deepseek-r1:8b") -> str:
    """
    Send messages to Ollama and return the assistant text.
    """
    payload = json.dumps({"model": model, "messages": messages, "stream": False}).encode()

    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
    return data["message"]["content"]


def strip_thinking(text: str) -> str:
    """
    Removes DeepSeek R1 <think>...</think> blocks
    """
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


TOOLS = {
    "file_read":      file_read,
    "file_write":     file_write,
    "shell_execute":  shell_execute,
    "search":         search,
}

DANGEROUS_TOOLS = {"shell_execute"}  # agent needs user's consent before running these.
#!Note: A dangerous tool needs to be listed both here and in the tools section.

TOOL_SCHEMAS = """
You have access to the following tools. When you want to use a tool, output
ONLY a JSON block (no other text) wrapped in triple backticks like this:

```json
{"tool": "<tool_name>", "args": {<arguments>}}
```

Available tools:

- file_read    : {"tool": "file_read", "args": {"path": "<file_path>"}}
- file_write   : {"tool": "file_write", "args": {"path": "<file_path>", "content": "<content>"}}
- shell_execute: {"tool": "shell_execute", "args": {"command": "<shell_command>"}}
- search       : {"tool": "search", "args": {"pattern": "<keyword_or_regex>", "path": "<directory>"}}

When you have finished the task and do NOT need another tool call, write your
final answer as plain text (no JSON block).
"""

SYSTEM_PROMPT = f"""You are an expert coding agent. You help users complete
software engineering tasks by reasoning step-by-step and using tools.

{TOOL_SCHEMAS}

Rules:
- Use one tool at a time.
- After each tool result, decide whether you need another tool or are done.
- Be concise. Do not repeat yourself.
- Always read file contents and avoid making assumptions about them.
"""


def parse_tool_call(text: str) -> dict | None:
    """
    Extracts a JSON tool call from the model's response, if present.

    FIX: the old regex used a non-greedy `(\\{.*?\\})`, which stopped at the
    FIRST closing brace. Any tool call with nested braces (e.g. file_write
    whose content contains a dict, JSON, or C-style code) was truncated and
    failed to parse, causing the agent to mistake a tool call for a final
    answer. We now capture everything up to the closing fence and let
    json.loads validate it, which handles arbitrary nesting.
    """
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if not match:
        return None
    try:
        obj = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    if isinstance(obj, dict) and "tool" in obj:
        return obj
    return None


def confirm_dangerous(tool_name: str, args: dict) -> bool:
    """
    Asks user to consent before running a dangerous tool.
    """
    print(f"\nDANGEROUS ACTION: {tool_name}")
    print(f"   Args: {json.dumps(args, indent=2)}")
    answer = input("   Proceed? [y/N] ").strip().lower()
    return answer == "y"


def dispatch(tool_name: str, args: dict) -> str:
    if tool_name not in TOOLS:
        return f"Error: unknown tool '{tool_name}'"

    if tool_name in DANGEROUS_TOOLS:
        if not confirm_dangerous(tool_name, args):
            return "Action cancelled by user."

    try:
        return TOOLS[tool_name](**args)
    except TypeError as e:
        return f"Error: bad arguments for {tool_name}: {e}"
    except Exception as e:
        return f"Error running {tool_name}: {e}"


MAX_STEPS = 15

def run_agent(user_message: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    print('\n')
    print(f"Task: {user_message}")
    print()

    for step in range(MAX_STEPS):
        print(f"\nStep {step + 1}")

        raw = call_ollama(messages)
        response = strip_thinking(raw)
        print(f"Agent: {response}")

        tool_call = parse_tool_call(response)

        if tool_call is None:
            print("\nTask complete.")
            return response

        tool_name = tool_call.get("tool", "")
        args = tool_call.get("args", {})
        print(f"\nCalling tool: {tool_name}({args})")

        result = dispatch(tool_name, args)
        print(f"Result: {result[:500]}{'...' if len(result) > 500 else ''}")

        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": f"Tool result:\n{result}"})

    print("\nMax steps reached.")
    return "Max steps reached without completing the task."


def main():
    skills = load_skills()

    print("Coding Agent (DeepSeek R1 via Ollama)")
    print("Type /help for available skills, or just describe your task.")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break
        if user_input == "/help":
            print("Available skills:")
            for name, skill in skills.items():
                print(f"  /{name} — {skill['description']}")
            continue
        if user_input.startswith("/"):
            parts = user_input[1:].split(None, 1)
            skill_name = parts[0]
            skill_args = parts[1] if len(parts) > 1 else ""
            if skill_name in skills:
                prompt = run_skill(skills[skill_name], skill_args)
                run_agent(prompt)
                continue
            else:
                print(f"Unknown skill '/{skill_name}'. Type /help to list skills.")
                continue
        run_agent(user_input)


if __name__ == "__main__":
    main()