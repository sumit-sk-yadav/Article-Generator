"""Task definitions for the content generation crew"""
from crewai import Task
from crewai_tools import ScrapeWebsiteTool, TavilySearchTool

def create_plan_task(planner_agent):
    """Planner performs REAL research and outputs structured scraped data"""

    search_tool = TavilySearchTool()
    scrape_tool = ScrapeWebsiteTool()

    return Task(
        description=(
            "Your ONLY job is to collect verifiable research about: {topic}.\n"
            "Do NOT write a narrative, do NOT outline content. Just research.\n\n"

            "PROCESS:\n"
            "1. Use TavilySearchTool to search for pages ONLY related to {topic}.\n"
            "2. For each search result URL:\n"
            "      - Scrape the page using ScrapeWebsiteTool\n"
            "      - Extract EXACT material from the page (no paraphrasing)\n\n"

            "STRICT RULES:\n"
            "- NEVER invent URLs, stats, or quotes.\n"
            "- If scraping fails, skip the URL. Do NOT guess or hallucinate missing content.\n"
            "- If content doesn’t mention {topic}, discard it.\n\n"

            "OUTPUT FORMAT (MANDATORY):\n"
            "Return ONLY a JSON list like this:\n"
            "[\n"
            "  {\n"
            "    'url': 'https://real-url.com/article',\n"
            "    'source': 'Harvard Business Review',\n"
            "    'title': 'Aligning AI Strategy in 2025',\n"
            "    'excerpt': 'Exact paragraph scraped from the page... ',\n"
            "    'stats': ['Copied stat 1', 'Copied stat 2'],\n"
            "    'quotes': ['Copied quote from the source']\n"
            "  }\n"
            "]\n\n"

            "IMPORTANT:\n"
            "- Do NOT produce bullet points or narrative writing.\n"
            "- Output MUST be valid JSON only. No commentary outside JSON."
        ),
        expected_output=(
            "JSON array with scraped research objects. "
            "Each object includes: url, source, title, excerpt, stats, quotes."
        ),
        tools=[search_tool, scrape_tool],
        agent=planner_agent,
    )



def create_write_task(writer_agent, plan_task):
    """Writer uses the structured research JSON to write the article"""

    return Task(
        description=(
            "You are given structured research scraped from real URLs.\n"
            "You must write a Medium article ONLY about: {topic}.\n"
            "Use ONLY the content inside the JSON research data.\n\n"

            "STRICT PROHIBITIONS:\n"
            "- Do NOT add new research.\n"
            "- Do NOT invent URLs, stats, or quotes.\n"
            "- If something is missing, skip it. Do NOT guess.\n\n"

            "Your output MUST:\n"
            "- Be 2000–2500 words\n"
            "- Use sections (## 1. Section Title)\n"
            "- Naturally cite data from the research JSON\n"

            "When citing URLs:\n"
            "- Use the exact URL from the JSON\n"
            "- If a JSON item has missing URL or title, write: 'URL unavailable in research data'\n"
        ),
        expected_output=(
            "A full article (2000–2500 words) created ONLY from the planner's JSON research."
        ),
        tools=[],
        context=[plan_task],   # <-- The planner's output is passed here
        agent=writer_agent,
    )




def create_edit_task(editor_agent, write_task):
    """Create editing task with topic and URL verification"""
    return Task(
        description=(
            "Edit the article with THREE critical checks:\n\n"
            "1. TOPIC VERIFICATION:\n"
            "   - Is this article ACTUALLY about: {topic}?\n"
            "   - If the article is about a different topic, REJECT IT\n"
            "   - Every section must relate to: {topic}\n\n"
            "2. URL VERIFICATION:\n"
            "   - Check EVERY reference URL\n"
            "   - REMOVE any fake/placeholder URLs like:\n"
            "     * https://buffer.com/... (if topic isn't about Buffer)\n"
            "     * https://example.com/...\n"
            "     * https://news.microsoft.com/... (if topic isn't about Microsoft)\n"
            "   - ONLY keep URLs that appear genuine and relevant to {topic}\n"
            "   - If uncertain, replace with: 'Source Title (URL unavailable)'\n\n"
            "3. CONTENT POLISHING:\n"
            "   - Remove: marketing speak, bullet lists, SEO sections\n"
            "   - Remove: <think> tags or internal reasoning\n"
            "   - Enhance: conversational flow, natural transitions\n"
            "   - Verify: proper markdown, short paragraphs\n\n"
            "- If any sentence is not clearly supported by research JSON, remove it."

            "OUTPUT:\n"
            "Return ONLY the final article that:\n"
            "- Is genuinely about {topic} (not a different topic)\n"
            "- Has ONLY real reference URLs (or marked as unavailable)\n"
            "- Has NO <think> tags, fake URLs, or off-topic content\n"
            "- Reads like an engaging Medium story"
        ),
        expected_output=(
            "Publication-ready article that: "
            "is concretely about {topic}, "
            "has ONLY verified real URLs or marked unavailable, "
            "NO fake reference links, "
            "NO off-topic content, "
            "conversational tone, "
            "proper markdown formatting"
        ),
        tools=[],
        context=[write_task],
        agent=editor_agent,
    )
