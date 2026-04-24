import json
import re
import time
import traceback
from google import genai
from google.genai import errors as genai_errors
from django.conf import settings

# Try models in order; fall back if a model is unavailable or quota-exhausted.
_MODELS = ['gemini-3.0-flash', 'gemini-2.5-flash', 'gemma-4-31b-it']

_RETRYABLE_STATUS_CODES = {408, 409, 429, 500, 502, 503, 504}
_MODEL_UNAVAILABLE_STATUS_CODES = {400, 403, 404}
_MODEL_UNAVAILABLE_HINTS = (
    'model not found',
    'does not exist',
    'unsupported model',
    'not available',
    'not enabled',
    'permission denied',
    'access denied',
)
_MAX_ATTEMPTS_PER_MODEL = 2
_BACKOFF_SECONDS = 0.7


def _is_retryable_error(error: genai_errors.ClientError) -> bool:
    return getattr(error, 'status_code', None) in _RETRYABLE_STATUS_CODES


def _is_model_unavailable_error(error: genai_errors.ClientError) -> bool:
    status = getattr(error, 'status_code', None)
    if status not in _MODEL_UNAVAILABLE_STATUS_CODES:
        return False
    message = str(error).lower()
    return any(hint in message for hint in _MODEL_UNAVAILABLE_HINTS)


def _parse_json_array(text: str) -> list | None:
    if not text:
        return None

    cleaned = text.strip()

    # First try direct parse.
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # Fallback: attempt to extract a JSON array from mixed output.
    match = re.search(r'\[[\s\S]*\]', cleaned)
    if not match:
        return None

    try:
        parsed = json.loads(match.group(0))
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        return None

    return None


def _call_gemini(client: genai.Client, prompt: str) -> str | None:
    """Try each model in _MODELS until one succeeds. Returns response text or None."""
    last_error: Exception | None = None

    for model in _MODELS:
        for attempt in range(1, _MAX_ATTEMPTS_PER_MODEL + 1):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                text = (getattr(response, 'text', None) or '').strip()
                if text:
                    return text

                print(f'[WARNING] Empty Gemini response (model={model}, attempt={attempt}); trying next model')
                break

            except genai_errors.ClientError as e:
                last_error = e

                if _is_retryable_error(e) and attempt < _MAX_ATTEMPTS_PER_MODEL:
                    delay = _BACKOFF_SECONDS * attempt
                    print(
                        f'[WARNING] Retryable Gemini error (model={model}, status={e.status_code}); '
                        f'retrying in {delay:.1f}s'
                    )
                    time.sleep(delay)
                    continue

                if _is_retryable_error(e) or _is_model_unavailable_error(e):
                    print(
                        f'[WARNING] Gemini fallback (model={model}, status={e.status_code}); '
                        'trying next model'
                    )
                    break

                raise

            except (TimeoutError, ConnectionError) as e:
                last_error = e
                if attempt < _MAX_ATTEMPTS_PER_MODEL:
                    delay = _BACKOFF_SECONDS * attempt
                    print(f'[WARNING] Network error (model={model}); retrying in {delay:.1f}s')
                    time.sleep(delay)
                    continue
                print(f'[WARNING] Network error persisted (model={model}); trying next model')
                break

            except Exception as e:
                # Keep service resilient: if one model path fails unexpectedly, try next model.
                last_error = e
                print(f'[WARNING] Unexpected Gemini error for model={model}: {e}; trying next model')
                break

    print(f'[ERROR] All Gemini models exhausted: {_MODELS}. last_error={last_error}')
    return None


def _build_features_from_description_prompt(description: str) -> str:
    return (
        'You are a senior software planning assistant.\n'
        'Return only valid JSON. No markdown, no commentary, no code fences.\n\n'
        'Output schema:\n'
        '[\n'
        '  {\n'
        '    "name": string,\n'
        '    "description": string,\n'
        '    "tasks": [\n'
        '      {\n'
        '        "title": string,\n'
        '        "description": string,\n'
        '        "priority": "low" | "medium" | "high"\n'
        '      }\n'
        '    ]\n'
        '  }\n'
        ']\n\n'
        'Rules:\n'
        '- Create 2 to 6 features.\n'
        '- Create 3 to 8 tasks per feature.\n'
        '- Use specific, actionable task titles.\n'
        '- No duplicate feature names.\n'
        '- No duplicate task titles within the same feature.\n'
        '- Keep descriptions concise and implementation-oriented.\n'
        '- If details are missing, make reasonable assumptions.\n'
        '- If input is too vague, return an empty array.\n\n'
        f'INPUT_DESCRIPTION:\n{description}'
    )


def _build_features_from_repo_prompt(repo_summary: str) -> str:
    return (
        'You are a senior engineer creating a practical backlog from repository context.\n'
        'Return only valid JSON. No markdown, no commentary, no code fences.\n\n'
        'Output schema:\n'
        '[\n'
        '  {\n'
        '    "name": string,\n'
        '    "description": string,\n'
        '    "tasks": [\n'
        '      {\n'
        '        "title": string,\n'
        '        "description": string,\n'
        '        "priority": "low" | "medium" | "high"\n'
        '      }\n'
        '    ]\n'
        '  }\n'
        ']\n\n'
        'Rules:\n'
        '- Focus on realistic, near-term engineering work.\n'
        '- Prefer concrete improvements over speculative rewrites.\n'
        '- Include architecture, quality, testing, and developer-experience tasks when justified.\n'
        '- No duplicate feature names.\n'
        '- No duplicate task titles within the same feature.\n'
        '- Keep tasks atomic and implementable.\n'
        '- If repository context is insufficient, return an empty array.\n\n'
        f'REPOSITORY_CONTEXT:\n{repo_summary}'
    )


def _build_analyze_commits_prompt(commit_messages: list[str], open_tasks: list[str]) -> str:
    return (
        'You are a conservative release manager.\n'
        'Goal: identify which open tasks are definitely completed by the commit messages.\n'
        'Return only a JSON array of task titles.\n'
        'Each returned title must exactly match one title from OPEN_TASKS.\n\n'
        'Decision rules:\n'
        '- Precision over recall.\n'
        '- Include a task only when completion is explicit or strongly evidenced.\n'
        '- Do not infer completion from vague messages like "cleanup", "wip", or "refactor" alone.\n'
        '- Never invent or paraphrase titles.\n'
        '- If uncertain, exclude the task.\n'
        '- If none are clearly complete, return [].\n\n'
        f'OPEN_TASKS:\n{json.dumps(open_tasks, ensure_ascii=False)}\n\n'
        f'COMMIT_MESSAGES:\n{json.dumps(commit_messages, ensure_ascii=False)}'
    )


def generate_features_and_tasks(description: str) -> list[dict]:
    """Use Gemini to parse a free-text description into features and tasks."""
    if not settings.GEMINI_API_KEY:
        return []

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    prompt = _build_features_from_description_prompt(description)

    text = _call_gemini(client, prompt)
    if text is None:
        return []

    parsed = _parse_json_array(text)
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]

    print(f'[ERROR] Failed to parse Gemini JSON for generate_features_and_tasks. Raw: {text[:200]}')
    return []


def generate_features_from_repo(repo_summary: str) -> list[dict]:
    """Use Gemini to generate features and tasks from a repository summary."""
    if not settings.GEMINI_API_KEY:
        return []

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    prompt = _build_features_from_repo_prompt(repo_summary)

    text = _call_gemini(client, prompt)
    if text is None:
        return []

    parsed = _parse_json_array(text)
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]

    print(f'[ERROR] Failed to parse Gemini JSON for generate_features_from_repo. Raw: {text[:200]}')
    return []


def analyze_commits(commit_messages: list[str], open_tasks: list[str]) -> list[str]:
    """Use Gemini to determine which open tasks were completed by the given commits."""
    if not settings.GEMINI_API_KEY:
        return []

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    prompt = _build_analyze_commits_prompt(commit_messages, open_tasks)

    text = _call_gemini(client, prompt)
    if text is None:
        return []

    parsed = _parse_json_array(text)
    if isinstance(parsed, list):
        open_task_set = set(open_tasks)
        return [t for t in parsed if isinstance(t, str) and t in open_task_set]

    print(f'[ERROR] Failed to parse Gemini JSON for analyze_commits. Raw: {text[:200]}')
    traceback.print_exc()
    return []
