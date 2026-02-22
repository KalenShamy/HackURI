import json
import re
import traceback
from google import genai
from google.genai import errors as genai_errors
from django.conf import settings

# Try models in order; fall back if a model is unavailable or quota-exhausted.
_MODELS = ['gemini-2.5-pro', 'gemini-2.0-flash']


def _call_gemini(client: genai.Client, prompt: str) -> str | None:
    """Try each model in _MODELS until one succeeds. Returns response text or None."""
    for model in _MODELS:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            try:
                return response.text.strip()
            except ValueError:
                print(f'[ERROR] Gemini response blocked or empty (model={model})')
                return None
        except genai_errors.ClientError as e:
            if e.status_code in (429, 503):
                print(f'[WARNING] Gemini model {model} unavailable ({e.status_code}), trying next...')
                continue
            raise
    print(f'[ERROR] All Gemini models exhausted: {_MODELS}')
    return None


def generate_features_and_tasks(description: str) -> list[dict]:
    """Use Gemini to parse a free-text description into features and tasks.

    Returns a list of dicts with shape:
        [{"name": str, "description": str, "tasks": [{"title": str, "description": str, "priority": "low"|"medium"|"high"}]}]
    Returns an empty list if Gemini is unavailable or parsing fails.
    """
    if not settings.GEMINI_API_KEY:
        return []

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = (
        'You are a project planning assistant. Given a product or feature description, '
        'break it down into a structured list of features and their tasks.\n\n'
        f'Description:\n{description}\n\n'
        'Return a JSON array where each element represents a feature with its tasks. '
        'Each feature object must have:\n'
        '  - "name": short feature name (string)\n'
        '  - "description": brief feature description (string)\n'
        '  - "tasks": array of task objects, each with:\n'
        '      - "title": concise task title (string)\n'
        '      - "description": what needs to be done (string)\n'
        '      - "priority": one of "low", "medium", or "high" (string)\n\n'
        'Respond with ONLY the JSON array, no other text.'
    )

    text = _call_gemini(client, prompt)
    if text is None:
        return []

    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)

    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except (json.JSONDecodeError, TypeError):
        print(f'[ERROR] Failed to parse Gemini JSON for generate_features_and_tasks. Raw: {text[:200]}')
        traceback.print_exc()

    return []


def generate_features_from_repo(repo_summary: str) -> list[dict]:
    """Use Gemini to generate features and tasks from a repository summary.

    repo_summary: concatenated string of README, language stats, and dep files.

    Returns a list of dicts with shape:
        [{"name": str, "description": str, "tasks": [{"title": str, "description": str, "priority": "low"|"medium"|"high"}]}]
    Returns an empty list if Gemini is unavailable or parsing fails.
    """
    if not settings.GEMINI_API_KEY:
        return []

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = (
        'You are analyzing a GitHub repository. Based on the provided repository files '
        '(README, language info, dependency files), generate features and tasks that represent '
        'the main areas of work or improvement for this project.\n\n'
        f'Repository content:\n{repo_summary}\n\n'
        'Return a JSON array where each element represents a feature with its tasks. '
        'Each feature object must have:\n'
        '  - "name": short feature name (string)\n'
        '  - "description": brief feature description (string)\n'
        '  - "tasks": array of task objects, each with:\n'
        '      - "title": concise task title (string)\n'
        '      - "description": what needs to be done (string)\n'
        '      - "priority": one of "low", "medium", or "high" (string)\n\n'
        'Respond with ONLY the JSON array, no other text.'
    )

    text = _call_gemini(client, prompt)
    if text is None:
        return []

    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)

    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except (json.JSONDecodeError, TypeError):
        print(f'[ERROR] Failed to parse Gemini JSON for generate_features_from_repo. Raw: {text[:200]}')
        traceback.print_exc()

    return []


def analyze_commits(commit_messages: list[str], open_tasks: list[str]) -> list[str]:
    """Use Gemini to determine which open tasks were completed by the given commits.

    Returns a list of task titles that Gemini considers completed.
    """
    if not settings.GEMINI_API_KEY:
        return []

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = (
        "You are an assistant that analyzes git commit messages to detect task completion.\n\n"
        f"Open tasks:\n{json.dumps(open_tasks)}\n\n"
        f"Commit messages:\n{json.dumps(commit_messages)}\n\n"
        "Return a JSON array of task titles (from the open tasks list) that these commits indicate "
        "are completed. Only include tasks you are confident were addressed. "
        "Return an empty array if none match. Respond with ONLY the JSON array, no other text."
    )

    text = _call_gemini(client, prompt)
    if text is None:
        return []

    json_match = re.search(r'\[.*\]', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)

    try:
        result = json.loads(text)
        if isinstance(result, list):
            return [t for t in result if t in open_tasks]
    except (json.JSONDecodeError, TypeError):
        print(f'[ERROR] Failed to parse Gemini JSON for analyze_commits. Raw: {text[:200]}')
        traceback.print_exc()

    return []
