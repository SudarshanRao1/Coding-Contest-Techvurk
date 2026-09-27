import os
import json

from dotenv import load_dotenv
from google import genai

from Agents.planning_agent import create_planner


load_dotenv()


API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


client = genai.Client(
    api_key=API_KEY
)


user_question = """
Tell me about Iron Man, including his history,
technology, abilities, and importance in Marvel.
"""


print("==============================================")
print("          TESTING PLANNER AGENT")
print("==============================================")

print("\nUser Question:")
print(user_question)


print("\nPlanning is going on...\n")


plan = create_planner(
    client,
    MODEL,
    user_question
)


print("Planner Output:")
print(
    json.dumps(
        plan,
        indent=4,
        ensure_ascii=False
    )
)