import json 
from google import genai
from google.genai import types

PLANNER_PROMPT = '''
You are the Planner Agent of an autonomous research system.

Your job is to convert the user's research request into a clear research plan.

You must:
1. Understand the user's main objective.
2. Break the objective into independent research questions.
3. Generate useful web-search queries.
4. Identify what evidence should be collected.
5. Avoid unnecessary questions.
6. Keep the research plan focused.

Return ONLY valid JSON in this format:

{
    "main_topic": "...",
    "research_questions": [
        "...",
        "...",
    ],
    "search_queries": [
        "...",
        "...",
    ],
    "expected_output": "..."
}
'''

def create_planner(client,model,user_question):
    response = client.models.generate_content(model = model, contents = user_question , config = types.GenerateContentConfig( system_instruction = PLANNER_PROMPT, temperature=0.2 , response_mime_type="application/json"))

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        raise ValueError("Planner is invalid json:  ", response.text)

