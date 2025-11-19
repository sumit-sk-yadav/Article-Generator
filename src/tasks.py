"""Task definitions for the content generation crew"""
from crewai import Task
from crewai_tools import ScrapeWebsiteTool, TavilySearchTool

def create_plan_task(planner_agent):
    """Planner researches deeply and returns detailed scraped data"""

    search_tool = TavilySearchTool(
        search_depth="advanced",
        max_results=15,
        include_answer=True
    )
    scrape_tool = ScrapeWebsiteTool()

    return Task(
        description=(
            "Your ONLY output will be structured research data about: {topic}.\n"
            "Return AS MUCH raw data as possible. Do NOT summarize, paraphrase, "
            "compress, or add interpretation.\n\n"

            "WORKFLOW:\n"
            "1. Perform MULTIPLE searches using TavilySearchTool:\n"
            "   - Use MANY query variations (e.g., '{topic} benefits', "
            "'{topic} challenges', '{topic} statistics', '{topic} case studies').\n"
            "   - Continue generating and executing new searches until results stop changing.\n\n"

            "2. For EVERY discovered URL:\n"
            "   - Scrape it using ScrapeWebsiteTool.\n"
            "   - Extract and copy ALL available raw information:\n"
            "       * Full page title\n"
            "       * Full body text (large paragraphs welcomed)\n"
            "       * Exact statistics (verbatim)\n"
            "       * Exact quotes\n"
            "       * Company names, authors, report names, publication details\n"
            "       * Any lists, examples, definitions (word-for-word)\n\n"

            "STRICT RULES:\n"
            "- NO summarizing, rewriting, or condensing.\n"
            "- NO hallucinating or filling in missing content.\n"
            "- If scraping fails OR content does not meaningfully discuss {topic}, SKIP IT.\n\n"

            "OUTPUT FORMAT (MANDATORY JSON):\n"
            "[\n"
            "  {\n"
            "    'url': 'https://real-url.com/article',\n"
            "    'source': 'Publication Name',\n"
            "    'title': 'Exact page title',\n"
            "    'content': 'Full scraped body text (not summarized)',\n"
            "    'stats': ['Copied stat 1', 'Copied stat 2'],\n"
            "    'quotes': ['Exact quote 1', 'Exact quote 2'],\n"
            "    'insights': ['Copied phrases only — absolutely no interpretation']\n"
            "  }\n"
            "]\n\n"

            "FINAL CHECK BEFORE RETURNING:\n"
            "- JSON only.\n"
            "- Every field must be copied exactly from the source page.\n"
            "- Absolutely ZERO narrative or analysis.\n"
        ),
        expected_output=(
            "A deeply detailed JSON array containing raw scraped text, "
            "verbatim stats, quotes, and extracted factual elements."
        ),
        tools=[search_tool, scrape_tool],
        agent=planner_agent,
    )


def create_write_task(writer_agent, plan_task):
    """Writer transforms the structured research JSON into a deep, fully-developed article"""

    return Task(
        description=(
            "You are given structured research scraped from real URLs.\n"
            "You must write an exceptionally detailed, long-form Medium article ONLY about: {topic}.\n"
            "Use ONLY the content inside the JSON research data—no outside knowledge.\n\n"

            "ARTICLE LENGTH (MANDATORY):\n"
            "- The article MUST be long and deeply developed.\n"
            "- Minimum length: **3000–3500 words**.\n"
            "- It MUST be a true 10-minute read: rich, layered, reflective, analytical.\n"
            "- Short or shallow content is not acceptable.\n\n"

            "CONTENT REQUIREMENTS FOR EACH SECTION:\n"
            "- Use sections formatted as: ## 1. Section Title\n"
            "- Each section must include:\n"
            "    • Deep background context extracted from multiple research items\n"
            "    • Technical explanations or conceptual analysis\n"
            "    • Practical examples and scenario breakdowns\n"
            "    • Side-by-side comparisons (when supported by research)\n"
            "    • Interpretation of statistics, quotes, or factual claims\n"
            "    • What the data implies, why it matters, and who it affects\n"
            "    • Suggestions for visuals, diagrams, or tables (no new data)\n"
            "    • Multi-paragraph depth—not surface summaries\n\n"

            "WRITING STYLE:\n"
            "- Polished, narrative, publication-quality prose.\n"
            "- No bullet-point dumping; information must be fully woven together.\n"
            "- Transitions should be smooth and explanatory.\n"
            "- Use analogies, storytelling hooks, and conceptual metaphors **only when derived from research**.\n\n"

            "STRICT PROHIBITIONS:\n"
            "- NO new research, NO external facts, NO invented claims.\n"
            "- NO guessing missing information.\n"
            "- NO invented URLs or quotes.\n"
            "- NO shallow summary paragraphs.\n\n"

            "CITATION RULES:\n"
            "- Cite URLs naturally in text using the EXACT URLs from the JSON.\n"
            "- If a JSON item is missing a URL: cite as 'URL unavailable in research data'.\n\n"

            "Your goal is to produce one of the most thorough, deeply-crafted, "
            "long-form articles possible using only the research provided.\n"
        ),
        expected_output=(
            "A polished, long-form 3000–3500 word article with deep analysis, "
            "narrative richness, and citations sourced ONLY from the planner's JSON."
        ),
        tools=[],
        context=[plan_task],
        agent=writer_agent,
    )


def create_edit_task(editor_agent, write_task):
    """Final editing: verification, purification, polishing"""

    return Task(
        description=(
            "Perform a rigorous final edit with THREE verification layers.\n\n"

            "1. TOPIC VERIFICATION:\n"
            "   - Ensure the entire article is unmistakably and consistently about: {topic}.\n"
            "   - Remove or rewrite any section that strays from {topic}.\n\n"

            "2. URL & CITATION VERIFICATION:\n"
            "   - Verify that EVERY cited URL appears exactly in the research JSON.\n"
            "   - Remove ANY fake, placeholder, irrelevant, or hallucinated URLs.\n"
            "   - If unsure, replace with: 'Source Title (URL unavailable)'.\n\n"

            "3. CONTENT POLISHING:\n"
            "   - Remove filler, marketing tone, SEO language, repetitive content.\n"
            "   - Improve narrative flow and transitions.\n"
            "   - Ensure clean Markdown formatting.\n"
            "   - Remove ANY statement not directly supported by research JSON.\n"
            "   - Remove all <think> tags or chain-of-thought artifacts.\n"
            "   - Preserve the long-form, detailed structure—do NOT shorten excessively.\n\n"

            "OUTPUT:\n"
            "Return ONLY the final, publication-ready article that:\n"
            "- Is genuinely about {topic}\n"
            "- Has only real research URLs or marks them unavailable\n"
            "- Has no hallucinated claims or fake links\n"
            "- Reads smoothly, professionally, and with long-form depth\n"
        ),
        expected_output=(
            "A final, publication-ready Medium article that is accurate, "
            "on-topic, citation-corrected, cleanly formatted, and long-form."
        ),
        tools=[],
        context=[write_task],
        agent=editor_agent,
    )
