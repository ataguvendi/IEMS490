import subprocess

TIMEOUT_SECONDS = 30
INCLUDE_GLOBS: list[str] = ["*.py", "*.txt", "*.md"]


def _run(cmd: list[str]) -> tuple[int, str]:
	'''
	Executes a subprocess command and returns its exit code and combined output.

	Parameters:
		cmd: A list of strings representing the command and its arguments
		     to be passed to subprocess.run.

	Returns:
		A tuple of (return_code, output) where return_code is the integer exit
		code of the process and output is the combined stdout and stderr as a
		stripped string. Returns (-1, error_message) if the command times out
		or raises an unexpected exception.
	'''
	try:
		result = subprocess.run(
			cmd,
			capture_output=True,
			text=True,
			timeout=TIMEOUT_SECONDS
		)
		return result.returncode, ((result.stdout or "") + (result.stderr or "")).strip()

	except subprocess.TimeoutExpired:
		return -1, f"Error: command timed out after {TIMEOUT_SECONDS}s"

	except Exception as e:
		return -1, f"Error running command: {e}"


def search(pattern: str, path: str = ".") -> str:
	'''
	Searches file contents for a pattern (grep) within a directory, and also
	reports filename matches using find. Only files matching INCLUDE_GLOBS
	extensions are scanned for content.

	Parameters:
		pattern: The keyword or regex string to search for in file contents
		         and to match against filenames.
		path:    The directory path to search within. Defaults to the current
		         directory.

	Returns:
		A formatted string containing labelled sections for content matches
		and/or filename matches. Returns "No matches found." if neither
		search produces results.
	'''
	grep_cmd: list[str] = ["grep", "-rn"]

	for glob in INCLUDE_GLOBS:
		grep_cmd.append(f"--include={glob}")

	grep_cmd += ["-e", pattern, "--", path]

	find_cmd: list[str] = ["find", path, "-name", f"*{pattern}*", "-type", "f"]

	parts: list[str] = []

	grep_code, grep_out = _run(grep_cmd)

	if grep_code == 0 and grep_out:
		parts.append(f"=== Content matches ===\n{grep_out}")

	elif grep_code not in (0, 1):
		parts.append(f"=== Content search error ===\n{grep_out}")

	find_code, find_out = _run(find_cmd)

	if find_code == 0 and find_out:
		parts.append(f"=== Filename matches ===\n{find_out}")

	return "\n\n".join(parts) if parts else "No matches found."
