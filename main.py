import os
import json
from dotenv import load_dotenv
from google import genai
from Agents.planning_agent import create_planner
from Agents.researching_agent import running_research
from Agents.summarizing_agent import summarize
from Tools.web_scraper import scrape_sources

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL","gemini-3.5-flash-lite")
print("MODEL BEING USED:", MODEL)

if not API_KEY:
    raise ValueError(
        "gemini api key is missing from .env"
    )

client = genai.Client(
    api_key=API_KEY
)

def collect_sources(research_results):
    sources = []

    for result in research_results:
        for source in result["sources"]:
            if source not in sources:
                sources.append(source)
    return sources

def save_json(data,filename):
    with open(filename,"w",encoding="utf-8") as file:
        json.dump(data,file,indent=2,ensure_ascii=False)

def main():

    print("-----------------------------------------------")
    print("             Our Research Agent                ")
    print("-----------------------------------------------")

    user_question = input("enter your Query:  ").strip()

    if not user_question:
        print("nothing is provided")
        return 

    # here is the planning agent

    print("\n Planning is going on")

    plan = create_planner(
        client,
        MODEL,
        user_question
    )

    # print("\n Research is going on")

    print("plan for the research: ")

    print(json.dumps(plan,indent = 2 , ensure_ascii=False))

    # here is the research agent

    print("\n research is going on")

    research_results = running_research(client,MODEL,plan["research_questions"])

    # here is the scraping of web

    print("\n web scraping is going on")

    sources = collect_sources(research_results)

    scraped_pages = scrape_sources(sources,max_sources=8)


    print(f"scrapped {len(scraped_pages)} sources")

    # here is the summarizing part

    print("\n summarizing agent")

    final_report = summarize(client,MODEL,user_question,research_results,scraped_pages)

    os.makedirs(
        "outputs",
        exist_ok=True
    )


    with open(
        "outputs/research_report.md",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(final_report)


    save_json(
        {
            "user_query": user_question,
            "plan": plan,
            "research": research_results,
            "scraped_pages": scraped_pages
        },
        "outputs/research_trace.json"
    )


    print("\n" + "=" * 60)

    print("FINAL RESEARCH REPORT")

    print("=" * 60)

    print(final_report)

    print("\nReport saved to:")

    print(
        "outputs/research_report.md"
    )

    print(
        "outputs/research_trace.json"
    )


if __name__ == "__main__":
    main()   