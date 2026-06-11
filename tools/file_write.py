import os


PROTECTED_PATHS: set[str] = {"/etc", "/usr", "/bin", "/sbin", "/boot", "/sys", "/proc"}


def file_write(path: str, content: str) -> str:
	'''
	Writes content to a file at the given path, creating any missing parent
	directories automatically. Refuses to write to a set of protected
	system paths.

	Parameters:
		path:    The destination filesystem path for the file. Supports ~ expansion.
		content: The text content to write to the file.

	Returns:
		A confirmation string reporting how many characters were written, or an
		error message string if the path is protected, permission is denied, or
		any other exception occurs during the write operation.
	'''
	path = os.path.expanduser(path)
	abs_path = os.path.realpath(os.path.abspath(path))

	for protected in PROTECTED_PATHS:

		if abs_path == protected or abs_path.startswith(protected + os.sep):
			return f"Error: refusing to write to protected path: {path}"

	try:
		parent = os.path.dirname(abs_path)

		if parent:
			os.makedirs(parent, exist_ok=True)

		with open(abs_path, "w", encoding="utf-8") as f:
			f.write(content)

		return f"OK: wrote {len(content)} characters to {path}"

	except PermissionError:
		return f"Error: permission denied: {path}"

	except Exception as e:
		return f"Error writing file: {e}"
