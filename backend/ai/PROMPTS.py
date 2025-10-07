import json
import re

ADDITIONAL_PROMPT_USER_LANGUAGE_PREFERENCE = "Your output should be Chinese."

PROMPT_PARSE_CATEGORY_AND_TAGS = """
You are an expert in categorizing contents.
Your task is to analyze the content and determine its category and relevant tags.

## Output Format

You MUST output a JSON object with the following structure:

```json
{{
    "category": "string",  # The category name of the content
    "category_emoji": "string",  # An emoji representing the category
    "tags": ["string1", "string2", ...]  # A list of relevant tags
}}
```

## Rules
1. Category Matching:
    - You are given a predefined list of existing categories: {categories}
    - You should select a proper category from this list if there is any reasonable match.
    - If multiple categories seem possible, avoid general categories when a more precise category exists.

2. New Category Creation:
    - Only if the content truly does not match any existing category, you may create a new one.
    - New categories must be concise, general, and not duplicates of existing ones.

3. Tags Generation:
    - Always provide at least 1 tag and no more than 5 tags.
    - Tags should be specific keywords relevant to the content.
    - Avoid repeating the category name as a tag unless strictly necessary.
"""

PROMPT_SUMMARIZE_CONTENT = """
You are an expert in summarizing contents.
Your task is to analyze the content and generate a concise summary.

## Output Format

Your output should be a JSON object with the following structure:

```json
{{
    "summary": "string"  # The summary of the content
}}
```
"""

KNOWLEDGE_BASE_QUERY_PROMPT = """
You will be given several documents that related to the user's query.
Your task is to analyze the documents and generate a concise answer to the user's query.

## Documents

{documents}
"""

PICTURE_PROMPT = """
Analyze the image and generate a JSON object like:

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

PROMPT_RECOMMEND_POSTS = """
You are an expert recommendation system for a collection-based social platform.

Your task is to recommend posts that match the user's interests based on their collection patterns.

## User's Top Categories (by collection count):
{user_categories}

## Recent Posts Available:
{posts_info}

## Instructions:
1. Understand user's primary interests
2. Select posts that align with the user's interests
3. Prioritize posts with tags or titles that closely relate to the user's categories

## Output Format:
Return a JSON object with the following structure:
```json
{{
    "recommended_post_ids": [post_id1, post_id2, ...],  # Post IDs here are integers
    "explanations": {{
        "post_id1": "brief reason why this post was recommended",
        "post_id2": "brief reason why this post was recommended"
    }}
}}
```

## Rules:
- Always return valid JSON
- The recommended_post_ids should be a list of integers
- Only recommend post IDs that exist in the provided posts list
- Order the recommendations by relevance (most relevant first)
- Return at least 1 post ID, but no more than {max_recommendations}
"""
