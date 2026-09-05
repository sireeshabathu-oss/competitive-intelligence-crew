"""
Defines the Competitive Intelligence crew: two agents working in sequence.

1. Searcher - gathers raw information about a company/competitor from the web
2. Analyst   - turns that raw research into a structured competitive intel report
"""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

load_dotenv()

MODEL = os.getenv("MODEL", "gpt-4o-mini")


def _build_search_tool() -> SerperDevTool:
    if not os.getenv("SERPER_API_KEY"):
        raise RuntimeError(
            "SERPER_API_KEY is not set. Get a free key at https://serper.dev and add it to your .env file."
        )
    try:
        return SerperDevTool()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize the Serper search tool: {e}") from e


def build_crew(company_name: str, focus_areas: str) -> Crew:
    if not company_name or not company_name.strip():
        raise ValueError("company_name must not be empty.")

    search_tool = _build_search_tool()

    searcher = Agent(
        role="Market Research Searcher",
        goal=(
            f"Find current, factual information about {company_name}: its products, "
            "pricing, recent news, leadership changes, funding, and public statements "
            "relevant to the requested focus areas."
        ),
        backstory=(
            "You are a sharp research analyst who knows how to find reliable, "
            "up-to-date information quickly. You prioritize primary sources "
            "(company sites, press releases, filings) over rumor or speculation, "
            "and you always note where information came from."
        ),
        tools=[search_tool],
        verbose=True,
        llm=MODEL,
    )

    analyst = Agent(
        role="Competitive Intelligence Analyst",
        goal=(
            "Turn raw research into a clear, structured competitive intelligence "
            "report that a business or product team could act on."
        ),
        backstory=(
            "You are a senior strategy consultant who has written hundreds of "
            "competitor briefings. You are excellent at separating signal from "
            "noise, spotting strategic implications, and writing concisely."
        ),
        verbose=True,
        llm=MODEL,
    )

    research_task = Task(
        description=(
            f"Research {company_name}, focusing on: {focus_areas}. "
            "Search for recent news, product updates, pricing changes, leadership "
            "moves, and any public statements relevant to these focus areas. "
            "Note the source and approximate date for each finding."
        ),
        expected_output=(
            "A raw list of findings about the company, each with a short note on "
            "source and recency."
        ),
        agent=searcher,
    )

    report_task = Task(
        description=(
            "Using the research findings, write a competitive intelligence report "
            f"on {company_name} covering: {focus_areas}. Structure it with clear "
            "headers: Summary, Key Findings (bulleted, grouped by focus area), "
            "Strategic Implications, and Open Questions / What to Watch Next."
        ),
        expected_output=(
            "A structured Markdown competitive intelligence report with the "
            "sections described above."
        ),
        agent=analyst,
        context=[research_task],
    )

    return Crew(
        agents=[searcher, analyst],
        tasks=[research_task, report_task],
        process=Process.sequential,
        verbose=True,
    )
