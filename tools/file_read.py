import os

MAX_CHARS = 50_000

def file_read(path: str) -> str:
	'''
	Reads and returns the text content of a file at the given path,
	truncating output if it exceeds the MAX_CHARS character limit.

	Parameters:
		path: The filesystem path to the file to be read. Supports ~ expansion.

	Returns:
		The file's text content as a string, or an error message string if the
		file does not exist, is not a regular file, is not valid UTF-8, or
		cannot be accessed due to permission restrictions. If the content
		exceeds MAX_CHARS characters it is truncated and a notice is appended.
	'''
	path = os.path.expanduser(path)

	if not os.path.exists(path):
		return f"Error: file not found: {path}"

	if not os.path.isfile(path):
		return f"Error: path is not a file: {path}"

	try:
		with open(path, "r", encoding="utf-8") as f:
			content = f.read(MAX_CHARS + 1)

		if len(content) > MAX_CHARS:
			return content[:MAX_CHARS] + f"\n\n[... truncated at {MAX_CHARS} characters ...]"

		return content

	except UnicodeDecodeError:
		return f"Error: file is not valid UTF-8 (binary file?): {path}"

	except PermissionError:
		return f"Error: permission denied: {path}"
