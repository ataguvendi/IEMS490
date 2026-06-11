import json
import os
import sys
from anthropic import Anthropic
from tools.file_read import file_read
from tools.file_write import file_write
from tools.shell_execute import shell_execute
from tools.search import search
from skills.loader import load_skills, run_skill


MODEL = os.environ.get("AGENT_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 4096
MAX_STEPS = 15

client = None

TOOLS = {
    "file_read":      file_read,
    "file_write":     file_write,
    "shell_execute":  shell_execute,
    "search":         search,
}

DANGEROUS_TOOLS = {"shell_execute"} 
TOOL_DEFINITIONS = [
    {
        "name": "file_read",
        "description": "Read and return the contents of a file at the given path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path of the file to read."},
            },
            "required": ["path"],
        },
    },
    {
        "name": "file_write",
        "description": "Write content to a file, creating parent directories as needed. Overwrites existing files.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path of the file to write."},
                "content": {"type": "string", "description": "Full content to write to the file."},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "shell_execute",
        "description": "Run a shell command and return combined stdout/stderr. Times out after 30 seconds. Requires user confirmation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to run."},
            },
            "required": ["command"],
        },
    },
    {
        "name": "search",
        "description": "Search file contents for a pattern (grep) within a directory, and also report filename matches.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Keyword or regex to search for."},
                "path": {"type": "string", "description": "Directory to search in (default: current directory)."},
            },
            "required": ["pattern"],
        },
    },
]

SYSTEM_PROMPT = """You are an expert coding agent. You help users complete
software engineering tasks by reasoning step-by-step and using tools.

Rules:
- Use one tool at a time when possible.
- After each tool result, decide whether you need another tool or are done.
- Be concise. Do not repeat yourself.
- Always read file contents and avoid making assumptions about them.
- When the task is complete, reply with your final answer in plain text
  without requesting any more tools.
"""


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


def run_agent(user_message: str):
    messages = [{"role": "user", "content": user_message}]

    print(f"\nTask: {user_message}\n")

    for step in range(MAX_STEPS):
        print(f"\nStep {step + 1}")

        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )
        text_parts = [b.text for b in response.content if b.type == "text"]
        if text_parts:
            print(f"Agent: {' '.join(text_parts)}")
        if response.stop_reason != "tool_use":
            print("\nTask complete.")
            return "\n".join(text_parts)

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"\nCalling tool: {block.name}({block.input})")
            result = dispatch(block.name, dict(block.input))
            print(f"Result: {result[:500]}{'...' if len(result) > 500 else ''}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    print("\nMax steps reached.")
    return "Max steps reached without completing the task."


def load_api_key(filepath: str = "api_key.txt") -> str | None:
    try:
        with open(filepath) as f:
            return f.read().strip() or None
    except FileNotFoundError:
        print(f"Error: API key file '{filepath}' not found.")
        return None


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY") or load_api_key()
    if not api_key:
        print("No API key found. Set ANTHROPIC_API_KEY or create api_key.txt.")
        return
    os.environ["ANTHROPIC_API_KEY"] = api_key
    global client
    client = Anthropic(api_key=api_key)
    skills = load_skills()
    print(f"Coding Agent ({MODEL} via Anthropic API)")
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