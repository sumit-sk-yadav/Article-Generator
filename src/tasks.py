"""Task definitions for the content generation crew"""
from crewai import Task
from crewai_tools import ScrapeWebsiteTool, TavilySearchTool

def create_plan_task(planner_agent):
    """Planner researches deeply and returns detailed scraped data"""

    search_tool = TavilySearchTool(
        search_depth = "advanced",
        max_results = 15,
        include_raw_content = True,
    )
    scrape_tool = ScrapeWebsiteTool()

    return Task(
        description=(
            "Your ONLY output will be structured research data about: {topic}.\n"
            "You must return as MUCH data as possible — do NOT summarize, do NOT write narratives.\n\n"

            "STEP-BY-STEP PROCESS:\n"
            "1) Perform MULTIPLE searches using TavilySearchTool.\n"
            "   - Use variations of the search query.\n"
            "   - Example: '{topic} benefits', '{topic} challenges', '{topic} examples', '{topic} statistics'.\n"
            "   - Continue generating new queries until no new results appear.\n\n"

            "2) For EVERY returned URL:\n"
            "   - Scrape the page using ScrapeWebsiteTool.\n"
            "   - Extract ALL of the following if available:\n"
            "       * Page title\n"
            "       * The full body text / large paragraphs\n"
            "       * Lists of statistics (exact numbers only)\n"
            "       * Quotes (must be verbatim)\n"
            "       * Company names, report names, author, publication\n\n"

            "STRICT RULES:\n"
            "- NO summarizing.\n"
            "- NO rewriting text.\n"
            "- NO hallucinating missing stats.\n"
            "- If scraping fails or data doesn’t mention {topic}, SKIP IT.\n\n"

            "OUTPUT FORMAT (MANDATORY):\n"
            "Return ONLY valid JSON like this:\n"
            "[\n"
            "  {\n"
            "    'url': 'https://real-url.com/article',\n"
            "    'source': 'Harvard Business Review',\n"
            "    'title': 'Aligning AI Strategy in 2025',\n"
            "    'content': 'Full scraped body text... (NOT summarized)',\n"
            "    'stats': ['Copied stat 1', 'Copied stat 2'],\n"
            "    'quotes': ['Exact quote from the page'],\n"
            "    'insights': ['Short extracted insights (copied phrases only — no interpretation)']\n"
            "  }\n"
            "]\n\n"

            "FINAL CHECK BEFORE RETURNING:\n"
            "- Does every item contain REAL data from scraping?\n"
            "- JSON only — no storytelling, no bullet points outside JSON.\n"
        ),
        expected_output=(
            "A detailed JSON array with multiple research objects containing large scraped text, "
            "multiple stats, quotes, and deep extraction."
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
            "- Be 3000–3500 words\n"
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
