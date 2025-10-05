import json
import re

ADDITIONAL_PROMPT_USER_LANGUAGE_PREFERENCE = "Your output should be Chinese."

PROMPT_PARSE_CATEGORY_AND_TAGS = """
You are a expert in categorizing contents.

Your task is to analyze the content and determine its category and relevant tags.

You must output a JSON object with the following structure:

```json
{{
    "category": "string",  # The category of the content
    "category_emoji": "string",  # An optional emoji representing the category
    "tags": ["string1", "string2", ...]  # A list of relevant tags
}}
```

## Rules
1. Strict Category Matching

    - You are given a predefined list of categories:
    {categories}

    - You must always select from this list if there is any reasonable match.

    - Do NOT create a new category if an existing one is suitable (even approximately).

2. Conflict Resolution

    - If multiple categories seem possible:

        - Prefer the most specific one.

        - Avoid general or vague categories when a more precise category exists.

3. New Category Creation

    - Only if the content truly does not match any existing category, you may create a new one.

    - New categories must be concise, general, and not duplicates of existing ones.

4. Tags

    - Always provide at least 1 tag and no more than 5 tags.

    - Tags should be specific keywords relevant to the content.

    - Avoid repeating the category name as a tag unless strictly necessary.

## Output Format

Return only the JSON object.
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


# 新的 prompts
# 提示AI通过知识库中的内容查找用户想要的收藏词条 TODO
COLLECTION_SEARCH_PROMPT = """
You are an expert in analyzing and matching user queries with collection data.

Your task is to analyze the user's query and find the most relevant collection from the provided context.

Context format:
Each collection is provided in the following format:
Collection ID: [collection_id]
URL: [url]
Title: [title]
Summary: [summary]
---

User Query: {query}

Collections Context:
{collections_context}

## Instructions:
1. Carefully analyze the user's query to understand what they are looking for
2. Compare the query against the titles and URLs of all collections
3. Consider semantic similarity, not just exact keyword matches
4. Choose the collection that best matches the user's intent
5. If no collection seems relevant, return null

## Output Format:
Return only a JSON object with the following structure:
```json
{{
    "collection_id": "string or null",  # The ID of the most relevant collection, or null if no good match
    "confidence": "high|medium|low",    # Your confidence level in this match
    "reason": "string"                  # Brief explanation of why this collection was chosen
}}
```

## Rules:
- Always return valid JSON
- Be selective - only return a collection_id if you are reasonably confident it matches
- Consider the context and intent behind the user's query
- Prefer exact matches in titles, but also consider semantic relevance
"""
