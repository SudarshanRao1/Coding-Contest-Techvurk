import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", bool(api_key))

client = genai.Client(
    api_key=api_key
)


MAX_RETRIES = 5


for attempt in range(1, MAX_RETRIES + 1):

    try:

        print(
            f"\nAttempt {attempt}/{MAX_RETRIES}"
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Say hello in one sentence."
        )

        print("\nGemini response:")
        print(response.text)

        break

    except Exception as e:

        print(
            f"\nGemini request failed:"
        )

        print(e)

        if attempt == MAX_RETRIES:

            print(
                "\nGemini is still unavailable."
            )

            print(
                "Please try again later."
            )

            raise

        wait_time = 2 ** attempt

        print(
            f"\nRetrying in {wait_time} seconds..."
        )

        time.sleep(wait_time)