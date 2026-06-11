import os
import json
from typing import Any

SKILLS_DIR = os.path.join(os.path.dirname(__file__))


def load_skills() -> dict[str, dict]:
	'''
	Scans SKILLS_DIR for every .json file, parses each one, and
	collects the results into a dictionary keyed by skill name.
	Files that cannot be parsed are skipped with a warning printed
	to stdout so the rest of the skills are still available.

	Parameters:
	    None

	Returns:
	    A dictionary mapping each skill's "name" field (str) to its
	    full parsed skill object (dict).
	'''

	skills: dict[str, dict] = {}

	for filename in os.listdir(SKILLS_DIR):

		if filename.endswith(".json"):
			skill_path = os.path.join(SKILLS_DIR, filename)

			try:

				with open(skill_path, "r", encoding="utf-8") as f:
					skill = json.load(f)

				name = skill.get("name")

				if name:
					skills[name] = skill

			except Exception as e:
				print(
					f"Warning: could not load skill {filename}: {e}"
				)

	return skills


def run_skill(skill: dict[str, Any], user_args: str = "") -> str:
	'''
	Fills in the prompt template stored inside a skill object with
	the caller-supplied arguments and returns the resulting string.
	The placeholder token "{{args}}" inside the template is replaced
	with user_args, and any leading/trailing whitespace is removed.

	Parameters:
	    skill     - A skill object (dict) that optionally contains a
	               "prompt_template" key whose value is the template
	               string to be rendered.
	    user_args - The string that will be substituted for every
	               occurrence of "{{args}}" in the template.
	               Defaults to an empty string when not provided.

	Returns:
	    The rendered prompt string with "{{args}}" replaced by
	    user_args and surrounding whitespace stripped.
	'''

	template = skill.get("prompt_template", "")

	return template.replace("{{args}}", user_args).strip()
