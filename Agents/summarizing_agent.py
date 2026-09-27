import json

SUMMARIZER_PROMPT = '''
You are the Senior Research Synthesizer Agent.

You receive research findings and scraped source material.

Your job is to create a high-quality research report.

Rules:

1. Use ONLY the provided research evidence.
2. Do not invent facts.
3. Do not invent citations.
4. Clearly identify uncertainty.
5. Combine information from multiple sources.
6. Remove duplicate information.
7. Highlight disagreements between sources.
8. Prefer technical and primary sources when available.

Structure the report as:

# Research Report

## 1. Executive Summary

## 2. Research Questions

## 3. Key Findings

## 4. Detailed Analysis

## 5. Comparison / Synthesis

## 6. Limitations

## 7. Conclusion

## 8. Sources

Use the supplied source URLs in the Sources section.
'''

def build_research_context(research_results,scrapped_pages):
    context = []

    context.append("Search Results:  \n")

    for item in research_results:

        context.append(
            f"QUESTION:\n{item['question']}\n"
        )

        context.append(
            f"RESEARCH ANSWER:\n{item['answer']}\n"
        )

        context.append(
            "SOURCES:\n"
        )

        for source in item["sources"]:

            context.append(
                f"- {source.get('title')} "
                f"| {source.get('url')}\n"
            )
    context.append("\n Scrapped Web Content  \n")

    for page in scrapped_pages:
        context.append(
            f"\nSOURCE: {page['title']}\n"
        )

        context.append(
            f"URL: {page['url']}\n"
        )

        context.append(
            f"CONTENT:\n{page['content']}\n"
        )

    return "\n".join(context)


def summarize(client,model,user_question,research_results,scrapped_pages):
    context = build_research_context(research_results,scrapped_pages)

    prompt = f"""
Original user research request:

{user_question}

Below is the research collected by the system:

{context}

Create the final research report now.
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "system_instruction": SUMMARIZER_PROMPT,
            "temperature": 0.2
        }
    )

    return response.text