import json
import re

PROMPT_PARSE_CATEGORY_AND_TAGS = """
You are a expert in categorizing contents.

Your task is to analyze the content and determine its category and relevant tags.

Your output should be a JSON object with the following structure:

```json
{{
    "category": "string",  # The category of the content
    "category_emoji": "string",  # An optional emoji representing the category
    "tags": ["string1", "string2", ...]  # A list of relevant tags
}}
```

For example, the category could be "AI", "Travel", etc., and the tags should be specific to the content, like "RAG", "LLM-Agent", "New York", etc.

currently, we have the following categories:

{categories}

## Limitations
- If the content does not fit into any of the existing categories, you should create a new category.
- Provide at least one tag but MUST no more than 5 tags.
"""

PROMPT_SUMMARIZE_CONTENT = """
You are a expert in summarizing contents.
Your task is to analyze the content and generate a concise summary.

Your output should be a JSON object with the following structure:

```json
{{
    "summary": "string"  # The summary of the content
}}
```
"""

def parse_json(text: str) -> dict:
    """Parse a JSON object from the given text.

    Args:
        text (str): The text to parse.

    Returns:
        dict: The parsed JSON object.
    """
    # Remove the code block markers
    if """```""" not in text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}
    pattern = re.compile(r"(?i)```json[\s\r\n]*(.*?)```", re.DOTALL)
    matches = pattern.findall(text)
    return json.loads(matches[0]) if matches else {}
