import json
import google.generativeai as genai
from django.conf import settings


def analyze_commits(commit_messages: list[str], open_tasks: list[str]) -> list[str]:
    """Use Gemini to determine which open tasks were completed by the given commits.

    Returns a list of task titles that Gemini considers completed.
    """
    if not settings.GEMINI_API_KEY:
        return []

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')

    prompt = (
        "You are an assistant that analyzes git commit messages to detect task completion.\n\n"
        f"Open tasks:\n{json.dumps(open_tasks)}\n\n"
        f"Commit messages:\n{json.dumps(commit_messages)}\n\n"
        "Return a JSON array of task titles (from the open tasks list) that these commits indicate "
        "are completed. Only include tasks you are confident were addressed. "
        "Return an empty array if none match. Respond with ONLY the JSON array, no other text."
    )

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Strip markdown code fences if present
    if text.startswith('```'):
        text = text.split('\n', 1)[-1].rsplit('```', 1)[0].strip()

    try:
        result = json.loads(text)
        if isinstance(result, list):
            return [t for t in result if t in open_tasks]
    except (json.JSONDecodeError, TypeError):
        pass

    return []
