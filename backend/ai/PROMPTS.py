import json
import re

ADDITIONAL_PROMPT_USER_LANGUAGE_PREFERENCE = "Your output should be Chinese."

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

KNOWLEDGE_BASE_QUERY_PROMPT = """
You will be givel several documents that related to the user's query.
Your task is to analyze the documents and generate a concise answer to the user's query.

Documents:
{documents}
"""

PICTURE_PROMPT = """
Anaylize the image and generate a JSON object like:

```json
{{
    "tags": ["tag1", "tag2", ...],  # A list of relevant tags
}}
```

User selected the category of the image is: {category}

## Limitations
If the provided category is one of the following, please try your best to include the following tags value:
- food: meal_type, foods_item(such as 鸡肉, 黑鱼片, 山竹), estimated_calories(such as `500kcal`)
- location: city_or_spot_name, coordinates(such as `40.7128,74.0060`), weather_condition
- exercise: type(such as 跑步, 骑行), intensity, duration_minutes
- learning: duration_minutes(such as `32min`), topics
- programming: tech_stack(such as Python, FastAPI)

If you cannot infer the tag value, do not add to it.
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
