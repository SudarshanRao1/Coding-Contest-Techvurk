import json
import time
from google.genai import types
from google.genai.errors import ClientError

RESEARCHER_PROMPT = '''
You are the Research Agent in an autonomous research system.

You will be given a numbered list of research questions.

Your task is to investigate ALL of them together using Google Search in a
single research pass, since they are related sub-questions of one broader
research topic.

Instructions:

1. Search the web for reliable information covering all the questions.
2. Prefer:
   - research papers
   - universities
   - government organizations
   - official documentation
   - established technical organizations
3. Avoid relying heavily on:
   - random blogs
   - SEO websites
   - unsourced claims
   - duplicate pages
4. Extract the important technical information for EACH question separately.
5. Clearly distinguish established facts from claims.
6. Do not invent sources.
7. Give a concise, evidence-oriented research response.

Return ONLY valid JSON in this exact format, with one entry per question,
in the same order they were given:

{
  "results": [
    {"question": "...", "answer": "..."},
    {"question": "...", "answer": "..."}
  ]
}

Do not include markdown code fences. Do not add any text outside the JSON.
'''


def _extract_sources(response):
    sources = []

    try:
        metadata = response.candidates[0].grounding_metadata
        if metadata and metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                if chunk.web:
                    source = {
                        "title": chunk.web.title,
                        "url": chunk.web.uri
                    }

                    if source["url"]:
                        sources.append(source)
    except Exception:
        pass

    return sources


def researching_batch(client, model, questions, max_retries=3):
    numbered_questions = "\n".join(
        f"{i+1}. {q}" for i, q in enumerate(questions)
    )

    prompt = f"Research the following questions:\n\n{numbered_questions}"

    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=RESEARCHER_PROMPT,
                    tools=[
                        types.Tool(
                            google_search=types.GoogleSearch()
                        )
                    ],
                    temperature=0.2
                )
            )

            sources = _extract_sources(response)

            raw_text = response.text.strip()

            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:].strip()

            try:
                parsed = json.loads(raw_text)
                parsed_results = parsed.get("results", [])
            except json.JSONDecodeError:
                parsed_results = []

            results = []

            for i, question in enumerate(questions):
                if i < len(parsed_results):
                    answer = parsed_results[i].get("answer", raw_text)
                else:
                    answer = raw_text

                results.append({
                    "question": question,
                    "answer": answer,
                    "sources": sources
                })

            return results

        except ClientError as e:
            last_error = e

            if getattr(e, "code", None) == 429 and attempt < max_retries - 1:
                wait = 15 * (attempt + 1)
                print(f"Rate limited (429), retrying in {wait}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                raise

    raise last_error


def running_research(client, model, research_question):
    print("agent searching (single batched grounded call):\n")

    for question in research_question:
        print(question)

    return researching_batch(client, model, research_question)
