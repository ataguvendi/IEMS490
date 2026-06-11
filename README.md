# Coding Agent

This has two deployment modes: a **local agent** powered by Ollama/DeepSeek and a **cloud agent** powered by Anthropic's Claude API. Both agents use the same tool suite, skill system, and interactive interface.

---

## Setup

### Prerequisites

- Python 3.10+
- For the local agent: [Ollama](https://ollama.com) installed and running
- For the cloud agent: an [Anthropic API key](https://console.anthropic.com)

### Install dependencies

```bash
pip install anthropic
```

The local agent has no pip dependencies — it speaks to the Ollama REST API directly.

### Pull the local model (local agent only)

```bash
ollama pull deepseek-r1:8b
ollama serve
```
Please note that you can also use any other model in Ollama just fine - refrain from models that are too slow.

### Configure the cloud agent

Provide your Anthropic API key in one of two ways:

```bash
# Option A — environment variable
export ANTHROPIC_API_KEY=sk-ant-...

# Option B — text file in the project, simply make the first line your API key.
api_key.txt
```

### Run

```bash
# Local agent
python agent.py

# Cloud agent
python agent_cloud.py
```

---

## Usage

Describe a task in plain English or invoke a built-in skill:

```
> explain the Calculator class in tests/test02.py
> /review tests/test03.py
> /explain tests/test01.py
> /format tests/test02.py
> /help
```

Type `exit` or `quit` to close the session.

---

## Tools

All tools are available to both agents. Tools that can modify the system or execute code require explicit user confirmation before running.

---

## Skills

Skills are pre-built prompt templates stored in `skills/` as JSON files. Invoke them with a leading `/` followed by the skill name and any arguments.

### `/explain <path>`

Reads a file and produces a plain-English walkthrough covering functions, classes, control flow, and potential gotchas. Aimed at readers who did not write the code.

### `/review <path>`

Reviews code for bugs, style issues, and improvement opportunities. Writes a structured report to `suggestions.txt` without modifying the source file. Sections: *Bugs*, *Style*, *Improvements*.

### `/format <path>`

Annotates a file in-place with type hints, header comments, and consistent formatting (single tabs, multi-line dicts, proper spacing). Does **not** change logic.

---

## Project Structure

```
coding_agent/
├── agent.py
├── agent_cloud.py
├── tools/
│   ├── file_read.py
│   ├── file_write.py
│   ├── shell_execute.py
│   └── search.py
├── skills/
│   ├── loader.py
│   ├── explain.json
│   ├── review.json
│   └── format.json
└── tests/
    ├── test01.py
    ├── test02.py
    └── test03.py
```

---

## Environment Variables

| Variable | Agent | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Cloud | — |
| `AGENT_MODEL` | Cloud | `claude-sonnet-4-6` |
