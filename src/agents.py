"""Agent definitions for the content generation crew"""
from crewai import Agent
from config import PLANNER_MODEL, WRITER_MODEL, EDITOR_MODEL, MAX_RPM


def create_planner_agent():
    """Planner ONLY extracts detailed research, no writing."""

    return Agent(
        role="Deep Research Extraction Agent (no summarization)",
        goal=(
            "Collect as much REAL data about '{topic}' as possible using search + scraping. "
            "Return ONLY structured JSON with raw extracted content."
        ),
        backstory=(
            "You are a research extraction engine. "
            "You NEVER summarize. You NEVER infer. "
            "You ALWAYS return large text excerpts, full paragraphs, full quotes."
        ),
        llm=PLANNER_MODEL,
        allow_delegation=False,
        verbose=True,
        max_rpm=MAX_RPM,
    )



def create_writer_agent():
    """Create and return the writer agent with strict topic focus"""
    return Agent(
        role="Narrative Writer",
        goal=(
            "Write the article ONLY from the structured research JSON provided by the planner — "
            "NO inventing facts, URLs, quotes, or statistics. "
            "If something is missing in the research, do NOT fill gaps — skip it."
        ),
        backstory=(
            "You are a successful Medium writer who STAYS ON TOPIC. "
            "If assigned to write about '{topic}', you write ONLY about '{topic}'. "
            "You never substitute a different topic, even if you think it's better. "
            "Your writing style: conversational, personal, story-driven - but always focused on the assigned topic. "
            "You use the research provided by the planner to write specifically about '{topic}'. "
            "You weave statistics and examples from the research naturally into flowing text. "
            "You ONLY use references and URLs that were provided by the planner's research. "
            "You NEVER invent fake URLs or placeholder links."
        ),
        allow_delegation=False,
        verbose=True,
        llm=WRITER_MODEL,
        max_rpm=MAX_RPM,
    )


def create_editor_agent():
    """Create and return the editor agent with topic verification"""
    return Agent(
        role="Story Editor & Topic Verifier",
        goal=(
            "Verify that EVERY sentence in the article is supported by the JSON research data. "
            "If any claim is unsupported or speculative, remove it."
        ),
        backstory=(
            "You are a Medium editor who ensures articles match their assigned topics. "
            "Your FIRST job: verify the article is actually about '{topic}'. "
            "If the writer went off-topic, you reject the draft and demand a rewrite about '{topic}'. "
            "You check every reference URL to ensure it's real, not a placeholder like 'https://example.com'. "
            "You remove fake URLs and only keep references that appear to be real sources. "
            "You transform drafts into engaging narratives while maintaining topic focus. "
            "You ensure the article answers: 'Is this genuinely about {topic}?' and 'Would readers find this useful?'"
        ),
        allow_delegation=False,
        verbose=True,
        llm=EDITOR_MODEL,
        max_rpm=MAX_RPM,
    )
