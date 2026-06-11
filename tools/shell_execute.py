import subprocess


BLOCKED_COMMANDS: list[str] = ["rm -rf /", "mkfs", "dd if=", ":(){:|:&};:", "chmod -R 777 /"]
TIMEOUT_SECONDS = 30

def shell_execute(command: str) -> str:
	'''
	Runs a shell command and returns its combined stdout and stderr output.
	Commands matching entries in BLOCKED_COMMANDS are rejected for safety.
	Execution is automatically terminated if it exceeds TIMEOUT_SECONDS.

	Parameters:
		command: The shell command string to execute.

	Returns:
		A string containing the combined stdout and stderr of the command.
		Returns an error message string if the command is blocked, times out,
		or raises an unexpected exception. Returns "(no output)" if the command
		produces no output. A non-zero exit code is appended to the output.
	'''
	for blocked in BLOCKED_COMMANDS:

		if blocked in command:
			return f"Error: command blocked for safety: {command}"

	try:
		result = subprocess.run(
			command,
			shell=True,
			capture_output=True,
			text=True,
			timeout=TIMEOUT_SECONDS
		)
		output = ""

		if result.stdout:
			output += result.stdout

		if result.stderr:
			output += result.stderr

		if result.returncode != 0:
			output += f"\n[exit code: {result.returncode}]"

		return output.strip() or "(no output)"

	except subprocess.TimeoutExpired:
		return f"Error: command timed out after {TIMEOUT_SECONDS}s"

	except Exception as e:
		return f"Error running command: {e}"
